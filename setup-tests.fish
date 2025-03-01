#!/usr/bin/env fish

podman machine start || true

cp ./kanidm-test-vol.tar.gz ./kanidm-test-vol.tar.gz.old || true

gzip -d ./kanidm-test-vol.tar.gz >kanidm-test-vol.tar

if not podman volume inspect kanidm-test-vol >/dev/null 2>&1
    podman volume create kanidm-test-vol
    sleep 1
    if test (uname -s) = Darwin
        set -gx PODMAN_VOL_PATH (pwd)
        podman machine ssh (podman machine inspect --format="{{.Name}}") sudo podman volume import kanidm-test-vol $PODMAN_VOL_PATH/kanidm-test-vol.tar
    else
        podman volume import kanidm-test-vol ./kanidm-test-vol.tar
    end
end

sleep 1

podman run --name=kanidm-test --publish=8443:8443 --volume=kanidm-test-vol:/data:rw --detach --rm docker.io/kanidm/server:latest

rm kanidm-test-vol.tar || true
mv ./kanidm-test-vol.tar.gz.old ./kanidm-test-vol.tar.gz || true
