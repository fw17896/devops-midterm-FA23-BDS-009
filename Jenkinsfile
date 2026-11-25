pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        timestamps()
    }

    triggers {
        githubPush()
    }

    environment {
        COMMITTER_EMAIL = ''
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

                    // Get the email recorded as the Git commit's committer
                    def email = sh(
                        script: "git log -1 --format='%ce'",
                        returnStdout: true
                    ).trim().toLowerCase()

                    // Allow only the known student and instructor addresses
                    if (email == 'fw7896@gmail.com') {
                        env.COMMITTER_EMAIL = 'fw7896@gmail.com'
                    } else if (email == 'qasimalik@gmail.com') {
                        env.COMMITTER_EMAIL = 'qasimalik@gmail.com'
                    } else {
                        env.COMMITTER_EMAIL = ''
                    }

                    echo "Committer email detected: ${email}"
                    echo "Notification recipient: ${env.COMMITTER_EMAIL ?: 'No approved recipient'}"
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
                    echo "Building updated Docker image..."
                    docker build -t ml-midterm:build-${BUILD_NUMBER} .
                    echo "New Docker image created successfully."
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                sh '''
                    echo "Replacing previous application container..."

                    docker rm -f ml-midterm || true

                    docker run -d \
                        --name ml-midterm \
                        --restart unless-stopped \
                        -p 8000:8000 \
                        ml-midterm:build-${BUILD_NUMBER}

                    echo "Updated model deployed successfully."
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
            script {
                if (env.COMMITTER_EMAIL) {
                    emailext(
                        to: env.COMMITTER_EMAIL,
                        subject: "SUCCESS: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                        body: """
                        <h2>ML Retraining Pipeline Successful!</h2>

                        <p>Hello,</p>

                        <p>Your GitHub commit successfully triggered the Jenkins pipeline.</p>

                        <b>Build Details:</b>
                        <ul>
                            <li>Project: ${env.JOB_NAME}</li>
                            <li>Build Number: ${env.BUILD_NUMBER}</li>
                            <li>Commit SHA: ${env.SOURCE_SHA}</li>
                            <li>Status: SUCCESS</li>
                        </ul>

                        <p>The model was trained, tested, built into a Docker image,
                        and deployed successfully.</p>

                        <p>Regards,<br>Jenkins CI/CD Pipeline</p>
                        """,
                        mimeType: 'text/html'
                    )

                    echo "Success notification sent to ${env.COMMITTER_EMAIL}"
                } else {
                    echo 'No approved committer email found. Notification skipped.'
                }
            }
        }

        failure {
            script {
                if (env.COMMITTER_EMAIL) {
                    emailext(
                        to: env.COMMITTER_EMAIL,
                        subject: "FAILED: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                        body: """
                        <h2>ML Retraining Pipeline Failed!</h2>

                        <p>Hello,</p>

                        <p>Your GitHub commit triggered the Jenkins pipeline,
                        but the build failed.</p>

                        <b>Build Details:</b>
                        <ul>
                            <li>Project: ${env.JOB_NAME}</li>
                            <li>Build Number: ${env.BUILD_NUMBER}</li>
                            <li>Commit SHA: ${env.SOURCE_SHA}</li>
                            <li>Status: FAILURE</li>
                        </ul>

                        <p>Please check the Jenkins console output for details.</p>

                        <p>Regards,<br>Jenkins CI/CD Pipeline</p>
                        """,
                        mimeType: 'text/html'
                    )

                    echo "Failure notification sent to ${env.COMMITTER_EMAIL}"
                } else {
                    echo 'No approved committer email found. Notification skipped.'
                }
            }
        }
    }
}
