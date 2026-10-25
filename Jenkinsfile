pipeline {
    agent any

    options {
        timeout(time: 5, unit: 'SECONDS')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Check dependencies') {
            steps {
                sh '''
                    pwd
                    ls
                    python3 --version
                    pip3 show Flask
                '''
            }
        }
        stage('Start Flask App') {
            steps {
                sh '''
                    export FLASK_APP=flask_app/app.py
                    export FLASK_RUN_HOST=0.0.0.0
                    export FLASK_RUN_PORT=5000

                    # 1. Start Flask in the background and ignore the Jenkins janitor cookie
                    JENKINS_NODE_COOKIE=dontKillMe PYTHONUNBUFFERED=1 python3 flask_app/app.py > flask.log 2>&1 &
                    APP_PID=$!

                    # 2. Start a separate background timer that kills the app after 10 minutes (600 seconds)
                    (sleep 600 && kill $APP_PID) &
                '''
                echo "Application started successfully! Jenkins will exit now, and the app will auto-destruct in 10 minutes."
            }
        }
    }

    post {
        always {
            echo 'Archiving build files...'
            archiveArtifacts    artifacts: '**/*', 
                                fingerprint: true,
                                allowEmptyArchive: true
        }
    }
}
