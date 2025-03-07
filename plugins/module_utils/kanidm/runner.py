from __future__ import absolute_import, annotations, division, print_function

from .arg_specs import (
    KanidmOauthArgs,
    KanidmGroupArgs,
    KanidmConf,
    PrefUsername,
)
from .exceptions import (
    KanidmAuthenticationFailure,
    KanidmModuleError,
    KanidmRequiredOptionError,
    KanidmArgsException,
)
import json
import traceback
from ansible.module_utils.compat.typing import (
    Callable,
    Optional,
    Dict,
    Any,
    Set,
    List,
    Tuple,
    TypedDict,
    Iterable,
)
import time


REQUESTS_IMP_ERR = None
try:
    from requests.sessions import Session
    from requests.auth import AuthBase
    from requests import Response, PreparedRequest, Request

    HAS_REQUESTS = True
except ImportError:
    REQUESTS_IMP_ERR = traceback.format_exc()
    HAS_REQUESTS = False
    AuthBase = object

REQUESTS_TOOLS_IMP_ERR = None
try:
    from requests_toolbelt.multipart.encoder import MultipartEncoder, FileWrapper

    HAS_REQUESTS_TOOLS = True
except ImportError:
    REQUESTS_TOOLS_IMP_ERR = traceback.format_exc()
    HAS_REQUESTS_TOOLS = False


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


def basic_from_prep_req(req: PreparedRequest) -> str:
    if req.method is not None:
        method = req.method
    else:
        method = ""

    if req.url is not None:
        url = req.url
    else:
        url = ""

    if req.body is not None:
        try:
            body = json.loads(req.body)
            return f"{method} {url} {body}"
        except Exception:
            return f"{method} {url}"

    return f"{method} {url}"


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


def basic_from_resp(res: Response) -> str:
    return f"{res.status_code} {res.reason} {res.text}"


process_request = {
    True: from_prep_req,
    False: basic_from_prep_req,
}

process_response = {
    True: from_resp,
    False: basic_from_resp,
}


class KanidmApi(object):
    def __init__(self, args: KanidmConf, debug: bool = False):
        self.args: KanidmConf = args
        self.session: Session = Session()
        self.response: Response | None = None
        self.json: Dict = {}
        self.token: str | None = None
        self.text: str = ""
        self.process_request: Callable[[PreparedRequest], str | RequestDict] = (
            process_request[debug]
        )
        self.process_response: Callable[[Response], str | ResponseDict] = (
            process_response[debug]
        )
        self.requests: Dict[str, RequestDict | str] = {}
        self.responses: Dict[str, ResponseDict | str] = {}
        self.session.verify = self.args.verify_ca
        if self.args.ca_path is not None:
            if self.args.ca_path.is_file():
                self.session.verify = str(
                    self.args.ca_path.expanduser().absolute().parent
                )
            else:
                self.session.verify = str(self.args.ca_path.expanduser().absolute())

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
        req = self.session.prepare_request(Request("GET", f"{self.args.uri}{path}"))
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
        pre_req = Request("POST", f"{self.args.uri}{path}")
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
        pre_req = Request("PATCH", f"{self.args.uri}{path}")
        if json is not None:
            pre_req.json = json
        if data is not None:
            pre_req.data = data
        req = self.session.prepare_request(pre_req)
        self.send(name, req)
        return self.verify_response()

    def send(self, name: str, req: PreparedRequest):
        self.requests[name] = self.process_request(req)
        self.response = self.session.send(req)
        self.responses[name] = self.process_response(self.response)

    def authenticate(self):
        if self.args.token is None and (
            self.args.username is None or self.args.password is None
        ):
            raise KanidmRequiredOptionError("No authentication method specified")
        if self.args.token is not None and self.check_token():
            return
        elif (
            self.args.username is not None and self.args.password is not None
        ) and self.login():
            return
        else:
            raise KanidmAuthenticationFailure(
                f"Authentication failed: {self.response.status_code} {self.response.reason} {self.response.text}"
            )

    def check_token(self) -> bool:
        if (
            self.args.token is None
            and not isinstance(self.session.auth, BearerAuth)
            and (
                isinstance(self.session.auth, BearerAuth)
                and self.session.auth.token is None
            )
        ):
            raise KanidmArgsException("No token specified")
        if self.args.token is not None and (
            not isinstance(self.session.auth, BearerAuth)
            or self.session.auth.token is None
        ):
            self.session.auth = BearerAuth(self.args.token)

        return self.get(name="check_token", path="/v1/auth/valid")

    def login(self) -> bool:
        if self.args.username is None or self.args.password is None:
            raise KanidmArgsException("No username or password specified")

        if not self.post(
            name="login_init",
            path="/v1/auth",
            json={
                "step": {
                    "init2": {
                        "username": self.args.username,
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
                        "password": self.args.password,
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

    def patch_oauth(
        self, name: str, oauth_name: str, attrs: Dict[str, List[str]]
    ) -> bool:
        return self.patch(
            name=name,
            path=f"/v1/oauth2/{oauth_name}",
            json={
                "attrs": attrs,
            },
        )


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
            time.sleep(1)
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
            self.api.text = self.api.json["attrs"]["uuid"]
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
                        "name": [self.args.name],
                        "entry_managed_by": [self.args.parent],
                    }
                },
            )
        else:
            return self.api.post(
                name="create_group",
                path="/v1/group",
                json={
                    "attrs": {
                        "name": [self.args.name],
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
            path=f"/v1/group/{self.args.name}/_attr/member",
            json=self.args.users,
        )


class KanidmOAuth(object):
    def __init__(self, args: KanidmOauthArgs):
        self.args: KanidmOauthArgs = args
        self.api = KanidmApi(args=args.kanidm, debug=args.debug)

    def create_oauth_client(self) -> str:
        self.api.authenticate()

        if not self.api.check_token():
            raise KanidmAuthenticationFailure(
                "Unable to establish an authenticated connection with the kanidm server"
            )

        if not self.get_client():
            if not self.args.public:
                if not self.create_basic_client():
                    raise KanidmModuleError(
                        f"Unable to create or get client {self.args.name}. Got {self.api.error}"
                    )
            else:
                if not self.create_public_client():
                    raise KanidmModuleError(
                        f"Unable to create or get public client {self.args.name}. Got {self.api.error}"
                    )

        if not self.get_client():
            raise KanidmModuleError(
                f"Unable to get client {self.args.name}. Got {self.api.error}"
            )

        if not self.args.public:
            if not self.set_pkce():
                raise KanidmModuleError(
                    f"Unable to set PKCE for client {self.args.name}. Got {self.api.error}"
                )

            if not self.set_legacy_crypto():
                raise KanidmModuleError(
                    f"Unable to set legacy crypto for client {self.args.name}. Got {self.api.error}"
                )
        else:
            if not self.set_localhost_redirect():
                raise KanidmModuleError(
                    f"Unable to set localhost redirect policy for client {self.args.name}. Got {self.api.error}"
                )

        if not self.add_redirect_urls():
            raise KanidmModuleError(
                f"Unable to add redirect URLs for client {self.args.name}. Got {self.api.error}"
            )

        if not self.update_scope_map():
            raise KanidmModuleError(
                f"Unable to update scope map for client {self.args.name}. Got {self.api.error}"
            )

        if not self.set_preferred_username():
            raise KanidmModuleError(
                f"Unable to set preferred username for client {self.args.name}. Got {self.api.error}"
            )

        if not self.set_strict_redirect():
            raise KanidmModuleError(
                f"Unable to set strict redirect for client {self.args.name}. Got {self.api.error}"
            )

        if self.args.image is not None:
            if not self.add_image():
                raise KanidmModuleError(
                    f"Unable to add image for client {self.args.name}. Got {self.api.error}"
                )

        if self.args.sup_scopes is not None:
            if not self.update_sup_scope_map():
                raise KanidmModuleError(
                    f"Unable to update supplemental scope map for client {self.args.name}. Got {self.api.error}"
                )

        if self.args.custom_claims is not None:
            if not self.update_custom_claim_map():
                raise KanidmModuleError(
                    f"Unable to update custom claim map for client {self.args.name}. Got {self.api.error}"
                )

            if not self.update_custom_claim_join():
                raise KanidmModuleError(
                    f"Unable to update custom claim join for client {self.args.name}. Got {self.api.error}"
                )

        if not self.get_client_secret():
            raise KanidmModuleError(
                f"Unable to get client secret for client {self.args.name}. Got {self.api.error}"
            )

        if self.api.text is None:
            raise KanidmModuleError(
                f"Unable to parse the client secret for client {self.args.name}. Got {self.api.text}"
            )

        return self.api.text

    def get_client(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        if not self.api.get(
            name="get_client",
            path=f"/v1/oauth2/{self.args.name}",
        ):
            return False

        try:
            self.api.text = self.api.json["attrs"]["uuid"][0]
        except Exception:
            self.api.text = ""
            return False

        return True

    def create_basic_client(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.url is None:
            raise KanidmRequiredOptionError("No url specified")

        return self.api.post(
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

    def create_public_client(self) -> bool:
        if not self.args.public:
            raise KanidmArgsException(
                "Unable to create a public client when public is not specified"
            )
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.url is None:
            raise KanidmRequiredOptionError("No url specified")

        return self.api.post(
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

        return self.api.post(
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
            return self.api.post(
                name=f"update_sup_scope_map[{index}]",
                path=f"/v1/oauth2/{self.args.name}/_sup_scopemap/{self.args.sup_scopes[index].group}",
                json=self.args.sup_scopes[index].scopes,
            )

        else:
            for i, sup_scope in enumerate(self.args.sup_scopes):
                if not self.api.post(
                    name=f"update_sup_scope_map[{i}]",
                    path=f"/v1/oauth2/{self.args.name}/_sup_scopemap/{sup_scope.group}",
                    json=sup_scope.scopes,
                ):
                    return False

        return self.api.verify_response()

    def add_image(self) -> bool:
        if self.args.image is None:
            raise KanidmRequiredOptionError("No image specified")
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        self.args.image.get()

        m = MultipartEncoder(
            {
                "image": (
                    f"{self.args.name}.{self.args.image.format.value}",
                    FileWrapper(open(self.args.image.src, "rb")),
                    self.args.image.format.mime(),
                )
            }
        )

        if not self.api.post(
            name="add_image",
            path=f"/v1/oauth2/{self.args.name}/_image",
            data=m,
            content_type=m.content_type,
        ):
            return False

        return True

    def set_pkce(self) -> bool:
        if self.args.pkce is None:
            raise KanidmRequiredOptionError("No PKCE specified")

        return self.api.patch_oauth(
            name="set_pkce",
            oauth_name=self.args.name,
            attrs={
                "oauth2_allow_insecure_client_disable_pkce": [
                    str(self.args.pkce).lower()
                ],
            },
        )

    def set_legacy_crypto(self) -> bool:
        if self.args.legacy_crypto is None:
            raise KanidmRequiredOptionError("No legacy crypto specified")

        return self.api.patch_oauth(
            name="set_legacy_crypto",
            oauth_name=self.args.name,
            attrs={
                "oauth2_jwt_legacy_crypto_enable": [
                    str(self.args.legacy_crypto).lower()
                ],
            },
        )

    def set_preferred_username(self) -> bool:
        if self.args.username is None:
            raise KanidmRequiredOptionError("No username specified")

        return self.api.patch_oauth(
            name="set_preferred_username",
            oauth_name=self.args.name,
            attrs={
                "oauth2_prefer_short_username": [
                    str(self.args.username == PrefUsername.short).lower()
                ],
            },
        )

    def set_localhost_redirect(self) -> bool:
        if self.args.local_redirect is None:
            raise KanidmRequiredOptionError("No localhost redirect specified")

        return self.api.patch_oauth(
            name="set_localhost_redirect",
            oauth_name=self.args.name,
            attrs={
                "oauth2_allow_localhost_redirect": [
                    str(self.args.local_redirect).lower()
                ]
            },
        )

    def set_strict_redirect(self) -> bool:
        if self.args.strict_redirect is None:
            raise KanidmRequiredOptionError("No strict redirect specified")

        return self.api.patch_oauth(
            name="set_strict_redirect",
            oauth_name=self.args.name,
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
            if not self.api.post(
                name=f"update_custom_claim_map[{i}]",
                path=f"/v1/oauth2/{self.args.name}/_claimmap/{self.args.name}/{self.args.group}",
                json=[str(v) for v in c.values],
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
            if not self.api.post(
                name=f"update_custom_claim_join[{i}]",
                path=f"/v1/oauth2/{self.args.name}/_claimmap/{self.args.claim_join}",
                json=self.args.claim_join,
            ):
                return False

        return True

    def add_redirect_urls(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.redirect_url is None:
            raise KanidmRequiredOptionError("No redirect URL specified")

        for url in self.args.redirect_url:
            if not self.api.patch_oauth(
                name=f"add_redirect_url[{url}]",
                oauth_name=self.args.name,
                attrs={"oauth2_rs_origin": [url]},
            ):
                return False
        return True

    def get_client_secret(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        return self.api.get(
            name="get_client_secret",
            path=f"/v1/oauth2/{self.args.name}/_basic_secret",
        )
