pipeline {
    agent any

    environment {
        APP_REPO = 'https://github.com/aqeelsql/Fitness-Tracker.git'
        APP_NAME = 'fitness-tracker-app'
        APP_IMAGE = 'fitness-tracker-test'
        APP_URL = 'http://localhost:5000'
    }

    triggers {
        githubPush()
    }

    stages {

        // ── 1. CLONE CODE ─────────────────────────────
        stage('Clone') {
            steps {
                echo '📥 Cloning GitHub repository...'
                git url: "${APP_REPO}", branch: 'main'
            }
        }

        // ── 2. BUILD DOCKER IMAGE ─────────────────────
        stage('Build Docker Image') {
            steps {
                echo '🔨 Building Docker image...'
                sh 'docker build -t ${APP_IMAGE} .'
            }
        }

        // ── 3. RUN SELENIUM TESTS (HEADLESS CHROME) ──
        stage('Test') {
            steps {
                echo '🧪 Running Selenium test suite...'
                sh '''
                    mkdir -p test-results

                    docker run --rm \
                        --shm-size=2g \
                        -v $(pwd)/test-results:/tests \
                        ${APP_IMAGE} \
                        bash -c "
                            echo 'Starting Flask app...'
                            python app.py & 
                            sleep 5

                            echo 'Running tests...'
                            pytest test_fitness_tracker.py \
                                -v \
                                --html=/tests/report.html \
                                --self-contained-html
                        "
                '''
            }
        }

        // ── 4. DEPLOY APPLICATION (KEEP RUNNING) ─────
        stage('Deploy') {
            steps {
                echo '🚀 Deploying Fitness Tracker...'
                sh '''
                    docker stop ${APP_NAME} || true
                    docker rm ${APP_NAME} || true

                    docker run -d \
                        --name ${APP_NAME} \
                        -p 5000:5000 \
                        ${APP_IMAGE} \
                        flask run --host=0.0.0.0 --port=5000

                    echo "Application deployed at ${APP_URL}"
                '''
            }
        }
    }

    // ── POST BUILD ACTIONS ─────────────────────────
    post {

        success {
            echo '✅ BUILD SUCCESS - Application is LIVE'
            echo "🌐 Visit: ${APP_URL}"
        }

        failure {
            echo '❌ BUILD FAILED - stopping container'
            sh 'docker stop fitness-tracker-app || true'
            sh 'docker rm fitness-tracker-app || true'
        }

        always {
            emailext(
                to: 'rajaaqeeltariq@gmail.com',
                subject: "Fitness Tracker Pipeline: ${currentBuild.currentResult} - Build #${env.BUILD_NUMBER}",
                body: """
                    <h2>Fitness Tracker CI/CD Results</h2>

                    <p><b>Status:</b> ${currentBuild.currentResult}</p>
                    <p><b>Build:</b> #${env.BUILD_NUMBER}</p>
                    <p><b>Job:</b> ${env.JOB_NAME}</p>

                    <h3>App URL</h3>
                    <p><a href="${APP_URL}">${APP_URL}</a></p>

                    <h3>Jenkins Console</h3>
                    <p><a href="${env.BUILD_URL}console">View Logs</a></p>

                    <p>This is an automated CI/CD pipeline email.</p>
                """,
                mimeType: 'text/html',
                attachLog: true
            )
        }
    }
}
