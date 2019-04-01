#!/bin/sh

ARTIFACTORY_API_KEY=$1
PATH_TO_FILE=$2
TARGET_FILE_PATH=$3

if [ -z "$3" ]; then
    TARGET_FILE_PATH=$2
fi

DIR_URL=https://na.artifactory.swg-devops.com/artifactory/iot-waw-trevis-generic-local/${TRAVIS_BRANCH}/${TRAVIS_BUILD_NUMBER}

curl -H 'X-JFrog-Art-Api: '${ARTIFACTORY_API_KEY} -O ${DIR_URL}/${PATH_TO_FILE}

mkdir -p `dirname ${TARGET_FILE_PATH}`
mv `basename ${PATH_TO_FILE}` ${TARGET_FILE_PATH}

