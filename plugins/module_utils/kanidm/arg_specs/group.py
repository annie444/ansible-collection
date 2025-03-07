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
class KanidmGroupArgs:
    name: str
    users: List[str]
    kanidm: KanidmConf
    parent: Optional[str] = None
    debug: bool = False

    def __init__(self, **kwargs):
        # Defaults
        self.parent = None
        self.debug = False

        # Set args
        try:
            if "name" in kwargs:
                self.name = Verify(kwargs.get("name"), "name").verify_str()
            else:
                raise KanidmRequiredOptionError("name is required")
            if "parent" in kwargs:
                self.parent = Verify(kwargs.get("parent"), "parent").verify_opt_str()
            else:
                raise KanidmRequiredOptionError("parent is required")
            if "users" in kwargs:
                self.users = Verify(kwargs.get("users"), "users").verify_list_str()
            else:
                raise KanidmRequiredOptionError("users is required")
            if "kanidm" in kwargs:
                self.kanidm = KanidmConf(
                    **Verify(kwargs.get("kanidm"), "kanidm").verify_dict()
                )
            else:
                raise KanidmRequiredOptionError("kanidm is required")
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
            "parent",
            "users",
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
                "aliases": ["client_name"],
                "description": "The name of the OAuth client.",
            },
            "parent": {
                "type": OptionType("str"),
                "required": False,
                "description": "The parent group of the group.",
            },
            "users": {
                "type": OptionType("list"),
                "elements": OptionType("str"),
                "required": True,
                "description": "The users in the group.",
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
