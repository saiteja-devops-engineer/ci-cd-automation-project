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
        stage('Checkout Repository') {
            steps {
                checkout scm
                // git url: 'git@github.com:your-user/your-repo.git', branch: 'main'
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
