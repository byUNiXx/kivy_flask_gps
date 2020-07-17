import pytest

from server.src.app import create_app
from server.src.extensions import db as _db


@pytest.fixture
def test_app():
    app = create_app("tests/config.py")

    test_client = app.test_client()

    with app.app_context():
        _db.create_all()
        yield test_client
        _db.session.close()
        _db.drop_all()
