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
                        sh 'aws ecr get-login --region us-east-1 --no-include-email | bash'
                        sh 'docker push ${REPO}:${TAG}'
                    }
                }
            }
        }
        stage("Deploy") {
            steps {
                script {
                    if (env.BRANCH_NAME == 'master' ) {
                        sh '''
                            KUBECTL_VERSION=$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)
                            curl -LO \
                                https://storage.googleapis.com/kubernetes-release/release/$KUBECTL_VERSION/bin/linux/amd64/kubectl
                            chmod +x kubectl
                            mkdir -p ~/.local/bin/
                            mv kubectl ~/.local/bin/
                        '''
                        sh '''
                            mkdir -p ~/.kube
                            aws s3 cp s3://devex-automated-settings/jenkins/services-kubeconfig.yaml ~/.kube/config
                        '''
                        sh '''
                            export PATH=$PATH:~/.local/bin

                            kubectl delete deploy/jarvis -n jarvis
                            sed -e "s#@@IMAGE@@#${REPO}:${TAG}#" manifests/jarvis-deploy.yaml | kubectl apply -f -
                        '''
                    }
                }
            }
        }
    }
}
