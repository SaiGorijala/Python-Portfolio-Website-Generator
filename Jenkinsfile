pipeline {
    agent any

    environment {
        IMAGE_NAME = "your-dockerhub-username/portfolio-generator"
        TAG = "${BUILD_NUMBER}"
        FRONTEND_VM = "frontend@your-frontend-ip"
        BACKEND_VM = "backend@your-backend-ip"
    }

    triggers {
        githubPush()
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/SaiGorijala/Python-Portfolio-Website-Generator.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t $IMAGE_NAME:$TAG ."
            }
        }

        stage('Login to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'USER',
                    passwordVariable: 'PASS'
                )]) {
                    sh "echo $PASS | docker login -u $USER --password-stdin"
                }
            }
        }

        stage('Push Image') {
            steps {
                sh "docker push $IMAGE_NAME:$TAG"
            }
        }

        stage('Deploy Backend (Private VM)') {
            steps {
                sshagent(['backend-ssh-key']) {
                    sh """
                    ssh -o StrictHostKeyChecking=no $BACKEND_VM '
                        docker pull $IMAGE_NAME:$TAG &&
                        docker stop backend || true &&
                        docker rm backend || true &&
                        docker run -d -p 8000:8000 --name backend $IMAGE_NAME:$TAG
                    '
                    """
                }
            }
        }

        stage('Deploy Frontend VM') {
            steps {
                sshagent(['frontend-ssh-key']) {
                    sh """
                    ssh -o StrictHostKeyChecking=no $FRONTEND_VM '
                        docker pull $IMAGE_NAME:$TAG &&
                        docker stop frontend || true &&
                        docker rm frontend || true &&
                        docker run -d -p 80:8000 --name frontend $IMAGE_NAME:$TAG
                    '
                    """
                }
            }
        }
    }
}
