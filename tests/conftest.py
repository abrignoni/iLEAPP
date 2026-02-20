import sys
from pathlib import Path
import pytest

ILEAPP_ROOT = Path(__file__).parents[1]

# Ensure the iLEAPP root is on sys.path so `scripts.*` imports work
if str(ILEAPP_ROOT) not in sys.path:
    sys.path.insert(0, str(ILEAPP_ROOT))


@pytest.fixture(autouse=True)
def reset_context():
    """Isolate Context singleton state between every test."""
    from scripts.context import Context
    Context.clear()
    yield
    Context.clear()


@pytest.fixture
def ileapp_root():
    return ILEAPP_ROOT


def pytest_addoption(parser):
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Regenerate golden output files",
    )


@pytest.fixture
def update_golden(request):
    return request.config.getoption("--update-golden")
