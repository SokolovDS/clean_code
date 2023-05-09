from datetime import date, timedelta

import pytest

from domain.model import Batch, OrderLine, allocate, OutOfStock

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_warehouse_batches_to_shipments():
    sku = "TABLE"
    latest = Batch(ref=1, sku=sku, qty=2, eta=date(2023, 3, 1))
    warehouse = Batch(ref=2, sku=sku, qty=2, eta=None)
    earliest = Batch(ref=3, sku=sku, qty=2, eta=date(2023, 1, 1))

    order_line = OrderLine(orderid="1", sku=sku, qty=2)

    allocate(order_line, [
        latest, warehouse, earliest
    ])
    assert latest.available_quantity == 2
    assert warehouse.available_quantity == 0
    assert earliest.available_quantity == 2


def test_prefers_earlier_batches():
    sku = "TABLE"

    latest = Batch(ref=1, sku=sku, qty=2, eta=date(2023, 3, 1))
    medium = Batch(ref=2, sku=sku, qty=2, eta=date(2023, 2, 1))
    earliest = Batch(ref=3, sku=sku, qty=2, eta=date(2023, 1, 1))

    order_line = OrderLine(orderid="1", sku=sku, qty=2)

    allocate(order_line, [
        latest, medium, earliest
    ])
    assert latest.available_quantity == 2
    assert medium.available_quantity == 2
    assert earliest.available_quantity == 0


def test_returns_allocated_batch_ref():
    sku = "TABLE"

    shipment_batch = Batch(ref="shipment-batch-ref", sku=sku, qty=2, eta=date(2023, 3, 1))
    in_stock_batch = Batch(ref="in-stock-batch-ref", sku=sku, qty=2, eta=None)
    order_line = OrderLine(orderid="1", sku=sku, qty=2)

    allocation = allocate(order_line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch('batch1', 'SMALL-FORK', 10, eta=today)
    allocate(OrderLine('order1', 'SMALL-FORK', 10), [batch])
    with pytest.raises(OutOfStock, match='SMALL-FORK'):
        allocate(OrderLine('order2', 'SMALL-FORK', 1), [batch])
