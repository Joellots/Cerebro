pipeline {
  
  agent none
  
  environment {
    DB_HOST='postgres'
    DB_NAME='cerebro_db'
    DB_PORT='5432'
    REGISTRY = 'joellots/cerebro'
    // KUBECONFIG = credentials('k8s-credential')
  }

  parameters {
    choice(name: 'VERSION', choices: ['v1.1.0', 'v1.2.0', 'v1.3.0'], description: '')
    booleanParam(name: 'executeTests', defaultValue: false, description: '')
  }
  
  stages {
    agent {
        kubernetes {
          yamlFile 'jenkins-agent-dind.yaml'
        }
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage("build") {  
      agent {
        kubernetes {
          yamlFile 'jenkins-agent-dind.yaml'
        }    
      steps {
        echo 'Building the application...'
        withCredentials([
          usernamePassword(credentialsId: 'DB_CREDENTIALS', usernameVariable: 'DB_USER', passwordVariable: 'DB_PASSWORD')
        ]){
          sh "docker compose -f docker-compose-db.yaml up -d --build"
          sh "docker compose -f docker-compose-app.yaml up -d --build"
          sh "docker container rm cerebro --force"
          sh "docker container rm postgres --force"
        }
      }
    }
    
    stage("test") {
      agent {
        kubernetes {
          yamlFile 'jenkins-agent-dind.yaml'
        }
      when {
        expression {
          params.executeTests == true
        }
      }
      
      steps {
        echo 'Testing the application...'
        sh "docker exec cerebro pytest --junitxml=test-results.xml --cov || true"
        sh "docker cp cerebro:/cerebro/test-results.xml /tmp/test-results.xml"
        sh "docker cp /tmp/test-results.xml build-container:/var/jenkins_home/workspace/cerebro_dev/test-results.xml"  
        sh "docker cp /tmp/test-results.xml build-container:/home/jenkins/workspace/cerebro_dev/test-results.xml"  
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
        // sh "docker container rm cerebro --force"
        // sh "docker container rm postgres --force"
      }
    }
  }
}
