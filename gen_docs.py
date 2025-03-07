import os
from pathlib import Path
from pprint import pprint
import importlib
from typing import List, Tuple


def filter_dir(base_dir) -> tuple[list[str], list[Path]]:
    files = []
    dirs = []
    for file in Path(base_dir).iterdir():
        if file.is_file() and file.suffix == ".py" and not file.name.startswith("__"):
            files.append(
                str(file.relative_to(Path(os.path.dirname(__file__))))
                .replace("/", ".")
                .replace(".py", "")
            )
        if file.is_dir() and not file.name.startswith("__"):
            dirs.append(file)
    return files, dirs


def write_doc(doc: str, plug: str, module):
    frag_name = doc.lower()
    try:
        document = eval(f"module.{doc}.documentation()")
    except Exception as e:
        print(f"Failed to generate documentation for {doc} in {plug}")
        print(e)
        return
    document = document.replace('"', "'")
    document = "\n".join([f"      {line}" for line in document.split("\n")])
    with open(
        f"{os.path.dirname(__file__)}/plugins/doc_fragments/{frag_name}.py", "w"
    ) as f:
        f.write(f'''
class ModuleDocFragment(object):
    DOCUMENTATION = r"""
    options:
{document}
    """
            ''')
    return


def get_all_dirs(dirs: List[Path], plugins: List[str]) -> Tuple[List[str], List[Path]]:
    more_dirs = []
    for dir in dirs:
        nested_plugins, this_dir = filter_dir(dir)
        more_dirs.extend(this_dir)
        plugins.extend(nested_plugins)
    if len(more_dirs) > 0:
        plugins, dirs = get_all_dirs(more_dirs, plugins)
    return plugins, dirs


def main():
    plugins: List[str] = []
    directories = []
    base_dir = Path(f"{os.path.dirname(__file__)}/plugins/module_utils")
    directories.append(base_dir)
    plugins, directories = get_all_dirs(directories, plugins)

    print("## Plugins")
    pprint(plugins)

    print("## Dirs")
    pprint(directories)

    for plug in plugins:
        module = importlib.import_module(plug)
        for name, cls in module.__dict__.items():
            if (
                isinstance(cls, type)
                and hasattr(cls, "documentation")
                and callable(getattr(cls, "documentation"))
            ):
                write_doc(cls.__name__, plug, module)


if __name__ == "__main__":
    main()
