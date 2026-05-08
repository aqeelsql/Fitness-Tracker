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

        // ── 1. Checkout ───────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 Cloning repository...'
                git branch: 'main', url: "${APP_REPO}"
            }
        }

        // ── 2. Build Docker Images ────────────────────
        stage('Build') {
            steps {
                echo '🔨 Building Docker images...'
                sh 'docker-compose build'
            }
        }

        // ── 3. Deploy Application (KEEP RUNNING) ─────
        stage('Deploy') {
            steps {
                echo '🚀 Deploying application (keeping containers running)...'
                sh '''
                    docker-compose down || true
                    docker-compose up -d --build

                    echo "Waiting for app to start..."
                    sleep 15
                '''
            }
        }

        // ── 4. Verify Deployment ──────────────────────
        stage('Verify Deployment') {
            steps {
                echo '🔍 Checking if website is accessible...'
                sh '''
                    for i in {1..10}; do
                        curl -s --fail ${APP_URL} && echo "App is UP" && exit 0
                        echo "Waiting for app..."
                        sleep 5
                    done

                    echo "App failed to start"
                    exit 1
                '''
            }
        }

        // ── 5. Selenium Tests (Headless Chrome) ───────
        stage('Selenium Tests') {
            steps {
                echo '🧪 Running Selenium tests...'
                sh '''
                    docker build -f Dockerfile.test -t fitness-tests .

                    docker run --rm \
                        --network host \
                        -e BASE_URL=${APP_URL} \
                        fitness-tests \
                        pytest -v test_fitness_tracker.py \
                        --junitxml=/tests/results.xml
                '''
            }

            post {
                always {
                    junit 'results.xml'
                    archiveArtifacts artifacts: 'results.xml', allowEmptyArchive: true
                }
            }
        }
    }

    // ── POST BUILD ACTIONS ─────────────────────────────
    post {

        success {
            echo '✅ Pipeline SUCCESS - Application is LIVE and RUNNING'
            echo "🌐 Visit: ${APP_URL}"
        }

        failure {
            echo '❌ Pipeline FAILED - stopping containers'
            sh 'docker-compose down || true'
        }
    }
}
