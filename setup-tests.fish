#!/usr/bin/env fish

podman machine start || true

podman run --name=kanidm-test --publish=8443:8443 --volume=kanidm-test-vol:/data:rw --detach --rm docker.io/kanidm/server:latest
