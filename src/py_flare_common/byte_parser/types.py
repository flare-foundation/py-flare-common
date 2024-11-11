from typing import Generic, TypeVar

from attrs import frozen

T = TypeVar("T")
U = TypeVar("U")


@frozen
class ParsedPayload(Generic[T]):
    protocol_id: int
    voting_round_id: int
    size: int
    payload: T


@frozen
class ParsedMessage(Generic[T, U]):
    fdc: ParsedPayload[U] | None
    ftso: ParsedPayload[T] | None


# Auxiliary types
@frozen
class Message:
    protocol_id: int
    random_quality_score: int
    merkle_root: str


@frozen
class Signature:
    v: str
    r: str
    s: str


# Types for FTSO protocol
@frozen
class FTSOS1:
    commit_hash: bytes


@frozen
class FTSOS2:
    random: int
    values: list[int | None]


@frozen
class FTSOSS:
    type: int
    message: Message
    signature: Signature


# Types for FDC protocol
@frozen
class FDCS1:
    pass


@frozen
class FDCS2:
    pass


@frozen
class FDCSS:
    pass
