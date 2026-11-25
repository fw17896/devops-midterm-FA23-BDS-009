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
        SOURCE_SHA = ''
    }

    stages {

        // ==========================================
        // STAGE 1: CHECKOUT AND IDENTIFY COMMITTER
        // ==========================================

        stage('Checkout') {
            steps {
                checkout scm

                script {
                    // Get latest commit SHA
                    env.SOURCE_SHA = sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()

                    // Get the email recorded in the latest commit
                    env.COMMITTER_EMAIL = sh(
                        script: "git log -1 --format='%ce'",
                        returnStdout: true
                    ).trim()

                    echo "Latest Commit SHA: ${env.SOURCE_SHA}"
                    echo "Committer Email: ${env.COMMITTER_EMAIL}"
                }

                echo 'Latest GitHub code downloaded successfully.'
            }
        }


        // ==========================================
        // STAGE 2: TRAIN MODEL AND RUN TESTS
        // ==========================================

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


        // ==========================================
        // STAGE 3: BUILD NEW DOCKER IMAGE
        // ==========================================

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "Building updated Docker image..."

                    docker build -t ml-midterm:build-${BUILD_NUMBER} .

                    echo "New Docker image created successfully."
                '''
            }
        }


        // ==========================================
        // STAGE 4: DEPLOY UPDATED APPLICATION
        // ==========================================

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


        // ==========================================
        // STAGE 5: VERIFY DEPLOYMENT
        // ==========================================

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


    // ==========================================
    // EMAIL NOTIFICATIONS
    // ==========================================

    post {

        // ======================================
        // SUCCESS EMAIL
        // ======================================

        success {
            script {

                if (env.COMMITTER_EMAIL?.trim()) {

                    try {

                        emailext(
                            to: env.COMMITTER_EMAIL,

                            subject: "SUCCESS: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",

                            mimeType: 'text/html',

                            body: """
                            <html>
                            <body>

                                <h2>ML Retraining Pipeline Successful!</h2>

                                <p>Hello,</p>

                                <p>Your GitHub commit successfully triggered the Jenkins CI/CD pipeline.</p>

                                <h3>Build Details:</h3>

                                <ul>
                                    <li><b>Project:</b> ${env.JOB_NAME}</li>
                                    <li><b>Build Number:</b> ${env.BUILD_NUMBER}</li>
                                    <li><b>Commit SHA:</b> ${env.SOURCE_SHA}</li>
                                    <li><b>Committer Email:</b> ${env.COMMITTER_EMAIL}</li>
                                    <li><b>Status:</b> SUCCESS</li>
                                </ul>

                                <h3>Completed Tasks:</h3>

                                <ul>
                                    <li>GitHub code checkout</li>
                                    <li>Model retraining</li>
                                    <li>Automated testing</li>
                                    <li>Docker image building</li>
                                    <li>Application deployment</li>
                                    <li>API verification</li>
                                </ul>

                                <p>Your updated machine learning model has been deployed successfully.</p>

                                <br>

                                <p>Regards,<br>
                                Jenkins CI/CD Pipeline</p>

                            </body>
                            </html>
                            """
                        )

                        echo "SUCCESS EMAIL SENT TO: ${env.COMMITTER_EMAIL}"

                    } catch (err) {

                        echo "EMAIL SENDING FAILED: ${err.getMessage()}"

                    }

                } else {

                    echo "No committer email found. Email notification skipped."

                }
            }
        }


        // ======================================
        // FAILURE EMAIL
        // ======================================

        failure {
            script {

                if (env.COMMITTER_EMAIL?.trim()) {

                    try {

                        emailext(
                            to: env.COMMITTER_EMAIL,

                            subject: "FAILED: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",

                            mimeType: 'text/html',

                            body: """
                            <html>
                            <body>

                                <h2>ML Retraining Pipeline Failed!</h2>

                                <p>Hello,</p>

                                <p>Your GitHub commit triggered the Jenkins CI/CD pipeline, but the build failed.</p>

                                <h3>Build Details:</h3>

                                <ul>
                                    <li><b>Project:</b> ${env.JOB_NAME}</li>
                                    <li><b>Build Number:</b> ${env.BUILD_NUMBER}</li>
                                    <li><b>Commit SHA:</b> ${env.SOURCE_SHA}</li>
                                    <li><b>Committer Email:</b> ${env.COMMITTER_EMAIL}</li>
                                    <li><b>Status:</b> FAILURE</li>
                                </ul>

                                <p>Please check Jenkins Console Output to identify the issue.</p>

                                <br>

                                <p>Regards,<br>
                                Jenkins CI/CD Pipeline</p>

                            </body>
                            </html>
                            """
                        )

                        echo "FAILURE EMAIL SENT TO: ${env.COMMITTER_EMAIL}"

                    } catch (err) {

                        echo "EMAIL SENDING FAILED: ${err.getMessage()}"

                    }

                } else {

                    echo "No committer email found. Email notification skipped."

                }
            }
        }
    }
}
