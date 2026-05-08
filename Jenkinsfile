pipeline {
    agent any

    environment {
        APP_REPO      = 'https://github.com/aqeelsql/Fitness-Tracker.git'
        APP_URL       = 'http://localhost:5000'
        RESULTS_FILE  = 'results.xml'
    }

    triggers {
        githubPush()
    }

    stages {

        // ── 1. ENSURE APP IS DOWN BEFORE ANYTHING ─────────────────
        stage('Shutdown') {
            steps {
                echo '🛑 Ensuring application is DOWN before pipeline starts...'
                sh '''
                    docker-compose down --remove-orphans || true
                    echo "All containers stopped. Website is NOT accessible yet."
                '''
            }
        }

        // ── 2. CHECKOUT ────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 Cloning repository...'
                git branch: 'main', url: "${APP_REPO}"
            }
        }

        // ── 3. BUILD DOCKER IMAGES ─────────────────────────────────
        stage('Build') {
            steps {
                echo '🔨 Building Docker images...'
                sh 'docker-compose build'
            }
        }

        // ── 4. RUN SELENIUM TESTS (App starts only for testing) ────
        stage('Selenium Tests') {
            steps {
                echo '🚀 Starting app temporarily for testing...'
                sh '''
                    docker-compose up -d
                    echo "Waiting for app to initialize..."
                    sleep 15
                '''

                echo '🔍 Verifying app is reachable before tests...'
                sh '''
                    for i in {1..10}; do
                        curl -s --fail ${APP_URL} && echo "App is UP - proceeding to tests" && break
                        echo "Attempt $i: App not ready yet, waiting..."
                        sleep 5
                    done
                '''

                echo '🧪 Running Selenium tests inside Docker container...'
                sh '''
                    docker build -f Dockerfile.test -t fitness-tests .
                    docker run --rm \
                        --network host \
                        -e BASE_URL=${APP_URL} \
                        -v ${WORKSPACE}:/tests \
                        fitness-tests \
                        pytest -v test_fitness_tracker.py \
                        --junitxml=/tests/results.xml
                '''
            }
            post {
                always {
                    // Collect results regardless of pass/fail
                    junit allowEmptyResults: true, testResults: "${RESULTS_FILE}"
                    archiveArtifacts artifacts: "${RESULTS_FILE}", allowEmptyArchive: true
                }
            }
        }

        // ── 5. DEPLOY (Only reached if tests PASSED) ───────────────
        stage('Deploy') {
            steps {
                echo '✅ Tests passed! Keeping application UP and RUNNING...'
                sh '''
                    echo "Application is already running from test stage."
                    echo "Website is now LIVE and accessible."
                    docker-compose ps
                '''
            }
        }
    }

    // ── POST BUILD ACTIONS ──────────────────────────────────────────
    post {

        success {
            echo '✅ Pipeline succeeded - sending success email...'
            script {
                // Get the email of whoever pushed the commit
                def pusherEmail = sh(
                    script: "git log -1 --pretty=format:'%ae'",
                    returnStdout: true
                ).trim()

                emailext(
                    to: "${pusherEmail}",
                    subject: "✅ [Jenkins] Fitness Tracker - Build #${BUILD_NUMBER} PASSED",
                    body: """
Hello,

Your recent push to the Fitness Tracker repository has been successfully built and tested.

────────────────────────────────────
 BUILD DETAILS
────────────────────────────────────
 Job        : ${JOB_NAME}
 Build No.  : #${BUILD_NUMBER}
 Status     : ✅ SUCCESS
 Duration   : ${currentBuild.durationString}
 Triggered  : ${currentBuild.getBuildCauses()[0]?.shortDescription ?: 'GitHub Push'}

────────────────────────────────────
 DEPLOYMENT
────────────────────────────────────
 🌐 Website is now LIVE at: ${APP_URL}
 All 15 Selenium test cases passed successfully.

────────────────────────────────────
 TEST RESULTS
────────────────────────────────────
 Please find the attached test results (results.xml) for full details.

Regards,
Jenkins CI/CD Pipeline
                    """,
                    attachmentsPattern: "${RESULTS_FILE}",
                    mimeType: 'text/plain'
                )
            }
        }

        failure {
            echo '❌ Pipeline FAILED - shutting down containers and sending failure email...'
            sh 'docker-compose down --remove-orphans || true'

            script {
                def pusherEmail = sh(
                    script: "git log -1 --pretty=format:'%ae'",
                    returnStdout: true
                ).trim()

                emailext(
                    to: "${pusherEmail}",
                    subject: "❌ [Jenkins] Fitness Tracker - Build #${BUILD_NUMBER} FAILED",
                    body: """
Hello,

Your recent push to the Fitness Tracker repository triggered a build that FAILED.

────────────────────────────────────
 BUILD DETAILS
────────────────────────────────────
 Job        : ${JOB_NAME}
 Build No.  : #${BUILD_NUMBER}
 Status     : ❌ FAILED
 Duration   : ${currentBuild.durationString}
 Triggered  : ${currentBuild.getBuildCauses()[0]?.shortDescription ?: 'GitHub Push'}

────────────────────────────────────
 DEPLOYMENT STATUS
────────────────────────────────────
 ⛔ Website has been taken DOWN.
 Containers stopped to prevent serving broken code.

────────────────────────────────────
 WHAT TO DO
────────────────────────────────────
 1. Check the Jenkins console logs for error details:
    ${BUILD_URL}console
 2. Fix the failing test cases or code issues.
 3. Push again to re-trigger the pipeline.

Regards,
Jenkins CI/CD Pipeline
                    """,
                    attachmentsPattern: "${RESULTS_FILE}",
                    mimeType: 'text/plain'
                )
            }
        }
    }
}
