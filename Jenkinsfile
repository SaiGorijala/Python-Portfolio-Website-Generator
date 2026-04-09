pipeline {
    agent any

    environment {
        FRONTEND_VM = "frontend@your-frontend-ip"
        BACKEND_VM  = "backend@your-backend-ip"
        APP_DIR     = "/home/ubuntu/app"
    }

    triggers {
        githubPush()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Deploy to Backend') {
            steps {
                sshagent(['backend-ssh-key']) {
                    sh """
                    ssh -o StrictHostKeyChecking=no $BACKEND_VM '
                        mkdir -p $APP_DIR
                    '

                    scp -o StrictHostKeyChecking=no -r * $BACKEND_VM:$APP_DIR

                    ssh -o StrictHostKeyChecking=no $BACKEND_VM '
                        cd $APP_DIR &&
                        source venv/bin/activate &&
                        pkill -f app.py || true &&
                        nohup python app.py > app.log 2>&1 &
                    '
                    """
                }
            }
        }

        stage('Deploy to Frontend') {
            steps {
                sshagent(['frontend-ssh-key']) {
                    sh """
                    ssh -o StrictHostKeyChecking=no $FRONTEND_VM '
                        mkdir -p $APP_DIR
                    '

                    scp -o StrictHostKeyChecking=no -r * $FRONTEND_VM:$APP_DIR

                    ssh -o StrictHostKeyChecking=no $FRONTEND_VM '
                        cd $APP_DIR &&
                        source venv/bin/activate &&
                        pkill -f app.py || true &&
                        nohup python app.py > app.log 2>&1 &
                    '
                    """
                }
            }
        }
    }
}
