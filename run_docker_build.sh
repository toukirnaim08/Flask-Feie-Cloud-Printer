#/bin/bash
PACKAGE_NAME=printing-solution

DOCKER_REG_URL=toukir08/${PACKAGE_NAME}-development:latest

echo "Building Docker Image with Params"
echo " > Package Name: ${PACKAGE_NAME}"
echo

docker build \
    --label PACKAGE_NAME=${PACKAGE_NAME} \
    -t ${DOCKER_REG_URL} \
    -f Dockerfile \
    .

# tag the image
docker tag ${DOCKER_REG_URL}

#echo
#echo "Pushing tagged containers:"
#echo " > ${DOCKER_REG_URL}"
#echo

# push generated docker image
#docker push ${DOCKER_REG_URL}
#docker push ${DOCKER_REG_VER_URL}
