from __future__ import absolute_import, annotations, division, print_function

from dataclasses import dataclass
import traceback

from ansible.module_utils.compat.typing import FrozenSet, Optional, List

from ...ansible_specs import (
    AnsibleArgumentSpec,
    AnsibleFullArgumentSpec,
    OptionType,
)
from ...verify import Verify
from ..exceptions import (
    KanidmArgsException,
    KanidmRequiredOptionError,
)
from .oauth_sub import (
    ClaimJoin,
    CustomClaim,
    Image,
    PrefUsername,
    Scope,
    SupScope,
)
from .conf import KanidmConf

STR_ENUM_IMP_ERR = None
try:
    from enum import StrEnum

    HAS_ENUM = True
except ImportError:
    try:
        from strenum import StrEnum

        HAS_ENUM = True
    except ImportError:
        STR_ENUM_IMP_ERR = traceback.format_exc()
        HAS_ENUM = False
        StrEnum = object


YAML_IMP_ERR = None
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    YAML_IMP_ERR = traceback.format_exc()


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
    claim_join: ClaimJoin = ClaimJoin("array")
    pkce: bool = True
    legacy_crypto: bool = False
    strict_redirect: bool = True
    local_redirect: bool = False
    username: PrefUsername = PrefUsername("spn")
    sup_scopes: Optional[List[SupScope]] = None
    custom_claims: Optional[List[CustomClaim]] = None
    image: Optional[Image] = None
    debug: bool = False

    def __init__(self, **kwargs):
        # Defaults
        self.display_name = kwargs.get("display_name", kwargs.get("name"))
        self.group = "idm_all_persons"
        self.public = False
        self.claim_join = ClaimJoin.array
        self.pkce = True
        self.legacy_crypto = False
        self.strict_redirect = True
        self.local_redirect = False
        self.username = PrefUsername.spn
        self.sup_scopes = None
        self.custom_claims = None
        self.image = None
        self.debug = False

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
            if "debug" in kwargs:
                self.debug = Verify(kwargs.get("debug"), "debug").verify_default_bool(
                    False
                )
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

        if self.public and not self.pkce:
            raise KanidmArgsException("Public clients must use PKCE")

        if not self.public and self.local_redirect:
            raise KanidmArgsException(
                "Local redirects are only allowed for public clients"
            )

        if self.local_redirect and not self.strict_redirect:
            raise KanidmArgsException(
                "Local redirects require strict redirect validation"
            )

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
            "debug",
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
                "type": OptionType("str"),
                "required": True,
                "aliases": ["client_name"],
                "description": "The name of the OAuth client.",
            },
            "url": {
                "type": OptionType("str"),
                "required": True,
                "aliases": ["client_url"],
                "description": "The URL of the OAuth client's landing page.",
            },
            "redirect_url": {
                "type": OptionType("list"),
                "elements": OptionType("str"),
                "required": True,
                "aliases": ["redirect_urls"],
                "description": "The redirect URLs for the OAuth client.",
            },
            "scopes": {
                "type": OptionType("list"),
                "elements": OptionType("str"),
                "choices": [e.value for e in Scope],
                "required": True,
                "aliases": ["scope"],
                "description": "The scopes requested by the OAuth client.",
            },
            "kanidm": {
                "type": OptionType("dict"),
                "options": kanidm,
                "required": True,
                "description": "Configuration for the Kanidm client.",
            },
            "display_name": {
                "type": OptionType("str"),
                "required": False,
                "aliases": ["client_display_name"],
                "default": "{{ name }}",
                "description": "The display name of the OAuth client.",
            },
            "group": {
                "type": OptionType("str"),
                "default": "idm_all_persons",
                "required": False,
                "description": "The group associated with the OAuth client. Defaults to all persons.",
            },
            "public": {
                "type": OptionType("bool"),
                "default": False,
                "required": False,
                "description": "Indicates if the client is public.",
            },
            "claim_join": {
                "type": OptionType("str"),
                "choices": [e.value for e in ClaimJoin],
                "default": ClaimJoin("array"),
                "required": False,
                "description": "How to join claims in the response. Defaults to array.",
            },
            "pkce": {
                "type": OptionType("bool"),
                "default": True,
                "required": False,
                "description": "Indicates if PKCE is enabled.",
            },
            "legacy_crypto": {
                "type": OptionType("bool"),
                "default": False,
                "required": False,
                "description": "Indicates if legacy cryptography is used.",
            },
            "strict_redirect": {
                "type": OptionType("bool"),
                "default": True,
                "required": False,
                "description": "Indicates if strict redirect validation is enabled.",
            },
            "local_redirect": {
                "type": OptionType("bool"),
                "default": False,
                "required": False,
                "description": "Indicates if local redirects are allowed.",
            },
            "sup_scopes": {
                "type": OptionType("list"),
                "elements": OptionType("dict"),
                "options": sup_scopes,
                "required": False,
                "description": "Additional scopes for specific groups.",
            },
            "username": {
                "type": OptionType("str"),
                "choices": [e.value for e in PrefUsername],
                "default": PrefUsername("spn"),
                "required": False,
                "description": "Preferred username format. Defaults to SPN which takes the format of '<username>@<kanidm.uri>'.",
            },
            "custom_claims": {
                "type": OptionType("list"),
                "elements": OptionType("dict"),
                "options": custom_claims,
                "required": False,
                "description": "Custom claims to be included in the OAuth response.",
            },
            "image": {
                "type": OptionType("dict"),
                "options": image,
                "required": False,
                "aliases": ["logo"],
                "description": "Image configuration for the OAuth client.",
            },
            "debug": {
                "type": OptionType("bool"),
                "default": False,
                "required": False,
                "description": "Enable debug mode.",
            },
        }

    @staticmethod
    def full_arg_spec() -> AnsibleFullArgumentSpec:
        kanidm_full_spec = KanidmConf.full_arg_spec()
        mutually_exclusive = []
        required_together = []

        if "mutually_exclusive" in kanidm_full_spec:
            for values in enumerate(kanidm_full_spec["mutually_exclusive"]):
                mutually_exclusive.append([])
                for item in values:
                    if (
                        isinstance(item, list)
                        or isinstance(item, tuple)
                        or isinstance(item, set)
                    ):
                        for v in item:
                            mutually_exclusive[-1].append(f"kanidm.{v}")
                    else:
                        mutually_exclusive[-1].append(f"kanidm.{item}")
        if "required_together" in kanidm_full_spec:
            for values in enumerate(kanidm_full_spec["required_together"]):
                required_together.append([])
                for item in values:
                    required_together[-1].append(f"kanidm.{item}")

        return {
            "argument_spec": KanidmOauthArgs.arg_spec(),
            "mutually_exclusive": mutually_exclusive,
            "required_together": required_together,
        }

    @classmethod
    def documentation(cls, indentation: Optional[int] = None) -> str:
        yaml.SafeDumper.add_multi_representer(
            StrEnum,
            yaml.representer.SafeRepresenter.represent_str,  # type: ignore
        )
        if indentation is not None:
            out: str = yaml.safe_dump(cls.arg_spec(), sort_keys=False)
            values = []
            for line in out.splitlines():
                values.append(f"{' ' * indentation}{line}")
            return "\n".join(values)
        return yaml.safe_dump(cls.arg_spec(), sort_keys=False)
