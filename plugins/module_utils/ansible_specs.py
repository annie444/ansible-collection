from __future__ import annotations, division
from ansible.module_utils.compat.typing import (
    Callable,
    TypedDict,
    List,
    Dict,
    Tuple,
    TypeVar,
    NotRequired,
    Union,
)
import traceback

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


class OptionType(StrEnum):  # type: ignore
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    DICT = "dict"
    LIST = "list"
    PATH = "path"
    RAW = "raw"
    JSONARG = "jsonarg"
    JSON = "json"
    BYTES = "bytes"
    BITS = "bits"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    @classmethod
    def documentation(cls) -> str:
        return str(cls.value)


class AnsiblePluginTypes(StrEnum):  # type: ignore
    LOOKUP = "lookup"
    ACTION = "action"
    BECOME = "become"
    CACHE = "cache"
    CALLBACK = "callback"
    CLI_CONF = "cliconf"
    CONNECTION = "connection"
    DOCS = "docs"
    FILTER = "filter"
    HTTPAPI = "httpapi"
    INVENTORY = "inventory"
    MODULE = "module"
    MODULE_UTILS = "module_utils"
    NETCONF = "netconf"
    SHELL = "shell"
    STRATEGY = "strategy"
    TERMINAL = "terminal"
    TEST = "test"
    VAR = "var"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    @classmethod
    def documentation(cls) -> str:
        return str(cls.value)


class AnsibleModuleSupport(StrEnum):  # type: ignore
    FULL = "full"
    NONE = "none"
    PARTIAL = "partial"
    NA = "N/A"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    @classmethod
    def documentation(cls) -> str:
        return str(cls.value)


T = TypeVar("T")
D = TypeVar("D")

S = TypeVar("S")
AnsibleSequence = Union[List[S], Tuple[S, ...]]


class AnsibleDeprecatedAlias(TypedDict):
    name: str
    version: NotRequired[str]
    date: NotRequired[str]
    collection_name: NotRequired[str]


class AnsibleOption(TypedDict):
    type: NotRequired[OptionType]
    elements: NotRequired[OptionType]
    default: NotRequired[D]
    fallback: NotRequired[Tuple[Callable[[T], D], List[T]]]
    required: NotRequired[bool]
    choices: NotRequired[List[D]]
    no_log: NotRequired[bool]
    options: NotRequired["AnsibleArgumentSpec"]
    apply_defaults: NotRequired[bool]
    removed_in_version: NotRequired[str]
    removed_at_date: NotRequired[str]
    removed_from_collection: NotRequired[str]
    deprecated_aliases: NotRequired[List[AnsibleDeprecatedAlias]]
    aliases: NotRequired[List[str]]
    description: NotRequired[str]
    documentation: NotRequired[str | List[str]]


AnsibleArgumentSpec = Dict[str, AnsibleOption]


class AnsibleFullArgumentSpec(TypedDict):
    argument_spec: AnsibleArgumentSpec
    mutually_exclusive: NotRequired[List[AnsibleSequence[str]]]
    required_together: NotRequired[List[AnsibleSequence[str]]]
    required_one_of: NotRequired[List[AnsibleSequence[str]]]
    required_if: NotRequired[
        List[AnsibleSequence[str | AnsibleSequence[str] | D | bool]]
        | Tuple[str | AnsibleSequence[str] | D | bool]
    ]
    required_by: NotRequired[Dict[str, str | AnsibleSequence[str]]]


class AnsibleSeeAlso(TypedDict):
    module: NotRequired[str]
    description: NotRequired[str | List[str]]
    plugin: NotRequired[str]
    plugin_type: NotRequired[AnsiblePluginTypes]
    link: NotRequired[str]
    ref: NotRequired[str]


class AnsibleModuleAttributes(TypedDict):
    description: NotRequired[str | List[str]]
    details: NotRequired[str | List[str]]
    support: AnsibleModuleSupport
    membership: NotRequired[str | List[str]]
    platforms: NotRequired[str | List[str]]
    version_added: NotRequired[str]


class AnsibleModuleSpec(TypedDict):
    module: str
    short_description: NotRequired[str]
    description: NotRequired[str | List[str]]
    version_added: NotRequired[str]
    author: NotRequired[str | List[str]]
    deprecated: NotRequired[str]
    options: AnsibleArgumentSpec
    requirements: NotRequired[List[str]]
    seealso: NotRequired[str | List[str | AnsibleSeeAlso]]
    attributes: NotRequired[AnsibleModuleAttributes]
    notes: NotRequired[str | List[str]]
