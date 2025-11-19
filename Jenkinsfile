pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        echo 'Building..'
        // e.g. sh 'mvn -B -DskipTests package'
      }
    }
    stage('Test') {
      steps {
        echo 'Testing..'
        // e.g. sh 'mvn test'
      }
    }
    stage('Deploy') {
      steps {
        echo 'Deploying....'
        // e.g. sh 'scp ...' or other deploy steps
      }
    }
  }
}
