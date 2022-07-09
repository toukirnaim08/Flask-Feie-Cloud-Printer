#/bin/bash
GIT_REVISION=$(git rev-parse --short  HEAD| tr --delete "\n")
VERSION=1.0.0
PACKAGE_NAME=unido-printing-service
FULL_VERSION=${VERSION}-${GIT_REVISION}
GENERATION_TIMESTAMP=`date --iso-8601=seconds`

DOCKER_REG_URL=pacdocker.azurecr.io/${PACKAGE_NAME}-production:latest
DOCKER_REG_VER_URL=pacdocker.azurecr.io/${PACKAGE_NAME}-production:${GIT_REVISION}

echo "Building Docker Image with Params"
echo " > Git Revision: ${GIT_REVISION}"
echo " > Full Version: ${FULL_VERSION}"
echo " > Package Name: ${PACKAGE_NAME}"
echo

# Create version file
mkdir -p static
echo "{\"version\": \"${FULL_VERSION}\", \"package_name\": \"${PACKAGE_NAME}\", \"generated\": \"${GENERATION_TIMESTAMP}\"}" > static/application_info.json

docker build \
    --label GIT_REVISION=${GIT_REVISION} \
    --build-arg GIT_REVISION=${GIT_REVISION} \
    --build-arg PACKAGE_NAME=${PACKAGE_NAME} \
    --build-arg FULL_VERSION=${FULL_VERSION} \
    -t ${DOCKER_REG_URL} \
    -f Dockerfile \
    .

# tag the image with revision
docker tag ${DOCKER_REG_URL} ${DOCKER_REG_VER_URL}

echo
echo "Pushing tagged containers:"
echo " > ${DOCKER_REG_URL}"
echo " > ${DOCKER_REG_VER_URL}"
echo

# push generated docker image
docker push ${DOCKER_REG_URL}
docker push ${DOCKER_REG_VER_URL}