#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=E0401,E402

from __future__ import absolute_import, annotations, division, print_function

__metaclass__ = type  # pylint: disable=C0103

from ..module_utils.kanidm.arg_specs import (
    KanidmOauthArgs,
)

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
""" + KanidmOauthArgs.documentation(indentation=2)

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
from ..module_utils.kanidm.runner import (  # pylint: disable=E0401  # noqa: E402
    Kanidm,
)
from ..module_utils.kanidm.exceptions import (  # pylint: disable=E0401  # noqa: E402
    KanidmArgsException,
    KanidmAuthenticationFailure,
    KanidmException,
    KanidmModuleError,
    KanidmRequiredOptionError,
)


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = KanidmOauthArgs.arg_spec()

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
        argument_spec=module_args,
        supports_check_mode=True,
    )

    try:
        args: KanidmOauthArgs = KanidmOauthArgs(**module.params)
    except KanidmArgsException as e:
        module.fail_json(msg=f"Error parsing arguments: {e}", **result)
    except KanidmRequiredOptionError as e:
        module.fail_json(msg=f"Missing required arguments: {e}", **result)
    except KanidmAuthenticationFailure as e:
        module.fail_json(msg=f"Authentication failed: {e}", **result)
    except KanidmException as e:
        module.fail_json(msg=f"Kanidm error: {e}", **result)
    except KanidmModuleError as e:
        module.fail_json(msg=f"Module error: {e}", **result)
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {e}", **result)

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
        module.fail_json(msg=f"Error parsing arguments: {e}", **result)
    except KanidmRequiredOptionError as e:
        result["requests"] = kanidm.requests
        result["responses"] = kanidm.responses
        result["message"] = "failed"
        module.fail_json(msg=f"Missing required arguments: {e}", **result)
    except KanidmAuthenticationFailure as e:
        result["requests"] = kanidm.requests
        result["responses"] = kanidm.responses
        result["message"] = "failed"
        module.fail_json(msg=f"Authentication failed: {e}", **result)
    except KanidmException as e:
        result["requests"] = kanidm.requests
        result["responses"] = kanidm.responses
        result["message"] = "failed"
        module.fail_json(msg=f"Kanidm error: {e}", **result)
    except KanidmModuleError as e:
        result["requests"] = kanidm.requests
        result["responses"] = kanidm.responses
        result["message"] = "failed"
        module.fail_json(msg=f"Module error: {e}", **result)
    except Exception as e:
        result["requests"] = kanidm.requests
        result["responses"] = kanidm.responses
        result["message"] = "failed"
        module.fail_json(msg=f"Unexpected error: {e}", **result)

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
