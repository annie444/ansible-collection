#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=E0401,E0402

from __future__ import absolute_import, annotations, division, print_function

__metaclass__ = type  # pylint: disable=C0103

DOCUMENTATION = r"""
---
module: kanidm_create_group
short_description: Create a Group in kanidm.
version_added: "1.0.0"
description:
  - This module creates or updates an Group in Kanidm.
  - This module requires the requests and requests-toolbelt Python packages.
requirements:
    - "requests>=2.32"
    - "requests-toolbelt>=1"
author: Annie Ehler (@annie444)
extends_documentation_fragment:
    - annie444.base.kanidmgroupargs
    - annie444.base.kanidmconf
"""

EXAMPLES = r"""
# Pass in a message
- name: Create a Group for nextcloud users
  annie444.base.kanidm_create_group:
    name: nextcloud
    users:
        - user1
        - user2
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
from ..module_utils.kanidm.arg_specs.group import (  # pylint: disable=E0401  # noqa: E402
    KanidmGroupArgs,
    HAS_YAML,
    YAML_IMP_ERR,
    HAS_ENUM,
    STR_ENUM_IMP_ERR,
)
from ..module_utils.kanidm.runner.group import KanidmGroup  # pylint: disable=E0401  # noqa: E402
from ..module_utils.kanidm.runner.api import (  # pylint: disable=E0401  # noqa: E402
    HAS_REQUESTS as RUN_HAS_REQ,
    REQUESTS_IMP_ERR as RUN_REQ_IMP_ERR,
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
    result = dict(changed=False, message="", requests={}, responses={})

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        supports_check_mode=True,
        **KanidmGroupArgs.full_arg_spec(),
    )

    if not RUN_HAS_REQ:
        module.fail_json(msg=missing_required_lib(RUN_REQ_IMP_ERR), **result)

    if not HAS_YAML:
        module.fail_json(msg=missing_required_lib(YAML_IMP_ERR), **result)

    if not HAS_ENUM:
        module.fail_json(msg=missing_required_lib(STR_ENUM_IMP_ERR), **result)

    try:
        args: KanidmGroupArgs = KanidmGroupArgs(**module.params)
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
        kanidm: KanidmGroup = KanidmGroup(args)
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {e}", **result)

    try:
        kanidm.create_group()
    except KanidmArgsException as e:
        result["requests"] = kanidm.api.requests
        result["responses"] = kanidm.api.responses
        result["message"] = "failed"
        module.fail_json(msg=e.message, **result)
    except KanidmRequiredOptionError as e:
        result["requests"] = kanidm.api.requests
        result["responses"] = kanidm.api.responses
        result["message"] = "failed"
        module.fail_json(msg=e.message, **result)
    except KanidmAuthenticationFailure as e:
        result["requests"] = kanidm.api.requests
        result["responses"] = kanidm.api.responses
        result["message"] = "failed"
        module.fail_json(msg=e.message, **result)
    except KanidmException as e:
        result["requests"] = kanidm.api.requests
        result["responses"] = kanidm.api.responses
        result["message"] = "failed"
        module.fail_json(msg=e.message, **result)
    except KanidmModuleError as e:
        result["requests"] = kanidm.api.requests
        result["responses"] = kanidm.api.responses
        result["message"] = "failed"
        module.fail_json(msg=e.message, **result)
    except KanidmApiError as e:
        result["requests"] = kanidm.api.requests
        result["responses"] = kanidm.api.responses
        result["message"] = "failed"
        module.fail_json(msg=e.message, **result)
    except KanidmUnexpectedError as e:
        result["requests"] = kanidm.api.requests
        result["responses"] = kanidm.api.responses
        result["message"] = "failed"
        module.fail_json(msg=e.message, **result)
    except Exception as e:
        result["requests"] = kanidm.api.requests
        result["responses"] = kanidm.api.responses
        result["message"] = "failed"
        module.fail_json(msg=KanidmUnexpectedError(f"{e}").message, **result)

    result["message"] = "success"
    result["changed"] = True
    result["requests"] = kanidm.api.requests
    result["responses"] = kanidm.api.responses

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
