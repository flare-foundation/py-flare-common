from typing import Callable

from attrs import Attribute, field, frozen


@frozen
class EpochFeed:
    @staticmethod
    def _length_validation(
        length: int,
    ) -> Callable[["EpochFeed", Attribute, bytes], None]:
        def validator(instance: "EpochFeed", attribute: Attribute, value: bytes):
            if len(value) != length:
                raise ValueError(f"{attribute.name} must have exactly {length} bytes.")

        return validator

    feed_id: bytes = field(validator=_length_validation(21))

    @property
    def representation(self) -> str:
        return self.feed_id[1:].decode().rstrip("\x00").strip()

    @property
    def type(self) -> int:
        return int(hex(self.feed_id[0]), 16)

    @classmethod
    def from_represenation_and_type(cls, type: int, representaion: str):
        encoded_type = type.to_bytes()
        encoded_rep = representaion.encode().ljust(20, b"\x00")

        return EpochFeed(encoded_type + encoded_rep)

    @classmethod
    def from_hexstr(cls, hexstr: str):
        return EpochFeed(bytes.fromhex(hexstr))
