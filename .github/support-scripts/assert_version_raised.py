import subprocess
import tomllib
import sys

def get_branch_version_from_git(branch: str) -> tuple[int, ...]:
    result = subprocess.run(
        ["git", "show", f"{branch}:pyproject.toml"],
        capture_output=True,
        text=True,
        check=True,
    )
    project_info = tomllib.loads(result.stdout)
    return tuple(map(int, project_info["project"]["version"].split(".")))

new_version = get_branch_version_from_git("HEAD")
main_version = get_branch_version_from_git("origin/main")

for index, name in enumerate(["major", "minor", "patch"]):
    if new_version[index] > main_version[index]:
        print(f"{name} version is raised")
        sys.exit(0)

print("Version has NOT been bumped!")
sys.exit(1)