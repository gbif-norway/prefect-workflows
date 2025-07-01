#!/bin/bash

# Setup script for Jenkins + Prefect integration
set -e

echo "Setting up Jenkins + Prefect integration..."

# Check if Prefect CLI is installed
if ! command -v prefect &> /dev/null; then
    echo "Installing Prefect CLI..."
    pip install prefect
fi

# Check if required environment variables are set
if [ -z "$PREFECT_API_URL" ]; then
    echo "Error: PREFECT_API_URL environment variable is not set"
    echo "Please set it to your Prefect instance URL"
    exit 1
fi

if [ -z "$PREFECT_API_KEY" ]; then
    echo "Error: PREFECT_API_KEY environment variable is not set"
    echo "Please set it to your Prefect API key"
    exit 1
fi

# Configure Prefect
echo "Configuring Prefect..."
prefect config set PREFECT_API_URL="$PREFECT_API_URL"
prefect config set PREFECT_API_KEY="$PREFECT_API_KEY"

# Test connection
echo "Testing Prefect connection..."
if prefect config view &> /dev/null; then
    echo "✓ Prefect connection successful"
else
    echo "✗ Failed to connect to Prefect"
    exit 1
fi

# Create common secrets if they don't exist
echo "Setting up common secrets..."

# Docker registry credentials
if ! prefect secret get docker-registry-username &> /dev/null; then
    echo "Creating docker-registry-username secret..."
    read -p "Enter Docker registry username: " docker_username
    prefect secret create docker-registry-username "$docker_username"
fi

if ! prefect secret get docker-registry-password &> /dev/null; then
    echo "Creating docker-registry-password secret..."
    read -s -p "Enter Docker registry password/token: " docker_password
    echo
    prefect secret create docker-registry-password "$docker_password"
fi

# Database URL
if ! prefect secret get database-url &> /dev/null; then
    echo "Creating database-url secret..."
    read -p "Enter database URL (or press Enter to skip): " database_url
    if [ -n "$database_url" ]; then
        prefect secret create database-url "$database_url"
    fi
fi

# External API keys
if ! prefect secret get external-api-keys &> /dev/null; then
    echo "Creating external-api-keys secret..."
    read -p "Enter external API keys (comma-separated, or press Enter to skip): " api_keys
    if [ -n "$api_keys" ]; then
        prefect secret create external-api-keys "$api_keys"
    fi
fi

echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Ensure Jenkins has the PREFECT_API_URL and PREFECT_API_KEY credentials configured"
echo "2. Run the Jenkins pipeline to test the integration"
echo "3. Check the logs to ensure secrets are being retrieved correctly"
echo ""
echo "Available secrets:"
prefect secret list 