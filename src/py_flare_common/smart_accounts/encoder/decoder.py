from collections.abc import Sequence
from typing import Self

from py_flare_common.smart_accounts.encoder import exceptions, instructions, validators


class Decoder:
    def __init__(
        self, instruction_types: Sequence[type[instructions.InstructionAbc]]
    ) -> None:
        self._instructions: dict[int, type[instructions.InstructionAbc]] = {}

        for instruction_cls in instruction_types:
            instruction_id = instruction_cls.INSTRUCTION_ID
            if instruction_id in self._instructions:
                raise ValueError(f"Duplicate instruction ID: {instruction_id}")

            self._instructions[instruction_id] = instruction_cls

    @classmethod
    def with_all_instructions(cls) -> Self:
        classes = [
            c
            for c in instructions.InstructionAbc.__subclasses__()
            if hasattr(c, "__attrs_attrs__")
        ]

        return cls(classes)

    def __contains__(self, instruction_cls: type[instructions.InstructionAbc]) -> bool:
        return instruction_cls.INSTRUCTION_ID in self._instructions

    def all(self) -> Sequence[type[instructions.InstructionAbc]]:
        return tuple(self._instructions.values())

    def decode(self, b: bytes | str) -> type[instructions.InstructionAbc]:
        b = validators.clean_str_or_bytes(b)
        if len(b) != 32:
            raise exceptions.DecodeError("must be 32 bytes")

        if b[0] not in self._instructions:
            raise exceptions.DecodeError("invalid instruction id")

        return self._instructions[b[0]]
