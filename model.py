from dataclasses import dataclass
from typing import List, Set


class OutOfStock(Exception):
    pass


@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(self, reference, sku, qty, eta):
        self.reference = reference
        self.sku = sku
        self._purchased_quantity = qty
        self.eta = eta

        self._allocations: Set[OrderLine] = set()

    @property
    def available_qty(self):
        return self._purchased_quantity - sum(map(lambda x: x.qty, self._allocations))

    def allocate(self, order_line: OrderLine):
        if self.can_allocate(order_line):
            self._allocations.add(order_line)

    def can_allocate(self, order_line: OrderLine) -> bool:
        return self.sku == order_line.sku \
            and self.available_qty >= order_line.qty \
            and order_line not in self._allocations

    def deallocate(self, order_line: OrderLine):
        if order_line in self._allocations:
            self._allocations.remove(order_line)

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


def allocate(order_line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(order_line))
    except StopIteration as e:
        raise OutOfStock(f'Артикула {order_line.sku} нет в наличии') from e

    batch.allocate(order_line)
    return batch.reference
