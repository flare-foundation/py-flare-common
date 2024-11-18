import pytest

from py_flare_common.b58.flare_b58 import flare_b58_decode_check, flare_b58_encode_check


@pytest.mark.parametrize(
    "v, expected", [
        (bytes.fromhex("92d2c7775a20416d70c987a8c6c7c756146460bb"), "EPLACd344ouymyJAQYXZBvbmU3NJ6ooeB"),
        (bytes.fromhex("9bead17f7138bc0b25a56585efb9b67b32760278"), "FDR3CXdwP3H3Zz9QKfL61fk56zkPEgdFV"),
        (bytes.fromhex("0824b9b47ef6f99c26bc10dd042ef35aa69f16ed"), "k4QG8eJ9bYu717nbj8Ki8VykK8g1VWK9"),
        (bytes.fromhex("0389d94ae54c777090a5d44844631b7868eefabc"), "KiAUisCU8UvXGnMRiUvoeyWneSdUm987"),
    ]
)  # fmt: skip
def test_flare_b58_encode_check(v, expected):
    encoded = flare_b58_encode_check(v).decode()
    assert encoded == expected


@pytest.mark.parametrize(
    "v, expected", [
        (b"EPLACd344ouymyJAQYXZBvbmU3NJ6ooeB", "92d2c7775a20416d70c987a8c6c7c756146460bb"),
        (b"FDR3CXdwP3H3Zz9QKfL61fk56zkPEgdFV", "9bead17f7138bc0b25a56585efb9b67b32760278"),
        (b"k4QG8eJ9bYu717nbj8Ki8VykK8g1VWK9", "0824b9b47ef6f99c26bc10dd042ef35aa69f16ed"),
        (b"KiAUisCU8UvXGnMRiUvoeyWneSdUm987", "0389d94ae54c777090a5d44844631b7868eefabc"),
    ]
)  # fmt: skip
def test_flare_b58_decode_check(v, expected):
    encoded = flare_b58_decode_check(v).hex()
    assert encoded == expected


@pytest.mark.parametrize(
    "v", [
        (b"EPLACd344ouymyJAQYXZBvbmU3NJ6ooeC"),
        (b"FDR3CXdwP3H3Zz9QKfL61fk56zkPEgdFX"),
        (b"k4QG8eJ9bYu717nbj8Ki8VykK8g1VWK8"),
        (b"KiAUisCU8UvXGnMRiUvoeyWneSdUm983"),
    ]
)  # fmt: skip
def test_flare_b58_decode_check_invalid_checksum(v):
    with pytest.raises(ValueError):
        flare_b58_decode_check(v)
