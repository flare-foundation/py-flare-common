# payment reference format (32 bytes):
# instruction id consists of instruction type (4 bits) and instruction command (4 bits)

# FXRP (instruction type 0)
# bytes 00: bytes1 (hex) -> instruction id
#     00: collateral reservation
#     01: transfer
#     02: redeem
# bytes 01: uint8 -> wallet identifier
# collateral reservation:
# bytes 02-11: uint80 -> value (lots)
# bytes 12-13: uint16 -> agent vault address id (collateral reservation)
# transfer:
# bytes 02-11: uint80 -> value (amount in drops)
# bytes 12-31: address (20 bytes) -> recipient address
# redeem:
# bytes 02-11: uint80 -> value (lots)

# Firelight vaults (instruction type 1)
# bytes 00: bytes1 (hex) -> instruction id
#     10: collateral reservation and deposit
#     11: deposit
#     12: redeem
#     13: claim withdraw
# bytes 01: uint8 -> wallet identifier
# collateral reservation and deposit:
# bytes 02-11: uint80 -> value (lots)
# bytes 12-13: uint16 -> agent vault address id
# bytes 14-15: uint16 -> deposit vault address id
# deposit:
# bytes 02-11: uint80 -> value (assets in drops)
# bytes 14-15: uint16 -> deposit vault address id
# redeem:
# bytes 02-11: uint80 -> value (shares in drops)
# bytes 14-15: uint16 -> withdraw vault address id
# claim withdraw:
# bytes 02-11: uint80 -> value (period)
# bytes 14-15: uint16 -> withdraw vault address id

# Upshift vaults (instruction type 2)
# bytes 00: bytes1 (hex) -> instruction id
#     20: collateral reservation and deposit
#     21: deposit
#     22: requestRedeem
#     23: claim
# bytes 01: uint8 -> wallet identifier
# collateral reservation and deposit:
# bytes 02-11: uint80 -> value (lots)
# bytes 12-13: uint16 -> agent vault address id
# bytes 14-15: uint16 -> deposit vault address id
# deposit:
# bytes 02-11: uint80 -> value (assets in drops)
# bytes 14-15: uint16 -> deposit vault address id
# requestRedeem:
# bytes 02-11: uint80 -> value (shares in drops)
# bytes 14-15: uint16 -> withdraw vault address id
# claim:
# bytes 02-11: uint80 -> value (date(yyyymmdd))
# bytes 14-15: uint16 -> withdraw vault address id

import abc
import datetime
from typing import ClassVar, Self

import attrs
from eth_typing import ChecksumAddress
from eth_utils.address import to_checksum_address

from py_flare_common.smart_accounts.encoder import exceptions, validators


class InstructionAbc(abc.ABC):
    INSTRUCTION_ID: ClassVar[int]

    @abc.abstractmethod
    def encode(self) -> bytes: ...

    @classmethod
    @abc.abstractmethod
    def decode(cls, b: bytes | str) -> Self: ...


@attrs.frozen
class FxrpCollateralReservation(InstructionAbc):
    INSTRUCTION_ID = 0x00

    wallet_id: int = attrs.field(validator=validators.make_uint_validator(8))
    value: int = attrs.field(validator=validators.make_uint_validator(80))
    agent_vault_id: int = attrs.field(validator=validators.make_uint_validator(16))

    def encode(self) -> bytes:
        b = bytearray(32)
        b[0] = self.INSTRUCTION_ID
        b[1] = self.wallet_id
        b[2:12] = self.value.to_bytes(10, "big")
        b[12:14] = self.agent_vault_id.to_bytes(2, "big")
        return bytes(b)

    @classmethod
    def decode(cls, b: bytes | str) -> Self:
        b = validators.clean_str_or_bytes(b)
        validators.validate_len_and_instruction_id(b, cls.INSTRUCTION_ID)

        wallet_id = b[1]
        value = int.from_bytes(b[2:12], "big")
        agent_vault_id = int.from_bytes(b[12:14], "big")

        try:
            return cls(
                wallet_id=wallet_id,
                value=value,
                agent_vault_id=agent_vault_id,
            )
        except exceptions.EncodeError as e:
            raise exceptions.DecodeError("invalid instruction") from e


@attrs.frozen
class FxrpTransfer(InstructionAbc):
    INSTRUCTION_ID = 0x01

    wallet_id: int = attrs.field(validator=validators.make_uint_validator(8))
    value: int = attrs.field(validator=validators.make_uint_validator(80))
    recipient_address: ChecksumAddress = attrs.field(
        validator=validators.checksum_address_validator
    )

    def encode(self) -> bytes:
        if len(self.recipient_address) != 42:
            raise exceptions.EncodeError("recipient_address must be 20 bytes")

        b = bytearray(32)
        b[0] = self.INSTRUCTION_ID
        b[1] = self.wallet_id
        b[2:12] = self.value.to_bytes(10, "big")
        b[12:32] = bytes.fromhex(self.recipient_address.removeprefix("0x"))
        return bytes(b)

    @classmethod
    def decode(cls, b: bytes | str) -> Self:
        b = validators.clean_str_or_bytes(b)
        validators.validate_len_and_instruction_id(b, cls.INSTRUCTION_ID)

        wallet_id = b[1]
        value = int.from_bytes(b[2:12], "big")
        recipient_address = to_checksum_address(b[12:32].hex())

        try:
            return cls(
                wallet_id=wallet_id,
                value=value,
                recipient_address=recipient_address,
            )
        except exceptions.EncodeError as e:
            raise exceptions.DecodeError("invalid instruction") from e


@attrs.frozen
class FxrpRedeem(InstructionAbc):
    INSTRUCTION_ID = 0x02

    wallet_id: int = attrs.field(validator=validators.make_uint_validator(8))
    value: int = attrs.field(validator=validators.make_uint_validator(80))

    def encode(self) -> bytes:
        b = bytearray(32)
        b[0] = self.INSTRUCTION_ID
        b[1] = self.wallet_id
        b[2:12] = self.value.to_bytes(10, "big")
        return bytes(b)

    @classmethod
    def decode(cls, b: bytes | str) -> Self:
        b = validators.clean_str_or_bytes(b)
        if len(b) != 32:
            raise exceptions.DecodeError("must be 32 bytes")

        if b[0] != cls.INSTRUCTION_ID:
            raise exceptions.DecodeError("invalid instruction id")

        wallet_id = b[1]
        value = int.from_bytes(b[2:12], "big")

        try:
            return cls(
                wallet_id=wallet_id,
                value=value,
            )
        except exceptions.EncodeError as e:
            raise exceptions.DecodeError("invalid instruction") from e


@attrs.frozen
class FirelightCollateralReservationAndDeposit(InstructionAbc):
    INSTRUCTION_ID = 0x10

    wallet_id: int = attrs.field(validator=validators.make_uint_validator(8))
    value: int = attrs.field(validator=validators.make_uint_validator(80))
    agent_vault_id: int = attrs.field(validator=validators.make_uint_validator(16))
    vault_id: int = attrs.field(validator=validators.make_uint_validator(16))

    def encode(self) -> bytes:
        b = bytearray(32)
        b[0] = self.INSTRUCTION_ID
        b[1] = self.wallet_id
        b[2:12] = self.value.to_bytes(10, "big")
        b[12:14] = self.agent_vault_id.to_bytes(2, "big")
        b[14:16] = self.vault_id.to_bytes(2, "big")
        return bytes(b)

    @classmethod
    def decode(cls, b: bytes | str) -> Self:
        b = validators.clean_str_or_bytes(b)
        if len(b) != 32:
            raise exceptions.DecodeError("must be 32 bytes")

        if b[0] != cls.INSTRUCTION_ID:
            raise exceptions.DecodeError("invalid instruction id")

        wallet_id = b[1]
        value = int.from_bytes(b[2:12], "big")
        agent_vault_id = int.from_bytes(b[12:14], "big")
        vault_id = int.from_bytes(b[14:16], "big")

        try:
            return cls(
                wallet_id=wallet_id,
                value=value,
                agent_vault_id=agent_vault_id,
                vault_id=vault_id,
            )
        except exceptions.EncodeError as e:
            raise exceptions.DecodeError("invalid instruction") from e


@attrs.frozen
class FirelightDeposit(InstructionAbc):
    INSTRUCTION_ID = 0x11

    wallet_id: int = attrs.field(validator=validators.make_uint_validator(8))
    value: int = attrs.field(validator=validators.make_uint_validator(80))
    vault_id: int = attrs.field(validator=validators.make_uint_validator(16))

    def encode(self) -> bytes:
        b = bytearray(32)
        b[0] = self.INSTRUCTION_ID
        b[1] = self.wallet_id
        b[2:12] = self.value.to_bytes(10, "big")
        b[14:16] = self.vault_id.to_bytes(2, "big")
        return bytes(b)

    @classmethod
    def decode(cls, b: bytes | str) -> Self:
        b = validators.clean_str_or_bytes(b)
        if len(b) != 32:
            raise exceptions.DecodeError("must be 32 bytes")

        if b[0] != cls.INSTRUCTION_ID:
            raise exceptions.DecodeError("invalid instruction id")

        wallet_id = b[1]
        value = int.from_bytes(b[2:12], "big")
        vault_id = int.from_bytes(b[14:16], "big")

        try:
            return cls(
                wallet_id=wallet_id,
                value=value,
                vault_id=vault_id,
            )
        except exceptions.EncodeError as e:
            raise exceptions.DecodeError("invalid instruction") from e


@attrs.frozen
class FirelightRedeem(InstructionAbc):
    INSTRUCTION_ID = 0x12

    wallet_id: int = attrs.field(validator=validators.make_uint_validator(8))
    value: int = attrs.field(validator=validators.make_uint_validator(80))
    vault_id: int = attrs.field(validator=validators.make_uint_validator(16))

    def encode(self) -> bytes:
        b = bytearray(32)
        b[0] = self.INSTRUCTION_ID
        b[1] = self.wallet_id
        b[2:12] = self.value.to_bytes(10, "big")
        b[14:16] = self.vault_id.to_bytes(2, "big")
        return bytes(b)

    @classmethod
    def decode(cls, b: bytes | str) -> Self:
        b = validators.clean_str_or_bytes(b)
        if len(b) != 32:
            raise exceptions.DecodeError("must be 32 bytes")

        if b[0] != cls.INSTRUCTION_ID:
            raise exceptions.DecodeError("invalid instruction id")

        wallet_id = b[1]
        value = int.from_bytes(b[2:12], "big")
        vault_id = int.from_bytes(b[14:16], "big")

        try:
            return cls(
                wallet_id=wallet_id,
                value=value,
                vault_id=vault_id,
            )
        except exceptions.EncodeError as e:
            raise exceptions.DecodeError("invalid instruction") from e


@attrs.frozen
class FirelightClaimWithdraw(InstructionAbc):
    INSTRUCTION_ID = 0x13

    wallet_id: int = attrs.field(validator=validators.make_uint_validator(8))
    value: int = attrs.field(validator=validators.make_uint_validator(80))
    vault_id: int = attrs.field(validator=validators.make_uint_validator(16))

    def encode(self) -> bytes:
        b = bytearray(32)
        b[0] = self.INSTRUCTION_ID
        b[1] = self.wallet_id
        b[2:12] = self.value.to_bytes(10, "big")
        b[14:16] = self.vault_id.to_bytes(2, "big")
        return bytes(b)

    @classmethod
    def decode(cls, b: bytes | str) -> Self:
        b = validators.clean_str_or_bytes(b)
        if len(b) != 32:
            raise exceptions.DecodeError("must be 32 bytes")

        if b[0] != cls.INSTRUCTION_ID:
            raise exceptions.DecodeError("invalid instruction id")

        wallet_id = b[1]
        value = int.from_bytes(b[2:12], "big")
        vault_id = int.from_bytes(b[14:16], "big")

        try:
            return cls(
                wallet_id=wallet_id,
                value=value,
                vault_id=vault_id,
            )
        except exceptions.EncodeError as e:
            raise exceptions.DecodeError("invalid instruction") from e


@attrs.frozen
class UpshiftCollateralReservationAndDeposit(InstructionAbc):
    INSTRUCTION_ID = 0x20

    wallet_id: int = attrs.field(validator=validators.make_uint_validator(8))
    value: int = attrs.field(validator=validators.make_uint_validator(80))
    agent_vault_id: int = attrs.field(validator=validators.make_uint_validator(16))
    vault_id: int = attrs.field(validator=validators.make_uint_validator(16))

    def encode(self) -> bytes:
        b = bytearray(32)
        b[0] = self.INSTRUCTION_ID
        b[1] = self.wallet_id
        b[2:12] = self.value.to_bytes(10, "big")
        b[12:14] = self.agent_vault_id.to_bytes(2, "big")
        b[14:16] = self.vault_id.to_bytes(2, "big")
        return bytes(b)

    @classmethod
    def decode(cls, b: bytes | str) -> Self:
        b = validators.clean_str_or_bytes(b)
        if len(b) != 32:
            raise exceptions.DecodeError("must be 32 bytes")

        if b[0] != cls.INSTRUCTION_ID:
            raise exceptions.DecodeError("invalid instruction id")

        wallet_id = b[1]
        value = int.from_bytes(b[2:12], "big")
        agent_vault_id = int.from_bytes(b[12:14], "big")
        vault_id = int.from_bytes(b[14:16], "big")

        try:
            return cls(
                wallet_id=wallet_id,
                value=value,
                agent_vault_id=agent_vault_id,
                vault_id=vault_id,
            )
        except exceptions.EncodeError as e:
            raise exceptions.DecodeError("invalid instruction") from e


@attrs.frozen
class UpshiftDeposit(InstructionAbc):
    INSTRUCTION_ID = 0x21

    wallet_id: int = attrs.field(validator=validators.make_uint_validator(8))
    value: int = attrs.field(validator=validators.make_uint_validator(80))
    vault_id: int = attrs.field(validator=validators.make_uint_validator(16))

    def encode(self) -> bytes:
        b = bytearray(32)
        b[0] = self.INSTRUCTION_ID
        b[1] = self.wallet_id
        b[2:12] = self.value.to_bytes(10, "big")
        b[14:16] = self.vault_id.to_bytes(2, "big")
        return bytes(b)

    @classmethod
    def decode(cls, b: bytes | str) -> Self:
        b = validators.clean_str_or_bytes(b)
        if len(b) != 32:
            raise exceptions.DecodeError("must be 32 bytes")

        if b[0] != cls.INSTRUCTION_ID:
            raise exceptions.DecodeError("invalid instruction id")

        wallet_id = b[1]
        value = int.from_bytes(b[2:12], "big")
        vault_id = int.from_bytes(b[14:16], "big")

        try:
            return cls(
                wallet_id=wallet_id,
                value=value,
                vault_id=vault_id,
            )
        except exceptions.EncodeError as e:
            raise exceptions.DecodeError("invalid instruction") from e


@attrs.frozen
class UpshiftRequestRedeem(InstructionAbc):
    INSTRUCTION_ID = 0x22

    wallet_id: int = attrs.field(validator=validators.make_uint_validator(8))
    value: int = attrs.field(validator=validators.make_uint_validator(80))
    vault_id: int = attrs.field(validator=validators.make_uint_validator(16))

    def encode(self) -> bytes:
        b = bytearray(32)
        b[0] = self.INSTRUCTION_ID
        b[1] = self.wallet_id
        b[2:12] = self.value.to_bytes(10, "big")
        b[14:16] = self.vault_id.to_bytes(2, "big")
        return bytes(b)

    @classmethod
    def decode(cls, b: bytes | str) -> Self:
        b = validators.clean_str_or_bytes(b)
        if len(b) != 32:
            raise exceptions.DecodeError("must be 32 bytes")

        if b[0] != cls.INSTRUCTION_ID:
            raise exceptions.DecodeError("invalid instruction id")

        wallet_id = b[1]
        value = int.from_bytes(b[2:12], "big")
        vault_id = int.from_bytes(b[14:16], "big")

        try:
            return cls(
                wallet_id=wallet_id,
                value=value,
                vault_id=vault_id,
            )
        except exceptions.EncodeError as e:
            raise exceptions.DecodeError("invalid instruction") from e


def date_to_yyyymmdd(date: datetime.date | int) -> int:
    if isinstance(date, int):
        return date

    return date.year * 10000 + date.month * 100 + date.day


def yyyymmdd_to_date(yyyymmdd: int | datetime.date) -> datetime.date:
    if isinstance(yyyymmdd, datetime.date):
        return yyyymmdd

    year = (yyyymmdd // 10000) % 10000
    month = (yyyymmdd // 100) % 100
    day = yyyymmdd % 100

    return datetime.date(year, month, day)


@attrs.frozen
class UpshiftClaim(InstructionAbc):
    INSTRUCTION_ID = 0x23

    wallet_id: int = attrs.field(validator=validators.make_uint_validator(8))
    value: datetime.date = attrs.field(converter=yyyymmdd_to_date)
    vault_id: int = attrs.field(validator=validators.make_uint_validator(16))

    def encode(self) -> bytes:
        b = bytearray(32)
        b[0] = self.INSTRUCTION_ID
        b[1] = self.wallet_id
        b[2:12] = date_to_yyyymmdd(self.value).to_bytes(10, "big")
        b[14:16] = self.vault_id.to_bytes(2, "big")
        return bytes(b)

    @classmethod
    def decode(cls, b: bytes | str) -> Self:
        b = validators.clean_str_or_bytes(b)
        if len(b) != 32:
            raise exceptions.DecodeError("must be 32 bytes")

        if b[0] != cls.INSTRUCTION_ID:
            raise exceptions.DecodeError("invalid instruction id")

        wallet_id = b[1]
        value = yyyymmdd_to_date(int.from_bytes(b[2:12], "big"))
        vault_id = int.from_bytes(b[14:16], "big")

        try:
            return cls(
                wallet_id=wallet_id,
                value=value,
                vault_id=vault_id,
            )
        except exceptions.EncodeError as e:
            raise exceptions.DecodeError("invalid instruction") from e


@attrs.frozen
class CustomInstruction(InstructionAbc):
    INSTRUCTION_ID = 0xFF

    wallet_id: int = attrs.field(validator=validators.make_uint_validator(8))
    call_hash: str = attrs.field(validator=validators.make_hexstr_validator(30))

    def encode(self) -> bytes:
        b = bytearray(32)
        b[0] = self.INSTRUCTION_ID
        b[1] = self.wallet_id
        b[2:32] = bytes.fromhex(self.call_hash.removeprefix("0x"))
        return bytes(b)

    @classmethod
    def decode(cls, b: bytes | str) -> Self:
        b = validators.clean_str_or_bytes(b)
        validators.validate_len_and_instruction_id(b, cls.INSTRUCTION_ID)

        wallet_id = b[1]
        call_hash = "0x" + b[2:32].hex()

        try:
            return cls(wallet_id=wallet_id, call_hash=call_hash)
        except exceptions.EncodeError as e:
            raise exceptions.DecodeError("invalid instruction") from e
