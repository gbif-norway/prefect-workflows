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

This repository includes Jenkins integration with Prefect secrets management:

### Setup Jenkins Integration

1. **Configure Prefect connection in Jenkins:**
   ```bash
   # Set these as Jenkins credentials
   PREFECT_API_URL="https://your-prefect-instance.com"
   PREFECT_API_KEY="your-prefect-api-key"
   ```

2. **Set up secrets in Prefect:**
   ```bash
   # Use the provided setup script
   ./scripts/setup_jenkins_prefect.sh
   
   # Or manually create secrets
   prefect secret create docker-registry-username "your-username"
   prefect secret create docker-registry-password "your-password"
   ```

3. **Run the Jenkins pipeline:**
   - The pipeline will automatically retrieve secrets from Prefect
   - Docker images are built and pushed to your registry
   - Flows are deployed to your Prefect instance

### Benefits of Prefect Secrets

- **Centralized management**: All secrets stored in Prefect
- **Better security**: Encrypted and access-controlled
- **Audit trail**: All secret access is logged
- **Integration**: Seamless with your Prefect workflows

See [Jenkins Integration Guide](docs/jenkins_prefect_integration.md) for detailed setup instructions.

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