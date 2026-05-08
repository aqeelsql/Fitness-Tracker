pipeline {
    agent any

    environment {
        APP_REPO = 'https://github.com/aqeelsql/Fitness-Tracker.git'
        APP_URL  = 'http://localhost:5000'
    }

    triggers {
        githubPush()
    }

    stages {

        stage('Checkout') {
            steps {
                echo '📥 Pulling latest code from GitHub...'
                git branch: 'main', url: "${APP_REPO}"
            }
        }

        stage('Deploy App') {
            steps {
                echo '🚀 Starting the Fitness Tracker application...'
                sh '''
                    cd ${WORKSPACE}
                    docker-compose down || true
                    docker-compose up -d --build
                    sleep 10
                '''
            }
        }

        stage('Test') {
            steps {
                echo '🧪 Running Selenium test cases in Docker container...'
                sh '''
                    docker build -f Dockerfile.test -t fitness-selenium-tests .
                    docker run --rm \
                        --network host \
                        --name selenium-tests \
                        fitness-selenium-tests \
                        python -m pytest test_fitness_tracker.py -v \
                            --tb=short \
                            --junit-xml=/tests/results.xml 2>&1 | tee test_output.txt
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'results.xml'
                    archiveArtifacts artifacts: 'test_output.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Stop App') {
            steps {
                echo '🛑 Stopping app containers...'
                sh '''
                    cd ${WORKSPACE}
                    docker-compose down || true
                '''
            }
        }
    }

    post {
        always {
            script {
                def committerEmail = sh(
                    script: "git log -1 --pretty=format:'%ae'",
                    returnStdout: true
                ).trim()

                def buildStatus = currentBuild.currentResult ?: 'UNKNOWN'
                def subject = "Fitness Tracker Test Results: ${buildStatus} [Build #${env.BUILD_NUMBER}]"
                def body = """
Hello,

Jenkins has finished running the automated Selenium test suite.

Pipeline  : ${env.JOB_NAME}
Build #   : ${env.BUILD_NUMBER}
Status    : ${buildStatus}
Duration  : ${currentBuild.durationString}

Full logs : ${env.BUILD_URL}console
Test Report: ${env.BUILD_URL}testReport/

---
This email was sent automatically by Jenkins CI/CD pipeline.
"""
                emailext(
                    subject: subject,
                    body: body,
                    to: committerEmail,
                    replyTo: committerEmail,
                    attachLog: true
                )
            }
        }
    }
}
}
