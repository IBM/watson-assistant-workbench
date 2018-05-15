#!/bin/sh

PATH_TO_FILE=$1

DIR_URL=https://na.artifactory.swg-devops.com/artifactory/iot-waw-trevis-generic-local/${TRAVIS_BRANCH}/${TRAVIS_BUILD_NUMBER}

# TODO It does not work for with nested folders
echo "Artifactory: deploy ${PATH_TO_FILE}";
for filename in ${PATH_TO_FILE}; do
    echo "Artifactory: deploy ${filename} to ${DIR_URL}/${filename}";
    curl -H 'X-JFrog-Art-Api: '${API_KEY} -T ${filename} ${DIR_URL}/${filename};
    echo "\n";
done
