pipeline {
    agent any

    environment {
        AWS_REGION     = 'eu-west-3'
        AWS_ACCOUNT_ID = '984941514401'
        ECR_REPO_NAME  = 'network-kpi-app'
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
    }
}