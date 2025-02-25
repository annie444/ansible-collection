#!/usr/bin/python
# -*- coding: utf-8 -*-

# kanidm.py - A custom action plugin for Ansible.
# Author: Your Name
# License: GPL-3.0-or-later
# pylint: disable=E0401

from __future__ import absolute_import, annotations, division, print_function

__metaclass__ = type  # pylint: disable=C0103

from typing import TYPE_CHECKING, List, Literal

from kanidm import KanidmClientConfig


if TYPE_CHECKING:
    from typing import Optional, Dict, Any, TypedDict

DOCUMENTATION = r"""
---
module: kanidm

short_description: A kanidm proof-of-concept module

version_added: "1.0.0"

description: This module creates an OAuth client in kanidm.

options:
    kanidm:
        description: The parameters used to connect to the Kanidm server.
        required: true
        type: dict
        options:
            uri:
                description: The URI of the kanidm server.
                required: true
                type: str
            token:
                description: The token to authenticate to the kanidm server.
                required: false
                type: str
            username:
                description: The username to authenticate to the kanidm server.
                required: false
                type: str
            password:
                description: The password to authenticate to the kanidm server.
                required: false
                type: str
            verify_hostnames:
                description: Whether to verify hostnames.
                default: true
                type: bool
            verify_certificate:
                description: Whether to verify certificates.
                default: true
                type: bool
            ca_path:
                description: The path to the CA certificate.
                required: false
                type: str
            ca_path_remote:
                description: Whether the CA certificate is remote.
                default: false
                type: bool
            ca_cert_data:
                description: The base64 encoded CA certificate data.
                required: false
                type: str
            verify_ca:
                description: Whether to verify the CA.
                default: true
                type: bool
            radius_cert_path:
                description: The path to the RADIUS certificate.
                required: false
                type: str
            radius_cert_path_remote:
                description: Whether the RADIUS certificate is remote.
                default: false
                type: bool
            radius_cert_data:
                description: The base64 encoded RADIUS certificate data.
                required: false
                type: str
            radius_key_path:
                description: The path to the RADIUS key.
                required: false
                type: str
            radius_key_path_remote:
                description: Whether the RADIUS key is remote.
                default: false
                type: bool
            radius_key_data:
                description: The base64 encoded RADIUS key data.
                required: false
                type: str
            radius_ca_path:
                description: The path to the RADIUS CA certificate.
                required: false
                type: str
            radius_ca_path_remote:
                description: Whether the RADIUS CA certificate is remote.
                default: false
                type: bool
            radius_ca_cert_data:
                description: The base64 encoded RADIUS CA certificate data.
                required: false
                type: str
            radius_ca_dir:
                description: The path to the RADIUS CA directory.
                required: false
                type: str
            radius_ca_dir_remote:
                description: Whether the RADIUS CA directory is remote.
                default: false
                type: bool
            radius_required_groups:
                description: The required RADIUS groups.
                required: false
                type: list
                elements: str
            radius_default_vlan:
                description: The default RADIUS VLAN.
                required: false
                type: int
            radius_groups:
                description: The RADIUS groups.
                required: false
                type: list
                elements: dict
                options:
                    group:
                        description: The group name.
                        type: str
                        required: true
                    vlan:
                        description: The VLAN for the group.
                        type: int
                        required: true
            radius_clients:
                description: The RADIUS clients.
                required: false
                type: list
                elements: dict
                options:
                    name:
                        description: The name of the client.
                        type: str
                        required: true
                    ip:
                        description: The IP address of the client.
                        type: str
                        required: true
                    secret:
                        description: The shared secret of the client.
                        type: str
                        required: true
            connect_timeout:
                description: The connection timeout.
                default: 30
                type: int
    name:
        description: The name of the OAuth client to create.
        required: true
        type: str
    display_name:
        description: The display name of the OAuth client to create.
        required: false
        type: str
    group:
        description: The user group to assign the OAuth client to.
        default: idm_all_persons
        type: str
    public:
        description: Whether the OAuth client is public.
        default: false
        type: bool
    claim_join:
        description: How to represent joined claims. Options are as a json array (array), as a comma separated list (csv), or as a space separated list (ssv).
        default: array
        type: str
        choices:
            - array
            - csv
            - ssv
    url:
        description:
            - The URL to the landing page for the application.
            - Kanidm will redirect to this URL after authentication if the client doesn't take over the OAuth flow. 
        required: true
        type: str
    redirect_url:
        description: The URL to redirect to after authentication.
        required: true
        type: list
        elements: str
    pkce:
        description: Whether to use PKCE.
        default: true
        type: bool
    legacy_crypto:
        description: Whether to use legacy crypto.
        default: false
        type: bool
    strict_redirect:
        description: Whether to strictly enforce redirect URLs.
        default: true
        type: bool
    local_redirect:
        description: 
            - Whether to allow local redirect URLs. (e.g. http://localhost)
            - Only applies if O(strict_redirect=false) and O(pkce=true).
        default: false
        type: bool
    username:
        description: The user data to use as the username for this OAuth client. The default is the subject principal name (spn) which takes the form of <username>@<kanidm-url>..
        default: spn
        type: str
        choices:
            - spn
            - short
    scopes:
        description:
            - The scopes to assign to the OAuth client.
            - If you are creating an OpenID Connect (OIDC) client you MUST provide a scope map containing O(scopes=["openid"]). Without this, OpenID Connect clients WILL NOT WORK!
        required: true
        type: list
        elements: str
        choices:
            - openid
            - profile
            - email
            - address
            - phone
            - groups
            - ssh_publickeys
    sup_scopes:
        description: The supplemental scopes to assign to the OAuth client.
        required: false
        type: list
        elements: dict
        options:
            group:
                description: The group to assign the scope to.
                type: str
                required: true
            scopes:
                description: The scopes to assign to the group.
                type: list
                elements: str
                required: true
                choices:
                    - openid
                    - profile
                    - email
                    - address
                    - phone
                    - groups
                    - ssh_publickeys
    custom_claims:
        description: Custom claims to assign to the client.
        type: list
        elements: dict
        options:
            name:
                description: The name of the claim.
                type: str
                required: true
            group:
                description: The group to assign the claim to. Defaults to O(group).
                type: str
                default: "{{ group }}"
            values:
                description: The values of the claim.
                type: list
                elements: str
                required: true
    image:
        description: The image to display for the client.
        required: false
        type: dict
        options:
            src:
                description: The URL or path to the image.
                type: str
                required: true
            remote_src:
                description: Whether the image is a remote file. (Will be ignored if O(image.src) is a URL.)
                default: false
                type: bool
            format:
                description: The image format.
                default: auto
                type: str
                choices:
                    - png
                    - jpg
                    - gif
                    - svg
                    - webp
                    - auto

author:
    - Annie Ehler (@annie444)
"""

EXAMPLES = r"""
# Pass in a message
- name: Create an OAuth client for Nextcloud
  annie444.base.kanidm:
    name: nextcloud
    display_name: Nextcloud Document Server
    url: https://nextcloud.example.com
    redirect_url:
        - https://nextcloud.example.com/apps/oauth2/authorize
        - https://nextcloud.example.com/apps/oauth2/api/v1/token
        # If pretty urls aren't enabled:
        - https://nextcloud.example.com/index.php/apps/oauth2/authorize
        - https://nextcloud.example.com/index.php/apps/oauth2/api/v1/token
    scopes:
        - openid
        - profile
        - email
    username: short
    image:
        src: https://nextcloud.com/c/uploads/2022/11/logo_nextcloud_blue.svg
        format: svg
"""

RETURN = r"""
secret:
    description: The client secret for the OAuth client.
    type: str
    returned: success
    sample: 'Y5g3PvCBwfDWbcE1WmVRdMFTtI9FyvHvTbjUKIV7hVKXpqxUjTeJfvpg1fzj4Nmx'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'Success'
"""


from ansible.module_utils.basic import AnsibleModule  # pylint: disable=E0401 # noqa: E402


class SubScope(TypedDict):
    group: str
    scopes: List[
        Literal[
            "openid", "profile", "email", "address", "phone", "groups", "ssh_publickeys"
        ]
    ]


class CustomClaim(TypedDict):
    name: str
    group: str
    values: List[str]


class Image(TypedDict):
    src: str
    remote_src: bool
    format: Literal["png", "jpg", "gif", "svg", "webp", "auto"]


class Args(TypedDict):
    name: str
    url: str

    redirect_url: List[str]
    scopes: List[
        Literal[
            "openid", "profile", "email", "address", "phone", "groups", "ssh_publickeys"
        ]
    ]
    display_name: Optional[str] = None
    group: str = "idm_all_persons"
    public: bool = False
    claim_join: Literal["array", "csv", "ssv"] = "array"
    pkce: bool = True
    legacy_crypto: bool = False
    strict_redirect: bool = True
    local_redirect: bool = False
    username: Literal["spn", "short"] = "spn"
    sup_scopes: Optional[List[SubScope]] = None
    custom_claims: Optional[List[CustomClaim]] = None
    image: Optional[Image] = None


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(
            type="str",
            required=True,
            description="The name of the OAuth client to create.",
        ),
        display_name=dict(
            type="str",
            required=False,
            default=None,
            description="The display name of the OAuth client to create.",
        ),
        group=dict(
            type="str",
            required=False,
            default="idm_all_persons",
            description="The user group to assign the OAuth client to.",
        ),
        public=dict(
            type="bool",
            required=False,
            default=False,
            description="Whether the OAuth client is public.",
        ),
        claim_join=dict(
            type="str",
            required=False,
            default="array",
            choices=["array", "csv", "ssv"],
            description="How to represent joined claims.",
        ),
        url=dict(
            type="str",
            required=True,
            description="The URL to the landing page for the application. Kanidm will redirect to this URL after authentication if the client doesn't take over the OAuth flow.",
        ),
        redirect_url=dict(
            type="list",
            elements="str",
            required=True,
            description="The URL to redirect to after authentication.",
        ),
        pkce=dict(
            type="bool",
            required=False,
            default=True,
            description="Whether to use PKCE.",
        ),
        legacy_crypto=dict(
            type="bool",
            required=False,
            default=False,
            description="Whether to use legacy crypto.",
        ),
        strict_redirect=dict(
            type="bool",
            required=False,
            default=True,
            description="Whether to strictly enforce redirect URLs.",
        ),
        local_redirect=dict(
            type="bool",
            required=False,
            default=False,
            description="Whether to allow local redirect URLs. (e.g. http://localhost) Only applies if O(strict_redirect=false) and O(pkce=true).",
        ),
        username=dict(
            type="str",
            required=False,
            default="spn",
            choices=["spn", "short"],
            description="The user data to use as the username for this OAuth client. The default is the subject principal name (spn) which takes the form of <username>@<kanidm-url>.",
        ),
        scopes=dict(
            type="list",
            elements="str",
            required=True,
            description="The scopes to assign to the OAuth client.",
            choices=[
                "openid",
                "profile",
                "email",
                "address",
                "phone",
                "groups",
                "ssh_publickeys",
            ],
        ),
        sup_scopes=dict(
            type="list",
            elements="dict",
            required=False,
            description="The supplemental scopes to assign to the OAuth client.",
            options=dict(
                group=dict(
                    type="str",
                    required=True,
                    description="The group to assign the scope to.",
                ),
                scopes=dict(
                    type="list",
                    elements="str",
                    required=True,
                    description="The scopes to assign to the group.",
                    choices=[
                        "openid",
                        "profile",
                        "email",
                        "address",
                        "phone",
                        "groups",
                        "ssh_publickeys",
                    ],
                ),
            ),
        ),
        custom_claims=dict(
            type="list",
            elements="dict",
            required=False,
            description="Custom claims to assign to the client.",
            options=dict(
                name=dict(
                    type="str", required=True, description="The name of the claim."
                ),
                group=dict(
                    type="str",
                    default="{{ group }}",
                    description="The group to assign the claim to. Defaults to O(group).",
                ),
                values=dict(
                    type="list",
                    elements="str",
                    required=True,
                    description="The values of the claim.",
                ),
            ),
        ),
        image=dict(
            type="dict",
            required=False,
            description="The image to display for the client.",
            options=dict(
                src=dict(
                    type="str",
                    required=True,
                    description="The URL or path to the image.",
                ),
                remote_src=dict(
                    type="bool",
                    default=False,
                    description="Whether the image is a remote file. (Will be ignored if O(image.src) is a URL.)",
                ),
                format=dict(
                    type="str",
                    default="auto",
                    choices=["png", "jpg", "gif", "svg", "webp", "auto"],
                    description="The image format.",
                ),
            ),
        ),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(changed=False, message="", secret="")

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    args: Args = Args(module.params)

    config = KanidmClientConfig()

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result["message"] = "goodbye"

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    if module.params["new"]:
        result["changed"] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if module.params["name"] == "fail me":
        module.fail_json(msg="You requested this to fail", **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
