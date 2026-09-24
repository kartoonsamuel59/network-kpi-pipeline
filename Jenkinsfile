pipeline {
    agent any

    environment {
        AWS_REGION     = 'eu-west-3'
        AWS_ACCOUNT_ID = '984941514401'
        ECR_REPO_NAME  = 'network-kpi-app'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        ECR_REGISTRY   = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh 'python3 test_app.py'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${ECR_REPO_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Push to ECR') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-ecr-credentials']]) {
                    sh """
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                        docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPO_NAME}:${IMAGE_TAG}
                        docker push ${ECR_REGISTRY}/${ECR_REPO_NAME}:${IMAGE_TAG}
                    """
                }
            }
        }
    }
}