import json
import os


def main():
    with open("failed.json", "r") as f:
        failed = json.load(f)
    dir = os.curdir + "/failed"
    os.makedirs(dir, exist_ok=True)
    for req, data in failed["requests"].items():
        name = ""
        for i in req:
            if i.isalnum():
                name += i
        with open(f"{dir}/{name}.json", "w") as f:
            json.dump(
                obj={"request": data, "response": failed["responses"][req] or None},
                fp=f,
                ensure_ascii=True,
                indent=4,
                sort_keys=True,
            )


if __name__ == "__main__":
    main()
