import pytest

from py_flare_common.fdc.attestation_type import AttestatioType


@pytest.mark.parametrize(
    "attestation_type",
    [
        b"12345678901234567890123456789012",
        b"\x00" * 32,
        b"\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x00\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x00",
        bytes.fromhex(
            "4164647265737356616c69646974790000000000000000000000000000000000"
        ),
    ],
)
def test_attestation_type_init(attestation_type):
    at = AttestatioType(attestation_type)
    assert at.attestation_type == attestation_type


@pytest.mark.parametrize(
    "attestation_type, representation",
    [
        (
            bytes.fromhex(
                "4164647265737356616c69646974790000000000000000000000000000000000"
            ),
            "AddressValidity",
        ),
    ],
)
def test_representation(attestation_type, representation):
    at = AttestatioType(attestation_type)
    assert at.representation == representation


@pytest.mark.parametrize(
    "attestation_type, representation",
    [
        (
            bytes.fromhex(
                "4164647265737356616c69646974790000000000000000000000000000000000"
            ),
            "AddressValidity",
        ),
    ],
)
def test_from_representation(attestation_type, representation):
    at = AttestatioType.from_represenation(representation)
    assert at.attestation_type == attestation_type


@pytest.mark.parametrize(
    "hexstr",
    [
        "4164647265737356616c69646974790000000000000000000000000000000000",
    ],
)
def test_from_hexstr(hexstr):
    at = AttestatioType.fromhex(hexstr)
    assert at.attestation_type == bytes.fromhex(hexstr)
