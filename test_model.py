from datetime import date, timedelta

import pytest

from model import Batch, OrderLine, allocate, OutOfStock

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def make_batch_and_line(sku, batch_qty, line_qty) -> (Batch, OrderLine):
    batch = Batch("batch-001", sku, batch_qty, eta=None)
    order_line = OrderLine("order-123", sku, line_qty)
    return batch, order_line


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, order_line = make_batch_and_line("TABLE", 10, 2)
    batch.allocate(order_line)
    assert batch.available_qty == 8


def test_can_allocate_if_available_greater_than_required():
    batch, order_line = make_batch_and_line("TABLE", 10, 2)
    assert batch.can_allocate(order_line) is True


def test_cannot_allocate_if_available_smaller_than_required():
    batch, order_line = make_batch_and_line("TABLE", 2, 10)
    assert batch.can_allocate(order_line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, order_line = make_batch_and_line("TABLE", 2, 2)
    assert batch.can_allocate(order_line) is True


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
    assert batch.can_allocate(different_sku_line) is False


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_qty == 20


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_qty == 18


def test_prefers_warehouse_batches_to_shipments():
    sku = "TABLE"
    latest = Batch(reference=1, sku=sku, qty=2, eta=date(2023, 3, 1))
    warehouse = Batch(reference=2, sku=sku, qty=2, eta=None)
    earliest = Batch(reference=3, sku=sku, qty=2, eta=date(2023, 1, 1))

    order_line = OrderLine(order_id="1", sku=sku, qty=2)

    allocate(order_line, [
        latest, warehouse, earliest
    ])
    assert latest.available_qty == 2
    assert warehouse.available_qty == 0
    assert earliest.available_qty == 2


def test_prefers_earlier_batches():
    sku = "TABLE"

    latest = Batch(reference=1, sku=sku, qty=2, eta=date(2023, 3, 1))
    medium = Batch(reference=2, sku=sku, qty=2, eta=date(2023, 2, 1))
    earliest = Batch(reference=3, sku=sku, qty=2, eta=date(2023, 1, 1))

    order_line = OrderLine(order_id="1", sku=sku, qty=2)

    allocate(order_line, [
        latest, medium, earliest
    ])
    assert latest.available_qty == 2
    assert medium.available_qty == 2
    assert earliest.available_qty == 0


def test_returns_allocated_batch_ref():
    sku = "TABLE"

    shipment_batch = Batch(reference="shipment-batch-ref", sku=sku, qty=2, eta=date(2023, 3, 1))
    in_stock_batch = Batch(reference="in-stock-batch-ref", sku=sku, qty=2, eta=None)
    order_line = OrderLine(order_id="1", sku=sku, qty=2)

    allocation = allocate(order_line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch('batch1', 'SMALL-FORK', 10, eta=today)
    allocate(OrderLine('order1', 'SMALL-FORK', 10), [batch])
    with pytest.raises(OutOfStock, match='SMALL-FORK'):
        allocate(OrderLine('order2', 'SMALL-FORK', 1), [batch])
