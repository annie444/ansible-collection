from __future__ import absolute_import, annotations, division, print_function

from dataclasses import dataclass
import traceback
from pathlib import Path

from ansible.module_utils.compat.typing import FrozenSet, Optional

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
    def full_arg_spec() -> AnsibleFullArgumentSpec:
        return {
            "argument_spec": KanidmConf.arg_spec(),
            "mutually_exclusive": [
                ["token", "username"],
                ["token", "password"],
                ["ca_path", "ca_cert_data"],
            ],
            "required_together": [
                ("username", "password"),
            ],
        }

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
                "type": OptionType("str"),
                "required": True,
                "aliases": ["kanidm_uri"],
                "description": "The URI of the Kanidm server.",
            },
            "token": {
                "type": OptionType("str"),
                "required": False,
                "no_log": True,
                "aliases": ["kanidm_token"],
                "description": "The token for authentication.",
            },
            "ca_path": {
                "type": OptionType("path"),
                "required": False,
                "aliases": ["kanidm_ca_path"],
                "description": "The path to the CA certificate.",
            },
            "username": {
                "type": OptionType("str"),
                "required": False,
                "no_log": True,
                "aliases": ["kanidm_username"],
                "description": "The username for authentication.",
            },
            "password": {
                "type": OptionType("str"),
                "required": False,
                "no_log": True,
                "aliases": ["kanidm_password"],
                "description": "The password for authentication.",
            },
            "ca_cert_data": {
                "type": OptionType("str"),
                "required": False,
                "no_log": True,
                "description": "The CA certificate data as a base64 encoded string.",
            },
            "verify_ca": {
                "type": OptionType("bool"),
                "required": False,
                "default": True,
                "description": "Whether to verify the Kanidm server's certificate chain.",
            },
            "connect_timeout": {
                "type": OptionType("int"),
                "required": False,
                "default": 30,
                "description": "The connection timeout in seconds.",
            },
        }

    @staticmethod
    def documentation(indentation: Optional[int] = None) -> str:
        yaml.SafeDumper.add_multi_representer(
            StrEnum,
            yaml.representer.SafeRepresenter.represent_str,  # type: ignore
        )
        if indentation is not None:
            out: str = yaml.safe_dump(KanidmConf.arg_spec(), sort_keys=False)
            values = []
            for line in out.splitlines():
                values.append(f"{' ' * indentation}{line}")
            return "\n".join(values)
        return yaml.safe_dump(KanidmConf.arg_spec(), sort_keys=False)
