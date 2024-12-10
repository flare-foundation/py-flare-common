import pytest

from py_flare_common.fdc.attestation_source import AttestationSource


@pytest.mark.parametrize(
    "source_id",
    [
        b"12345678901234567890123456789012",
        b"\x00" * 32,
        b"\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x00\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x00",
        bytes.fromhex(
            "7465737442544300000000000000000000000000000000000000000000000000"
        ),
    ],
)
def test_attestation_source_init(source_id):
    ats = AttestationSource(source_id)
    assert ats.source_id == source_id


@pytest.mark.parametrize(
    "source_id, representation",
    [
        (
            bytes.fromhex(
                "7465737442544300000000000000000000000000000000000000000000000000"
            ),
            "testBTC",
        ),
    ],
)
def test_representation(source_id, representation):
    ats = AttestationSource(source_id)
    assert ats.representation == representation


@pytest.mark.parametrize(
    "source_id, representation",
    [
        (
            bytes.fromhex(
                "7465737442544300000000000000000000000000000000000000000000000000"
            ),
            "testBTC",
        ),
        (
            bytes.fromhex(
                "74657374444f4745000000000000000000000000000000000000000000000000"
            ),
            "testDOGE",
        ),
        (
            bytes.fromhex(
                "7465737458525000000000000000000000000000000000000000000000000000"
            ),
            "testXRP",
        ),
    ],
)
def test_from_representation(source_id, representation):
    ats = AttestationSource.from_represenation(representation)
    assert ats.source_id == source_id


@pytest.mark.parametrize(
    "hexstr",
    [
        "7465737442544300000000000000000000000000000000000000000000000000",
    ],
)
def test_from_hexstr(hexstr):
    ats = AttestationSource.fromhex(hexstr)
    assert ats.source_id == bytes.fromhex(hexstr)
