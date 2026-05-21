import pytest


@pytest.fixture
def default_snake_body():
    return [(15, 15), (14, 15), (13, 15)]


@pytest.fixture
def empty_mines():
    return []
