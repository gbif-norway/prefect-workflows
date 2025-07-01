pipeline {
    agent any
    
    environment {
        REGISTRY = 'ghcr.io'
        IMAGE_NAME = 'gbifnorway/automations'
        DOCKER_IMAGE = "${REGISTRY}/${IMAGE_NAME}"
        // Prefect configuration for deployment
        PREFECT_API_URL = credentials('prefect-api-url')
        PREFECT_API_KEY = credentials('prefect-api-key')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Prefect') {
            steps {
                script {
                    // Configure Prefect client for deployment
                    sh '''
                        prefect config set PREFECT_API_URL=${PREFECT_API_URL}
                        prefect config set PREFECT_API_KEY=${PREFECT_API_KEY}
                    '''
                }
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
            // Clean up Docker images
            sh 'docker system prune -f'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
} 
