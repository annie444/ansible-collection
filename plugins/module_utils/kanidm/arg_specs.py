from dataclasses import dataclass
from typing import FrozenSet, Optional, List
from enum import StrEnum
import yaml
import tempfile
import requests
from pathlib import Path

from ..ansible_specs import (
    AnsibleArgumentSpec,
    OptionType,
)
from ..verify import Verify
from .exceptions import (
    KanidmArgsException,
    KanidmException,
    KanidmModuleError,
    KanidmRequiredOptionError,
)


class Scope(StrEnum):
    openid = "openid"
    profile = "profile"
    email = "email"
    address = "address"
    phone = "phone"
    groups = "groups"
    ssh_publickeys = "ssh_publickeys"


class ImageFormat(StrEnum):
    png = "png"
    jpg = "jpg"
    gif = "gif"
    svg = "svg"
    webp = "webp"
    auto = "auto"

    def get(self) -> str:
        if self == ImageFormat.auto:
            return ""
        return self.value

    def mime(self) -> str:
        if self == ImageFormat.png:
            return "image/png"
        elif self == ImageFormat.jpg:
            return "image/jpeg"
        elif self == ImageFormat.gif:
            return "image/gif"
        elif self == ImageFormat.svg:
            return "image/svg+xml"
        elif self == ImageFormat.webp:
            return "image/webp"
        else:
            raise ValueError(f"Invalid image format: {self.value}")


class ClaimJoin(StrEnum):
    array = "array"
    csv = "csv"
    ssv = "ssv"


class PrefUsername(StrEnum):
    spn = "spn"
    short = "short"


@dataclass
class KanidmConf:
    uri: str
    token: Optional[str] = None
    ca_path: Optional[Path] = None
    username: Optional[str] = None
    password: Optional[str] = None
    ca_cert_data: Optional[str] = None
    verify_ca: bool = True
    connect_timeout: int = 30

    def __init__(self, **kwargs):
        try:
            if "uri" in kwargs:
                self.uri = Verify(kwargs.get("uri"), "uri").verify_str()
            else:
                raise KanidmRequiredOptionError("kanidm uri is required")
            if "token" in kwargs:
                self.token = Verify(kwargs.get("token"), "token").verify_opt_str()
            if "ca_path" in kwargs:
                self.ca_path = Verify(
                    kwargs.get("ca_path"), "ca_path"
                ).verify_opt_path()
            if "username" in kwargs:
                self.username = Verify(
                    kwargs.get("username"), "username"
                ).verify_opt_str()
            if "password" in kwargs:
                self.password = kwargs.get("password")
            if "ca_cert_data" in kwargs:
                self.ca_path = Verify(
                    kwargs.get("ca_cert_data"), "ca_cert_data"
                ).verify_opt_content_as_path()
            if "verify_ca" in kwargs:
                self.verify_ca = Verify(
                    kwargs.get("verify_ca"), "verify_ca"
                ).verify_default_bool(True)
            if "connect_timeout" in kwargs:
                self.connect_timeout = Verify(
                    kwargs.get("connect_timeout"), "connect_timeout"
                ).verify_default_int(30)
        except TypeError as e:
            raise KanidmArgsException(str(e), e)
        except ValueError as e:
            raise KanidmArgsException(str(e), e)
        except AttributeError as e:
            raise KanidmRequiredOptionError(str(e), e)
        except FileNotFoundError as e:
            raise KanidmArgsException(str(e), e)
        except Exception as e:
            raise e

    @staticmethod
    def valid_args() -> FrozenSet[str]:
        return frozenset(
            [
                "uri",
                "token",
                "ca_path",
                "username",
                "password",
                "ca_cert_data",
                "verify_ca",
                "connect_timeout",
            ]
        )

    @staticmethod
    def arg_spec() -> AnsibleArgumentSpec:
        return {
            "uri": {
                "type": OptionType.STR,
                "required": True,
                "aliases": ["kanidm_uri"],
                "documentation": "The URI of the Kanidm server.",
            },
            "token": {
                "type": OptionType.STR,
                "required": False,
                "no_log": True,
                "aliases": ["kanidm_token"],
                "documentation": "The token for authentication.",
            },
            "ca_path": {
                "type": OptionType.PATH,
                "required": False,
                "aliases": ["kanidm_ca_path"],
                "documentation": "The path to the CA certificate.",
            },
            "username": {
                "type": OptionType.STR,
                "required": False,
                "no_log": True,
                "aliases": ["kanidm_username"],
            },
            "password": {
                "type": OptionType.STR,
                "required": False,
                "no_log": True,
                "aliases": ["kanidm_password"],
            },
            "ca_cert_data": {
                "type": OptionType.STR,
                "required": False,
                "no_log": True,
                "documentation": "The CA certificate data as a base64 encoded string.",
            },
            "verify_ca": {
                "type": OptionType.BOOL,
                "required": False,
                "default": True,
                "documentation": "Whether to verify the Kanidm server's certificate chain.",
            },
            "connect_timeout": {
                "type": OptionType.INT,
                "required": False,
                "default": 30,
                "documentation": "The connection timeout in seconds.",
            },
        }

    @staticmethod
    def documentation(indentation: Optional[int] = None) -> str:
        if indentation is not None:
            out: str = yaml.dump(KanidmConf.arg_spec(), sort_keys=False)
            values = []
            for line in out.splitlines():
                values.append(f"{' ' * indentation}{line}")
            return "\n".join(values)
        return yaml.dump(KanidmConf.arg_spec(), sort_keys=False)


@dataclass
class SupScope:
    group: str
    scopes: List[Scope]

    def __init__(self, **kwargs):
        try:
            if "group" in kwargs:
                self.group = Verify(
                    kwargs.get("group"), "sup_scopesp[].group"
                ).verify_str()
            else:
                raise KanidmRequiredOptionError("sup_scopesp[].group not defined")
            if "scopes" in kwargs:
                self.scopes = [
                    Scope(s)
                    for s in Verify(
                        kwargs.get("scopes"), "sup_scopesp[].scopes"
                    ).verify_list_str()
                ]
            else:
                raise KanidmRequiredOptionError("sup_scopesp[].scopes not defined")
        except TypeError as e:
            raise KanidmArgsException(str(e), e)
        except ValueError as e:
            raise KanidmArgsException(str(e), e)
        except AttributeError as e:
            raise KanidmRequiredOptionError(str(e), e)
        except Exception as e:
            raise e

    @staticmethod
    def valid_args() -> FrozenSet[str]:
        return frozenset(["group", "scopes"])

    @staticmethod
    def arg_spec() -> AnsibleArgumentSpec:
        return {
            "group": {
                "type": OptionType.STR,
                "required": True,
                "aliases": ["sup_scope_group"],
                "documentation": "The group to which the additional scopes apply.",
            },
            "scopes": {
                "type": OptionType.LIST,
                "elements": OptionType.STR,
                "choices": [e.value for e in Scope],
                "required": True,
                "documentation": "The additional scopes for the group.",
            },
        }

    @staticmethod
    def documentation(indentation: Optional[int] = None) -> str:
        if indentation is not None:
            out: str = yaml.dump(SupScope.arg_spec(), sort_keys=False)
            values = []
            for line in out.splitlines():
                values.append(f"{' ' * indentation}{line}")
            return "\n".join(values)
        return yaml.dump(SupScope.arg_spec(), sort_keys=False)


@dataclass
class CustomClaim:
    name: str
    group: str
    values: List[str]

    def __init__(self, **kwargs):
        try:
            if "name" in kwargs:
                self.name = Verify(
                    kwargs.get("name"), "custom_claims[].name"
                ).verify_str()
            else:
                raise KanidmRequiredOptionError("custom_claims[].name not defined")
            if "group" in kwargs:
                self.group = Verify(
                    kwargs.get("group"), "custom_claims[].group"
                ).verify_str()
            else:
                raise KanidmRequiredOptionError("custom_claims[].group not defined")
            if "values" in kwargs:
                self.values = Verify(
                    kwargs.get("values"), "custom_claims[].values"
                ).verify_list_str()
            else:
                raise KanidmRequiredOptionError("custom_claims[].values not defined")
        except TypeError as e:
            raise KanidmArgsException(str(e), e)
        except ValueError as e:
            raise KanidmArgsException(str(e), e)
        except AttributeError as e:
            raise KanidmRequiredOptionError(str(e), e)
        except Exception as e:
            raise e

    @staticmethod
    def valid_args() -> FrozenSet[str]:
        return frozenset(["name", "group", "values"])

    @staticmethod
    def arg_spec() -> AnsibleArgumentSpec:
        return {
            "name": {
                "type": OptionType.STR,
                "required": True,
                "aliases": ["claim_name"],
                "documentation": "The name of the custom claim.",
            },
            "group": {
                "type": OptionType.STR,
                "required": True,
                "aliases": ["claim_group"],
                "documentation": "The group to which the custom claim applies.",
            },
            "values": {
                "type": OptionType.LIST,
                "elements": OptionType.STR,
                "required": True,
                "documentation": "The values for the custom claim.",
            },
        }

    @staticmethod
    def documentation(indentation: Optional[int] = None) -> str:
        if indentation is not None:
            out: str = yaml.dump(CustomClaim.arg_spec(), sort_keys=False)
            values = []
            for line in out.splitlines():
                values.append(f"{' ' * indentation}{line}")
            return "\n".join(values)
        return yaml.dump(CustomClaim.arg_spec(), sort_keys=False)


@dataclass
class Image:
    src: str
    format: ImageFormat = ImageFormat.auto

    def __init__(self, **kwargs):
        try:
            if "src" in kwargs:
                self.src = Verify(kwargs.get("src"), "image.src").verify_str()
            else:
                raise KanidmRequiredOptionError("image.src is not defined")
            if "format" in kwargs:
                self.format = ImageFormat(
                    Verify(kwargs.get("format"), "image.format").verify_str()
                )
            else:
                raise KanidmRequiredOptionError("image.format is not defined")
        except TypeError as e:
            raise KanidmArgsException(str(e), e)
        except ValueError as e:
            raise KanidmArgsException(str(e), e)
        except AttributeError as e:
            raise KanidmRequiredOptionError(str(e), e)
        except Exception as e:
            raise e

    @staticmethod
    def valid_args() -> FrozenSet[str]:
        return frozenset(["src", "format"])

    @staticmethod
    def arg_spec() -> AnsibleArgumentSpec:
        return {
            "src": {
                "type": OptionType.STR,
                "required": True,
                "aliases": ["image_src"],
                "documentation": "The source URL of the image.",
            },
            "format": {
                "type": OptionType.STR,
                "choices": [e.value for e in ImageFormat],
                "default": ImageFormat.auto,
                "required": False,
                "documentation": "The format of the image. Defaults to auto.",
            },
        }

    @staticmethod
    def documentation(indentation: Optional[int] = None) -> str:
        if indentation is not None:
            out: str = yaml.dump(Image.arg_spec(), sort_keys=False)
            values = []
            for line in out.splitlines():
                values.append(f"{' ' * indentation}{line}")
            return "\n".join(values)
        return yaml.dump(Image.arg_spec(), sort_keys=False)

    def get(self) -> Path:
        src = self.src
        dest = Path()

        if self.format == ImageFormat.auto:
            if self.src.endswith(".png"):
                self.format = ImageFormat.png
            elif self.src.endswith(".jpg") or self.src.endswith(".jpeg"):
                self.format = ImageFormat.jpg
            elif self.src.endswith(".gif"):
                self.format = ImageFormat.gif
            elif self.src.endswith(".svg"):
                self.format = ImageFormat.svg
            elif self.src.endswith(".web") or self.src.endswith(".webp"):
                self.format = ImageFormat.webp

        if (
            self.src.startswith("http://")
            or self.src.startswith("https://")
            or self.src.startswith("ftp://")
        ):
            _, temp = tempfile.mkstemp(suffix=self.format.get())
            response = requests.get(self.src)
            if response.status_code == 200:
                with open(temp, "wb") as f:
                    f.write(response.content)

            else:
                raise KanidmModuleError(f"Failed to download image from {self.src}")
            self.src = temp
            dest = Path(temp)
        else:
            dest = Path(self.src)

        if self.format == ImageFormat.auto:
            header: list[bytes] = []
            with open(self.src, "rb") as f:
                for i in range(12):
                    header.append(f.read(1))

            if header[0:8] == [
                b"\x89",
                b"\x50",
                b"\x4e",
                b"\x47",
                b"\x0d",
                b"\x0a",
                b"\x1a",
                b"\x0a",
            ]:
                self.format = ImageFormat.png

            elif (
                header[0:12]
                == [
                    b"\xff",
                    b"\xd8",
                    b"\xff",
                    b"\xe0",
                    b"\x00",
                    b"\x10",
                    b"\x4a",
                    b"\x46",
                    b"\x49",
                    b"\x46",
                    b"\x00",
                    b"\x01",
                ]
                or header[0:4] == [b"\xff", b"\xd8", b"\xff", b"\xee"]
                or (
                    header[0:4] == [b"\xff", b"\xd8", b"\xff", b"\xe1"]
                    and header[6:10]
                    == [b"\x45", b"\x78", b"\x69", b"\x66", b"\x00", b"\x00"]
                )
                or header[0:4] == [b"\xff", b"\xd8", b"\xff", b"\xe0"]
                or header[0:12]
                == [
                    b"\x00",
                    b"\x00",
                    b"\x00",
                    b"\x0c",
                    b"\x6a",
                    b"\x50",
                    b"\x20",
                    b"\x20",
                    b"\x0d",
                    b"\x0a",
                    b"\x87",
                    b"\x0a",
                ]
                or header[0:4] == [b"\xff", b"\x4f", b"\xff", b"\x51"]
            ):
                self.format = ImageFormat.jpg

            elif header[0:6] == [
                b"\x47",
                b"\x49",
                b"\x46",
                b"\x38",
                b"\x37",
                b"\x61",
            ] or header[0:6] == [b"\x47", b"\x49", b"\x46", b"\x38", b"\x39", b"\x61"]:
                self.format = ImageFormat.gif

            elif header[0:4] == [b"\x52", b"\x49", b"\x46", b"\x46"] and header[
                8:12
            ] == [b"\x57", b"\x45", b"\x42", b"\x50"]:
                self.format = ImageFormat.webp

            else:
                with open(self.src, "rt") as f:
                    for line in f:
                        if (
                            line.startswith("<svg")
                            or line.startswith("<?xml")
                            or line.startswith("<!DOCTYPE svg")
                        ):
                            self.format = ImageFormat.svg
                            break

        if self.format == ImageFormat.auto:
            raise KanidmException(f"Unknown image format for {src}")
        return dest


@dataclass
class KanidmOauthArgs:
    name: str
    url: str
    redirect_url: List[str]
    scopes: List[Scope]
    kanidm: KanidmConf
    display_name: Optional[str] = None
    group: str = "idm_all_persons"
    public: bool = False
    claim_join: ClaimJoin = ClaimJoin.array
    pkce: bool = True
    legacy_crypto: bool = False
    strict_redirect: bool = True
    local_redirect: bool = False
    username: PrefUsername = PrefUsername.spn
    sup_scopes: Optional[List[SupScope]] = None
    custom_claims: Optional[List[CustomClaim]] = None
    image: Optional[Image] = None

    def __init__(self, **kwargs):
        # Defaults
        self.claim_join = ClaimJoin.array
        self.pkce = True
        self.legacy_crypto = False
        self.strict_redirect = True
        self.local_redirect = False
        self.username = PrefUsername.spn
        self.sup_scopes = None
        self.custom_claims = None
        self.image = None

        # Set args
        try:
            if "name" in kwargs:
                self.name = Verify(kwargs.get("name"), "name").verify_str()
            else:
                raise KanidmRequiredOptionError("name is required")
            if "url" in kwargs:
                self.url = Verify(kwargs.get("url"), "url").verify_str()
            else:
                raise KanidmRequiredOptionError("url is required")
            if "redirect_url" in kwargs:
                self.redirect_url = Verify(
                    kwargs.get("redirect_url"), "redirect_url"
                ).verify_list_str()
            else:
                raise KanidmRequiredOptionError("redirect_url is required")
            if "scopes" in kwargs:
                self.scopes = [
                    Scope(s)
                    for s in Verify(kwargs.get("scopes"), "scopes").verify_list_str()
                ]
            else:
                raise KanidmRequiredOptionError("scopes is required")
            if "kanidm" in kwargs:
                self.kanidm = KanidmConf(
                    **Verify(kwargs.get("kanidm"), "kanidm").verify_dict()
                )
            else:
                raise KanidmRequiredOptionError("kanidm is required")
            if "display_name" in kwargs:
                self.display_name = Verify(
                    kwargs.get("display_name", self.name), "display_name"
                ).verify_str()
            if "group" in kwargs:
                self.group = Verify(kwargs.get("group"), "group").verify_default_str(
                    "idm_all_persons"
                )
            if "public" in kwargs:
                self.public = Verify(
                    kwargs.get("public"), "public"
                ).verify_default_bool(False)
            if "claim_join" in kwargs:
                self.claim_join = ClaimJoin(
                    Verify(kwargs.get("claim_join"), "claim_join").verify_default_str(
                        ClaimJoin.array
                    )
                )
            if "pkce" in kwargs:
                self.pkce = Verify(kwargs.get("pkce"), "pkce").verify_default_bool(True)
            if "legacy_crypto" in kwargs:
                self.legacy_crypto = Verify(
                    kwargs.get("legacy_crypto"), "legacy_crypto"
                ).verify_default_bool(False)
            if "strict_redirect" in kwargs:
                self.strict_redirect = Verify(
                    kwargs.get("strict_redirect"), "strict_redirect"
                ).verify_default_bool(True)
            if "local_redirect" in kwargs:
                self.local_redirect = Verify(
                    kwargs.get("local_redirect"), "local_redirect"
                ).verify_default_bool(False)
            if "username" in kwargs:
                username = Verify(
                    kwargs.get("username"), "username"
                ).verify_default_str(PrefUsername.spn)
                self.username = PrefUsername(username)
            if "sup_scopes" in kwargs:
                sup_scopes: list[dict] | None = Verify(
                    kwargs.get("sup_scopes"), "sup_scopes"
                ).verify_opt_list_dict()
                self.sup_scopes = (
                    [SupScope(**scope) for scope in sup_scopes]
                    if sup_scopes is not None
                    else None
                )
            if "custom_claims" in kwargs:
                cc = Verify(
                    kwargs.get("custom_claims"), "custom_claims"
                ).verify_opt_list_dict()
                if cc is None:
                    self.custom_claims = None
                else:
                    self.custom_claims = [CustomClaim(**claim) for claim in cc]
            if "image" in kwargs:
                img = Verify(kwargs.get("image"), "image").verify_opt_dict()
                self.image = Image(**img) if img is not None else None
        except TypeError as e:
            raise KanidmArgsException(str(e), e)
        except ValueError as e:
            raise KanidmArgsException(str(e), e)
        except AttributeError as e:
            raise KanidmRequiredOptionError(str(e), e)
        except FileNotFoundError as e:
            raise KanidmArgsException(str(e), e)
        except Exception as e:
            raise e

    @staticmethod
    def valid_args() -> FrozenSet[str]:
        kanidm = [f"kanidm.{k}" for k in KanidmConf.valid_args()]
        sup_scopes = [f"sup_scopes.{k}" for k in SupScope.valid_args()]
        custom_claims = [f"custom_claims.{k}" for k in CustomClaim.valid_args()]
        image = [f"image.{k}" for k in Image.valid_args()]
        args = [
            "name",
            "url",
            "redirect_url",
            "scopes",
            "display_name",
            "group",
            "public",
            "claim_join",
            "pkce",
            "legacy_crypto",
            "strict_redirect",
            "local_redirect",
            "username",
        ]
        args.extend(kanidm)
        args.extend(sup_scopes)
        args.extend(custom_claims)
        args.extend(image)
        return frozenset(args)

    @staticmethod
    def arg_spec() -> AnsibleArgumentSpec:
        kanidm = KanidmConf.arg_spec()
        sup_scopes = SupScope.arg_spec()
        custom_claims = CustomClaim.arg_spec()
        image = Image.arg_spec()
        return {
            "name": {
                "type": OptionType.STR,
                "required": True,
                "aliases": ["client_name"],
                "documentation": "The name of the OAuth client.",
            },
            "url": {
                "type": OptionType.STR,
                "required": True,
                "aliases": ["client_url"],
                "documentation": "The URL of the OAuth client's landing page.",
            },
            "redirect_url": {
                "type": OptionType.LIST,
                "elements": OptionType.STR,
                "required": True,
                "aliases": ["redirect_urls"],
                "documentation": "The redirect URLs for the OAuth client.",
            },
            "scopes": {
                "type": OptionType.LIST,
                "elements": OptionType.STR,
                "choices": [e.value for e in Scope],
                "required": True,
                "aliases": ["scope"],
                "documentation": "The scopes requested by the OAuth client.",
            },
            "kanidm": {
                "type": OptionType.DICT,
                "options": kanidm,
                "required": True,
                "documentation": "Configuration for the Kanidm client.",
            },
            "display_name": {
                "type": OptionType.STR,
                "required": False,
                "aliases": ["client_display_name"],
                "default": "{{ name }}",
                "documentation": "The display name of the OAuth client.",
            },
            "group": {
                "type": OptionType.STR,
                "default": "idm_all_persons",
                "required": False,
                "documentation": "The group associated with the OAuth client. Defaults to all persons.",
            },
            "public": {
                "type": OptionType.BOOL,
                "default": False,
                "required": False,
                "documentation": "Indicates if the client is public.",
            },
            "claim_join": {
                "type": OptionType.STR,
                "choices": [e.value for e in ClaimJoin],
                "default": ClaimJoin.array,
                "required": False,
                "documentation": "How to join claims in the response. Defaults to array.",
            },
            "pkce": {
                "type": OptionType.BOOL,
                "default": True,
                "required": False,
                "documentation": "Indicates if PKCE is enabled.",
            },
            "legacy_crypto": {
                "type": OptionType.BOOL,
                "default": False,
                "required": False,
                "documentation": "Indicates if legacy cryptography is used.",
            },
            "strict_redirect": {
                "type": OptionType.BOOL,
                "default": True,
                "required": False,
                "documentation": "Indicates if strict redirect validation is enabled.",
            },
            "local_redirect": {
                "type": OptionType.BOOL,
                "default": False,
                "required": False,
                "documentation": "Indicates if local redirects are allowed.",
            },
            "sup_scopes": {
                "type": OptionType.LIST,
                "elements": OptionType.DICT,
                "options": sup_scopes,
                "required": False,
                "documentation": "Additional scopes for specific groups.",
            },
            "username": {
                "type": OptionType.STR,
                "choices": [e.value for e in PrefUsername],
                "default": PrefUsername.spn,
                "required": False,
                "documentation": "Preferred username format. Defaults to SPN which takes the format of '<username>@<kanidm.uri>'.",
            },
            "custom_claims": {
                "type": OptionType.LIST,
                "elements": OptionType.DICT,
                "options": custom_claims,
                "required": False,
                "documentation": "Custom claims to be included in the OAuth response.",
            },
            "image": {
                "type": OptionType.DICT,
                "options": image,
                "required": False,
                "aliases": ["logo"],
                "documentation": "Image configuration for the OAuth client.",
            },
        }

    @classmethod
    def documentation(cls, indentation: Optional[int] = None) -> str:
        if indentation is not None:
            out: str = yaml.dump(cls.arg_spec(), sort_keys=False)
            values = []
            for line in out.splitlines():
                values.append(f"{' ' * indentation}{line}")
            return "\n".join(values)
        return yaml.dump(cls.arg_spec(), sort_keys=False)
