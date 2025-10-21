pipeline {
    agent any
    tools {
        Git 'GIT_2_43'
        Python 'PYTHON_3_12_3'
    }
    environment {
        VENV_DIR = '/opt/python3_vir_env'
    }
    options {
        timeout(time: 6, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '50', artifactNumToKeepStr: '50'))
        disableConcurrentBuilds()
        disableRestartFromStage()
        timestamps()
    }
    stages {
        stage('Checkout Repository') {
            options {
                timeout(time: 2, unit: 'MINUTES')
            }
            steps {
                checkout scm
            }
        }
        stage('Python Virtual Env Setup') {
            options {
                timeout(time: 2, unit: 'MINUTES')
            }
            steps {
                sh '''
                    source $VENV_DIR/bin/activate
                    pip install --upgrade pip
                    pip install -r flask_app/requirements.txt
                '''
            }
        }
        stage('Run Flask App') {
            options {
                timeout(time: 2, unit: 'MINUTES')
            }
            steps {
                sh '''
                    source $VENV_DIR/bin/activate
                    python -m flask --version || { echo "Flask not found"; exit 1; }
                    python flask_app/app.py & 

                    timeout=0
                    while ! curl -s http://127.0.0.1:5000 > /dev/null; do
                        sleep 2
                        timeout=$((timeout+2))
                        if [ $timeout -gt 20 ]; then
                            echo "Flask did not start in 20 seconds"
                            exit 1
                        fi
                    done

                    curl http://127.0.0.1:5000
                '''
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: '*',
                             allowEmptyArchive: true,
                             fingerprint: true
        }
    }
}
