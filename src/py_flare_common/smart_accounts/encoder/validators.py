from collections.abc import Callable
from typing import Any

from eth_typing import ChecksumAddress
from eth_utils.address import to_checksum_address

from py_flare_common.smart_accounts.encoder import exceptions


def clean_str_or_bytes(s: str | bytes) -> bytes:
    if isinstance(s, bytes):
        return s

    try:
        return bytes.fromhex(s.removeprefix("0x"))
    except ValueError as e:
        raise exceptions.DecodeError(f"invalid hex string: {s}") from e


def make_uint_validator(bits: int) -> Callable[[Any, Any, int], None]:
    def validator(instance, attribute, value):
        max_value = (1 << bits) - 1

        if not isinstance(value, int):
            raise exceptions.EncodeError(f"{attribute.name} must be an integer")

        if not (0 <= value <= max_value):
            raise exceptions.EncodeError(
                f"{attribute.name} must be between 0 and {max_value} (inclusive)"
            )

    return validator


def checksum_address_validator(
    instance: Any, attribute: Any, value: ChecksumAddress
) -> None:
    try:
        to_checksum_address(value)
    except ValueError as e:
        raise exceptions.EncodeError(
            f"{attribute.name} must be a valid checksum address"
        ) from e


def validate_len_and_instruction_id(b: bytes, i: int) -> None:
    if len(b) != 32:
        raise exceptions.DecodeError(
            f"Instruction ID must be 32 bytes long, got {len(b)} bytes"
        )
    if i < 0 or i > 255:
        raise exceptions.DecodeError(
            f"Instruction index must be between 0 and 255, got {i}"
        )
