pipeline {
    agent any
    
    environment {
        REGISTRY = 'ghcr.io'
        IMAGE_NAME = 'ACME/automations'
        DOCKER_IMAGE = "${REGISTRY}/${IMAGE_NAME}"
        // Prefect configuration
        PREFECT_API_URL = credentials('prefect-api-url') // Keep this for initial connection
        PREFECT_API_KEY = credentials('prefect-api-key') // Keep this for initial connection
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
                    // Configure Prefect client to connect to your Prefect instance
                    sh '''
                        prefect config set PREFECT_API_URL=${PREFECT_API_URL}
                        prefect config set PREFECT_API_KEY=${PREFECT_API_KEY}
                    '''
                }
            }
        }
        
        stage('Retrieve Secrets') {
            steps {
                script {
                    // Retrieve secrets from Prefect storage
                    sh '''
                        # Get Docker registry credentials from Prefect secrets
                        DOCKER_USERNAME=$(prefect secret get docker-registry-username)
                        DOCKER_PASSWORD=$(prefect secret get docker-registry-password)
                        
                        # Get any other secrets you need
                        # DATABASE_URL=$(prefect secret get database-url)
                        # API_KEYS=$(prefect secret get external-api-keys)
                        
                        # Export for use in subsequent stages
                        echo "DOCKER_USERNAME=${DOCKER_USERNAME}" >> env.properties
                        echo "DOCKER_PASSWORD=${DOCKER_PASSWORD}" >> env.properties
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    // Load secrets from properties file
                    load env.properties
                    
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
                    // Load secrets from properties file
                    load env.properties
                    
                    // Login to registry using Prefect secrets
                    sh '''
                        echo "${DOCKER_PASSWORD}" | docker login ${REGISTRY} -u ${DOCKER_USERNAME} --password-stdin
                    '''
                    
                    // Push images
                    docker.image("${DOCKER_IMAGE}:${env.BUILD_NUMBER}").push()
                    docker.image("${DOCKER_IMAGE}:latest").push()
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
            // Clean up Docker images and sensitive files
            sh '''
                docker system prune -f
                rm -f env.properties
            '''
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
} 
