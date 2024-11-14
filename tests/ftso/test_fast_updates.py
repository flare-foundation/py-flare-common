import pytest

from py_flare_common.ftso.fast_updates import encode_update_array


@pytest.mark.parametrize("deltas", [[5, 10], [0], [], [1, 3, 1, 255]])
def test_encode_update_array_against_old_function(deltas):
    array = "".join(f"{i:08b}" for i in deltas)
    assert len(array) % 2 == 0
    update_array = [
        -int(array[u + 1]) if array[u] == "1" else int(array[u + 1])
        for u in range(0, len(array), 2)
    ]

    assert encode_update_array(deltas) == update_array


@pytest.mark.parametrize(
    "deltas, expected",
    [([14, 23, 255], [0, 0, -1, 0, 0, 1, 1, -1, -1, -1, -1, -1]), ([], [])],
)
def test_encode_update_array(deltas, expected):
    assert encode_update_array(deltas) == expected


@pytest.mark.parametrize(
    "deltas",
    [[14, 23, 256], [14, -1, 255], [-34, 23, 255], [0, 0, -1]],
)
def test_encode_update_array_wrong_input(deltas):
    with pytest.raises(ValueError):
        encode_update_array(deltas)
