pipeline {
    agent any

    environment {
        FRONTEND_VM = "ubuntu@13.62.226.35"
        BACKEND_VM  = "ubuntu@10.0.0.134"
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
                        if [ ! -d "venv" ]; then
                            python3 -m venv venv
                        fi &&
                        . venv/bin/activate &&
                        pip install -r requirements.txt &&
                        pkill -f app.py || true &&
                        nohup python3 app.py --host=0.0.0.0 --port=5000 > app.log 2>&1 &
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
                        if [ ! -d "venv" ]; then
                            python3 -m venv venv
                        fi &&
                        . venv/bin/activate &&
                        pip install -r requirements.txt &&
                        pkill -f app.py || true &&
                        nohup python3 app.py --host=0.0.0.0 --port=5000 > app.log 2>&1 &
                    '
                    """
                }
            }
        }
    }
}
