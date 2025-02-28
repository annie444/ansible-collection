from ansible.errors import (
    AnsibleError,
    AnsibleOptionsError,
    AnsibleModuleError,
    AnsibleAuthenticationFailure,
    AnsibleRequiredOptionError,
)


class KanidmException(AnsibleError):
    pass


class KanidmArgsException(AnsibleOptionsError):
    pass


class KanidmRequiredOptionError(AnsibleRequiredOptionError):
    pass


class KanidmModuleError(AnsibleModuleError):
    pass


class KanidmAuthenticationFailure(AnsibleAuthenticationFailure):
    pass
