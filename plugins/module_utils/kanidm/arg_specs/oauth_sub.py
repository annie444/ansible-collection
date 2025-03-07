from __future__ import absolute_import, annotations, division, print_function

from dataclasses import dataclass
import traceback
import tempfile
from pathlib import Path

from ansible.module_utils.compat.typing import FrozenSet, Optional, List

from ...ansible_specs import (
    AnsibleArgumentSpec,
    OptionType,
)
from ...verify import Verify
from ..exceptions import (
    KanidmArgsException,
    KanidmException,
    KanidmModuleError,
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


REQUESTS_IMP_ERR = None
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    REQUESTS_IMP_ERR = traceback.format_exc()


class Scope(StrEnum):  # type: ignore
    openid = "openid"
    profile = "profile"
    email = "email"
    address = "address"
    phone = "phone"
    groups = "groups"
    ssh_publickeys = "ssh_publickeys"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class ImageFormat(StrEnum):  # type: ignore
    png = "png"
    jpg = "jpg"
    gif = "gif"
    svg = "svg"
    webp = "webp"
    auto = "auto"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

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


class ClaimJoin(StrEnum):  # type: ignore
    array = "array"
    csv = "csv"
    ssv = "ssv"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class PrefUsername(StrEnum):  # type: ignore
    spn = "spn"
    short = "short"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


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
                "type": OptionType("str"),
                "required": True,
                "aliases": ["sup_scope_group"],
                "description": "The group to which the additional scopes apply.",
            },
            "scopes": {
                "type": OptionType("list"),
                "elements": OptionType("str"),
                "choices": [e.value for e in Scope],
                "required": True,
                "description": "The additional scopes for the group.",
            },
        }

    @staticmethod
    def documentation(indentation: Optional[int] = None) -> str:
        yaml.SafeDumper.add_multi_representer(
            StrEnum,
            yaml.representer.SafeRepresenter.represent_str,  # type: ignore
        )
        if indentation is not None:
            out: str = yaml.safe_dump(SupScope.arg_spec(), sort_keys=False)
            values = []
            for line in out.splitlines():
                values.append(f"{' ' * indentation}{line}")
            return "\n".join(values)
        return yaml.safe_dump(SupScope.arg_spec(), sort_keys=False)


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
                "type": OptionType("str"),
                "required": True,
                "aliases": ["claim_name"],
                "description": "The name of the custom claim.",
            },
            "group": {
                "type": OptionType("str"),
                "required": True,
                "aliases": ["claim_group"],
                "description": "The group to which the custom claim applies.",
            },
            "values": {
                "type": OptionType("list"),
                "elements": OptionType("str"),
                "required": True,
                "description": "The values for the custom claim.",
            },
        }

    @staticmethod
    def documentation(indentation: Optional[int] = None) -> str:
        yaml.SafeDumper.add_multi_representer(
            StrEnum,
            yaml.representer.SafeRepresenter.represent_str,  # type: ignore
        )
        if indentation is not None:
            out: str = yaml.safe_dump(CustomClaim.arg_spec(), sort_keys=False)
            values = []
            for line in out.splitlines():
                values.append(f"{' ' * indentation}{line}")
            return "\n".join(values)
        return yaml.safe_dump(CustomClaim.arg_spec(), sort_keys=False)


@dataclass
class Image:
    src: str
    format: ImageFormat = ImageFormat("auto")

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
                "type": OptionType("str"),
                "required": True,
                "aliases": ["image_src"],
                "description": "The source URL of the image.",
            },
            "format": {
                "type": OptionType("str"),
                "choices": [e.value for e in ImageFormat],
                "default": ImageFormat.auto,
                "required": False,
                "description": "The format of the image. Defaults to auto.",
            },
        }

    @staticmethod
    def documentation(indentation: Optional[int] = None) -> str:
        yaml.SafeDumper.add_multi_representer(
            StrEnum,
            yaml.representer.SafeRepresenter.represent_str,  # type: ignore
        )
        if indentation is not None:
            out: str = yaml.safe_dump(Image.arg_spec(), sort_keys=False)
            values = []
            for line in out.splitlines():
                values.append(f"{' ' * indentation}{line}")
            return "\n".join(values)
        return yaml.safe_dump(Image.arg_spec(), sort_keys=False)

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
            temp = tempfile.mkstemp(suffix=self.format.get())[1]
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
