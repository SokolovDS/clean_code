from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set


class OutOfStock(Exception):
    pass


def allocate(order_line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(order_line))
    except StopIteration as e:
        raise OutOfStock(f'Артикула {order_line.sku} нет в наличии') from e

    batch.allocate(order_line)
    return batch.reference


class NotAllocated(Exception):
    pass


def deallocate(order_line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if order_line in b._allocations)
    except StopIteration as e:
        raise NotAllocated(f'Заказ {order_line.sku} не размещён ни в одной партии') from e

    batch.deallocate(order_line)
    return batch.reference


@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta

        self._purchased_quantity = qty
        self._allocations: Set[OrderLine] = set()

    def __repr__(self):
        return f"<Batch {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, order_line: OrderLine):
        if self.can_allocate(order_line):
            self._allocations.add(order_line)

    def deallocate(self, order_line: OrderLine):
        if order_line in self._allocations:
            self._allocations.remove(order_line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, order_line: OrderLine) -> bool:
        return self.sku == order_line.sku \
            and self.available_quantity >= order_line.qty \
            and order_line not in self._allocations


class Product:
    def __init__(self, sku, batches):
        self.sku = sku
        self.batches: List[Batch] = batches

    def allocate(self, order_line: OrderLine) -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(order_line))
        except StopIteration as e:
            raise OutOfStock(f'Артикула {order_line.sku} нет в наличии') from e

        batch.allocate(order_line)
        return batch.reference
