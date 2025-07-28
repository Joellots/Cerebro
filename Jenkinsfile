pipeline {
  
  agent {
    docker { image 'docker:24' }
  }
  
  environment {
    DB_HOST='postgres'
    DB_NAME='cerebro_db'
    DB_PORT='5432'
    // KUBECONFIG = credentials('k8s-credential')
    REGISTRY = 'joellots/cerebro'
  }

  parameters {
    choice(name: 'VERSION', choices: ['v1.1.0', 'v1.2.0', 'v1.3.0'], description: '')
    booleanParam(name: 'executeTests', defaultValue: false, description: '')
  }
  
  stages {
    
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage("build") {      
      steps {
        echo 'Building the application...'
        withCredentials([
          usernamePassword(credentialsId: 'DB_CREDENTIALS', usernameVariable: 'DB_USER', passwordVariable: 'DB_PASSWORD')
        ]){
          sh "docker-compose -f docker-compose-db.yaml down --volumes --remove-orphans"
          sh "docker-compose -f docker-compose-app.yaml down --volumes --remove-orphans"
          sh "docker-compose -f docker-compose-db.yaml up -d --build"
          sh "docker-compose -f docker-compose-app.yaml up -d --build"
        }
      }
    }
    
    stage("test") {
      when {
        expression {
          params.executeTests == true
        }
      }
      
      steps {
        echo 'Testing the application...'
        sh "docker exec cerebro pytest --junitxml=test-results.xml --cov || true"
        sh "docker cp cerebro:/cerebro/test-results.xml ./test-results.xml"  
      }
      post {
        always {
          junit 'test-results.xml'
          archiveArtifacts artifacts: 'test-results.xml', fingerprint: true
        }
      }
    }

    stage('dockerhub-login'){
      steps{
        echo 'Logging into Dockerhub...'
        withCredentials([
          usernamePassword(credentialsId: 'joellots-dockerhub', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASSWORD')
        ]){
          sh "echo $DH_PASSWORD | docker login -u $DH_USER --password-stdin"
        }
      }
    }

    stage('push'){
      steps {
        sh "docker tag ${REGISTRY}:latest ${REGISTRY}:${params.VERSION}"
        sh "docker push ${REGISTRY}:${params.VERSION}"
      }
    }   
    

    stage("deploy-app") { 
      agent {
        kubernetes {
          yamlFile 'k8s/cerebro.yaml'
        } 
      }
      steps {
        echo "Deployed Cerebro Application"
        echo "Deployed version ${params.VERSION}"
        input message: 'Do you want to continue?', ok: 'Yes'
      }
    }    
  }

  post {
    always{
      echo 'Logging out of Docker...'
      sh "docker logout"

      echo 'Removing Containers...'
      withCredentials([
        usernamePassword(credentialsId: 'DB_CREDENTIALS', usernameVariable: 'DB_USER', passwordVariable: 'DB_PASSWORD')
      ]){
        sh "docker-compose -f docker-compose-db.yaml down --volumes --remove-orphans"
        sh "docker-compose -f docker-compose-app.yaml down --volumes --remove-orphans"
      }
    }
  }
}
