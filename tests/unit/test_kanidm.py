import json
import unittest

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


class TestKanidmModule(unittest.TestCase):
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
            kanidm.main()

    def test_kanidm_auth_succeeds(self):
        with self.assertRaises(AnsibleFailJson):
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
                }
            )
            kanidm.main()

    def test_kanidm_creates_client_if_not_exists(self):
        with self.assertRaises(AnsibleExitJson):
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
                }
            )
            kanidm.main()

    def test_kanidm_updates_client_if_exists(self):
        with self.assertRaises(AnsibleExitJson):
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
                }
            )
            kanidm.main()

        with self.assertRaises(AnsibleExitJson):
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
                        }
                    ],
                }
            )
            kanidm.main()

    def test_kanidm_creates_client_with_different_group(self):
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
            }
        )
        kanidm.main()
