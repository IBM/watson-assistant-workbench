#!/bin/sh

LOG_FILE=log.log
TAR_NAME=outputs.tar
TAR_GZ_NAME=${TAR_NAME}.gz

cd ./ci

for folder in `find . -name outputs`;
do
    if [ -e "${TAR_NAME}" ]
    then
        echo "Adding ${folder} to ${TAR_NAME}";
        tar --xform s:'./':: -uvf ${TAR_NAME} ${folder};
    else
        echo "Creating ${TAR_NAME} from ${folder}";
        tar --xform s:'./':: -cvf ${TAR_NAME} ${folder};
    fi
done

gzip ${TAR_NAME}

../scripts/artifactory/artifactory-deploy.sh ${TAR_GZ_NAME}

cd ..
./scripts/artifactory/artifactory-deploy.sh ${LOG_FILE}

