import json
import os
import sys
import unittest

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.annie444.base.plugins.modules import kanidm_create_oauth


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
                    / f"{datetime.now().isoformat(timespec='microseconds')}_test_kanidm_create_oauth.json",
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
                    dir / f"{kwargs['time']}_test_kanidm_create_oauth.json",
                    "w",
                ) as f:
                    f.write(json.dumps(kwargs, indent=4))
            else:
                sys.stderr.write(json.dumps(kwargs, indent=4))
    raise AnsibleFailJson(kwargs)


class TestKanidmOauthModule(unittest.TestCase):
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
            kanidm_create_oauth.main()

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
                    "display_name": "Test Authentication",
                    "url": "https://testauth.local",
                    "redirect_url": ["https://testauth.local/callback"],
                    "scopes": ["openid", "profile", "email"],
                },
            )
            kanidm_create_oauth.main()
        raised = ej.exception
        self.assertEqual(raised.data["changed"], True)
        self.assertIsInstance(raised.data["secret"], str)
        self.assertTrue(len(raised.data["secret"]) > 0)
        self.assertEqual(raised.data["message"].lower(), "success")

    def test_kanidm_creates_client_if_not_exists(self):
        with self.assertRaises(AnsibleExitJson) as ej:
            set_module_args(
                {
                    "kanidm": {
                        "uri": "https://localhost:8443",
                        "username": "idm_admin",
                        "password": "aSLXKGvBjCad9q6jh22y3dfk8pzZJ3VhFf7VW6NkDv6ZKUvp",
                        "verify_ca": False,
                    },
                    "name": "test_nonexistet_client",
                    "display_name": "Created client when not exists",
                    "url": "https://testnonexistetclient.local",
                    "redirect_url": ["https://testnonexistetclient.local/callback"],
                    "scopes": ["openid", "profile", "email"],
                },
            )
            kanidm_create_oauth.main()
        raised = ej.exception
        self.assertEqual(raised.data["changed"], True)
        self.assertIsInstance(raised.data["secret"], str)
        self.assertTrue(len(raised.data["secret"]) > 0)
        self.assertEqual(raised.data["message"].lower(), "success")

    def test_kanidm_updates_client_if_exists(self):
        with self.assertRaises(AnsibleExitJson) as ej:
            set_module_args(
                {
                    "kanidm": {
                        "uri": "https://localhost:8443",
                        "username": "idm_admin",
                        "password": "aSLXKGvBjCad9q6jh22y3dfk8pzZJ3VhFf7VW6NkDv6ZKUvp",
                        "verify_ca": False,
                    },
                    "name": "test_existing_client",
                    "display_name": "Test existing client",
                    "url": "https://testexistingclient.local",
                    "redirect_url": ["https://testexistingclient.local/callback"],
                    "scopes": ["openid", "profile", "email"],
                },
            )
            kanidm_create_oauth.main()
        raised = ej.exception
        self.assertEqual(raised.data["changed"], True)
        self.assertIsInstance(raised.data["secret"], str)
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
                    "name": "test_existing_client",
                    "display_name": "Test existing client",
                    "url": "https://testexistingclient.local",
                    "redirect_url": ["https://testexistingclient.local/callback"],
                    "scopes": ["openid", "profile", "email"],
                    "sup_scopes": [
                        {
                            "group": "idm_admins",
                            "scopes": ["openid", "profile", "email"],
                        },
                    ],
                },
            )
            kanidm_create_oauth.main()
        raised = ej.exception
        self.assertEqual(raised.data["changed"], True)
        self.assertIsInstance(raised.data["secret"], str)
        self.assertTrue(len(raised.data["secret"]) > 0)
        self.assertEqual(raised.data["message"].lower(), "success")

    def test_kanidm_creates_client_with_different_group(self):
        with self.assertRaises(AnsibleExitJson) as ej:
            set_module_args(
                {
                    "kanidm": {
                        "uri": "https://localhost:8443",
                        "username": "idm_admin",
                        "password": "aSLXKGvBjCad9q6jh22y3dfk8pzZJ3VhFf7VW6NkDv6ZKUvp",
                        "verify_ca": False,
                    },
                    "name": "test_different_group",
                    "display_name": "Test different group",
                    "url": "https://testdifferentgroup.local",
                    "group": "idm_admins",
                    "redirect_url": ["https://testdifferentgroup.local/callback"],
                    "scopes": ["openid", "profile", "email"],
                },
            )
            kanidm_create_oauth.main()
        raised = ej.exception
        self.assertEqual(raised.data["changed"], True)
        self.assertIsInstance(raised.data["secret"], str)
        self.assertTrue(len(raised.data["secret"]) > 0)
        self.assertEqual(raised.data["message"].lower(), "success")

    def test_kanidm_oauth_example(self):
        with self.assertRaises(AnsibleExitJson) as ej:
            set_module_args(
                {
                    "name": "nextcloud",
                    "display_name": "Nextcloud Document Server",
                    "url": "https://nextcloud.example.com",
                    "redirect_url": [
                        "https://nextcloud.example.com/apps/oauth2/authorize",
                        "https://nextcloud.example.com/apps/oauth2/api/v1/token",
                        "https://nextcloud.example.com/index.php/apps/oauth2/authorize",
                        "https://nextcloud.example.com/index.php/apps/oauth2/api/v1/token",
                    ],
                    "scopes": [
                        "openid",
                        "profile",
                        "email",
                    ],
                    "username": "short",
                    "image": {
                        "src": "https://nextcloud.com/c/uploads/2022/11/logo_nextcloud_blue.svg",
                        "format": "svg",
                    },
                    "kanidm": {
                        "uri": "https://localhost:8443",
                        "username": "idm_admin",
                        "password": "aSLXKGvBjCad9q6jh22y3dfk8pzZJ3VhFf7VW6NkDv6ZKUvp",
                        "verify_ca": False,
                    },
                },
            )
            kanidm_create_oauth.main()
        raised = ej.exception
        self.assertEqual(raised.data["changed"], True)
        self.assertIsInstance(raised.data["secret"], str)
        self.assertTrue(len(raised.data["secret"]) > 0)
        self.assertEqual(raised.data["message"].lower(), "success")

    def test_kanidm_oauth_basic_all_args(self):
        with self.assertRaises(AnsibleExitJson) as ej:
            set_module_args(
                {
                    "name": "all_args",
                    "display_name": "Oauth with all args",
                    "url": "https://allargs.com",
                    "redirect_url": [
                        "https://allargs.com/apps/oauth2/authorize",
                        "https://allargs.com/apps/oauth2/api/v1/token",
                        "https://allargs.com/index.php/apps/oauth2/authorize",
                        "https://allargs.com/index.php/apps/oauth2/api/v1/token",
                        "https://allargs.com/index.php/apps/oauth2/authorize/index.html",
                        "https://allargs.com/index.php/apps/oauth2/api/v1/token/index.html",
                    ],
                    "scopes": [
                        "openid",
                        "profile",
                        "email",
                        "address",
                        "phone",
                    ],
                    "group": "idm_admins",
                    "public": False,
                    "claim_join": "array",
                    "pkce": True,
                    "legacy_crypto": False,
                    "strict_redirect": True,
                    "local_redirect": False,
                    "username": "short",
                    "sup_scopes": [
                        {
                            "group": "idm_admins",
                            "scopes": ["openid", "profile", "email", "groups"],
                        },
                        {
                            "group": "idm_all_persons",
                            "scopes": ["openid", "profile", "email", "ssh_publickeys"],
                        },
                    ],
                    "image": {
                        "src": "https://nextcloud.com/c/uploads/2022/11/logo_nextcloud_blue.svg",
                        "format": "svg",
                    },
                    "custom_claims": [
                        {
                            "name": "custom_claim",
                            "values": ["custom_value1", "custom_value2"],
                            "group": "idm_admins",
                        },
                        {
                            "name": "custom_claim2",
                            "values": ["custom_value3", "custom_value4"],
                            "group": "idm_all_persons",
                        },
                    ],
                    "kanidm": {
                        "uri": "https://localhost:8443",
                        "username": "idm_admin",
                        "password": "aSLXKGvBjCad9q6jh22y3dfk8pzZJ3VhFf7VW6NkDv6ZKUvp",
                        "verify_ca": False,
                    },
                },
            )
            kanidm_create_oauth.main()
        raised = ej.exception
        self.assertEqual(raised.data["changed"], True)
        self.assertIsInstance(raised.data["secret"], str)
        self.assertTrue(len(raised.data["secret"]) > 0)
        self.assertEqual(raised.data["message"].lower(), "success")

    def test_kanidm_oauth_public_all_args(self):
        with self.assertRaises(AnsibleExitJson) as ej:
            set_module_args(
                {
                    "name": "all_args_public",
                    "display_name": "Oauth public with all args",
                    "url": "https://allargs.com",
                    "public": True,
                    "redirect_url": [
                        "https://allargs.com/apps/oauth2/authorize",
                        "https://allargs.com/apps/oauth2/api/v1/token",
                        "https://allargs.com/index.php/apps/oauth2/authorize",
                        "https://allargs.com/index.php/apps/oauth2/api/v1/token",
                        "https://allargs.com/index.php/apps/oauth2/authorize/index.html",
                        "https://allargs.com/index.php/apps/oauth2/api/v1/token/index.html",
                    ],
                    "scopes": [
                        "openid",
                        "profile",
                        "email",
                        "address",
                        "phone",
                    ],
                    "group": "idm_admins",
                    "local_redirect": True,
                    "claim_join": "array",
                    "pkce": True,
                    "legacy_crypto": False,
                    "strict_redirect": True,
                    "username": "short",
                    "sup_scopes": [
                        {
                            "group": "idm_admins",
                            "scopes": ["openid", "profile", "email", "groups"],
                        },
                        {
                            "group": "idm_all_persons",
                            "scopes": ["openid", "profile", "email", "ssh_publickeys"],
                        },
                    ],
                    "image": {
                        "src": "https://nextcloud.com/c/uploads/2022/11/logo_nextcloud_blue.svg",
                        "format": "svg",
                    },
                    "custom_claims": [
                        {
                            "name": "custom_claim",
                            "values": ["custom_value1", "custom_value2"],
                            "group": "idm_admins",
                        },
                        {
                            "name": "custom_claim2",
                            "values": ["custom_value3", "custom_value4"],
                            "group": "idm_all_persons",
                        },
                    ],
                    "kanidm": {
                        "uri": "https://localhost:8443",
                        "username": "idm_admin",
                        "password": "aSLXKGvBjCad9q6jh22y3dfk8pzZJ3VhFf7VW6NkDv6ZKUvp",
                        "verify_ca": False,
                    },
                },
            )
            kanidm_create_oauth.main()
        raised = ej.exception
        self.assertEqual(raised.data["changed"], True)
        self.assertIsInstance(raised.data["secret"], str)
        self.assertTrue(len(raised.data["secret"]) > 0)
        self.assertEqual(raised.data["message"].lower(), "success")
