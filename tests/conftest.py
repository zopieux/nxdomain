from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def testdir():
    return Path(__file__).parent.resolve()
