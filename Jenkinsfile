pipeline {
    agent any

    stages {
        stage('Clone Repository') {
            steps {
                echo 'Cloning GitHub repository...'
                git branch: 'main',
                    url: 'https://github.com/aqeelsql/Fitness-Tracker.git'
            }
        }

        stage('Build with Docker Compose') {
            steps {
                echo 'Stopping old containers...'
                sh 'docker compose down || true'

                echo 'Starting Flask app...'
                sh 'docker compose up -d'
            }
        }

        stage('Verify') {
            steps {
                sh 'docker ps'
            }
        }
    }

    post {
        success {
            echo 'App is live on port 5001!'
        }
        failure {
            echo 'Something went wrong!'
        }
    }
}
