#!/bin/bash
#
# run server in docker

set -o errexit
set -o pipefail
set -o nounset

APP_NAME="regexplanet-python3"

ENVFILE=${1:-.env}

if [ ! -r "${ENVFILE}" ]
then
    echo "ERROR: no .env file '${ENVFILE}'!"
    exit 1
fi

echo "INFO: building docker image..."
docker build \
    --build-arg COMMIT=local@$(git rev-parse --short HEAD) \
    --build-arg LASTMOD=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
    --progress=plain \
    --tag "${APP_NAME}" \
    .

export $(grep -v ^# "${ENVFILE}")

docker run \
    --env PORT=${PORT} \
    --interactive \
    --name "${APP_NAME}" \
    --publish ${PORT}:${PORT} \
    --rm \
    --tty \
    "${APP_NAME}"
