from typing import Iterable, Optional, Dict, List, TypedDict, Any, Set, Tuple
from requests import Response, PreparedRequest, Request
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
from requests_toolbelt.multipart.encoder import MultipartEncoder, FileWrapper
import json


class BearerAuth(AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = "Bearer " + self.token
        return r


class RequestDict(TypedDict):
    body: Any
    headers: Dict[str, str]
    method: str
    url: str


def from_prep_req(req: PreparedRequest) -> RequestDict:
    if req.body is not None:
        try:
            body = json.loads(req.body)
        except Exception:
            body = str(req.body)
    else:
        body = ""

    if req.method is not None:
        method = req.method
    else:
        method = ""

    if req.url is not None:
        url = req.url
    else:
        url = ""

    headers = {}
    for k, v in req.headers.items():
        headers[k] = v

    return json.loads(
        json.dumps(
            {
                "body": body,
                "headers": headers,
                "method": method,
                "url": url,
            }
        )
    )


class ResponseDict(TypedDict):
    cookies: Dict[str, str]
    elapsed: str
    encoding: str
    headers: Dict[str, str]
    redirect: bool
    json: Dict | List | Set | Tuple
    reason: str
    status_code: int
    text: str
    url: str


def from_resp(res: Response) -> ResponseDict:
    try:
        js = res.json()
    except Exception:
        js = {}

    try:
        cookies = res.cookies.get_dict()
    except Exception:
        cookies = {}

    if res.text is not None:
        try:
            text = json.loads(res.text)
        except Exception:
            text = str(res.text)
    else:
        text = ""

    elapsed = str(res.elapsed)

    headers = {}
    for k, v in res.headers.items():
        headers[k] = v

    return json.loads(
        json.dumps(
            {
                "cookies": cookies,
                "elapsed": elapsed,
                "encoding": res.encoding
                if res.encoding is not None
                else res.apparent_encoding,
                "headers": headers,
                "redirect": res.is_redirect,
                "json": js,
                "reason": res.reason,
                "status_code": res.status_code,
                "text": text,
                "url": res.url,
            }
        )
    )


class Kanidm(object):
    def __init__(self, args: KanidmOauthArgs):
        self.args: KanidmOauthArgs = args
        self.session = Session()
        self.response: Response | None = None
        self.json: Dict = {}
        self.token: str | None = None
        self.text: str = ""
        self.requests: Dict[str, RequestDict] = {}
        self.responses: Dict[str, ResponseDict] = {}
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

    def set_headers(self, content_type: str = "application/json"):
        self.session.headers["User-Agent"] = "Ansible-Kanidm"
        self.session.headers["Content-Type"] = content_type
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
                if not self.set_localhost_redirect():
                    raise KanidmException(
                        f"Unable to set localhost redirect policy for client {self.args.name}. Got {self.error}"
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
        if self.response.status_code < 200 or self.response.status_code >= 300:
            return False

        try:
            self.json = self.response.json()
        except Exception:
            self.json = {}
        self.text = self.response.text
        if "nomatchingentries" in self.text:
            return False
        return True

    def get(self, name: str, path: str) -> bool:
        self.set_headers()
        req = self.session.prepare_request(
            Request("GET", f"{self.args.kanidm.uri}{path}")
        )
        self.send(name, req)
        return self.verify_response()

    def post(
        self,
        name: str,
        path: str,
        json: Optional[Iterable] = None,
        data: Optional[Any] = None,
        content_type: str = "application/json",
    ) -> bool:
        self.set_headers(content_type=content_type)
        pre_req = Request("POST", f"{self.args.kanidm.uri}{path}")
        if json is not None:
            pre_req.json = json
        if data is not None:
            pre_req.data = data
        req = self.session.prepare_request(pre_req)
        self.send(name, req)
        return self.verify_response()

    def patch(
        self,
        name: str,
        path: str,
        json: Optional[Iterable] = None,
        data: Optional[Any] = None,
    ) -> bool:
        self.set_headers()
        pre_req = Request("PATCH", f"{self.args.kanidm.uri}{path}")
        if json is not None:
            pre_req.json = json
        if data is not None:
            pre_req.data = data
        req = self.session.prepare_request(pre_req)
        self.send(name, req)
        return self.verify_response()

    def send(self, name: str, req: PreparedRequest):
        self.requests[name] = from_prep_req(req)
        self.response = self.session.send(req)
        self.responses[name] = from_resp(self.response)

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

        return self.get(name="check_token", path="/v1/auth/valid")

    def login(self) -> bool:
        if self.args.kanidm.username is None or self.args.kanidm.password is None:
            raise KanidmArgsException("No username or password specified")

        if not self.post(
            name="login_init",
            path="/v1/auth",
            json={
                "step": {
                    "init2": {
                        "username": self.args.kanidm.username,
                        "issue": "token",
                        "privileged": True,
                    }
                }
            },
        ):
            return False

        if "state" not in self.json:
            return False
        if "choose" not in self.json["state"]:
            return False
        if "password" not in self.json["state"]["choose"]:
            return False

        if not self.post(
            name="login_begin",
            path="/v1/auth",
            json={
                "step": {
                    "begin": "password",
                }
            },
        ):
            return False

        if "state" not in self.json:
            return False
        if "continue" not in self.json["state"]:
            return False
        if "password" not in self.json["state"]["continue"]:
            return False

        if not self.post(
            name="login_send",
            path="/v1/auth",
            json={
                "step": {
                    "cred": {
                        "password": self.args.kanidm.password,
                    }
                }
            },
        ):
            return False

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

        return self.post(
            name="create_basic_client",
            path="/v1/oauth2/_basic",
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

    def get_client(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        if not self.get(
            name="get_client",
            path=f"/v1/oauth2/{self.args.name}",
        ):
            return False

        try:
            self.text = self.json["attrs"]["uuid"][0]
        except Exception:
            self.text = ""
            return False

        return True

    def create_public_client(self) -> bool:
        if not self.args.public:
            raise KanidmArgsException(
                "Unable to create a public client when public is not specified"
            )
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.url is None:
            raise KanidmRequiredOptionError("No url specified")

        return self.post(
            name="create_public_client",
            path="/v1/oauth2/_public",
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

    def update_scope_map(self) -> bool:
        if not self.args.group:
            raise KanidmRequiredOptionError("No group specified")
        if not self.args.name:
            raise KanidmRequiredOptionError("No name specified")
        if not self.args.scopes:
            raise KanidmRequiredOptionError("No scopes specified")

        return self.post(
            name="update_scope_map",
            path=f"/v1/oauth2/{self.args.name}/_scopemap/{self.args.group}",
            json=self.args.scopes,
        )

    def update_sup_scope_map(self, index: Optional[int] = None) -> bool:
        if not self.args.sup_scopes:
            raise KanidmRequiredOptionError("No supplemental scopes specified")
        if not self.args.name:
            raise KanidmRequiredOptionError("No name specified")

        if index is not None:
            return self.post(
                name=f"update_sup_scope_map[{index}]",
                path=f"/v1/oauth2/{self.args.name}/_sup_scopemap/{self.args.sup_scopes[index].group}",
                json=self.args.sup_scopes[index].scopes,
            )

        else:
            for i, sup_scope in enumerate(self.args.sup_scopes):
                if not self.post(
                    name=f"update_sup_scope_map[{i}]",
                    path=f"/v1/oauth2/{self.args.name}/_sup_scopemap/{sup_scope.group}",
                    json=sup_scope.scopes,
                ):
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

        m = MultipartEncoder(
            {
                "image": (
                    f"{self.args.name}.{self.args.image.format.value}",
                    FileWrapper(open(self.args.image.src, "rb")),
                    self.args.image.format.mime(),
                )
            }
        )

        self.session.headers["Content-Type"] = m.content_type

        if not self.post(
            name="add_image",
            path=f"/v1/oauth2/{self.args.name}/_image",
            data=m,
            content_type=m.content_type,
        ):
            return False

        return True

    def patch_oauth(self, name: str, attrs: Dict[str, List[str]]) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        return self.patch(
            name=name,
            path=f"/v1/oauth2/{self.args.name}",
            json={
                "attrs": attrs,
            },
        )

    def set_pkce(self) -> bool:
        if self.args.pkce is None:
            raise KanidmRequiredOptionError("No PKCE specified")

        return self.patch_oauth(
            name="set_pkce",
            attrs={
                "oauth2_allow_insecure_client_disable_pkce": [
                    str(self.args.pkce).lower()
                ],
            },
        )

    def set_legacy_crypto(self) -> bool:
        if self.args.legacy_crypto is None:
            raise KanidmRequiredOptionError("No legacy crypto specified")

        return self.patch_oauth(
            name="set_legacy_crypto",
            attrs={
                "oauth2_jwt_legacy_crypto_enable": [
                    str(self.args.legacy_crypto).lower()
                ],
            },
        )

    def set_preferred_username(self) -> bool:
        if self.args.username is None:
            raise KanidmRequiredOptionError("No username specified")

        return self.patch_oauth(
            name="set_preferred_username",
            attrs={
                "oauth2_prefer_short_username": [
                    str(self.args.username == PrefUsername.short).lower()
                ],
            },
        )

    def set_localhost_redirect(self) -> bool:
        if self.args.local_redirect is None:
            raise KanidmRequiredOptionError("No localhost redirect specified")

        return self.patch_oauth(
            name="set_localhost_redirect",
            attrs={
                "oauth2_allow_localhost_redirect": [
                    str(self.args.local_redirect).lower()
                ]
            },
        )

    def set_strict_redirect(self) -> bool:
        if self.args.strict_redirect is None:
            raise KanidmRequiredOptionError("No strict redirect specified")

        return self.patch_oauth(
            name="set_strict_redirect",
            attrs={
                "oauth2_strict_redirect_uri": [str(self.args.strict_redirect).lower()],
            },
        )

    def update_custom_claim_map(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.custom_claims is None:
            raise KanidmRequiredOptionError("No claims specified")
        if self.args.group is None:
            raise KanidmRequiredOptionError("No group specified")

        for i, c in enumerate(self.args.custom_claims):
            if not self.post(
                name=f"update_custom_claim_map[{i}]",
                path=f"/v1/oauth2/_claimmap/{self.args.name}/{self.args.group}",
                json=c.values,
            ):
                return False
        return True

    def update_custom_claim_join(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.claim_join is None:
            raise KanidmRequiredOptionError("No claim join specified")
        if self.args.custom_claims is None:
            raise KanidmRequiredOptionError("No claims specified")

        for i, c in enumerate(self.args.custom_claims):
            if not self.post(
                name=f"update_custom_claim_join[{i}]",
                path=f"/v1/oauth2/{self.args.name}/_claimmap/{self.args.claim_join}",
                json=c.values,
            ):
                return False

        return True

    def add_redirect_urls(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.redirect_url is None:
            raise KanidmRequiredOptionError("No redirect URL specified")

        for url in self.args.redirect_url:
            if not self.patch_oauth(
                name=f"add_redirect_url[{url}]",
                attrs={"oauth2_rs_origin": [url]},
            ):
                return False
        return True

    def get_client_secret(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        return self.get(
            name="get_client_secret",
            path=f"/v1/oauth2/{self.args.name}/_basic_secret",
        )
