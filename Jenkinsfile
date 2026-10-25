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
                    python3 --version
                    pip3 show Flask
                '''
            }
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
