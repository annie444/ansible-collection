#!/usr/bin/env fish

if not command -v podman >/dev/null 2>&1 && not command -v docker >/dev/null 2>&1
    echo "Neither Podman nor Docker is installed"
    exit 1
end

cp ./tests/data/kanidm-test-vol.tar.gz ./tests/data/kanidm-test-vol.tar.gz.old || true

gzip -d ./tests/data/kanidm-test-vol.tar.gz >./tests/data/kanidm-test-vol.tar

if command -v podman >/dev/null 2>&1
    if podman container top kanidm-test >/dev/null 2>&1
        exit 0
    end

    if test (uname -s) = Darwin
        podman machine start || true
    end
    if not podman volume inspect kanidm-test-vol >/dev/null 2>&1
        podman volume create kanidm-test-vol
        sleep 1
        if test (uname -s) = Darwin
            set -gx PODMAN_VOL_PATH (pwd)/tests/data
            podman machine ssh (podman machine inspect --format="{{.Name}}") sudo podman volume import kanidm-test-vol $PODMAN_VOL_PATH/kanidm-test-vol.tar
        else
            podman volume import kanidm-test-vol ./tests/data/kanidm-test-vol.tar
        end
    end

    sleep 1
    podman run --name=kanidm-test --publish=8443:8443 --volume=kanidm-test-vol:/data:rw --detach --rm docker.io/kanidm/server:latest

else
    if docker container top kanidm-test >/dev/null 2>&1
        exit 0
    end
    if not docker volume inspect kanidm-test-vol >/dev/null 2>&1
        docker volume create kanidm-test-vol
        sleep 1
        docker volume import kanidm-test-vol ./tests/data/kanidm-test-vol.tar
    end

    sleep 1
    docker run --name=kanidm-test --publish=8443:8443 --volume=kanidm-test-vol:/data:rw --detach --rm docker.io/kanidm/server:latest

end

rm ./tests/data/kanidm-test-vol.tar || true
mv ./tests/data/kanidm-test-vol.tar.gz.old ./tests/data/kanidm-test-vol.tar.gz || true
