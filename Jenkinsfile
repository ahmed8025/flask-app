pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/ahmed8025/flask-app.git'
            }
        }

        stage('Setup Python') {
            steps {
                sh 'python3 -m venv ${VENV_DIR}'
                sh 'source ${VENV_DIR}/bin/activate && pip install --upgrade pip'
            }
        }

        stage('Run') {
            steps {
                sh 'source ${VENV_DIR}/bin/activate && python app2.py'
            }
        }
    }

    post {
        success {
            echo 'Pipeline finished successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs.'
        }
    }
}
