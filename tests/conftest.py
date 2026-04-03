from collections.abc import Iterator
from pathlib import Path

from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory
import pytest
from pytest_mock import (
    MockerFixture,
)

from divine.app_factory import create_app
from divine.dependencies import (
    inject_device_repo,
    inject_user_repo,
)
from divine.settings import get_settings
from divine.shared.auth import get_current_user
from divine.users.domain.repository_interface import BaseUserRepository
from divine.users.persistence.db_models import DbUser

from tests.factories.base_factory import BaseDbFactory
from tests.factories.phone_provider import MobileProvider
from tests.factories.size_provider import SizeProvider
from tests.utils import (
    configure_test_logging,
    define_markers,
    log_basic_conf,
    modify_item_markers,
)


# Get the current root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.absolute()
FORBIDDEN_WORDS = ["PASSWORD", "_KEY", "SECRET"]
# this env vars values won't be logged in pytest


# fake = Faker()
# fake.add_provider(SizeProvider)


@pytest.fixture
def test_name(request) -> Iterator[str]:
    """Shortcut to get the test_name to use as fixture, good for tracing problematic tests"""
    yield request.node.name


def pytest_configure(config):
    """General configuration between running the test suite"""

    configure_test_logging(info_logs=("asyncio", "blib2to3"))
    define_markers(
        config,
        extra=[  # remember to add them in modify_item_markers too
            "users: User domain related tests",
            "devices: Device domain related test",
        ],
    )
    log_basic_conf(FORBIDDEN_WORDS)
    BaseDbFactory.__faker__.add_provider(SizeProvider)
    BaseDbFactory.__faker__.add_provider(MobileProvider)
    ModelFactory.__faker__.add_provider(MobileProvider)


def pytest_collection_modifyitems(items):
    """Adds markers like unit, integration ... by folder name"""
    modify_item_markers(items, extra_folders=["users", "devices"])


@pytest.fixture(scope="session")
def test_settings():  # -> AppSettings
    yield get_settings()


@pytest.fixture(scope="session", name="mock_user_repo")
def mock_user_repo_fx(session_mocker: MockerFixture):
    yield session_mocker.MagicMock(spec=BaseUserRepository)


@pytest.fixture(scope="session", name="mock_device_repo")
def mock_device_repo_fx(session_mocker: MockerFixture):
    yield session_mocker.MagicMock(spec=BaseUserRepository)


@pytest.fixture(scope="session")
def test_client(mock_user_repo, mock_device_repo, session_mocker):
    test_app = create_app()
    # test_app.dependency_overrides[get_db] = get_test_db

    mock_user = session_mocker.MagicMock(spec=DbUser)
    mock_user.templated_id = 7777

    test_app.dependency_overrides[inject_user_repo] = lambda: mock_user_repo
    test_app.dependency_overrides[inject_device_repo] = lambda: mock_device_repo
    test_app.dependency_overrides[get_current_user] = lambda: mock_user

    # NOTE that this client is sync and meant for unit tests
    with TestClient(test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()
