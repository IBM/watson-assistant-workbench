#!/bin/sh

END_TIME=$(date +%s%N -d "${ARTIFACTORY_KEEP_DAYS} day ago" | cut -b1-13)

# TODO deleteOld does not work because travis does not update 'lastUpdate' nor 'lastModified' so we just delete files and folders remain

#deleteOld()
#{
#    URL=${1}
#    local DEPTH=${2}
#    echo "Artifactory: process folder ${URL}";
#    LAST_MODIFIED=`curl -s -X GET -H 'X-JFrog-Art-Api: '${ARTIFACTORY_API_KEY} ${URL} | grep "lastModified" | awk -F"\"" '{print $4}'`;
#    echo "Artifactory: last modified ${LAST_MODIFIED}";
#    LAST_MODIFIED_MS=$(date +%s%N -d "${LAST_MODIFIED}" | cut -b1-13);
#
#    if [ "${DEPTH}" -le "0" ]; then
#        echo "Maximal depth reached"
#    elif [ "${END_TIME}" -gt "${LAST_MODIFIED_MS}" ]; then
#        echo "Artifactory: deleting folder because it is older then ${ARTIFACTORY_KEEP_DAYS} days";
#        #curl -X DELETE -H 'X-JFrog-Art-Api: '${ARTIFACTORY_API_KEY}  "https://na.artifactory.swg-devops.com/artifactory/api/storage/iot-waw-trevis-generic-local/${1}"
#    else
#        echo "Artifactory: processing subfolders because folder it is newer then ${ARTIFACTORY_KEEP_DAYS} days";
#        RESULTS=`curl -s -X GET -H 'X-JFrog-Art-Api: '${ARTIFACTORY_API_KEY} ${URL} | grep "    \"uri" | awk -F"\"" '{print $4}'`
#
#        local DEPTH=$((DEPTH-1))
#        for RESULT in ${RESULTS}; do
#            deleteOld ${1}${RESULT} ${DEPTH};
#        done
#    fi
#}

# Delete old folders
#deleteOld "https://na.artifactory.swg-devops.com/artifactory/api/storage/iot-waw-trevis-generic-local" 2
#exit

RESULTS=`curl -s -X GET -H 'X-JFrog-Art-Api: '${ARTIFACTORY_API_KEY} "https://na.artifactory.swg-devops.com/artifactory/api/search/creation?from=0&to=${END_TIME}&repos=iot-waw-trevis-generic-local" | grep uri | awk '{print $3}' | sed s'/.$//' | sed s'/.$//' | sed -r 's/^.{1}//'`

# Delete old files
for RESULT in ${RESULTS}; do
    PATH_TO_FILE=`curl -s -X GET -H 'X-JFrog-Art-Api: '${ARTIFACTORY_API_KEY} ${RESULT} | grep downloadUri | awk '{print $3}' | sed s'/.$//' | sed s'/.$//' | sed -r 's/^.{1}//'`
    echo "Artifactory: delete ${PATH_TO_FILE}"
    if [ -z "${ARTIFACTORY_API_KEY}" ]; then
        echo "Artifactory: skip - API KEY is not provided for pull requests from forks";
        continue
    fi
    curl -X DELETE -H 'X-JFrog-Art-Api: '${ARTIFACTORY_API_KEY}  ${PATH_TO_FILE}
done

