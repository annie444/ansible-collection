from __future__ import absolute_import, annotations, division, print_function

try:
    from typing import Callable
except ImportError:
    from typing_extensions import Callable

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

try:
    from typing import List
except ImportError:
    from typing_extensions import List

try:
    from typing import Dict
except ImportError:
    from typing_extensions import Dict

try:
    from typing import Tuple
except ImportError:
    from typing_extensions import Tuple

try:
    from typing import TypeVar
except ImportError:
    from typing_extensions import TypeVar

try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired

try:
    from typing import Union
except ImportError:
    from typing_extensions import Union

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum


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


class AnsibleModuleSupport(StrEnum):  # type: ignore
    FULL = "full"
    NONE = "none"
    PARTIAL = "partial"
    NA = "N/A"


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
