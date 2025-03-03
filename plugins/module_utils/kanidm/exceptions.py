from __future__ import absolute_import, annotations, division, print_function

from ansible.module_utils.errors import (
    AnsibleError,
    AnsibleOptionsError,
    AnsibleModuleError,
    AnsibleAuthenticationFailure,
)

try:
    from ansible.module_utils.errors import AnsibleRequiredOptionError
except ImportError:
    from ansible.module_utils.errors import (
        AnsibleOptionsError as AnsibleRequiredOptionError,
    )


class KanidmException(AnsibleError):
    @property
    def message(self):
        return f"Kanidm error: {self._message}"


class KanidmArgsException(AnsibleOptionsError):
    @property
    def message(self):
        return f"Kanidm argument error: {self._message}"


class KanidmRequiredOptionError(AnsibleRequiredOptionError):
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
