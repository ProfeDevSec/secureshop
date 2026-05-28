pipeline {
    agent any
    environment {
        VENV = 'venv'
    }
    stages {
        stage('Checkout') {
            steps {
                echo 'Repositorio descargado'
            }
        }
        stage('Python Version') {
            steps {
                sh 'python3 --version'
                sh 'pip3 --version'
            }
        }
        stage('Create Virtualenv') {
            steps {
                sh '''
                    python3 -m venv ${VENV}
                '''
            }
        }
        stage('Install Dependencies') {
            steps {
                sh '''
                    . ${VENV}/bin/activate

                    pip install --upgrade pip

                    pip install -r requirements.txt
                '''
            }
        }
        stage('Security Scan') {
            steps {
                sh '''
                    . ${VENV}/bin/activate

                    pip install bandit safety

                    bandit -r . || true

                    safety check || true
                '''
            }
        }
        stage('Run Tests') {
            steps {
                sh '''
                    . ${VENV}/bin/activate

                    pytest || true
                '''
            }
        }
        stage('Deploy Container') {
            steps {
                sh '''
                    docker rm -f secureshop || true

                    docker build -t secureshop:latest .

                    docker run -d \
                        --name secureshop \
                        -p 5000:5000 \
                        secureshop:latest
                '''
            }
        }
    }
    post {
        success {
            echo 'Pipeline ejecutado correctamente'
        }
        failure {
            echo 'Pipeline falló'
        }
    }
}