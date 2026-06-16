import tomllib
from pathlib import Path


def get_version() -> str:
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"

    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

        return pyproject_data["project"]["version"]