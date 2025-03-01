from typing import Optional, Dict, List
from requests import Response
from .arg_specs import (
    KanidmOauthArgs,
    PrefUsername,
)
from .exceptions import (
    KanidmAuthenticationFailure,
    KanidmException,
    KanidmRequiredOptionError,
    KanidmArgsException,
)
from requests.sessions import Session
from requests.auth import AuthBase
from requests_toolbelt.multipart.encoder import MultipartEncoder


class BearerAuth(AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = "Bearer " + self.token
        return r


class Kanidm(object):
    def __init__(self, args: KanidmOauthArgs):
        self.args: KanidmOauthArgs = args
        self.session = Session()
        self.response: Response | None = None
        self.json: Dict | None = None
        self.token: str | None = None
        self.text: str | None = None
        self.session.verify = self.args.kanidm.verify_ca
        if self.args.kanidm.ca_path is not None:
            if self.args.kanidm.ca_path.is_file():
                self.session.verify = str(
                    self.args.kanidm.ca_path.expanduser().absolute().parent
                )
            else:
                self.session.verify = str(
                    self.args.kanidm.ca_path.expanduser().absolute()
                )

    def set_headers(self):
        self.session.headers["User-Agent"] = "Ansible-Kanidm"
        self.session.headers["Content-Type"] = "application/json"
        self.session.headers["Cache-Control"] = "no-cache"
        self.session.headers["Accept"] = "*/*"
        self.session.headers["Accept-Encoding"] = "gzip, deflate, br"
        self.session.headers["Connection"] = "keep-alive"

    @property
    def error(self) -> str:
        return (
            f"{self.response.status_code} {self.response.reason} {self.response.text}"
        )

    def create_oauth_client(self):
        self.authenticate()
        if not self.check_token():
            raise KanidmAuthenticationFailure(
                "Unable to establish an authenticated connection with the kanidm server"
            )

        if not self.get_client():
            if not self.args.public:
                if not self.create_basic_client():
                    raise KanidmException(
                        f"Unable to create or get client {self.args.name}. Got {self.error}"
                    )
            else:
                if not self.create_public_client():
                    raise KanidmException(
                        f"Unable to create or get public client {self.args.name}. Got {self.error}"
                    )

        if not self.get_client():
            raise KanidmException(
                f"Unable to get client {self.args.name}. Got {self.error}"
            )

        if not self.add_redirect_urls():
            raise KanidmException(
                f"Unable to add redirect URLs for client {self.args.name}. Got {self.error}"
            )

        if not self.update_scope_map():
            raise KanidmException(
                f"Unable to update scope map for client {self.args.name}. Got {self.error}"
            )

        if not self.set_pkce():
            raise KanidmException(
                f"Unable to set PKCE for client {self.args.name}. Got {self.error}"
            )

        if not self.set_legacy_crypto():
            raise KanidmException(
                f"Unable to set legacy crypto for client {self.args.name}. Got {self.error}"
            )

        if not self.set_preferred_username():
            raise KanidmException(
                f"Unable to set preferred username for client {self.args.name}. Got {self.error}"
            )

        if not self.set_localhost_redirect():
            raise KanidmException(
                f"Unable to set localhost redirect policy for client {self.args.name}. Got {self.error}"
            )

        if not self.set_strict_redirect():
            raise KanidmException(
                f"Unable to set strict redirect for client {self.args.name}. Got {self.error}"
            )

        if self.args.image is not None:
            if not self.add_image():
                raise KanidmException(
                    f"Unable to add image for client {self.args.name}. Got {self.error}"
                )

        if self.args.sup_scopes is not None:
            if not self.update_sup_scope_map():
                raise KanidmException(
                    f"Unable to update supplemental scope map for client {self.args.name}. Got {self.error}"
                )

        if self.args.custom_claims is not None:
            if not self.update_custom_claim_map():
                raise KanidmException(
                    f"Unable to update custom claim map for client {self.args.name}. Got {self.error}"
                )

            if not self.update_custom_claim_join():
                raise KanidmException(
                    f"Unable to update custom claim join for client {self.args.name}. Got {self.error}"
                )

        if not self.get_client_secret():
            raise KanidmException(
                f"Unable to get client secret for client {self.args.name}. Got {self.error}"
            )

        if self.text is None:
            raise KanidmException(
                f"Unable to parse the client secret for client {self.args.name}. Got {self.text}"
            )

        return self.text

    def verify_response(self) -> bool:
        if self.response.status_code < 200 and self.response.status_code >= 300:
            return False

        self.json = self.response.json()
        self.text = self.response.text
        return True

    def authenticate(self):
        if self.args.kanidm.token is None and (
            self.args.kanidm.username is None or self.args.kanidm.password is None
        ):
            raise KanidmRequiredOptionError("No authentication method specified")
        if self.args.kanidm.token is not None and self.check_token():
            return
        elif (
            self.args.kanidm.username is not None
            and self.args.kanidm.password is not None
        ) and self.login():
            return
        else:
            raise KanidmAuthenticationFailure(
                f"Authentication failed: {self.response.status_code} {self.response.reason} {self.response.text}"
            )

    def check_token(self) -> bool:
        if (
            self.args.kanidm.token is None
            and not isinstance(self.session.auth, BearerAuth)
            and (
                isinstance(self.session.auth, BearerAuth)
                and self.session.auth.token is None
            )
        ):
            raise KanidmArgsException("No token specified")
        if self.args.kanidm.token is not None and (
            not isinstance(self.session.auth, BearerAuth)
            or self.session.auth.token is None
        ):
            self.session.auth = BearerAuth(self.args.kanidm.token)
        self.set_headers()
        self.session.cookies.clear_expired_cookies()
        self.response = self.session.get(f"{self.args.kanidm.uri}/v1/auth/valid")
        if self.response.status_code == 200:
            return True
        return False

    def login(self) -> bool:
        if self.args.kanidm.username is None or self.args.kanidm.password is None:
            raise KanidmArgsException("No username or password specified")
        self.set_headers()
        self.session.cookies.clear_expired_cookies()

        self.response = self.session.post(
            f"{self.args.kanidm.uri}/v1/auth",
            json={
                "step": {
                    "init2": {
                        "username": self.args.kanidm.username,
                        "issue": "token",
                        "privileged": True,
                    }
                }
            },
        )

        if not self.verify_response():
            return False

        assert self.json is not None

        if "state" not in self.json:
            return False
        if "choose" not in self.json["state"]:
            return False
        if "password" not in self.json["state"]["choose"]:
            return False

        self.response = self.session.post(
            f"{self.args.kanidm.uri}/v1/auth",
            json={
                "step": {
                    "begin": "password",
                }
            },
        )

        if not self.verify_response():
            return False

        assert self.json is not None

        if "state" not in self.json:
            return False
        if "continue" not in self.json["state"]:
            return False
        if "password" not in self.json["state"]["continue"]:
            return False

        self.response = self.session.post(
            f"{self.args.kanidm.uri}/v1/auth",
            json={
                "step": {
                    "cred": {
                        "password": self.args.kanidm.password,
                    }
                }
            },
        )

        if not self.verify_response():
            return False

        assert self.json is not None

        if "state" not in self.json:
            return False
        if "success" not in self.json["state"]:
            return False

        self.session.auth = BearerAuth(self.json["state"]["success"])
        return True

    def create_basic_client(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.url is None:
            raise KanidmRequiredOptionError("No url specified")

        self.set_headers()
        self.response = self.session.post(
            f"{self.args.kanidm.uri}/v1/oauth2/_basic",
            json={
                "attrs": {
                    "name": [self.args.name],
                    "displayname": [self.args.display_name],
                    "oauth2_rs_origin_landing": [self.args.url],
                    "oauth2_strict_redirect_uri": [
                        str(self.args.strict_redirect).lower()
                    ],
                }
            },
        )

        return self.verify_response()

    def get_client(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        self.set_headers()
        self.response = self.session.get(
            f"{self.args.kanidm.uri}/v1/oauth2/{self.args.name}",
        )

        return self.verify_response()

    def create_public_client(self) -> bool:
        if not self.args.public:
            raise KanidmArgsException(
                "Unable to create a public client when public is not specified"
            )
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.url is None:
            raise KanidmRequiredOptionError("No url specified")

        self.set_headers()
        self.response = self.session.post(
            f"{self.args.kanidm.uri}/v1/oauth2/_public",
            json={
                "attrs": {
                    "name": [self.args.name],
                    "displayname": [self.args.display_name],
                    "oauth2_rs_origin_landing": [self.args.url],
                    "oauth2_strict_redirect_uri": [
                        str(self.args.strict_redirect).lower()
                    ],
                }
            },
        )

        return self.verify_response()

    def update_scope_map(self) -> bool:
        if not self.args.group:
            raise KanidmRequiredOptionError("No group specified")
        if not self.args.name:
            raise KanidmRequiredOptionError("No name specified")
        if not self.args.scopes:
            raise KanidmRequiredOptionError("No scopes specified")

        self.set_headers()
        self.response = self.session.post(
            f"{self.args.kanidm.uri}/v1/oauth2/{self.args.name}/_scopemap/{self.args.group}",
            json=self.args.scopes,
        )

        return self.verify_response()

    def update_sup_scope_map(self, index: Optional[int] = None) -> bool:
        if not self.args.sup_scopes:
            raise KanidmRequiredOptionError("No supplemental scopes specified")
        if not self.args.name:
            raise KanidmRequiredOptionError("No name specified")

        if index is not None:
            self.set_headers()
            self.response = self.session.post(
                f"{self.args.kanidm.uri}/v1/oauth2/{self.args.name}/_sup_scopemap/{self.args.sup_scopes[index].group}",
                json=self.args.sup_scopes[index].scopes,
            )

        else:
            for sup_scope in self.args.sup_scopes:
                self.set_headers()
                self.response = self.session.post(
                    f"{self.args.kanidm.uri}/v1/oauth2/{self.args.name}/_sup_scopemap/{sup_scope.group}",
                    json=sup_scope.scopes,
                )
                if not self.verify_response():
                    return False

        return self.verify_response()

    def add_image(self) -> bool:
        if self.args.image is None:
            raise KanidmRequiredOptionError("No image specified")
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        self.args.image.get()
        self.session.headers["User-Agent"] = "Ansible-Kanidm"
        self.session.headers["Cache-Control"] = "no-cache"
        self.session.headers["Accept"] = "*/*"
        self.session.headers["Accept-Encoding"] = "gzip, deflate, br"
        self.session.headers["Connection"] = "keep-alive"

        with open(self.args.image.src, "rb") as f:
            contents = f.read()

        m = MultipartEncoder(
            {
                "image": (
                    f"{self.args.name}.{self.args.image.format.value}",
                    contents,
                    self.args.image.format.mime(),
                )
            }
        )

        self.session.headers["Content-Type"] = m.content_type

        self.response = self.session.post(
            f"{self.args.kanidm.uri}/v1/oauth2/{self.args.name}/_image",
            data=m,
        )

        if self.response.status_code < 200 or self.response.status_code >= 300:
            return False
        return True

    def patch_oauth(self, attrs: Dict[str, List[str]]) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        self.set_headers()
        self.response = self.session.patch(
            f"{self.args.kanidm.uri}/v1/oauth2/{self.args.name}",
            json={
                "attrs": attrs,
            },
        )

        return self.verify_response()

    def set_pkce(self) -> bool:
        if self.args.pkce is None:
            raise KanidmRequiredOptionError("No PKCE specified")

        return self.patch_oauth(
            {
                "oauth2_allow_insecure_client_disable_pkce": [
                    str(self.args.pkce).lower()
                ],
            }
        )

    def set_legacy_crypto(self) -> bool:
        if self.args.legacy_crypto is None:
            raise KanidmRequiredOptionError("No legacy crypto specified")

        return self.patch_oauth(
            {
                "oauth2_jwt_legacy_crypto_enable": [
                    str(self.args.legacy_crypto).lower()
                ],
            }
        )

    def set_preferred_username(self) -> bool:
        if self.args.username is None:
            raise KanidmRequiredOptionError("No username specified")

        return self.patch_oauth(
            {
                "oauth2_prefer_short_username": [
                    str(self.args.username == PrefUsername.short).lower()
                ],
            }
        )

    def set_localhost_redirect(self) -> bool:
        if self.args.local_redirect is None:
            raise KanidmRequiredOptionError("No localhost redirect specified")

        return self.patch_oauth(
            {"oauth2_allow_localhost_redirect": [str(self.args.local_redirect).lower()]}
        )

    def set_strict_redirect(self) -> bool:
        if self.args.strict_redirect is None:
            raise KanidmRequiredOptionError("No strict redirect specified")

        return self.patch_oauth(
            {
                "oauth2_strict_redirect_uri": [str(self.args.strict_redirect).lower()],
            }
        )

    def update_custom_claim_map(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.custom_claims is None:
            raise KanidmRequiredOptionError("No claims specified")
        if self.args.group is None:
            raise KanidmRequiredOptionError("No group specified")

        for c in self.args.custom_claims:
            self.set_headers()
            self.response = self.session.post(
                f"{self.args.kanidm.uri}/v1/oauth2/_claimmap/{self.args.name}/{self.args.group}",
                json=c.values,
            )
            if not self.verify_response():
                return False
        return True

    def update_custom_claim_join(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.claim_join is None:
            raise KanidmRequiredOptionError("No claim join specified")
        if self.args.custom_claims is None:
            raise KanidmRequiredOptionError("No claims specified")

        for c in self.args.custom_claims:
            self.set_headers()
            self.response = self.session.post(
                f"{self.args.kanidm.uri}/v1/oauth2/{self.args.name}/_claimmap/{self.args.claim_join}",
                json=c.values,
            )
            if not self.verify_response():
                return False

        return True

    def add_redirect_urls(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.redirect_url is None:
            raise KanidmRequiredOptionError("No redirect URL specified")

        for url in self.args.redirect_url:
            self.set_headers()
            self.response = self.session.post(
                f"{self.args.kanidm.uri}/v1/oauth2/{self.args.name}/_attr/oauth2_rs_origin",
                json=[url],
            )
            if not self.verify_response():
                return False
        return True

    def get_client_secret(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        self.set_headers()
        self.response = self.session.get(
            f"{self.args.kanidm.uri}/v1/oauth2/{self.args.name}/_basic_secret",
        )

        return self.verify_response()
