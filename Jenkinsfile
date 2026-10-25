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
				# 1. Force-kill anything running on port 5000 to clear out zombies
				echo "Cleaning up any old processes on port 5000..."
				sudo fuser -k 5000/tcp || true
				
				# 2. Make absolutely sure we are in the right directory and execute the file directly
				cd "$WORKSPACE"
				
				# 3. Launch using explicit host binding flags in the command line tool argument
				JENKINS_NODE_COOKIE=dontKillMe PYTHONUNBUFFERED=1 python3 flask_app/app.py --host=0.0.0.0 --port=5000 > flask.log 2>&1 &
				APP_PID=$!
				
				# 4. Set the 10-minute auto-destruct window
				(sleep 600 && kill -9 $APP_PID) &
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
