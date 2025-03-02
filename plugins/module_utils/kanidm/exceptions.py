from ansible.errors import (
    AnsibleError,
    AnsibleOptionsError,
    AnsibleModuleError,
    AnsibleAuthenticationFailure,
    AnsibleRequiredOptionError,
)


class KanidmException(AnsibleError):
    @property
    def message(self):
        return f"Kanidm error: {super()}"


class KanidmArgsException(AnsibleOptionsError):
    @property
    def message(self):
        return f"Kanidm argument error: {super()}"


class KanidmRequiredOptionError(AnsibleRequiredOptionError):
    @property
    def message(self):
        return f"Kanidm required argument error: {super()}"


class KanidmModuleError(AnsibleModuleError):
    @property
    def message(self):
        return f"Kanidm module error: {super()}"


class KanidmAuthenticationFailure(AnsibleAuthenticationFailure):
    @property
    def message(self):
        return f"Kanidm authentication error: {super()}"


class KanidmUnexpectedError(AnsibleError):
    @property
    def message(self):
        return f"Kanidm unexpected error: {super()}"


class KanidmApiError(AnsibleModuleError):
    @property
    def message(self):
        return f"Kanidm API error: {super()}"
