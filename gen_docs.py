import os
import sys
from pathlib import Path
from pprint import pprint
import importlib
from typing import List
from importlib import util


def import_from_path(module_name: str, file_path: str):
    spec = util.spec_from_file_location(module_name, file_path)
    assert spec is not None
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def filter_dir(base_dir) -> tuple[list[Path], list[Path]]:
    files = []
    dirs = []
    for file in Path(base_dir).iterdir():
        if file.is_file() and file.suffix == ".py" and not file.name.startswith("__"):
            files.append(file)
        if file.is_dir() and not file.name.startswith("__"):
            dirs.append(file)
    return files, dirs


def main():
    plugins: List[Path] = []
    directories = []
    base_dir = Path(f"{os.path.dirname(__file__)}/plugins/module_utils")
    directories.append(base_dir)
    base_files, base_dirs = filter_dir(base_dir)
    plugins.extend(base_files)
    directories.extend(base_dirs)

    for dir in base_dirs:
        files, _ = filter_dir(dir)
        plugins.extend(files)

    clean_plugins = []
    for plug in plugins:
        clean_plugins.append(plug.relative_to(Path(os.path.dirname(__file__))))

    plugin_imports = []
    for plug in clean_plugins:
        p = str(plug).replace("/", ".").replace(".py", "")
        plugin_imports.append(p)

    print("## Plugins")
    pprint(plugin_imports)

    print("## Dirs")
    pprint(directories)

    classes = {}
    for plug in plugin_imports:
        module = importlib.import_module(plug)
        classes[plug] = dict(
            [
                (name, cls)
                for name, cls in module.__dict__.items()
                if isinstance(cls, type)
            ]
        )

    print("## Classes")
    pprint(classes)

    gen_docs = []
    gen_mods = []

    for plug, classes in classes.items():
        module = importlib.import_module(plug)
        for class_obj in module.__dict__.values():
            if hasattr(class_obj, "documentation"):
                gen_mods.append(plug)
                gen_docs.append(class_obj.__name__)

    print("## Gen Docs")
    pprint(gen_docs)

    for doc, plug in zip(gen_docs, gen_mods):
        module = importlib.import_module(plug)
        frag_name = doc.lower()
        try:
            document = eval(f"module.{doc}.documentation(indentation=6)")
        except Exception as e:
            print(f"Failed to generate documentation for {doc} in {plug}")
            print(e)
            continue
        with open(
            f"{os.path.dirname(__file__)}/plugins/doc_fragments/{frag_name}.py", "w"
        ) as f:
            f.write(
                'class ModuleDocFragment(object):\n    DOCUMENTATION = r"""\n    options:\n'
            )
            f.write(document)
            f.write('\n    """\n')


if __name__ == "__main__":
    main()
