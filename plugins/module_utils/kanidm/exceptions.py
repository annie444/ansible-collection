from ansible.errors import (
    AnsibleError,
    AnsibleOptionsError,
    AnsibleModuleError,
    AnsibleAuthenticationFailure,
)


class KanidmException(AnsibleError):
    @property
    def message(self):
        return f"Kanidm error: {self._message}"


class KanidmArgsException(AnsibleOptionsError):
    @property
    def message(self):
        return f"Kanidm argument error: {self._message}"


class KanidmRequiredOptionError(AnsibleOptionsError):
    @property
    def message(self):
        return f"Kanidm required argument error: {self._message}"


class KanidmModuleError(AnsibleModuleError):
    @property
    def message(self):
        return f"Kanidm module error: {self._message}"


class KanidmAuthenticationFailure(AnsibleAuthenticationFailure):
    @property
    def message(self):
        return f"Kanidm authentication error: {self._message}"


class KanidmUnexpectedError(AnsibleError):
    @property
    def message(self):
        return f"Kanidm unexpected error: {self._message}"


class KanidmApiError(AnsibleModuleError):
    @property
    def message(self):
        return f"Kanidm API error: {self._message}"
