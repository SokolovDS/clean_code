from __future__ import annotations

from datetime import date
from typing import Optional

from domain import model
from domain.model import OrderLine
from service_layer.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date],
              uow: AbstractUnitOfWork) -> None:
    uow.batches.add(model.Batch(ref=ref, sku=sku, qty=qty, eta=eta))
    uow.commit()


def allocate(orderid: str, sku: str, qty: int,
             uow: AbstractUnitOfWork) -> str:
    line = OrderLine(orderid, sku, qty)
    batches = uow.batches.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f'Недопустимый артикул {line.sku}')
    batchref = model.allocate(line, batches)
    uow.commit()
    return batchref


def deallocate(orderid: str, sku: str, qty: int,
               uow: AbstractUnitOfWork) -> str:
    line = OrderLine(orderid=orderid, sku=sku, qty=qty)
    batches = uow.batches.list()
    batchref = model.deallocate(line, batches)
    uow.commit()
    return batchref
