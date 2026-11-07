pipeline {
    agent any

    options {
        timeout(time: 5, unit: 'MINUTES')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Distroless Image') {
            steps {
                sh 'docker build -t holiday-calendar-app:latest .'
            }
        }

        stage('Deploy Container') {
            steps {
                sh '''
                    echo "Stopping any existing container instance..."
                    docker stop holiday-app-instance || true
                    docker rm holiday-app-instance || true

                    echo "Starting new Distroless container..."
                    docker run -d --name holiday-app-instance -p 5000:5000 holiday-calendar-app:latest

                    # Detach subshell to auto-destruct container after 10 minutes (600s)
                    nohup sh -c "sleep 600 && docker stop holiday-app-instance && docker rm holiday-app-instance" > /dev/null 2>&1 &
                '''
                echo "Application live! Access at: http://<your-jenkins-server-ip>:5000"
            }
        }
    }

    post {
        failure {
            echo "Deployment failed. Fetching container logs:"
            sh 'docker logs holiday-app-instance || true'
        }
    }
}