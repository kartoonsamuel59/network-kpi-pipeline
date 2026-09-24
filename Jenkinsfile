pipeline {
    agent any

    environment {
        AWS_REGION     = 'eu-west-3'
        AWS_ACCOUNT_ID = '984941514401'
        ECR_REPO_NAME  = 'network-kpi-app'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
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
    }
}