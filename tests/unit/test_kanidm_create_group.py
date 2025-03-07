import json
import unittest
import os
from pathlib import Path
import sys
from datetime import datetime

from ansible_collections.annie444.base.plugins.modules import kanidm_create_group

from unittest.mock import patch
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


test_name = "create_group"


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""

    def __init__(self, data):
        self.data = data


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""

    def __init__(self, data):
        self.data = data


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if "changed" not in kwargs:
        raise ValueError("changed is a required key in exit_json")
    if os.environ.get("ANSIBLE_VERBOSITY", "0").isnumeric():
        verbosity = int(os.environ.get("ANSIBLE_VERBOSITY", "0"))
        if verbosity >= 1:
            if (
                verbosity >= 3
                and "requests" in kwargs
                and "responses" in kwargs
                and "name" in list(kwargs["requests"].values())[0]
                and "name" in list(kwargs["responses"].values())[0]
            ):
                paired_calls = {}
                for req, data in kwargs["requests"].items():
                    name = ""
                    for i in req:
                        if i.isalnum():
                            name += i
                    paired_calls[req] = {
                        "request": data,
                        "response": kwargs["responses"][req] or {},
                    }
                kwargs["paired_calls"] = paired_calls

            log_dir = os.environ.get("LOG_DIR")
            if log_dir is not None and isinstance(log_dir, str):
                dir = Path(log_dir)
                if not dir.exists():
                    os.makedirs(dir)
                with open(
                    dir
                    / f"{datetime.now().isoformat(timespec='microseconds')}_test_kanidm_{test_name}.json",
                    "w",
                ) as f:
                    f.write(json.dumps(kwargs, indent=4))
            else:
                sys.stderr.write(json.dumps(kwargs, indent=4))

    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs["failed"] = True
    if os.environ.get("ANSIBLE_VERBOSITY", "0").isnumeric():
        verbosity = int(os.environ.get("ANSIBLE_VERBOSITY", "0"))
        if verbosity >= 1:
            kwargs["time"] = datetime.now().isoformat(timespec="microseconds")
            if (
                verbosity >= 3
                and "requests" in kwargs
                and "responses" in kwargs
                and "name" in list(kwargs["requests"].values())[0]
                and "name" in list(kwargs["responses"].values())[0]
            ):
                paired_calls = {}
                for req, data in kwargs["requests"].items():
                    name = ""
                    for i in req:
                        if i.isalnum():
                            name += i
                    paired_calls[req] = {
                        "request": data,
                        "response": kwargs["responses"][req] or {},
                    }
                kwargs["paired_calls"] = paired_calls

            log_dir = os.environ.get("LOG_DIR")
            if log_dir is not None and isinstance(log_dir, str):
                dir = Path(log_dir)
                if not dir.exists():
                    os.makedirs(dir)
                with open(
                    dir / f"{kwargs['time']}_test_kanidm_{test_name}.json",
                    "w",
                ) as f:
                    f.write(json.dumps(kwargs, indent=4))
            else:
                sys.stderr.write(json.dumps(kwargs, indent=4))
    raise AnsibleFailJson(kwargs)


class TestKanidmGroupModule(unittest.TestCase):
    def setUp(self):
        self.mock_module_helper = patch.multiple(
            basic.AnsibleModule,
            exit_json=exit_json,
            fail_json=fail_json,
        )
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_module_fail_when_required_args_missing(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            kanidm_create_group.main()

    def test_kanidm_auth_succeeds(self):
        with self.assertRaises(AnsibleExitJson) as ej:
            set_module_args(
                {
                    "kanidm": {
                        "uri": "https://localhost:8443",
                        "username": "idm_admin",
                        "password": "aSLXKGvBjCad9q6jh22y3dfk8pzZJ3VhFf7VW6NkDv6ZKUvp",
                        "verify_ca": False,
                    },
                    "name": "test_auth",
                    "users": ["user1", "user2"],
                }
            )
            kanidm_create_group.main()
        raised = ej.exception
        self.assertEqual(raised.data["changed"], True)
        self.assertIsInstance(raised.data["secret"], str)
        self.assertEqual(raised.data["message"].lower(), "success")

    def test_kanidm_updates_users_if_exists(self):
        with self.assertRaises(AnsibleExitJson) as ej:
            set_module_args(
                {
                    "kanidm": {
                        "uri": "https://localhost:8443",
                        "username": "idm_admin",
                        "password": "aSLXKGvBjCad9q6jh22y3dfk8pzZJ3VhFf7VW6NkDv6ZKUvp",
                        "verify_ca": False,
                    },
                    "name": "test_auth",
                    "users": ["user1", "user2"],
                }
            )
            kanidm_create_group.main()
        raised = ej.exception
        self.assertEqual(raised.data["changed"], True)
        self.assertTrue(len(raised.data["secret"]) > 0)
        self.assertEqual(raised.data["message"].lower(), "success")

        with self.assertRaises(AnsibleExitJson) as ej:
            set_module_args(
                {
                    "kanidm": {
                        "uri": "https://localhost:8443",
                        "username": "idm_admin",
                        "password": "aSLXKGvBjCad9q6jh22y3dfk8pzZJ3VhFf7VW6NkDv6ZKUvp",
                        "verify_ca": False,
                    },
                    "name": "test_auth",
                    "users": ["user1", "user2", "user3"],
                }
            )
            kanidm_create_group.main()
        raised = ej.exception
        self.assertEqual(raised.data["changed"], True)
        self.assertIsInstance(raised.data["secret"], str)
        self.assertEqual(raised.data["message"].lower(), "success")

    def test_kanidm_group_all_args(self):
        with self.assertRaises(AnsibleExitJson) as ej:
            set_module_args(
                {
                    "name": "all_args",
                    "users": ["user1", "user2"],
                    "parent": "idm_admins",
                    "kanidm": {
                        "uri": "https://localhost:8443",
                        "username": "idm_admin",
                        "password": "aSLXKGvBjCad9q6jh22y3dfk8pzZJ3VhFf7VW6NkDv6ZKUvp",
                        "verify_ca": False,
                    },
                }
            )
            kanidm_create_group.main()
        raised = ej.exception
        self.assertEqual(raised.data["changed"], True)
        self.assertTrue(len(raised.data["secret"]) > 0)
        self.assertEqual(raised.data["message"].lower(), "success")
