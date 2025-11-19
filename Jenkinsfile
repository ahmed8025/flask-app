pipeline {
  agent any
  parameters {
    booleanParam(name: 'executeTests', defaultValue: true, description: 'Run tests?')
  }
  environment {
    NODE_VERSION = '16.20.0'
  }
  stages {
    stage('Build') {
      steps {
        echo 'Building..'
        // sh 'mvn -B -DskipTests package'
      }
    }
    stage('Test') {
      when {
        expression { return params.executeTests == true }
      }
      steps {
        echo 'Testing..'
        // sh 'mvn test'
      }
    }
    stage('Deploy') {
      steps {
        echo "Deploying to ${params.DEPLOY_ENV ?: 'staging'}"
      }
    }
  }
  post {
    success { echo 'Success — you can notify here.' }
    failure { echo 'Failure — notify and cleanup.' }
  }
}
