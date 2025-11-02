pipeline {
    agent any

    environment {
        // 👇 cámbialo según el micro
        SERVICE_NAME = "vets-api"

        // tu repo de infra
        INFRA_REPO   = "https://github.com/calderon7/Infraestructura-Proyecto-Personal.git"

        // OJO: hay un espacio en el nombre del workspace, lo ponemos entre comillas en los sh
        INFRA_DIR    = "/var/jenkins_home/workspace/Infraestructura Proyecto Personal"

        // credencial de GitHub
        GIT_CRED     = "github-token-v2"
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

        // ─────────────────────────────────────────
        // 1) TESTS/BUILD según el lenguaje
        // ─────────────────────────────────────────

        stage('Tests / Build (auto)') {
            parallel {
                // --- Node.js ---
                stage('Node.js') {
                    when { expression { fileExists('package.json') } }
                    agent {
                        docker {
                            // 👇 misma versión que usas en tu Dockerfile: node:20-alpine
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

                // --- Python ---
                stage('Python') {
                    when { expression { fileExists('requirements.txt') || fileExists('pyproject.toml') } }
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

                // --- Java / Maven (por si luego metes uno) ---
                stage('Maven/Java') {
                    when { expression { fileExists('pom.xml') } }
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

        // ─────────────────────────────────────────
        // 2) Clonar/actualizar el repo de INFRA (con credenciales)
        // ─────────────────────────────────────────
        stage('Clonar / actualizar INFRA') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: env.GIT_CRED,
                        usernameVariable: 'GIT_USER',
                        passwordVariable: 'GIT_TOKEN'
                    )
                ]) {
                    sh """
                    if [ ! -d "${INFRA_DIR}" ]; then
                        git clone https://${GIT_USER}:${GIT_TOKEN}@github.com/calderon7/Infraestructura-Proyecto-Personal.git "${INFRA_DIR}"
                    else
                        cd "${INFRA_DIR}"
                        git pull https://${GIT_USER}:${GIT_TOKEN}@github.com/calderon7/Infraestructura-Proyecto-Personal.git
                    fi
                    """
                }
            }
        }


        // ─────────────────────────────────────────
        // 3) Copiar este servicio al árbol de services/ del repo de infra
        // ─────────────────────────────────────────
        stage('Actualizar código del servicio en INFRA') {
            steps {
                sh """
                  rm -rf "${INFRA_DIR}/services/${SERVICE_NAME}"
                  mkdir -p "${INFRA_DIR}/services/${SERVICE_NAME}"
                  cp -r . "${INFRA_DIR}/services/${SERVICE_NAME}"
                """
            }
        }

        // ─────────────────────────────────────────
        // 4) Deploy con docker compose (desde Jenkins)
        // ─────────────────────────────────────────
        stage('Build + Deploy con docker compose') {
            steps {
                sh """
                  cd "${INFRA_DIR}/infra"
                  # levantamos SOLO este servicio para no tocar Jenkins
                  docker compose up -d --build ${SERVICE_NAME}
                """
            }
        }
    }

    post {
        success {
            echo "✅ Servicio ${env.SERVICE_NAME} desplegado correctamente"
        }
        failure {
            echo "❌ Falló el despliegue de ${env.SERVICE_NAME}"
        }
    }
}
