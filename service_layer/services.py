from __future__ import annotations

from datetime import date
from typing import Optional

from adapters.repository import AbstractRepository
from adapters.session import AbstractSession
from domain import model
from domain.model import OrderLine


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date],
              repo: AbstractRepository, session: AbstractSession) -> None:
    repo.add(model.Batch(ref=ref, sku=sku, qty=qty, eta=eta))
    session.commit()


def allocate(orderid: str, sku: str, qty: int,
             repo: AbstractRepository, session: AbstractSession) -> str:
    line = OrderLine(orderid, sku, qty)
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f'Недопустимый артикул {line.sku}')
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def deallocate(orderid: str, sku: str, qty: int, repo: AbstractRepository, session: AbstractSession) -> str:
    line = OrderLine(orderid=orderid, sku=sku, qty=qty)
    batches = repo.list()
    batchref = model.deallocate(line, batches)
    session.commit()
    return batchref
