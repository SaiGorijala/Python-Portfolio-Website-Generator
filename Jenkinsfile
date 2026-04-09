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
                git branch: 'main',
                    url: 'https://github.com/SaiGorijala/Python-Portfolio-Website-Generator.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                '''
            }
        }

        stage('Deploy to Backend VM (Private)') {
            steps {
                sshagent(['backend-ssh-key']) {
                    sh """
                    ssh -o StrictHostKeyChecking=no $BACKEND_VM '
                        rm -rf $APP_DIR &&
                        mkdir -p $APP_DIR
                    '

                    scp -o StrictHostKeyChecking=no -r * $BACKEND_VM:$APP_DIR

                    ssh -o StrictHostKeyChecking=no $BACKEND_VM '
                        cd $APP_DIR &&
                        python3 -m venv venv &&
                        . venv/bin/activate &&
                        pip install -r requirements.txt &&
                        pkill -f app.py || true &&
                        nohup python3 app.py > app.log 2>&1 &
                    '
                    """
                }
            }
        }

        stage('Deploy to Frontend VM') {
            steps {
                sshagent(['frontend-ssh-key']) {
                    sh """
                    ssh -o StrictHostKeyChecking=no $FRONTEND_VM '
                        rm -rf $APP_DIR &&
                        mkdir -p $APP_DIR
                    '

                    scp -o StrictHostKeyChecking=no -r * $FRONTEND_VM:$APP_DIR

                    ssh -o StrictHostKeyChecking=no $FRONTEND_VM '
                        cd $APP_DIR &&
                        python3 -m venv venv &&
                        . venv/bin/activate &&
                        pip install -r requirements.txt &&
                        pkill -f app.py || true &&
                        nohup python3 app.py > app.log 2>&1 &
                    '
                    """
                }
            }
        }
    }
}
