pipeline {
    agent any

    environment {
        SERVICE_NAME       = "vets-api"
        INFRA_REPO         = "https://github.com/calderon7/Infraestructura-Proyecto-Personal.git"
        INFRA_DIR          = "/var/jenkins_home/workspace/Infraestructura Proyecto Personal"
        GIT_CRED           = "github-token-v2"

        SONARQUBE_ENV      = "sonarqube-local"
        SONAR_SCANNER      = "sonar-scanner"
        SONAR_PROJECT_KEY  = "vets-api"
    }

    options {
        timestamps()
    }

    stages {

        stage('Checkout servicio') {
            steps {
                checkout([$class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: env.GIT_URL ?: scm.userRemoteConfigs[0].getUrl(),
                        credentialsId: env.GIT_CRED
                    ]]
                ])
            }
        }

        stage('Tests / Build (auto)') {
            parallel {

                stage('Node.js') {
                    when {
                        expression { fileExists('package.json') }
                    }
                    agent {
                        docker {
                            image 'node:20-alpine'
                            args '-v $PWD:/app -w /app'
                        }
                    }
                    steps {
                        sh '''
                          npm install
                          npm test || true
                          npm run build || true
                        '''
                    }
                }

                stage('Python') {
                    when {
                        expression { fileExists('requirements.txt') || fileExists('pyproject.toml') }
                    }
                    agent {
                        docker {
                            image 'python:3.12-slim'
                            args '-v $PWD:/app -w /app'
                        }
                    }
                    steps {
                        sh '''
                          if [ -f requirements.txt ]; then
                            pip install -r requirements.txt
                          fi
                          pytest || true
                        '''
                    }
                }

                stage('Maven/Java') {
                    when {
                        expression { fileExists('pom.xml') }
                    }
                    agent {
                        docker {
                            image 'maven:3.9-eclipse-temurin-17'
                            args '-v $PWD:/app -w /app'
                        }
                    }
                    steps {
                        sh 'mvn -B -DskipTests package'
                    }
                }
            }
        }

        stage('Clonar / actualizar INFRA') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.GIT_CRED, usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                    sh """
                      if [ ! -d "${INFRA_DIR}" ]; then
                        git clone https://${GIT_USER}:${GIT_TOKEN}@github.com/calderon7/Infraestructura-Proyecto-Personal.git "${INFRA_DIR}"
                      else
                        cd "${INFRA_DIR}" && git pull https://${GIT_USER}:${GIT_TOKEN}@github.com/calderon7/Infraestructura-Proyecto-Personal.git
                      fi
                    """
                }
            }
        }

        stage('Actualizar código del servicio en INFRA') {
            steps {
                sh """
                  rm -rf "${INFRA_DIR}/services/${SERVICE_NAME}"
                  mkdir -p "${INFRA_DIR}/services/${SERVICE_NAME}"
                  cp -r . "${INFRA_DIR}/services/${SERVICE_NAME}"
                """
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONARQUBE_ENV}") {
                    script {
                        def scannerHome = tool "${SONAR_SCANNER}"
                        sh """
                          ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=$SONAR_HOST_URL \
                            -Dsonar.login=$SONAR_AUTH_TOKEN \
                            || true
                        """
                    }
                }
            }
        }

        stage('Build + Deploy con docker compose') {
            steps {
                sh """
                  cd "${INFRA_DIR}/infra"
                  docker compose up -d --build ${SERVICE_NAME}
                """
            }
        }
    }

    post {
        success {
            echo "✅ Servicio ${env.SERVICE_NAME} desplegado y analizado"
        }
        failure {
            echo "❌ Falló el pipeline"
        }
    }
}
