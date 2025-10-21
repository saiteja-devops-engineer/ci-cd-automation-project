pipeline {
    agent any
    tools {
        git 'GIT_2_43'  // Your Git tool configured in Jenkins
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
                script {
                    // Using ShiningPanda to select Python
                    withPythonEnv(python: 'PYTHON_3_12_3') {
                        sh '''
                            # Create virtual environment if it doesn't exist
                            [ ! -d "${VENV_DIR}" ] && python -m venv ${VENV_DIR}

                            # Activate virtual environment
                            source $VENV_DIR/bin/activate

                            # Upgrade pip and install dependencies
                            pip install --upgrade pip
                            pip install -r flask_app/requirements.txt
                        '''
                    }
                }
            }
        }
        stage('Run Flask App') {
            options {
                timeout(time: 2, unit: 'MINUTES')
            }
            steps {
                script {
                    // Using ShiningPanda to select Python
                    withPythonEnv(python: 'PYTHON_3_12_3') {
                        sh '''
                            # Activate virtual environment
                            source $VENV_DIR/bin/activate

                            # Ensure Flask is installed
                            python -m flask --version || { echo "Flask not found"; exit 1; }

                            # Start Flask in background
                            python flask_app/app.py & 

                            # Wait loop for Flask startup (max 20s)
                            timeout=0
                            while ! curl -s http://127.0.0.1:5000 > /dev/null; do
                                sleep 2
                                timeout=$((timeout+2))
                                if [ $timeout -gt 20 ]; then
                                    echo "Flask did not start in 20 seconds"
                                    exit 1
                                fi
                            done

                            # Test endpoint
                            curl http://127.0.0.1:5000
                        '''
                    }
                }
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
