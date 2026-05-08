pipeline {
    agent any

    environment {
        APP_REPO = 'https://github.com/aqeelsql/Fitness-Tracker.git'
        APP_DIR  = '/home/ubuntu/fitness-tracker'
        APP_URL  = "http://${env.PUBLIC_IP}:5000"  // Use the public IP for app URL
    }

    triggers {
        githubPush()  // Trigger on every GitHub push
    }

    stages {

        // ── STAGE 1: Clone / Pull latest code ──────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 Pulling latest code from GitHub...'
                git branch: 'main', url: "${APP_REPO}"
            }
        }

        // ── STAGE 2: Deploy application with Docker Compose ────────────
        stage('Deploy App') {
            steps {
                echo '🚀 Starting the Fitness Tracker application...'
                sh '''
                    cd ${WORKSPACE}
                    docker-compose down || true   # Ensure any previous containers are stopped
                    docker-compose up -d --build  # Start the app in detached mode
                    sleep 10   # Wait for Flask app to be ready
                '''
            }
        }

        // ── STAGE 3: Run Selenium Tests inside Docker ──────────────────
        stage('Test') {
            steps {
                echo '🧪 Running Selenium test cases in Docker container...'
                sh '''
                    # Build the test Docker image
                    docker build -f Dockerfile.test -t fitness-selenium-tests .

                    # Run tests; container shares host network so it can reach localhost:5000
                    docker run --rm \
                        --network host \
                        -e BASE_URL=${APP_URL} \
                        --name selenium-tests \
                        fitness-selenium-tests \
                        python -m pytest test_fitness_tracker.py -v \
                            --tb=short \
                            --junit-xml=/tests/results.xml 2>&1 | tee test_output.txt

                    # Copy results out of the container for archiving
                    docker cp selenium-tests:/tests/results.xml . 2>/dev/null || true
                '''
            }
            post {
                always {
                    // Archive JUnit XML so Jenkins shows pass/fail per test
                    junit allowEmptyResults: true, testResults: 'results.xml'
                    // Archive raw log
                    archiveArtifacts artifacts: 'test_output.txt', allowEmptyArchive: true
                }
            }
        }

        // ── REMOVE STAGE 4: Stop App (Leave the app running after the test)
        // stage('Stop App') {
        //     steps {
        //         echo '🛑 Stopping app containers (deployment stays down per assignment)...'
        //         sh '''
        //             cd ${WORKSPACE}
        //             docker-compose down || true
        //         '''
        //     }
        // }
    }

    // ── POST: Email test results to the committer ──────────────────────
    post {
        always {
            script {
                def committerEmail = sh(
                    script: "git log -1 --pretty=format:'%ae'",
                    returnStdout: true
                ).trim()

                def buildStatus = currentBuild.currentResult ?: 'UNKNOWN'
                def subject     = "Fitness Tracker Test Results: ${buildStatus} [Build #${env.BUILD_NUMBER}]"

                def body = """
Hello,

Jenkins has finished running the automated Selenium test suite for the Fitness Tracker app.

Pipeline  : ${env.JOB_NAME}
Build #   : ${env.BUILD_NUMBER}
Status    : ${buildStatus}
Duration  : ${currentBuild.durationString}

Full logs : ${env.BUILD_URL}console
Test Report: ${env.BUILD_URL}testReport/

---
This email was sent automatically by the Jenkins CI/CD pipeline.
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
