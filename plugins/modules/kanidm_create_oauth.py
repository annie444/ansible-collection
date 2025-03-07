#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=E0401,E0402

from __future__ import absolute_import, annotations, division, print_function

__metaclass__ = type  # pylint: disable=C0103

DOCUMENTATION = r"""
---
module: kanidm_create_oauth
short_description: Create an OAuth client in kanidm.
version_added: "1.0.0"
description:
    - This module creates or updates an OAuth client in Kanidm.
    - This module requires the requests Python package.
requirements:
    - "requests>=2.32"
    - "requests-toolbelt>=1"
author: Annie Ehler (@annie444)
options:
    name:
        type: str
        required: true
        aliases:
            - client_name
        description: The name of the OAuth client.

    url:
        type: str
        required: true
        aliases:
            - client_url
        description: The URL of the OAuth client's landing page.

    redirect_url:
        type: list
        elements: str
        required: true
        aliases:
            - redirect_urls
        description: The redirect URLs for the OAuth client.

    scopes:
        type: list
        elements: str
        description: The scopes requested by the OAuth client.
        choices:
            - openid
            - profile
            - email
            - address
            - phone
            - groups
            - ssh_publickeys
        required: true
        aliases:
            - scope

    kanidm:
        type: dict
        required: true
        description: Configuration for the Kanidm client.
        options:
            uri:
                type: str
                required: true
                aliases:
                    - kanidm_uri
                description: The URI of the Kanidm server.
            token:
                type: str
                required: false
                aliases:
                    - kanidm_token
                description: The token for authentication.
            ca_path:
                type: path
                required: false
                aliases:
                    - kanidm_ca_path
                description: The path to the CA certificate.
            username:
                type: str
                required: false
                aliases:
                    - kanidm_username
                description: The username for authentication.
            password:
                type: str
                required: false
                aliases:
                    - kanidm_password
                description: The password for authentication.
            ca_cert_data:
                type: str
                required: false
                description: The CA certificate data as a base64 encoded string.
            verify_ca:
                type: bool
                required: false
                default: true
                description: Whether to verify the Kanidm server's certificate chain.
            connect_timeout:
                type: int
                required: false
                default: 30
                description: The connection timeout in seconds.
        
    display_name:
        type: str
        required: false
        aliases:
            - client_display_name
        default: '{{ name }}'
        description: The display name of the OAuth client.
    group:
        type: str
        default: idm_all_persons
        required: false
        description: The group associated with the OAuth client. Defaults to all persons.
    public:
        type: bool
        default: false
        required: false
        description: Indicates if the client is public.
    claim_join:
        type: str
        choices:
            - array
            - csv
            - ssv
        default: array
        required: false
        description: How to join claims in the response. Defaults to array.
    pkce:
        type: bool
        default: true
        required: false
        description: Indicates if PKCE is enabled.
    legacy_crypto:
        type: bool
        default: false
        required: false
        description: Indicates if legacy cryptography is used.
    strict_redirect:
        type: bool
        default: true
        required: false
        description: Indicates if strict redirect validation is enabled.
    local_redirect:
        type: bool
        default: false
        required: false
        description: Indicates if local redirects are allowed.
    sup_scopes:
        type: list
        elements: dict
        options:
            group:
                type: str
                required: true
                aliases:
                    - sup_scope_group
                description: The group to which the additional scopes apply.
            scopes:
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
                required: true
                description: The additional scopes for the group.
        required: false
        description: Additional scopes for specific groups.

    username:
        type: str
        choices:
            - spn
            - short
        default: spn
        required: false
        description: Preferred username format. Defaults to SPN which takes the format of '<username>@<kanidm.uri>'.

    custom_claims:
        type: list
        elements: dict
        options:
            name:
                type: str
                required: true
                aliases:
                    - claim_name
                description: The name of the custom claim.
            group:
                type: str
                required: true
                aliases:
                    - claim_group
                description: The group to which the custom claim applies.
            values:
                type: list
                elements: str
                required: true
                description: The values for the custom claim.
        required: false
        description: Custom claims to be included in the OAuth response.
    image:
        type: dict
        options:
            src:
                type: str
                required: true
                aliases:
                    - image_src
                description: The source URL of the image.
            format:
                type: str
                choices:
                    - png
                    - jpg
                    - gif
                    - svg
                    - webp
                    - auto
                default: auto
                required: false
                description: The format of the image. Defaults to auto.
        required: false
        aliases:
            - logo
        description: Image configuration for the OAuth client.
    debug:
        type: bool
        default: false
        required: false
        description: Enable debug mode.

"""

EXAMPLES = r"""
# Pass in a message
- name: Create an OAuth client for Nextcloud
  annie444.base.kanidm_create_oauth:
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
    kanidm:
        uri: https://kanidm.example.com
        username: admin
        password: password
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
changed:
    description: A boolean value that indicates if the module has made changes.
    type: bool
    returned: always
    sample: true
requests:
    description: A dictionary of request names and their objects
    type: dict
    returned: always
responses:
    description: A dictionary or request names and their response objects
    type: dict
    returned: always
"""

from ansible.module_utils.basic import AnsibleModule  # pylint: disable=E0401  # noqa: E402
from ansible.module_utils.basic import missing_required_lib  # pylint: disable=E0401  # noqa: E402
from ..module_utils.kanidm.arg_specs import (  # pylint: disable=E0401  # noqa: E402
    KanidmOauthArgs,
    HAS_REQUESTS as ARGS_HAS_REQ,
    REQUESTS_IMP_ERR as ARGS_REQ_IMP_ERR,
    HAS_YAML,
    YAML_IMP_ERR,
    HAS_ENUM,
    STR_ENUM_IMP_ERR,
)
from ..module_utils.kanidm.runner import (  # pylint: disable=E0401  # noqa: E402
    Kanidm,
    HAS_REQUESTS as RUN_HAS_REQ,
    REQUESTS_IMP_ERR as RUN_REQ_IMP_ERR,
    HAS_REQUESTS_TOOLS,
    REQUESTS_TOOLS_IMP_ERR,
)
from ..module_utils.kanidm.exceptions import (  # pylint: disable=E0401  # noqa: E402
    KanidmApiError,
    KanidmArgsException,
    KanidmAuthenticationFailure,
    KanidmException,
    KanidmModuleError,
    KanidmRequiredOptionError,
    KanidmUnexpectedError,
)


def run_module():
    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(changed=False, message="", secret="", requests={}, responses={})

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        supports_check_mode=True,
        **KanidmOauthArgs.full_arg_spec(),
    )

    if not ARGS_HAS_REQ:
        module.fail_json(msg=missing_required_lib(ARGS_REQ_IMP_ERR), **result)

    if not RUN_HAS_REQ:
        module.fail_json(msg=missing_required_lib(RUN_REQ_IMP_ERR), **result)

    if not HAS_REQUESTS_TOOLS:
        module.fail_json(msg=missing_required_lib(REQUESTS_TOOLS_IMP_ERR), **result)

    if not HAS_YAML:
        module.fail_json(msg=missing_required_lib(YAML_IMP_ERR), **result)

    if not HAS_ENUM:
        module.fail_json(msg=missing_required_lib(STR_ENUM_IMP_ERR), **result)

    try:
        args: KanidmOauthArgs = KanidmOauthArgs(**module.params)
    except KanidmArgsException as e:
        module.fail_json(msg=e.message, **result)
    except KanidmRequiredOptionError as e:
        module.fail_json(msg=e.message, **result)
    except KanidmAuthenticationFailure as e:
        module.fail_json(msg=e.message, **result)
    except KanidmException as e:
        module.fail_json(msg=e.message, **result)
    except KanidmModuleError as e:
        module.fail_json(msg=e.message, **result)
    except Exception as e:
        module.fail_json(msg=KanidmUnexpectedError(f"{e}").message, **result)

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    try:
        kanidm: Kanidm = Kanidm(args)
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {e}", **result)

    try:
        result["secret"] = kanidm.create_oauth_client()
    except KanidmArgsException as e:
        result["requests"] = kanidm.requests
        result["responses"] = kanidm.responses
        result["message"] = "failed"
        module.fail_json(msg=e.message, **result)
    except KanidmRequiredOptionError as e:
        result["requests"] = kanidm.requests
        result["responses"] = kanidm.responses
        result["message"] = "failed"
        module.fail_json(msg=e.message, **result)
    except KanidmAuthenticationFailure as e:
        result["requests"] = kanidm.requests
        result["responses"] = kanidm.responses
        result["message"] = "failed"
        module.fail_json(msg=e.message, **result)
    except KanidmException as e:
        result["requests"] = kanidm.requests
        result["responses"] = kanidm.responses
        result["message"] = "failed"
        module.fail_json(msg=e.message, **result)
    except KanidmModuleError as e:
        result["requests"] = kanidm.requests
        result["responses"] = kanidm.responses
        result["message"] = "failed"
        module.fail_json(msg=e.message, **result)
    except KanidmApiError as e:
        result["requests"] = kanidm.requests
        result["responses"] = kanidm.responses
        result["message"] = "failed"
        module.fail_json(msg=e.message, **result)
    except KanidmUnexpectedError as e:
        result["requests"] = kanidm.requests
        result["responses"] = kanidm.responses
        result["message"] = "failed"
        module.fail_json(msg=e.message, **result)
    except Exception as e:
        result["requests"] = kanidm.requests
        result["responses"] = kanidm.responses
        result["message"] = "failed"
        module.fail_json(msg=KanidmUnexpectedError(f"{e}").message, **result)

    result["message"] = "success"
    result["changed"] = True
    result["requests"] = kanidm.requests
    result["responses"] = kanidm.responses

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
