# ACME Automations

A production-ready Prefect 3 automation repository with Docker packaging and Kubernetes deployment.

## Quick Start

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd ACME-automations
   poetry install
   ```

2. **Configure Prefect blocks:**
   ```bash
   prefect block create secret stripe --value "sk_test_1234567890abcdef"
   prefect block create s3-bucket landing-bucket --bucket-name "my-landing-bucket"
   ```

3. **Deploy the flow:**
   ```bash
   prefect deploy -n example -p my-k8s-pool
   ```

4. **Run the flow:**
   ```bash
   prefect deployment run 'example/example'
   ```

5. **Monitor execution:**
   ```bash
   prefect flow-run logs <flow-run-id>
   ```

## CI/CD with Jenkins

This repository includes Jenkins integration with clean separation of concerns:

### Architecture

- **Jenkins**: Handles build-time credentials (Docker registry, Git access)
- **Prefect**: Manages runtime environment variables for K8s clusters

### Setup Jenkins Integration

1. **Configure Jenkins credentials:**
   ```bash
   # Add these as Jenkins credentials
   - prefect-api-url: "https://your-prefect-instance.com"
   - prefect-api-key: "your-prefect-api-key"
   - docker-registry-credentials: "username/password for Docker registry"
   ```

2. **Set up runtime secrets in Prefect:**
   ```bash
   # Runtime environment variables for K8s clusters
   prefect secret create database-url "postgresql://user:pass@host:port/db"
   prefect secret create external-api-keys "key1,key2,key3"
   prefect secret create k8s-namespace "production"
   prefect secret create k8s-service-account "prefect-worker"
   ```

3. **Run the Jenkins pipeline:**
   - Uses Jenkins credentials for Docker registry access
   - Deploys flows to Prefect with runtime secret access
   - Flows retrieve runtime secrets when executing in K8s

### Benefits of This Approach

- **Clear separation**: Build vs runtime concerns
- **Security**: Jenkins handles build secrets, Prefect handles runtime secrets
- **Scalability**: Runtime secrets can be updated without rebuilding
- **Compliance**: Different access controls for different environments

See [Architecture Guide](docs/architecture.md) for detailed design and [Jenkins Integration Guide](docs/jenkins_prefect_integration.md) for setup instructions.

## Architecture

- **Prefect 3** with Block-based secrets management
- **Docker** packaging for Kubernetes deployment
- **Python 3.12** with Poetry dependency management
- **Jenkins** CI/CD pipeline with Prefect secrets integration
- **S3 integration** for file uploads

## Development

- Add new flows in `src/automations/flows/`
- Configure blocks via Prefect UI or CLI
- Deploy with `prefect deploy -n <name> -p my-k8s-pool`

## Production

The repository includes:
- Docker image building on every push to main
- Automatic deployment to `my-k8s-pool` work pool
- Environment variable parameterization
- No runtime volume mounts (credentials via blocks)
- Secure secret management through Prefect

## Available Scripts

- `scripts/setup_jenkins_prefect.sh` - Setup Jenkins + Prefect integration
- `scripts/setup_prefect_secrets.py` - Manage Prefect secrets programmatically