import pytest
import shutil
from pathlib import Path


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--clear",
        action="store_true",
    )


@pytest.fixture(scope="session", autouse=True)
def clear_output(request):
    should_clear = request.config.getoption("--clear")
    path = Path("tests/output")
    if should_clear and path.exists():
        shutil.rmtree("tests/output")
        Path("tests/output").mkdir()
