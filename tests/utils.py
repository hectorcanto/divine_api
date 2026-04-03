import logging
import os
from pathlib import Path
import sys

from dotenv import load_dotenv
import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent.absolute()
logger = logging.getLogger(__name__)


# NOTE: not using pytest-dotenv as it is stale
def load_env(route: str | Path):
    """Load dot env from private vars

    Args:
        route: relative file route path starting from ROOT of project
    """

    in_ci = True if os.environ.get("GITLAB_CI", None) is not None else False
    if not in_ci and not load_dotenv(route, override=True):
        raise ImportError(f"`{route}` not available, need for instrumented tests")


def load_envs(file_route: str | Path = ".private/.test.env"):
    """Load dot env from private vars

    Use in pytest_configure in order to run as early as possible
    """
    full_path = PROJECT_ROOT / file_route
    load_env(full_path)


def configure_test_logging(warning_logs=(), info_logs=()):
    """Disabling verbose loggers"""
    # Default in pyproject:pytest:log_cli_level or warning
    logging.root.setLevel(os.environ.get("APP_LOG_LEVEL", logging.INFO))

    for log_name in warning_logs:
        logging.getLogger(log_name).setLevel("WARNING")
    for log_name in info_logs:
        logging.getLogger(log_name).setLevel("INFO")


def log_basic_conf(forbidden_words: list[str]):
    envs = "Environmental Vars:\n"
    for key, value in os.environ.items():
        if key.startswith("AHEAD_"):
            shown_value = value
            if any(word in key for word in forbidden_words):
                shown_value = "*****"
            envs += f"{key.strip('AHEAD_')}={shown_value}\n"

    stream_handler = logging.StreamHandler(sys.stdout)
    logging.root.addHandler(stream_handler)
    logging.root.info(envs)


def define_markers(config, extra: list[str] | None = None):
    """Define usual markers to avoid warnings running the test suite"""
    markers = [
        "smoke: basic tests",
        "unit: unitary tests",
        "integration: integration tests, needs docker-compose sometimes",
        "current: in development",
        "first: run first",
        "last: run last",
        "extensions: related to extension modules",
        "instrumented: tests that hit real services, to skip in CI",
    ]
    if extra:
        markers.extend(extra)

    for line in markers:
        config.addinivalue_line("markers", line)


def modify_item_markers(items, extra_folders: list[str] | None = None):
    """Add markers to tests depending on the folders they belong to

    Usage:
        pytest -m unit
        pytest -m "not integration"
    """
    folders = [
        "unit",
        "integration",
        "smoke",
        "instrumented",
    ]
    if extra_folders:
        folders.extend(extra_folders)
    for item in items:
        for folder in folders:
            if folder in item.nodeid:
                item.add_marker(getattr(pytest.mark, folder))
