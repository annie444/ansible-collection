from __future__ import absolute_import, annotations, division, print_function

from dataclasses import dataclass
import traceback
from datetime import timedelta

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
class KanidmPersonArgs:
    name: str
    kanidm: KanidmConf
    display_name: Optional[str] = None
    debug: bool = False
    ttl: int | timedelta = timedelta(days=5)

    def __init__(self, **kwargs):
        # Defaults
        self.display_name = None
        self.debug = False
        self.ttl = timedelta(days=5)

        # Set args
        try:
            if "name" in kwargs:
                self.name = Verify(kwargs.get("name"), "name").verify_str()
            else:
                raise KanidmRequiredOptionError("name is required")
            if "display_name" in kwargs:
                self.display_name = Verify(
                    kwargs.get("display_name"), "display_name"
                ).verify_opt_str()
            if "kanidm" in kwargs:
                self.kanidm = KanidmConf(
                    **Verify(kwargs.get("kanidm"), "kanidm").verify_dict()
                )
            else:
                raise KanidmRequiredOptionError("kanidm is required")
            if "debug" in kwargs:
                self.debug = Verify(kwargs.get("debug"), "debug").verify_bool()
            if "ttl" in kwargs:
                self.ttl = Verify(kwargs.get("ttl"), "ttl").verify_int()
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
        args = [
            "name",
            "display_name",
            "ttl",
            "debug",
        ]
        args.extend(kanidm)
        return frozenset(args)

    @staticmethod
    def arg_spec() -> AnsibleArgumentSpec:
        kanidm = KanidmConf.arg_spec()
        return {
            "name": {
                "type": OptionType("str"),
                "required": True,
                "aliases": ["username"],
                "description": "The username for the user.",
            },
            "display_name": {
                "type": OptionType("str"),
                "required": False,
                "default": "{{ name }}",
                "aliases": ["fullname"],
                "description": "The display name of the User.",
            },
            "ttl": {
                "type": OptionType("int"),
                "required": False,
                "default": timedelta(days=5).seconds,
                "description": "The TTL of the credential reset token.",
            },
            "kanidm": {
                "type": OptionType("dict"),
                "options": kanidm,
                "required": True,
                "description": "Configuration for the Kanidm client.",
            },
            "debug": {
                "type": OptionType("bool"),
                "default": False,
                "required": False,
                "description": "Enable debug mode.",
            },
        }

    @classmethod
    def full_arg_spec(cls) -> AnsibleFullArgumentSpec:
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
            "argument_spec": cls.arg_spec(),
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
