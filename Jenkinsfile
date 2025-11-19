pipeline {
    agent any

    environment {
        VENV_DIR = "${WORKSPACE}/venv"
        PYTHON = "${VENV_DIR}/bin/python"
        PIP = "${VENV_DIR}/bin/pip"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                // Create virtual environment and install dependencies
                sh '''
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install --upgrade pip
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi
                '''
            }
        }

        stage('Test') {
            steps {
                // Run pytest if tests exist
                sh '''
                    source venv/bin/activate
                    if [ -d tests ]; then
                        pytest tests
                    else
                        echo "No tests directory found, skipping tests."
                    fi
                '''
            }
        }

        stage('SonarQube Analysis') {
            environment {
                SONARQUBE = 'SonarQube' // replace with your SonarQube installation name in Jenkins
            }
            steps {
                script {
                    withSonarQubeEnv('SonarQube') {
                        sh '''
                            source venv/bin/activate
                            sonar-scanner \
                                -Dsonar.projectKey=flask-app \
                                -Dsonar.sources=. \
                                -Dsonar.host.url=$SONAR_HOST_URL \
                                -Dsonar.login=$SONAR_AUTH_TOKEN
                        '''
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying Flask app..."
                // Add deployment steps here (e.g., docker build/run or scp to server)
            }
        }
    }

    post {
        always {
            node {
                echo 'Archiving artifacts...'
                archiveArtifacts artifacts: '**/*', allowEmptyArchive: true
            }
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
