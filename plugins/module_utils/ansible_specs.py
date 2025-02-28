from typing import Callable, TypedDict, List, Dict, Any, Tuple, TypeVar, NotRequired
from enum import StrEnum


class OptionType(StrEnum):
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


T = TypeVar("T")
D = TypeVar("D")

S = TypeVar("S")
AnsibleSequence = List[S] | Tuple[S]


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
    mutually_exclusive: NotRequired[List[AnsibleSequence[str]]]
    required_together: NotRequired[List[AnsibleSequence[str]]]
    required_one_of: NotRequired[List[AnsibleSequence[str]]]
    required_if: NotRequired[
        List[AnsibleSequence[str | AnsibleSequence[str] | D | bool]]
        | Tuple[str | AnsibleSequence[str] | D | bool]
    ]
    required_by: NotRequired[Dict[str, str | AnsibleSequence[str]]]
    documentation: NotRequired[str | List[str]]


AnsibleArgumentSpec = Dict[str, AnsibleOption]


class AnsiblePluginTypes(StrEnum):
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


class AnsibleModuleSupport(StrEnum):
    FULL = "full"
    NONE = "none"
    PARTIAL = "partial"
    NA = "N/A"


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
