pipeline {
    agent any

    environment {
        // SonarQube environment variables injected by withSonarQubeEnv
        SONAR_HOST_URL = credentials('sonarqube-url')       // Your SonarQube URL
        SONAR_AUTH_TOKEN = credentials('sonarqube-token')  // SonarQube token
        PYTHON_VERSION = 'python3'
        VENV_DIR = 'venv'
    }

    options {
        skipDefaultCheckout(true)
        timeout(time: 1, unit: 'HOURS')
        //ansiColor('xterm')
    }

    stages {

        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo "Creating virtual environment and installing dependencies..."
                sh """
                    ${PYTHON_VERSION} -m venv ${VENV_DIR}
                    ./${VENV_DIR}/bin/pip install --upgrade pip
                    ./${VENV_DIR}/bin/pip install -r requirements.txt
                """
            }
        }

        stage('Static Code Analysis (SonarQube)') {
            steps {
                script {
                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ./venv/bin/sonar-scanner \
                                -Dsonar.projectKey=jenkinspipeline-flask \
                                -Dsonar.sources=. \
                                -Dsonar.host.url=$SONAR_HOST_URL \
                                -Dsonar.login=$SONAR_AUTH_TOKEN
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                script {
                    // Only works if your SonarQube plugin supports waitForQualityGate
                    timeout(time: 1, unit: 'HOURS') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }

        stage('Test') {
            steps {
                echo "Running unit tests..."
                sh """
                    ./${VENV_DIR}/bin/python -m unittest discover -s tests
                """
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying Flask app..."
                sh """
                    # Example: run Flask app (adjust as per your deployment)
                    ./${VENV_DIR}/bin/python app.py &
                """
            }
        }
    }

    post {
        always {
            echo 'Archiving workspace artifacts...'
            archiveArtifacts artifacts: '**/*', allowEmptyArchive: true
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
        }
    }
}
