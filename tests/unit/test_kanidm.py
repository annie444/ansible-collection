import subprocess
import shutil
import json
import unittest
import os
from pathlib import Path

from ansible_collections.annie444.base.plugins.modules import kanidm

from unittest.mock import patch
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""

    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""

    pass


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


def setUpContainer():
    path = os.environ.get("PATH", "")
    home = os.environ.get("HOME", "")
    proc_path: list[Path] = [
        Path(home) / ".local" / "bin",
        Path(home) / "bin",
        Path("/opt/podman/bin"),
        Path("/opt/homebrew/bin"),
        Path("/opt/homebrew/sbin"),
        Path("/usr/local/bin"),
        Path("/usr/local/sbin"),
        Path("/usr/bin"),
        Path("/bin"),
        Path("/usr/sbin"),
        Path("/sbin"),
    ]
    proc_path.extend([Path(p) for p in list(Path(path).parts)])
    proc_path = list(set(proc_path))
    podman = (
        shutil.which("podman", path=os.pathsep.join([str(p) for p in proc_path]))
        or "podman"
    )
    containers = subprocess.run(
        podman + " ps --format='{{.Names}}'",
        shell=True,
        timeout=60,
        check=True,
        executable=os.environ.get("SHELL", "/bin/bash"),
        user=os.environ.get("USER"),
        capture_output=True,
    )
    running = containers.stdout.decode("utf-8").splitlines()
    running.extend(containers.stderr.decode("utf-8").splitlines())
    if "kanidm-test" not in running:
        subprocess.run(
            f"{podman} machine init",
            shell=True,
            timeout=60,
            check=False,
            executable=os.environ.get("SHELL", "/bin/bash"),
            user=os.environ.get("USER"),
        )
        subprocess.run(
            f"{podman} machine start",
            shell=True,
            timeout=60,
            check=False,
            executable=os.environ.get("SHELL", "/bin/bash"),
            user=os.environ.get("USER"),
        )
        subprocess.run(
            f"{podman} run --name=kanidm-test --publish=8443:8443 --volume=kanidm-test-vol:/data:rw --detach --rm docker.io/kanidm/server:latest",
            shell=True,
            timeout=60,
            check=True,
            executable=os.environ.get("SHELL", "/bin/bash"),
            user=os.environ.get("USER"),
        )


def tearDownContainer():
    path = os.environ.get("PATH", "")
    home = os.environ.get("HOME", "")
    proc_path: list[Path] = [
        Path(home) / ".local" / "bin",
        Path(home) / "bin",
        Path("/opt/podman/bin"),
        Path("/opt/homebrew/bin"),
        Path("/opt/homebrew/sbin"),
        Path("/usr/local/bin"),
        Path("/usr/local/sbin"),
        Path("/usr/bin"),
        Path("/bin"),
        Path("/usr/sbin"),
        Path("/sbin"),
    ]
    proc_path.extend([Path(p) for p in list(Path(path).parts)])
    proc_path = list(set(proc_path))
    podman = (
        shutil.which("podman", path=os.pathsep.join([str(p) for p in proc_path]))
        or "podman"
    )
    subprocess.run(
        f"{podman} stop kanidm-test",
        shell=True,
        timeout=60,
        check=True,
        executable=os.environ.get("SHELL", "/bin/bash"),
        user=os.environ.get("USER"),
    )


class TestKanidmModule(unittest.TestCase):
    def setUp(self):
        setUpContainer()
        self.mock_module_helper = patch.multiple(
            basic.AnsibleModule,
            exit_json=exit_json,
            fail_json=fail_json,
        )
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)
        self.addCleanup(tearDownContainer)

    def test_module_fail_when_required_args_missing(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            kanidm.main()

    def test_kanidm_auth_succeeds(self):
        set_module_args(
            {
                "kanidm": {
                    "uri": "https://localhost:8443",
                    "username": "idm_admin",
                    "password": "aSLXKGvBjCad9q6jh22y3dfk8pzZJ3VhFf7VW6NkDv6ZKUvp",
                    "verify_hostnames": "false",
                    "verify_certificate": "false",
                },
                "name": "test_one",
                "display_name": "Test 1",
                "url": "https://test1.local",
                "redirect_url": ["https://test1.local/callback"],
                "scopes": ["openid", "profile", "email"],
            }
        )
        kanidm.main()

    def test_kanidm_creates_group_if_not_exists(self):
        set_module_args(
            {
                "kanidm": {
                    "uri": "https://localhost:8443",
                    "username": "idm_admin",
                    "password": "aSLXKGvBjCad9q6jh22y3dfk8pzZJ3VhFf7VW6NkDv6ZKUvp",
                    "verify_hostnames": "false",
                    "verify_certificate": "false",
                },
                "name": "test_two",
                "display_name": "Test 2",
                "url": "https://test2.local",
                "group": "test_group",
                "redirect_url": ["https://test2.local/callback"],
                "scopes": ["openid", "profile", "email"],
            }
        )
        kanidm.main()

    def test_kanidm_creates_group_if_exists(self):
        set_module_args(
            {
                "kanidm": {
                    "uri": "https://localhost:8443",
                    "username": "idm_admin",
                    "password": "aSLXKGvBjCad9q6jh22y3dfk8pzZJ3VhFf7VW6NkDv6ZKUvp",
                    "verify_hostnames": "false",
                    "verify_certificate": "false",
                },
                "name": "test_three",
                "display_name": "Test 3",
                "url": "https://test3.local",
                "group": "idm_admins",
                "redirect_url": ["https://test3.local/callback"],
                "scopes": ["openid", "profile", "email"],
            }
        )
        kanidm.main()
