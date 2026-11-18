pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        timestamps()
    }

    triggers {
        githubPush()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm

                script {
                    env.SOURCE_SHA = sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()
                }

                echo 'Latest GitHub code downloaded successfully.'
            }
        }

        stage('Train Model and Test') {
            steps {
                sh '''
                    docker run --rm \
                    --user "$(id -u):$(id -g)" \
                    -v "$WORKSPACE:/workspace" \
                    -w /workspace \
                    -e GIT_COMMIT="$SOURCE_SHA" \
                    python:3.14-slim \
                    sh -c '
                        python -m venv /tmp/ci-venv &&
                        /tmp/ci-venv/bin/pip install --no-cache-dir -r requirements-dev.txt &&
                        GIT_COMMIT="$GIT_COMMIT" /tmp/ci-venv/bin/python train.py &&
                        PYTHONPATH=. /tmp/ci-venv/bin/python -m pytest -v
                    '
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ml-midterm:latest .
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                sh '''
                    docker rm -f ml-midterm || true

                    docker run -d \
                        --name ml-midterm \
                        --restart unless-stopped \
                        -p 8000:8000 \
                        ml-midterm:latest
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    echo "Checking application..."

                    for i in $(seq 1 20); do
                        if curl -fsS http://localhost:8000/metrics; then
                            echo ""
                            echo "Application is running successfully!"
                            exit 0
                        fi

                        sleep 3
                    done

                    echo "Deployment verification failed!"
                    docker logs ml-midterm
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD Pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD Pipeline failed. Check Jenkins console output.'
        }
    }
}
