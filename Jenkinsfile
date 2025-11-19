pipeline {
  agent any

  parameters {
    booleanParam(name: 'executeTests', defaultValue: true, description: 'Run tests?')
    string(name: 'DEPLOY_ENV', defaultValue: 'staging', description: 'Deploy environment')
  }

  environment {
    // optional environment variables
    NODE_VERSION = '16.20.0'
  }

  tools {
    // Make sure these tool names exist in Manage Jenkins -> Global Tool Configuration
    // If you don't use Maven, remove this block or adjust.
    maven 'Maven3.9.11'
  }

  stages {
    stage('Checkout') {
      steps {
        // If using GitHub locally, you can use a local file URL (file:///path/to/repo)
        git url: 'https://github.com/ahmed8025/flask-app.git', branch: 'main'
      }
    }

    stage('Build') {
      steps {
        echo 'Building...'
        // Example for Maven builds:
        sh 'mvn -B -DskipTests package || true'
      }
    }

    stage('Static Code Analysis (SonarQube)') {
      steps {
        script {
          // Use withSonarQubeEnv 'SonarQube' (the name you configured in Jenkins)
          withSonarQubeEnv('SonarQube') {
            // If using Maven:
            sh "mvn sonar:sonar -Dsonar.projectKey=jenkins-pipeline-lab -Dsonar.host.url=${env.SONAR_HOST_URL} -Dsonar.login=${env.SONAR_AUTH_TOKEN}"

            // OR, if using sonar-scanner CLI (uncomment and adjust):
            // sh "sonar-scanner -Dsonar.projectKey=jenkins-pipeline-lab -Dsonar.sources=./src -Dsonar.host.url=${env.SONAR_HOST_URL} -Dsonar.login=${env.SONAR_AUTH_TOKEN}"
          }
        }
      }
    }

    // Optional: wait for quality gate (this waits for Sonar analysis to finish and returns result)
    stage('Quality Gate') {
      steps {
        script {
          timeout(time: 5, unit: 'MINUTES') {
            def qg = waitForQualityGate()   // requires SonarQube plugin
            echo "Quality Gate status: ${qg.status}"
            if (qg.status != 'OK') {
              error "Pipeline aborted due to SonarQube Quality Gate status: ${qg.status}"
            }
          }
        }
      }
    }

    stage('Test') {
      when {
        expression { return params.executeTests == true }
      }
      steps {
        echo 'Running tests...'
        sh 'mvn test'
      }
    }

    stage('Deploy') {
      when {
        branch 'main'
      }
      steps {
        echo "Deploying to ${params.DEPLOY_ENV}"
        // deployment steps go here
      }
    }
  }

  post {
    always {
      // Archive any reports for your lab submission
      archiveArtifacts artifacts: '**/target/*.jar, **/target/site/**, **/sonar-report/**/*', allowEmptyArchive: true
    }
    success { echo 'Pipeline completed successfully.' }
    failure { echo 'Pipeline failed.' }
  }
}
