from typing import Callable

from py_flare_common.byte_parser.byte_parser import ByteParser
from py_flare_common.byte_parser.types import (
    FDCS1,
    FDCS2,
    FDCSS,
    FTSOS1,
    FTSOS2,
    FTSOSS,
    Message,
    ParsedMessage,
    ParsedPayload,
    Signature,
    T,
    U,
)
from py_flare_common.merkle.hexstr import to_bytes


def gen_parse(
    message: bytes | str,
    pid_100_parse: Callable[[bytes], T],
    pid_200_parse: Callable[[bytes], U],
) -> ParsedMessage[T, U]:
    kwargs: dict[str, ParsedPayload | None] = {"ftso": None, "fdc": None}
    message = to_bytes(message)
    bp = ByteParser(message)

    while not bp.is_empty():
        protocol_id = bp.uint8()
        voting_round_id = bp.uint32()
        payload_length = bp.uint16()
        payload = bp.next_n(payload_length)

        if protocol_id == 100:
            parsed = pid_100_parse(payload)
            kwargs["ftso"] = ParsedPayload(
                protocol_id, voting_round_id, payload_length, parsed
            )

        if protocol_id == 200:
            parsed = pid_200_parse(payload)
            kwargs["fdc"] = ParsedPayload(
                protocol_id, voting_round_id, payload_length, parsed
            )

    return ParsedMessage(**kwargs)


def parse_submit1(message: bytes | str) -> ParsedMessage[FTSOS1, FDCS1]:
    return gen_parse(message, ftso_submit1, fdc_submit1)


def parse_submit2(message: bytes | str) -> ParsedMessage[FTSOS2, FDCS2]:
    return gen_parse(message, ftso_submit2, fdc_submit2)


def parse_submit_signature(message: bytes | str) -> ParsedMessage[FTSOSS, FDCSS]:
    return gen_parse(message, ftso_submit_signature, fdc_submit_signature)


def ftso_submit1(payload: bytes) -> FTSOS1:
    assert len(payload.hex()) == 32
    return FTSOS1(payload)


def fdc_submit1(payload: bytes) -> FDCS1:
    raise Exception


def ftso_submit2(payload: bytes) -> FTSOS2:
    EMPTY_FEED_VALUE = "0" * 8

    bp = ByteParser(payload)
    random = bp.uint256()
    values: list[int | None] = []

    while not bp.is_empty():
        raw_value = bp.next_n(4).hex()
        value = int(raw_value, 16) - 2**31 if raw_value != EMPTY_FEED_VALUE else None
        values.append(value)

    return FTSOS2(random=random, values=values)


def fdc_submit2(payload: bytes) -> FDCS2: ...


def ftso_submit_signature(payload: bytes) -> FTSOSS:
    # Do I need to un_prefix_0x ?
    payload_bp = ByteParser(payload)
    type = payload_bp.uint8()
    message_to_parse = payload_bp.next_n(38)
    signature_to_parse = payload_bp.next_n(65)
    assert payload_bp.is_empty()

    message_bp = ByteParser(message_to_parse)
    protocol_id = message_bp.uint8()
    message_bp.next_n(4)
    random_quality_score = message_bp.uint8()
    merkle_root = message_bp.drain().hex()
    message = Message(
        protocol_id=protocol_id,
        random_quality_score=random_quality_score,
        merkle_root=merkle_root,
    )

    signature_bp = ByteParser(signature_to_parse)
    v = signature_bp.next_n(1).hex()
    r = signature_bp.next_n(32).hex()
    s = signature_bp.next_n(32).hex()
    assert signature_bp.is_empty()
    signature = Signature(v=v, r=r, s=s)

    return FTSOSS(
        type=type,
        message=message,
        signature=signature,
    )


def fdc_submit_signature(payload: bytes) -> FDCSS: ...
