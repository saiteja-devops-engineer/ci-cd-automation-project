pipeline {
    agent any

    options {
        timeout(time: 5, unit: 'SECONDS')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
        disableConcurrentBuilds()
        disableResume()
    }

    stages {
        stage('Checkout') {
            checkout scm
        }
        stage('Start Flask App') {
            steps {
                sh 'PYTHONUNBUFFERED=1 python3 flask_app/app.py &'
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
