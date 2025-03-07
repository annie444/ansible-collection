import requests


def main():
    url = (
        "https://github.com/kanidm/kanidm/raw/refs/heads/master/proto/src/constants.rs"
    )
    response = requests.get(url)
    attrs = []
    for line in response.text.split("\n"):
        if "pub mod" in line:
            continue
        else:
            line = line.replace(";", "")
            line = line.replace("///", "##")
            line = line.replace("//", "#")
            line = line.replace("pub const ", "")
            line = line.replace("[&str 5]", "list[str]")
            line = line.replace("&str", "str")
            line = line.replace("String", "str")
            line = line.replace("i64", "int")
            line = line.replace("u64", "int")
            line = line.replace("usize", "int")
            line = line.replace("Duration::from_secs(", "timedelta(seconds=")
            line = line.replace(
                "use std::time::Duration", "from datetime import timedelta\nimport os"
            )
            line = line.replace("Duration", "timedelta")
            line = line.replace("#!", "###")
            if "env!" in line:
                line = line.replace("env!", "os.environ.get")
                line = line.replace(")", ', "")')
            if line.endswith("="):
                line = f"{line} \\"
            attrs.append(line)
    with open("./plugins/module_utils/kanidm/runner/attrs.py", "w") as f:
        f.write("\n".join(attrs))


if __name__ == "__main__":
    main()
