pipeline {
    agent any

    // 👇 ajusta estas tres según el repo
    environment {
        SERVICE_NAME = "vets-api"   // <- cámbialo en cada repo
        INFRA_REPO   = "https://github.com/calderon7/Infraestructura-Proyecto-Personal.git"
        INFRA_DIR    = "/var/jenkins_home/workspace/Infraestructura Proyecto Personal"  // carpeta donde clonamos infra
        GIT_CRED     = "github-token-v2" // el ID de la credencial en Jenkins
    }

    options {
        timestamps()
    }

    stages {

        stage('Checkout servicio') {
            steps {
                // este es el repo actual (el del servicio)
                checkout([$class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: env.GIT_URL ?: scm.userRemoteConfigs[0].getUrl(), // usa el del job
                        credentialsId: env.GIT_CRED
                    ]]
                ])
            }
        }

        stage('Tests / Lint (opcional)') {
            when {
                expression { fileExists('package.json') || fileExists('pyproject.toml') || fileExists('requirements.txt') }
            }
            steps {
                script {
                    if (fileExists('package.json')) {
                        sh '''
                          npm install
                          npm test || true
                        '''
                    } else if (fileExists('requirements.txt')) {
                        sh '''
                          python3 -m venv .venv
                          . .venv/bin/activate
                          pip install -r requirements.txt
                          pytest || true
                        '''
                    }
                }
            }
        }

        stage('Clonar / actualizar INFRA') {
            steps {
                sh """
                  if [ ! -d ${INFRA_DIR} ]; then
                    git clone ${INFRA_REPO} ${INFRA_DIR}
                  else
                    cd ${INFRA_DIR} && git pull
                  fi
                """
            }
        }

        stage('Actualizar código del servicio en INFRA') {
            steps {
                sh """
                  rm -rf ${INFRA_DIR}/services/${SERVICE_NAME}
                  mkdir -p ${INFRA_DIR}/services/${SERVICE_NAME}
                  cp -r . ${INFRA_DIR}/services/${SERVICE_NAME}
                """
            }
        }

        stage('Build + Deploy con docker compose') {
            steps {
                sh """
                  cd ${INFRA_DIR}/infra
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
