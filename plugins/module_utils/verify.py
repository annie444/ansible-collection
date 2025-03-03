from __future__ import annotations, division

from pathlib import Path
import tempfile
from base64 import b64decode
import gzip
import zlib
import bz2
import tarfile
import zipfile
import os
from ansible.module_utils.compat.typing import Any

from ansible.module_utils.common.validation import (
    check_type_bool,
    check_type_list,
    check_type_int,
    check_type_str,
    check_type_dict,
)


def decode_file(content: bytes, header: list[bytes]) -> str:
    if header[0:2] == [b"\x1f", b"\x8b"]:
        path = tempfile.mkstemp()[1]
        with open(path, "wb") as f:
            f.write(gzip.decompress(content))
        return str(path)
    elif header[0:2] == [b"\x1f", b"\xa0"]:
        path = tempfile.mkstemp(suffix=".tar.z")[1]
        with open(path, "wb") as f:
            f.write(content)
        temp_path = tempfile.mkdtemp()
        with tarfile.open(path) as f:
            members = f.getmembers()
            f.extractall(path=temp_path)
        os.remove(path)
        path = f"{temp_path}/{members[0].name}"
        return str(path)
    elif header[0:3] == [b"\x42", b"\x5a", b"\x68"]:
        path = tempfile.mkstemp()[1]
        with open(path, "wb") as f:
            f.write(bz2.decompress(content))
        return str(path)
    elif header[0:4] == [b"\x50", b"\x4b", b"\x03", b"\x04"] or header[0:4] == [
        b"\x50",
        b"\x4b",
        b"\x07",
        b"\x08",
    ]:
        path = tempfile.mkstemp(suffix=".zip")[1]
        with open(path, "wb") as f:
            f.write(content)
        temp_path = tempfile.mkdtemp()
        zip_file = zipfile.ZipFile(path)
        members = zip_file.namelist()
        zip_file.extractall(path=temp_path)
        zip_file.close()
        os.remove(path)
        path = f"{temp_path}/{members[0]}"
        return str(path)
    elif header[0:4] == [b"\x50", b"\x4b", b"\x05", b"\x06"]:
        raise ValueError("Path is an empty zip file")
    elif header[0:3] == [b"\xef", b"\xbb", b"\xbf"]:
        path = tempfile.mkstemp()[1]
        with open(path, "wb") as f:
            f.write(content)
        return str(path)
    elif header[0:2] == [b"\xff", b"\xfe"]:
        path = tempfile.mkstemp()[1]
        with open(path, "w") as f:
            f.write(content.decode("utf-16-le"))
        return str(path)
    elif header[0:2] == [b"\xfe", b"\xff"]:
        path = tempfile.mkstemp()[1]
        with open(path, "w") as f:
            f.write(content.decode("utf-16-be"))
        return str(path)
    elif header[0:4] == [b"\xff", b"\xfe", b"\x00", b"\x00"]:
        path = tempfile.mkstemp()[1]
        with open(path, "w") as f:
            f.write(content.decode("utf-32-le"))
        return str(path)
    elif header[0:4] == [b"\x00", b"\x00", b"\xfe", b"\xff"]:
        path = tempfile.mkstemp()[1]
        with open(path, "w") as f:
            f.write(content.decode("utf-32-be"))
        return str(path)
    elif (
        header[0:4] == [b"\x2b", b"\x2f", b"\x76", b"\x38"]
        or header[0:4] == [b"\x2b", b"\x2f", b"\x76", b"\x39"]
        or header[0:4] == [b"\x2b", b"\x2f", b"\x76", b"\x2b"]
        or header[0:4] == [b"\x2b", b"\x2f", b"\x76", b"\x2f"]
    ):
        path = tempfile.mkstemp()[1]
        with open(path, "w") as f:
            f.write(content.decode("utf-7"))
        return str(path)
    elif header[0:2] == [b"\x1f", b"\x8b"]:
        path = tempfile.mkstemp(suffix=".tar.gz")[1]
        temp_path = tempfile.mkdtemp()
        with tarfile.open(path) as f:
            members = f.getmembers()
            f.extractall(path=temp_path)
        os.remove(path)
        path = f"{temp_path}/{members[0].name}"
        return str(path)
    elif header[0:6] == [b"\xfd", b"\x37", b"\x7a", b"\x58", b"\x5a", b"\x00"]:
        path = tempfile.mkstemp(suffix=".tar.xz")[1]
        temp_path = tempfile.mkdtemp()
        with tarfile.open(path) as f:
            members = f.getmembers()
            f.extractall(path=temp_path)
        os.remove(path)
        path = f"{temp_path}/{members[0].name}"
        return str(path)
    elif (
        header[0:2] == [b"\x78", b"\x01"]
        or header[0:2] == [b"\x78", b"\x5e"]
        or header[0:2] == [b"\x78", b"\x9c"]
        or header[0:2] == [b"\x78", b"\xda"]
        or header[0:2] == [b"\x78", b"\x20"]
        or header[0:2] == [b"\x78", b"\x7d"]
        or header[0:2] == [b"\x78", b"\xbb"]
        or header[0:2] == [b"\x78", b"\xf9"]
    ):
        path = tempfile.mkstemp()[1]
        with open(path, "wb") as f:
            f.write(zlib.decompress(content))
        return str(path)
    else:
        raise ValueError("Unable to decode file")


class Verify:
    def __init__(self, value: Any | None, name: str):
        self.value = value
        self.name = name

    def verify_opt_str(self) -> str | None:
        if self.value is None:
            return None
        self.value = check_type_str(self.value)
        if not isinstance(self.value, str):
            raise TypeError(f"{self.name} must be a string")
        else:
            return self.value

    def verify_opt_path(self) -> Path | None:
        val = self.verify_opt_str()
        if val is None:
            return None
        path = Path(val)
        if not path.exists():
            raise FileNotFoundError(f"{self.name} does not exist")
        else:
            return path

    def verift_opt_str_as_str(self) -> str:
        ret = self.verify_opt_str()
        if ret is None:
            return ""
        return ret

    def verify_default_str(self, default: str) -> str:
        ret = self.verify_opt_str()
        if ret is None:
            return default
        return ret

    def verify_opt_int(self) -> int | None:
        if self.value is None:
            return None
        self.value = check_type_int(self.value)
        if not isinstance(self.value, int):
            raise TypeError(f"{self.name} must be an integer")
        else:
            return self.value

    def verify_default_int(self, default: int) -> int:
        ret = self.verify_opt_int()
        if ret is None:
            return default
        return ret

    def verify_opt_bool(self) -> bool | None:
        if self.value is None:
            return None
        self.value = check_type_bool(self.value)
        if not isinstance(self.value, bool):
            raise TypeError(f"{self.name} must be a boolean")
        else:
            return self.value

    def verify_default_bool(self, default: bool) -> bool:
        ret = self.verify_opt_bool()
        if ret is None:
            return default
        else:
            return ret

    def verify_opt_list(self) -> list | None:
        if self.value is None:
            return None
        self.value = check_type_list(self.value)
        if not (
            isinstance(self.value, list)
            or isinstance(self.value, tuple)
            or isinstance(self.value, set)
        ):
            raise TypeError(f"{self.name} must be a list")
        else:
            return list(self.value)

    def verify_opt_list_str(self) -> list[str] | None:
        verified_list = self.verify_opt_list()
        if verified_list is None:
            return None
        for item in verified_list:
            Verify(item, self.name).verify_str()
        return verified_list

    def verify_opt_list_int(self) -> list[int] | None:
        verified_list = self.verify_opt_list()
        if verified_list is None:
            return None
        for item in verified_list:
            Verify(item, self.name).verify_int()
        return verified_list

    def verify_opt_list_bool(self) -> list[bool] | None:
        verified_list = self.verify_opt_list()
        if verified_list is None:
            return None
        for item in verified_list:
            Verify(item, self.name).verify_bool()
        return verified_list

    def verify_opt_list_dict(self) -> list[dict] | None:
        verified_list = self.verify_opt_list()
        if verified_list is None:
            return None
        for item in verified_list:
            Verify(item, self.name).verify_dict()
        return verified_list

    def verify_opt_list_str_as_list(self) -> list[str]:
        ret = self.verify_opt_list_str()
        if ret is None:
            return []
        return ret

    def verify_opt_list_int_as_list(self) -> list[int]:
        ret = self.verify_opt_list_int()
        if ret is None:
            return []
        return ret

    def verify_opt_list_bool_as_list(self) -> list[bool]:
        ret = self.verify_opt_list_bool()
        if ret is None:
            return []
        return ret

    def verify_opt_list_dict_as_list(self) -> list[dict]:
        ret = self.verify_opt_list_dict()
        if ret is None:
            return []
        return ret

    def verify_opt_dict(self) -> dict | None:
        if self.value is None:
            return None
        self.value = check_type_dict(self.value)
        if not isinstance(self.value, dict):
            raise TypeError(f"{self.name} must be a dict")
        else:
            return self.value

    def verify_str(self) -> str:
        if self.value is None:
            raise AttributeError(f"{self.name} must not be None")
        self.value = check_type_str(self.value)
        if not isinstance(self.value, str):
            raise TypeError(f"{self.name} must be a string")
        else:
            return self.value

    def verify_path(self) -> Path:
        path = Path(self.verify_str())
        if not path.exists():
            raise FileNotFoundError(f"{self.name} does not exist")
        else:
            return path

    def verify_int(self) -> int:
        if self.value is None:
            raise AttributeError(f"{self.name} must not be None")
        self.value = check_type_int(self.value)
        if not isinstance(self.value, int):
            raise TypeError(f"{self.name} must be an integer")
        else:
            return self.value

    def verify_bool(self) -> bool:
        if self.value is None:
            raise AttributeError(f"{self.name} must not be None")
        self.value = check_type_bool(self.value)
        if not isinstance(self.value, bool):
            raise TypeError(f"{self.name} must be a boolean")
        else:
            return self.value

    def verify_list(self) -> list:
        if self.value is None:
            raise AttributeError(f"{self.name} must not be None")
        self.value = check_type_list(self.value)
        if not (
            isinstance(self.value, list)
            or isinstance(self.value, tuple)
            or isinstance(self.value, set)
        ):
            raise TypeError(f"{self.name} must be a list")
        else:
            return list(self.value)

    def verify_list_str(self) -> list[str]:
        verified_list = self.verify_list()
        for item in verified_list:
            Verify(item, self.name).verify_str()
        return verified_list

    def verify_list_int(self) -> list[int]:
        verified_list = self.verify_list()
        for item in verified_list:
            Verify(item, self.name).verify_int()
        return verified_list

    def verify_list_bool(self) -> list[bool]:
        verified_list = self.verify_list()
        for item in verified_list:
            Verify(item, self.name).verify_bool()
        return verified_list

    def verify_list_dict(self) -> list[dict]:
        verified_list = self.verify_list()
        for item in verified_list:
            Verify(item, self.name).verify_dict()
        return verified_list

    def verify_dict(self) -> dict:
        if self.value is None:
            raise AttributeError(f"{self.name} must not be None")
        self.value = check_type_dict(self.value)
        if not isinstance(self.value, dict):
            raise TypeError(f"{self.name} must be a dict")
        else:
            return self.value

    def verify_opt_content(self) -> str | None:
        if self.value is None:
            return None
        self.value = check_type_str(self.value)
        if not isinstance(self.value, str):
            raise TypeError(f"{self.name} should be a base64 encoded string")

        content = b64decode(self.value)
        header = []
        for i in range(0, 6):
            header.append(bytes([list(content)[i]]))
        return decode_file(content, header)

    def verify_opt_content_as_path(self) -> Path | None:
        val = self.verify_opt_content()
        if val is None:
            return None
        path = Path(val)
        if not path.exists():
            raise FileNotFoundError(f"{self.name} does not exist")
        return path

    def verify_content(self) -> str:
        if self.value is None:
            raise AttributeError(f"{self.name} must be defined")
        self.value = check_type_str(self.value)
        if not isinstance(self.value, str):
            raise TypeError(f"{self.name} should be a base64 encoded string")
        content = b64decode(self.value)
        header = []
        for i in range(0, 6):
            header.append(bytes([list(content)[i]]))
        return decode_file(content, header)

    def verify_content_as_path(self) -> Path:
        path = Path(self.verify_content())
        if not path.exists():
            raise FileNotFoundError(f"{self.name} does not exist")
        else:
            return path
