from __future__ import absolute_import, annotations, division, print_function

from ..base_exception import BaseAnsibleError


class KanidmException(BaseAnsibleError):
    @property
    def message(self):
        return f"Kanidm error: {self._message}"


class KanidmArgsException(BaseAnsibleError):
    @property
    def message(self):
        return f"Kanidm argument error: {self._message}"


class KanidmRequiredOptionError(BaseAnsibleError):
    @property
    def message(self):
        return f"Kanidm required argument error: {self._message}"


class KanidmModuleError(BaseAnsibleError):
    @property
    def message(self):
        return f"Kanidm module error: {self._message}"


class KanidmAuthenticationFailure(BaseAnsibleError):
    @property
    def message(self):
        return f"Kanidm authentication error: {self._message}"


class KanidmUnexpectedError(BaseAnsibleError):
    @property
    def message(self):
        return f"Kanidm unexpected error: {self._message}"


class KanidmApiError(BaseAnsibleError):
    @property
    def message(self):
        return f"Kanidm API error: {self._message}"
