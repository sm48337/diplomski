#!/bin/bash
FILE_PATH="${@: -1}"
REAL_PATH=$(pwd)/"${FILE_PATH}"
VIRTUAL_PATH="/docker/${FILE_PATH}"

# Remove last argument
set -- "${@:1:$(($#-1))}"

docker run --rm -v "${REAL_PATH}":"${VIRTUAL_PATH}" cincan/sleuthkit "${@}" "${VIRTUAL_PATH}"
