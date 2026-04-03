from importlib.metadata import (
    PackageNotFoundError,
    version,
)


def get_version() -> str:
    try:
        return version("divine")  # must match [tool.poetry].name in pyproject.toml
    except PackageNotFoundError:
        return "unknown"
