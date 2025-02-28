#!/usr/bin/env fish

podman machine start || true

gzip -d ./kanidm-test-vol.tar.gz >kanidm-test-vol.tar

if not podman volume inspect kanidm-test-vol >/dev/null 2>&1
    if test (uname -s) = Darwin
        podman machine ssh podman-machine-default podman volume import kanidm-test-vol (pwd)/kanidm-test-vol.tar
    else
        podman volume import kanidm-test-vol ./kanidm-test-vol.tar
    end
end

podman run --name=kanidm-test --publish=8443:8443 --volume=kanidm-test-vol:/data:rw --detach --rm docker.io/kanidm/server:latest
