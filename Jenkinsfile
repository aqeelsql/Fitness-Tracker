pipeline {
    agent any
    stages {
        stage('Clone') {
            steps {
                git url: 'https://github.com/aqeelsql/Fitness-Tracker.git', branch: 'main'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t fitness-tracker-test .'
            }
        }
        stage('Test') {
            steps {
                sh '''
                    mkdir -p test-results
                    docker run --rm \
                        --shm-size=2g \
                        -v $(pwd)/test-results:/app/test-results \
                        fitness-tracker-test \
                        bash -c "
                            python app.py &
                            sleep 3
                            pytest test_fitness_tracker.py \
                                --html=test-results/report.html \
                                --self-contained-html \
                                -v
                        "
                '''
            }
        }
        stage('Deploy') {
            steps {
                sh '''
                    docker stop fitness-tracker-app || true
                    docker rm fitness-tracker-app || true
                    docker run -d \
                        --name fitness-tracker-app \
                        -p 5000:5000 \
                        fitness-tracker-test \
                        flask run --host=0.0.0.0 --port=5000
                '''
            }
        }
    }
    post {
        always {
            emailext(
                to: 'rajaaqeeltariq@gmail.com',
                subject: "Fitness Tracker Test Results: ${currentBuild.currentResult} - Build #${env.BUILD_NUMBER}",
                body: """
                    <h2>Test Results: ${currentBuild.currentResult}</h2>
                    <p><b>Job:</b> ${env.JOB_NAME}</p>
                    <p><b>Build:</b> #${env.BUILD_NUMBER}</p>
                    <p><b>App URL:</b> <a href="http://YOUR_EC2_IP:5000">http://YOUR_EC2_IP:5000</a></p>
                    <p><b>Console:</b> <a href="${env.BUILD_URL}console">View Console Output</a></p>
                """,
                mimeType: 'text/html',
                recipientProviders: [
                    [$class: 'DevelopersRecipientProvider'],
                    [$class: 'RequesterRecipientProvider']
                ],
                attachLog: true
            )
        }
    }
}
