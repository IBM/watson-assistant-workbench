#!/bin/sh

PATH_TO_FILE=$1

DIR_URL=https://na.artifactory.swg-devops.com/artifactory/iot-waw-trevis-generic-local/${TRAVIS_BRANCH}/${TRAVIS_BUILD_NUMBER}

echo "Artifactory: deploy ${PATH_TO_FILE}";
if [ -z "${ARTIFACTORY_API_KEY}" ]; then
    echo "Artifactory: skip - API KEY is not provided for pull requests from forks";
    exit 0
fi

# TODO It does not work with nested folders
for FILENAME in ${PATH_TO_FILE}; do
    echo "Artifactory: deploy ${FILENAME} to ${DIR_URL}/${FILENAME}";
    curl -H 'X-JFrog-Art-Api: '${ARTIFACTORY_API_KEY} -T ${FILENAME} ${DIR_URL}/${TRAVIS_BRANCH}_${TRAVIS_BUILD_NUMBER}_${FILENAME};
    echo "\n";
done
