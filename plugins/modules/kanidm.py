#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=E0401,E402

from __future__ import absolute_import, annotations, division, print_function

__metaclass__ = type  # pylint: disable=C0103


DOCUMENTATION = r"""
---
module: kanidm

short_description: A kanidm proof-of-concept module

version_added: "1.0.0"

description: This module creates an OAuth client in kanidm.

options:
    kanidm:
        description: The parameters used to connect to the Kanidm server.
        required: false
        type: dict
        options:
            file:
                description: The path to the kanidm configuration file.
                required: false
                type: "str"
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
            radius_cert_data:
                description: The base64 encoded RADIUS certificate data.
                required: false
                type: str
            radius_key_path:
                description: The path to the RADIUS key.
                required: false
                type: str
            radius_key_data:
                description: The base64 encoded RADIUS key data.
                required: false
                type: str
            radius_ca_path:
                description: The path to the RADIUS CA certificate.
                required: false
                type: str
            radius_ca_cert_data:
                description: The base64 encoded RADIUS CA certificate data.
                required: false
                type: str
            radius_ca_dir:
                description: The path to the RADIUS CA directory.
                required: false
                type: str
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


import asyncio  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from typing import Coroutine, List, Literal, Optional  # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # pylint: disable=E0401  # noqa: E402

from kanidm import KanidmClient  # noqa: E402
from kanidm.exceptions import (
    AuthBeginFailed,
    AuthCredFailed,
    AuthInitFailed,
    AuthMechUnknown,
    NoMatchingEntries,
    ServerURLNotSet,
)
from kanidm.types import ClientResponse, KanidmClientConfig  # noqa: E402


@dataclass
class RadGroup:
    group: str
    vlan: int


@dataclass
class RadClient:
    name: str
    ip: str
    secret: str


@dataclass
class KanidmConf:
    uri: str
    token: Optional[str] = None
    verify_hostnames: bool = True
    verify_certificate: bool = False
    ca_path: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    ca_cert_data: Optional[str] = None
    verify_ca: bool = False
    radius_cert_path: Optional[str] = None
    radius_cert_data: Optional[str] = None
    radius_key_path: Optional[str] = None
    radius_key_data: Optional[str] = None
    radius_ca_path: Optional[str] = None
    radius_ca_cert_data: Optional[str] = None
    radius_ca_dir: Optional[str] = None
    radius_required_groups: Optional[List[str]] = None
    radius_default_vlan: Optional[int] = None
    radius_groups: Optional[List[RadGroup]] = None
    radius_clients: Optional[List[RadClient]] = None
    connect_timeout: int = 30


@dataclass
class ClientConfig:
    uri: str
    token: Optional[str] = None
    verify_hostnames: bool = True
    verify_certificate: bool = False
    ca_path: Optional[str] = None
    file: Optional[str] = None
    config: Optional[KanidmConf] = None

    def __init__(self, **kwargs):
        if "config" in kwargs:
            self.config = KanidmConf(
                uri=kwargs["uri"],
                token=kwargs["token"],
                verify_hostnames=kwargs["verify_hostnames"],
                verify_certificate=kwargs["verify_certificate"],
                ca_path=kwargs["ca_path"],
                **kwargs["config"],
            )
            del kwargs["config"]
        super().__init__(**kwargs)


@dataclass
class SubScope:
    group: str
    scopes: List[
        Literal[
            "openid", "profile", "email", "address", "phone", "groups", "ssh_publickeys"
        ]
    ]


@dataclass
class CustomClaim:
    name: str
    group: str
    values: List[str]


@dataclass
class Image:
    src: str
    format: Literal["png", "jpg", "gif", "svg", "webp", "auto"] = "auto"


@dataclass
class KanidmArgs:
    name: str
    url: str
    redirect_url: List[str]
    scopes: List[
        Literal[
            "openid", "profile", "email", "address", "phone", "groups", "ssh_publickeys"
        ]
    ]
    kanidm: ClientConfig
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


async def create_basic_client(client: KanidmClient, args: KanidmArgs) -> ClientResponse:
    valid = await client.check_token_valid()
    if not valid:
        if (
            args.kanidm.config
            and args.kanidm.config.username
            and args.kanidm.config.password
        ):
            await client.authenticate_password(
                args.kanidm.config.username, args.kanidm.config.password
            )
    groups = await client.group_list()
    if args.group not in [g.name for g in groups]:
        await client.group_create(args.group)
        if args.kanidm.config and args.kanidm.config.username:
            await client.group_set_members(args.group, [args.kanidm.config.username])
    basic_client = await client.oauth2_rs_basic_create(
        rs_name=args.name,
        displayname=args.display_name if args.display_name is not None else args.name,
        origin=args.url,
    )
    return basic_client


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        kanidm=dict(
            description="The parameters used to connect to the Kanidm server.",
            required=True,
            type="dict",
            options=dict(
                file=dict(
                    description="The path to the kanidm configuration file.",
                    required=False,
                    type="str",
                ),
                token=dict(
                    description="The token to authenticate to the kanidm server.",
                    required=False,
                    type="str",
                ),
                username=dict(
                    description="The username to authenticate to the kanidm server.",
                    required=False,
                    type="str",
                ),
                password=dict(
                    description="The password to authenticate to the kanidm server.",
                    required=False,
                    type="str",
                ),
                verify_hostnames=dict(
                    description="Whether to verify hostnames.",
                    default=True,
                    type="bool",
                ),
                verify_certificate=dict(
                    description="Whether to verify certificates.",
                    default=True,
                    type="bool",
                ),
                ca_path=dict(
                    description="The path to the CA certificate.",
                    required=False,
                    type="str",
                ),
                ca_cert_data=dict(
                    description="The base64 encoded CA certificate data.",
                    required=False,
                    type="str",
                ),
                verify_ca=dict(
                    description="Whether to verify the CA.",
                    default=True,
                    type="bool",
                ),
                radius_cert_path=dict(
                    description="The path to the RADIUS certificate.",
                    required=False,
                    type="str",
                ),
                radius_cert_data=dict(
                    description="The base64 encoded RADIUS certificate data.",
                    required=False,
                    type="str",
                ),
                radius_key_path=dict(
                    description="The path to the RADIUS key.",
                    required=False,
                    type="str",
                ),
                radius_key_data=dict(
                    description="The base64 encoded RADIUS key data.",
                    required=False,
                    type="str",
                ),
                radius_ca_path=dict(
                    description="The path to the RADIUS CA certificate.",
                    required=False,
                    type="str",
                ),
                radius_ca_cert_data=dict(
                    description="The base64 encoded RADIUS CA certificate data.",
                    required=False,
                    type="str",
                ),
                radius_ca_dir=dict(
                    description="The path to the RADIUS CA directory.",
                    required=False,
                    type="str",
                ),
                radius_required_groups=dict(
                    description="The required RADIUS groups.",
                    required=False,
                    type="list",
                    elements="str",
                ),
                radius_default_vlan=dict(
                    description="The default RADIUS VLAN.",
                    required=False,
                    type="int",
                ),
                radius_groups=dict(
                    description="The RADIUS groups.",
                    required=False,
                    type="list",
                    elements="dict",
                    options=dict(
                        group=dict(
                            description="The group name.",
                            type="str",
                            required=True,
                        ),
                        vlan=dict(
                            description="The VLAN for the group.",
                            type="int",
                            required=True,
                        ),
                    ),
                ),
                radius_clients=dict(
                    description="The RADIUS clients.",
                    required=False,
                    type="list",
                    elements="dict",
                    options=dict(
                        name=dict(
                            description="The name of the client.",
                            type="str",
                            required=True,
                        ),
                        ip=dict(
                            description="The IP address of the client.",
                            type="str",
                            required=True,
                        ),
                        secret=dict(
                            description="The shared secret of the client.",
                            type="str",
                            required=True,
                        ),
                    ),
                ),
                connect_timeout=dict(
                    description="The connection timeout.",
                    default=30,
                    type="int",
                ),
            ),
        ),
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
                format=dict(
                    type="str",
                    default="auto",
                    choices=["png", "jpg", "gif", "svg", "webp", "auto"],
                    description="The image format.",
                ),
            ),
        ),
    )

    mutually_exclusive = [
        ["kanidm.file", "kanidm.username", "kanidm.radius_cert_path"],
        [
            "kanidm.token",
            "kanidm.username",
            "kanidm.radius_cert_path",
        ],
        ["kanidm.radius_cert_path", "kanidm.radius_cert_data"],
        ["kanidm.radius_key_path", "kanidm.radius_key_data"],
        ["kanidm.radius_ca_path", "kanidm.radius_ca_cert_data"],
        ["kanidm.radius_ca_dir", "kanidm.radius_ca_dir_remote"],
    ]
    required_together = [
        ["kanidm.username", "kanidm.password"],
    ]
    required_if = [
        [
            "kanidm.file",
            None,
            (
                "kanidm.token",
                "kanidm.username",
                "kanidm.radius_cert_path",
                "kanidm.radius_cert_data",
            ),
            False,
        ],
    ]

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
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=mutually_exclusive,
        required_together=required_together,
        required_if=required_if,
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    args: KanidmArgs = KanidmArgs(**module.params)

    if args.kanidm.file:
        client = KanidmClient(
            config_file=args.kanidm.file,
            uri=args.kanidm.uri,
            token=args.kanidm.token,
            verify_hostnames=args.kanidm.verify_hostnames,
            verify_certificate=args.kanidm.verify_certificate,
            ca_path=args.kanidm.ca_path,
        )
    else:
        config = KanidmClientConfig(**args.kanidm.config.__dict__)
        client = KanidmClient(config)

    try:
        run = asyncio.run(create_basic_client(client, args))
    except AuthBeginFailed:
        module.fail_json(
            msg="Unable to begin authentication. Possibly incorrect username.", **result
        )
    except AuthCredFailed:
        module.fail_json(msg="Incorrect username or password.", **result)
    except AuthInitFailed:
        module.fail_json(msg="Unable to initalize authentication", **result)
    except AuthMechUnknown:
        module.fail_json(msg="Unable to determine authentication mechanism", **result)
    except ServerURLNotSet:
        module.fail_json(msg="Invalid kanidm server url", **result)
    except NoMatchingEntries:
        module.fail_json(msg="User not found", **result)

    if run.status_code >= 200 and run.status_code < 300:
        result["message"] = "success"
        result["changed"] = True

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
