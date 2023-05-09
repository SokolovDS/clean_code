import pytest

from adapters.repository import FakeRepository
from adapters.session import FakeSession
from service_layer import services


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed


def test_allocate_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, repo,
                       session)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo,
                               session)
    assert result == "batch1"


def test_error_for_invalid_sku():
    repo = FakeRepository([])
    session = FakeSession()

    services.add_batch("b1", "AREALSKU", 100, None,
                       repo, session)

    with pytest.raises(services.InvalidSku, match="Недопустимый артикул NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10,
                          repo, session)


def test_commits():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "OMINOUS-MIRROR", 100, None, repo,
                       session)
    services.allocate("o1", "OMINOUS-MIRROR", 10, repo,
                      session)
    assert session.committed is True


def test_returns_deallocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, repo,
                       session)
    services.allocate("o1", "COMPLICATED-LAMP", 10, repo,
                      session)
    result = services.deallocate("o1", "COMPLICATED-LAMP", 10, repo, FakeSession())
    assert result == "b1"
