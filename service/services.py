import datetime
from typing import Optional

from adapters.repository import AbstractRepository
from adapters.session import AbstractSession
from domain import model
from domain.model import OrderLine


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(orderid: str, sku: str, qty: int, repo: AbstractRepository, session: AbstractSession) -> str:
    batches = repo.list()

    line = OrderLine(orderid=orderid, sku=sku, qty=qty)
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f'Недопустимый артикул {line.sku}')

    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def deallocate(orderid: str, sku: str, qty: int, repo: AbstractRepository, session: AbstractSession) -> str:
    batches = repo.list()
    line = OrderLine(orderid=orderid, sku=sku, qty=qty)
    batchref = model.deallocate(line, batches)
    session.commit()
    return batchref


def add_batch(reference: str, sku: str, qty: int, eta: Optional[datetime.datetime],
              repo: AbstractRepository, session: AbstractSession) -> None:
    batch = model.Batch(reference=reference, sku=sku, qty=qty, eta=eta)
    repo.add(batch)
    session.commit()
