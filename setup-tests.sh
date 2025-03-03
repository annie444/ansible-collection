#!/usr/bin/env bash

if ! command -v podman >/dev/null 2>&1 && ! command -v docker >/dev/null 2>&1; then
    echo "Neither Podman nor Docker is installed"
    exit 1
fi

cp ./tests/data/kanidm-test-vol.tar.gz ./tests/data/kanidm-test-vol.tar.gz.old || true

gzip -d ./tests/data/kanidm-test-vol.tar.gz >./tests/data/kanidm-test-vol.tar

if command -v podman >/dev/null 2>&1; then

    if podman container top kanidm-test >/dev/null 2>&1; then
        exit 0
    fi

    if [ "$(uname -s)" = "Darwin" ]; then
        podman machine start || true
    fi

    if ! podman volume inspect kanidm-test-vol >/dev/null 2>&1; then
        podman volume create kanidm-test-vol
        sleep 1
        if [ "$(uname -s)" = "Darwin" ]; then
            PODMAN_VOL_PATH="$(pwd)/tests/data"
            export PODMAN_VOL_PATH
            PODMAN_MACHINE_NAME="$(podman machine inspect --format='{{.Name}}')"
            export PODMAN_MACHINE_NAME
            podman machine ssh "${PODMAN_MACHINE_NAME}" sudo podman volume import kanidm-test-vol "${PODMAN_VOL_PATH}/kanidm-test-vol.tar"
        else
            podman volume import kanidm-test-vol ./tests/data/kanidm-test-vol.tar
        fi
    fi

    sleep 1
    podman run --name=kanidm-test --publish=8443:8443 --volume=kanidm-test-vol:/data:rw --detach --rm docker.io/kanidm/server:latest

else
    if docker container top kanidm-test >/dev/null 2>&1; then
        exit 0
    fi

    if ! docker volume inspect kanidm-test-vol >/dev/null 2>&1; then
        docker volume create kanidm-test-vol
        sleep 1
        docker volume import kanidm-test-vol ./tests/data/kanidm-test-vol.tar
    fi

    sleep 1
    docker run --name=kanidm-test --publish=8443:8443 --volume=kanidm-test-vol:/data:rw --detach --rm docker.io/kanidm/server:latest
fi

rm ./tests/data/kanidm-test-vol.tar || true
mv ./tests/data/kanidm-test-vol.tar.gz.old ./tests/data/kanidm-test-vol.tar.gz || true
