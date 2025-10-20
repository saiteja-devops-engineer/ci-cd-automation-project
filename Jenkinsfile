pipeline {
    agent any
    options {
        timeout(time: 1, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '50', artifactNumToKeepStr: '50'))
        disableConcurrentBuilds()
        disableRestartFromStage()
        timestamps()
    }
    stages {
        stage('Build') {
            steps {
                echo 'Started building package from the App code.'
                sleep 2
                echo 'Completed Build package from code.'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing the App Package.'
                sleep 2
                echo 'Completed Testing of the App Package.'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Started Deploying the App.'
                sleep 2
                echo 'Completed Deploying the App.'
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
