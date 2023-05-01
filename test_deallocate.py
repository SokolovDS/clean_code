import pytest

import model
import services


def test_success_deallocate():
    line = model.OrderLine('o1', 'OMINOUS-MIRROR', 10)
    batch = model.Batch('b1', 'OMINOUS-MIRROR', 100, eta=None)
    batch.allocate(line)
    result = model.deallocate(line, [batch])
    assert result == "b1"


def test_deallocate_note_allocated():
    line = model.OrderLine('o1', 'OMINOUS-MIRROR', 10)
    batch = model.Batch('b1', 'OMINOUS-MIRROR', 100, eta=None)

    with pytest.raises(model.NotAllocated, match=f'Заказ {line.sku} не размещён ни в одной партии'):
        model.deallocate(line, [batch])
