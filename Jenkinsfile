pipeline {
    agent any
    
    environment {
        REGISTRY = 'ghcr.io'
        IMAGE_NAME = 'gbifnorway/automations'
        DOCKER_IMAGE = "${REGISTRY}/${IMAGE_NAME}"
    }
    
    options {
        // Ensure we're working with the main branch
        skipDefaultCheckout(false)
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build and Push Docker Image') {
            steps {
                script {
                    // Build the Docker image using Kaniko
                    echo "Building Docker image: ${DOCKER_IMAGE}:${env.BUILD_NUMBER}"
                    sh """
                        docker run --rm \
                            -v \${WORKSPACE}:/workspace \
                            -v /var/run/docker.sock:/var/run/docker.sock \
                            gcr.io/kaniko-project/executor:latest \
                            --dockerfile /workspace/Dockerfile \
                            --context /workspace \
                            --destination ${DOCKER_IMAGE}:${env.BUILD_NUMBER} \
                            --cache=true
                    """
                    
                    echo "Building Docker image: ${DOCKER_IMAGE}:latest"
                    sh """
                        docker run --rm \
                            -v \${WORKSPACE}:/workspace \
                            -v /var/run/docker.sock:/var/run/docker.sock \
                            gcr.io/kaniko-project/executor:latest \
                            --dockerfile /workspace/Dockerfile \
                            --context /workspace \
                            --destination ${DOCKER_IMAGE}:latest \
                            --cache=true
                    """
                }
            }
        }
        
        stage('Deploy to Prefect') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // Get Prefect credentials if available
                    def prefectApiUrl = ''
                    def prefectApiKey = ''
                    
                    try {
                        prefectApiUrl = credentials('prefect-api-url')
                        prefectApiKey = credentials('prefect-api-key')
                    } catch (Exception e) {
                        echo "Prefect credentials not available, skipping deployment"
                        return
                    }
                    
                    // Configure Prefect client for deployment
                    sh '''
                        prefect config set PREFECT_API_URL=${prefectApiUrl}
                        prefect config set PREFECT_API_KEY=${prefectApiKey}
                    '''
                    
                    // Deploy to Prefect using the built image
                    sh '''
                        prefect deploy -n example -p my-k8s-pool
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
} 
