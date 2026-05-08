pipeline {
    agent any

    triggers {
        githubPush()
    }

    stages {
        stage('Clone') {
            steps {
                echo '📥 Cloning GitHub repository...'
                git url: 'https://github.com/aqeelsql/Fitness-Tracker.git', branch: 'main'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🔨 Building Docker image...'
                sh 'docker build -f Dockerfile.test -t fitness-tracker-test .'
            }
        }

        stage('Test') {
            steps {
                echo '🧪 Running tests...'
                sh '''
                    mkdir -p test-results
                    docker run --rm \
                        --shm-size=2g \
                        -v $(pwd)/test-results:/app/test-results \
                        fitness-tracker-test \
                        bash -c "
                            python application.py &
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
                echo '🚀 Deploying application...'
                sh '''
                    # Stop and remove old container
                    docker stop fitness-tracker-app || true
                    docker rm fitness-tracker-app || true

                    # Run with explicit host binding — critical for EC2
                    docker run -d \
                        --name fitness-tracker-app \
                        --restart unless-stopped \
                        -p 0.0.0.0:5000:5000 \
                        -e FLASK_APP=application.py \
                        -e FLASK_RUN_HOST=0.0.0.0 \
                        fitness-tracker-test \
                        flask run --host=0.0.0.0 --port=5000

                    # Wait for container to start
                    sleep 5

                    # Verify container is actually running
                    if docker ps | grep -q fitness-tracker-app; then
                        EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
                        echo "✅ App deployed successfully!"
                        echo "🌐 Visit: http://$EC2_IP:5000"
                    else
                        echo "❌ Container failed to start!"
                        docker logs fitness-tracker-app
                        exit 1
                    fi
                '''
            }
        }
    }

    post {
        always {
            script {
                def ec2Ip = sh(
                    script: 'curl -s http://169.254.169.254/latest/meta-data/public-ipv4',
                    returnStdout: true
                ).trim()

                emailext(
                    to: 'rajaaqeeltariq@gmail.com',
                    subject: "Fitness Tracker: ${currentBuild.currentResult} - Build #${env.BUILD_NUMBER}",
                    body: """
                        <h2>Build Result: ${currentBuild.currentResult}</h2>
                        <p><b>Job:</b> ${env.JOB_NAME}</p>
                        <p><b>Build:</b> #${env.BUILD_NUMBER}</p>
                        <p><b>App URL:</b> <a href="http://${ec2Ip}:5000">http://${ec2Ip}:5000</a></p>
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
}
