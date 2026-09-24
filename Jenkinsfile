pipeline {
    agent any

    environment {
        AWS_REGION     = 'eu-west-3'
        AWS_ACCOUNT_ID = '984941514401'
        ECR_REPO_NAME  = 'network-kpi-app'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        ECR_REGISTRY   = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        EC2_HOST       = 'ec2-user@35.180.31.120'
    }

    stages {
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

        stage('Deploy to EC2') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_HOST} '
                            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY} &&
                            docker pull ${ECR_REGISTRY}/${ECR_REPO_NAME}:${IMAGE_TAG} &&
                            docker stop network-kpi-app || true &&
                            docker rm network-kpi-app || true &&
                            docker run -d -p 80:3000 --name network-kpi-app ${ECR_REGISTRY}/${ECR_REPO_NAME}:${IMAGE_TAG}
                        '
                    """
                }
            }
        }
    }
}