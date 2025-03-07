from __future__ import absolute_import, annotations, division, print_function

from ..arg_specs.person import (
    KanidmPersonArgs,
)
from ..exceptions import (
    KanidmAuthenticationFailure,
    KanidmModuleError,
    KanidmRequiredOptionError,
)
from .api import KanidmApi
from .attrs import ATTR_NAME, ATTR_UUID, ATTR_DISPLAYNAME
from urllib.parse import urlencode


class KanidmPerson(object):
    def __init__(self, args: KanidmPersonArgs):
        self.args: KanidmPersonArgs = args
        self.api = KanidmApi(args=args.kanidm, debug=args.debug)

    def create_person(self) -> str:
        self.api.authenticate()

        if not self.api.check_token():
            raise KanidmAuthenticationFailure(
                "Unable to establish an authenticated connection with the kanidm server"
            )

        if not self.get_person():
            if not self.make_person():
                raise KanidmModuleError(
                    f"Unable to create or get person {self.args.name}. Got {self.api.error}"
                )

        if not self.get_person():
            raise KanidmModuleError(
                f"Unable to get person {self.args.name}. Got {self.api.error}"
            )

        if not self.credential_update_url():
            raise KanidmModuleError(
                f"Unable to get credential update URL for person {self.args.name}. Got {self.api.error}"
            )

        return self.api.text

    def get_person(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        self.api.get(
            name="get_person",
            path=f"/v1/person/{self.args.name}",
        )

        try:
            self.api.text = self.api.json["attrs"][ATTR_UUID]
        except Exception:
            self.api.text = ""
            return False

        return True

    def make_person(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        if self.args.display_name is None:
            return self.api.post(
                name="make_person",
                path="/v1/person",
                json={
                    "attrs": {
                        ATTR_NAME: [self.args.name],
                    }
                },
            )
        else:
            return self.api.post(
                name="make_person",
                path="/v1/person",
                json={
                    "attrs": {
                        ATTR_NAME: [self.args.name],
                        ATTR_DISPLAYNAME: [self.args.display_name],
                    }
                },
            )

    def credential_update_url(self):
        if not self.api.get(
            "credential_update_url[update_intent]",
            f"/v1/person/{self.args.name}/_credential/_update_intent/{self.args.ttl}",
        ):
            return False

        self.api.text = f"{self.api.args.uri}/ui/reset?{urlencode({'token': self.api.json['token']})}"
        return True
