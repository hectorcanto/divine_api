# alembic/hooks.py
import logging
from pathlib import Path
import subprocess


logger = logging.getLogger(__name__)


def ruff_post_write(revision_path: str, **kwargs) -> None:
    """
    Run ruff on the newly generated Alembic migration.

    :param revision_path: path to the new migration file
    """
    path = Path(revision_path)
    if path.exists():
        logger.info(f"Running ruff on {path}")
        subprocess.run(["ruff", "check", "--fix", str(path)], check=False)
        subprocess.run(["ruff", "format", str(path)], check=False)
