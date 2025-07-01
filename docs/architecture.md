# Architecture: Jenkins + Prefect Integration

This document explains the clean separation of concerns between Jenkins (build-time) and Prefect (runtime) in our CI/CD pipeline.

## Overview

We use a **two-tier secret management approach**:

- **Jenkins**: Handles build-time credentials and secrets
- **Prefect**: Manages runtime environment variables for Kubernetes clusters

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Git Repo      │    │    Jenkins      │    │    Prefect      │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │   Code      │ │    │ │ Build       │ │    │ │ Runtime     │ │
│ │ Jenkinsfile │ │───▶│ │ Credentials │ │───▶│ │ Secrets     │ │
│ │             │ │    │ │             │ │    │ │             │ │
│ │             │ │    │ │ • Git       │ │    │ │ • Database  │ │
│ │             │ │    │ │ • Docker    │ │    │ │ • API Keys  │ │
│ │             │ │    │ │ • Registry  │ │    │ │ • K8s Config│ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Docker Image  │    │   K8s Cluster   │
                       │                 │    │                 │
                       │ • Built with    │    │ • Runs with     │
                       │   Jenkins creds │    │   Prefect       │
                       │                 │    │   runtime vars  │
                       └─────────────────┘    └─────────────────┘
```

## Build-Time (Jenkins)

### Responsibilities
- Source code checkout
- Docker image building
- Image pushing to registry
- Prefect deployment

### Credentials Managed
```yaml
jenkins_credentials:
  - prefect-api-url: "https://your-prefect-instance.com"
  - prefect-api-key: "your-prefect-api-key"
  - docker-registry-credentials: "username/password"
  - git-credentials: "username/token"  # if private repo
```

### Pipeline Stages
1. **Checkout**: Get code from Git
2. **Setup Prefect**: Configure Prefect client
3. **Build Docker Image**: Create container image
4. **Push Docker Image**: Upload to registry
5. **Deploy to Prefect**: Deploy flow to Prefect

## Runtime (Prefect + K8s)

### Responsibilities
- Flow execution in Kubernetes
- Runtime environment configuration
- Dynamic secret retrieval
- Application-specific configuration

### Secrets Managed
```yaml
prefect_runtime_secrets:
  - database-url: "postgresql://user:pass@host:port/db"
  - external-api-keys: "key1,key2,key3"
  - k8s-namespace: "production"
  - k8s-service-account: "prefect-worker"
  - application-config: "json_config_string"
  - feature-flags: "enabled_features"
```

### Flow Execution
1. **Secret Retrieval**: Get runtime secrets from Prefect
2. **Environment Setup**: Configure runtime environment
3. **Task Execution**: Run tasks with runtime configuration
4. **Resource Management**: Handle K8s resources

## Benefits of This Approach

### 🔒 Security
- **Build secrets** stay in Jenkins (Docker registry, Git access)
- **Runtime secrets** managed by Prefect (database, APIs, K8s config)
- Different access controls for different environments

### 🔄 Scalability
- Runtime secrets can be updated without rebuilding images
- New secrets can be added without pipeline changes
- Environment-specific configurations

### 🛠️ Maintainability
- Clear separation of concerns
- Easier debugging (build vs runtime issues)
- Independent credential rotation

### 📋 Compliance
- Audit trails for both build and runtime access
- Different retention policies
- Environment-specific access controls

## Configuration Examples

### Jenkins Pipeline
```groovy
pipeline {
    environment {
        PREFECT_API_URL = credentials('prefect-api-url')
        PREFECT_API_KEY = credentials('prefect-api-key')
    }
    
    stages {
        stage('Push Docker Image') {
            steps {
                docker.withRegistry("https://${REGISTRY}", 'docker-registry-credentials') {
                    docker.image("${DOCKER_IMAGE}").push()
                }
            }
        }
    }
}
```

### Prefect Flow
```python
@task
def get_runtime_config():
    """Get runtime configuration from Prefect secrets."""
    secret = Secret.load("database-url")
    return secret.get()

@flow
def my_flow():
    db_url = get_runtime_config()
    # Use runtime configuration
```

## Migration Guide

### From Monolithic Secret Management

1. **Identify secret types:**
   - Build-time: Docker registry, Git access, Prefect API
   - Runtime: Database, APIs, K8s config, app settings

2. **Move build secrets to Jenkins:**
   ```bash
   # Remove from Prefect
   prefect secret delete docker-registry-username
   prefect secret delete docker-registry-password
   
   # Add to Jenkins credentials
   # (via Jenkins UI or JCasC)
   ```

3. **Keep runtime secrets in Prefect:**
   ```bash
   # These stay in Prefect
   prefect secret create database-url "your-db-url"
   prefect secret create external-api-keys "key1,key2"
   ```

4. **Update pipeline:**
   - Remove Prefect secret retrieval from Jenkinsfile
   - Use Jenkins credentials for build operations
   - Keep Prefect deployment stage

## Best Practices

### Jenkins Credentials
- Use least-privilege access
- Rotate regularly
- Use environment-specific credentials
- Monitor access logs

### Prefect Secrets
- Use descriptive names
- Version control secret schemas
- Implement secret rotation
- Monitor usage patterns

### Security
- Never commit secrets to code
- Use different credentials per environment
- Implement proper RBAC
- Regular security audits 