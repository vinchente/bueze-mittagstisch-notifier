import json
import tomllib
import sys
from pathlib import Path

def get_branch_version(branch: Path) -> tuple[int, ...]:
    pyproject_toml = branch / "pyproject.toml"
    version_json = branch / "version.json"

    project_info = tomllib.loads(pyproject_toml.read_text(encoding="utf-8"))

    if "project" in project_info:
        return tuple(map(int, project_info["project"]["version"].split(".")))
    else:
        version_object = json.loads(version_json.read_text(encoding="utf-8"))
        return (
            version_object["major"],
            version_object["minor"],
            version_object["fix"],
        )


new_version_tuple = get_branch_version(Path("feature"))
target_version_tuple = get_branch_version(Path("main"))

for index, name in enumerate(["major", "minor", "fix"]):
    if new_version_tuple[index] > target_version_tuple[index]:
        print(f"{name} version is raised")
        sys.exit(0)

print("Versions are the same between current branch and main branch")
sys.exit(1)
