# Copyright: Hallux team, 2023
import pytest


def pytest_addoption(parser):
    parser.addoption("--real-openai-test", dest="real_test", action="store_true", default=False)


@pytest.fixture(scope="session")
def real_openai_test(pytestconfig):
    return pytestconfig.getoption("real_test")
