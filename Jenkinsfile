#!groovy

pipeline {
    agent { node { label 'docker' } }
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    environment {
        REPO = "406396564037.dkr.ecr.us-east-1.amazonaws.com/jarvis"
        TAG = "${GIT_COMMIT}"
    }
    stages {
        stage('Build') {
            steps {
                sh 'docker build --tag ${REPO}:${TAG} .'
            }
        }
        stage("Push") {
            steps {
                script {
                    if (env.BRANCH_NAME == "master") {
                        sh 'sudo pip install awscli'
                        sh 'aws ecr get-login --region us-east-1 --no-include-email | bash'
                        sh 'docker push ${REPO}:${TAG}'
                    }
                }
            }
        }
    }
}
