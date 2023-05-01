from domain import model
from domain.model import OrderLine
from adapters.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f'Недопустимый артикул {line.sku}')

    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def deallocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    batchref = model.deallocate(line, batches)
    session.commit()
    return batchref
