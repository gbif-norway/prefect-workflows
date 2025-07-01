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
        
        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image
                    docker.build("${DOCKER_IMAGE}:${env.BUILD_NUMBER}")
                    docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }
        
        stage('Push Docker Image') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // Login to registry using Jenkins credentials
                    docker.withRegistry("https://${REGISTRY}", 'docker-registry-credentials') {
                        docker.image("${DOCKER_IMAGE}:${env.BUILD_NUMBER}").push()
                        docker.image("${DOCKER_IMAGE}:latest").push()
                    }
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
        always {
            node('any') {
                // Clean up Docker images
                sh 'docker system prune -f'
            }
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
} 
