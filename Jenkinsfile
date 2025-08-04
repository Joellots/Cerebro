pipeline {
  agent none

  environment {
    DB_HOST='postgres'
    DB_NAME='cerebro_db'
    DB_PORT='5432'
    REGISTRY = 'joellots/cerebro'
    SEMGREP_APP_TOKEN = credentials('SEMGREP_APP_TOKEN')
  }

  parameters {
    choice(name: 'VERSION', choices: ['v1.1.0', 'v1.2.0', 'v1.3.0'], description: '')
    booleanParam(name: 'executeTests', defaultValue: false, description: '')
  }

  
  stages {

    stage('Checkout') {
        agent {
        label 'jenkins-agent-dind'
      }
        checkout scm
    }


    stage('Build') {
      agent {
        label 'jenkins-agent-dind'
      }
      steps {
        echo 'Building the application...'
        withCredentials([
          usernamePassword(credentialsId: 'DB_CREDENTIALS', usernameVariable: 'DB_USER', passwordVariable: 'DB_PASSWORD')
        ]) {
          sh "docker compose -f docker-compose-db.yaml up -d --build"
          sh "docker compose -f docker-compose-app.yaml up -d --build"
        }
      }
    }

    stage('Unit Tests') {
      when {
        expression { params.executeTests }
      }
      agent {
        label 'jenkins-agent-dind'
      }
      steps {
        echo 'Running tests...'
        sh "docker exec cerebro pytest --junitxml=test-results.xml --cov || true"
        sh "docker cp cerebro:/cerebro/test-results.xml /tmp/test-results.xml" 
        sh "docker cp /tmp/test-results.xml build-container:/home/jenkins/workspace/cerebro_dev/test-results.xml"  
      }
      post {
        always {
          junit 'test-results.xml'
          archiveArtifacts artifacts: 'test-results.xml', fingerprint: true
        }
      }
    }


    stage('Gitleaks Secret Scan') {
      agent {
        kubernetes {
        yaml '''
            apiVersion: v1
            kind: Pod
            spec:
            containers:
            - name: gitleaks
                image: zricethezav/gitleaks
                command:
                - cat
                tty: true
            '''
        }
      }
      steps {
        sh '''
            echo "[INFO] Running Gitleaks scan..."
            gitleaks detect --verbose --source . -f json -r gitleaks.json || true
            echo "[INFO] Gitleaks scan complete. Artifacts will be archived."
          '''       
      }
      post {
        always {
          archiveArtifacts artifacts: 'gitleaks.json', fingerprint: true
        }
      }
    }

    stage('Semgrep Scan') {
      agent {
        kubernetes {
        yaml '''
            apiVersion: v1
            kind: Pod
            spec:
            containers:
            - name: semgrep
                image: semgrep/semgrep
                command:
                - cat
                tty: true
            '''
        }
      }
      steps {
        sh '''
            echo "[INFO] Running Semgrep scan..."
            semgrep ci --json --output semgrep.json
            echo "[INFO] Semgrep scan complete. Artifacts will be archived."
          '''       
      }
      post {
        always {
          archiveArtifacts artifacts: 'semgrep.json', fingerprint: true
        }
      }
    }


    stage('Push Image') {
      agent {
        label 'jenkins-agent-dind'
      }
      steps {
        withCredentials([
          usernamePassword(credentialsId: 'joellots-dockerhub', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASSWORD')
        ]) {
          sh "echo $DH_PASSWORD | docker login -u $DH_USER --password-stdin"
          sh "docker tag ${REGISTRY}:latest ${REGISTRY}:${params.VERSION}"
          sh "docker push ${REGISTRY}:${params.VERSION}"
        }
        
      }
    }


    stage('deploy App') {
      agent {
        kubernetes {
          yamlFile 'k8s/jenkins-agent-dind.yaml'
        }
      }
      steps {
        echo "Deploying version ${params.VERSION} of Cerebro Application"
        input message: 'Do you want to continue?', ok: 'Yes'
        echo "Pushing new deployment manifest to GitOps repo..."

        withCredentials([
        usernamePassword(credentialsId: 'gitops-credentials', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_PASS')
        ]) {
        sh """
            git config --global user.email "${GIT_USER}@gmail.com"
            git config --global user.name "${GIT_USER}"


            git clone https://${GIT_USER}:${GIT_PASS}@gitlab.com/cerebro393109/gitops-cerebro.git
            cd gitops-cerebro/base

            sed -i 's|image: joellots/cerebro:.*|image: joellots/cerebro:${params.VERSION}|' deployment.yaml
            
            cd ..
            git init
            git add .
            git commit -m "Deploy Cerebro ${params.VERSION} via CI pipeline"
            git branch -M main
            git remote add origin https://${GIT_USER}:${GIT_PASS}@gitlab.com/cerebro393109/gitops-cerebro.git
            git push origin main
        """
        }
      }
    }
  }
}
