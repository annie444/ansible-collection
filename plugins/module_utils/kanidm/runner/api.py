from __future__ import absolute_import, annotations, division, print_function

from ..arg_specs.conf import (
    KanidmConf,
)
from ..exceptions import (
    KanidmAuthenticationFailure,
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
