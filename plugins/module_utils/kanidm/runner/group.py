from __future__ import absolute_import, annotations, division, print_function

from ..arg_specs.group import (
    KanidmGroupArgs,
)
from ..exceptions import (
    KanidmAuthenticationFailure,
    KanidmModuleError,
    KanidmRequiredOptionError,
)
from .api import KanidmApi
from .attrs import ATTR_NAME, ATTR_UUID, ATTR_ENTRY_MANAGED_BY, ATTR_MEMBER


class KanidmGroup(object):
    def __init__(self, args: KanidmGroupArgs):
        self.args: KanidmGroupArgs = args
        self.api = KanidmApi(args=args.kanidm, debug=args.debug)

    def create_group(self):
        self.api.authenticate()

        if not self.api.check_token():
            raise KanidmAuthenticationFailure(
                "Unable to establish an authenticated connection with the kanidm server"
            )

        if not self.get_group():
            if not self.make_group():
                raise KanidmModuleError(
                    f"Unable to create or get group {self.args.name}. Got {self.api.error}"
                )

        if not self.get_group():
            raise KanidmModuleError(
                f"Unable to get group {self.args.name}. Got {self.api.error}"
            )

        if not self.add_members():
            raise KanidmModuleError(
                f"Unable to add members to group {self.args.name}. Got {self.api.error}"
            )

    def get_group(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        self.api.get(
            name="get_group",
            path=f"/v1/group/{self.args.name}",
        )

        try:
            self.api.text = self.api.json["attrs"][ATTR_UUID]
        except Exception:
            self.api.text = ""
            return False

        return True

    def make_group(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        if self.args.parent is not None:
            return self.api.post(
                name="create_group",
                path="/v1/group",
                json={
                    "attrs": {
                        ATTR_NAME: [self.args.name],
                        ATTR_ENTRY_MANAGED_BY: [self.args.parent],
                    }
                },
            )
        else:
            return self.api.post(
                name="create_group",
                path="/v1/group",
                json={
                    "attrs": {
                        ATTR_NAME: [self.args.name],
                    }
                },
            )

    def add_members(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.users is None:
            raise KanidmRequiredOptionError("No users specified")

        return self.api.post(
            name="add_members",
            path=f"/v1/group/{self.args.name}/_attr/{ATTR_MEMBER}",
            json=self.args.users,
        )
