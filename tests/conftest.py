import pytest
import app as vulnlab

@pytest.fixture
def client(tmp_path, monkeypatch):

    # Creates a temporary database for tests
    test_db = tmp_path / "test.db"

    # Replace the real database to a test database
    monkeypatch.setattr(vulnlab, "DB", test_db)

    # Iniciates the temp database and configure it to use the tables from the real database
    vulnlab.init_db()
    vulnlab.app.config.update(TESTING=True)

    # Creates a test client and make it available to test
    with vulnlab.app.test_client() as test_client:
        yield test_client