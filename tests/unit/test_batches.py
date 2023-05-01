from domain.model import Batch, OrderLine


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


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_qty == 18


def test_deallocation():
    batch, line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.allocate(line)
    batch.deallocate(line)
    assert batch.available_qty == 20


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_qty == 20
