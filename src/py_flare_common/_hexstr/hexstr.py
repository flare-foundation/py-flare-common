import string

__all__ = []


def un_prefix_0x(s: str) -> str:
    return s.removeprefix("0x")


def prefix_0x(s: str) -> str:
    return "0x" + un_prefix_0x(s)


def is_hex_str(s: str):
    s = un_prefix_0x(s)
    return all(c in string.hexdigits for c in s)


SUBMISSION_METHOD_SELECTORS = {
    b"\x6c\x53\x2f\xae",  # submit1
    b"\x9d\x00\xc9\xfd",  # submit2
    b"\xe1\xb1\x57\xe7",  # submit3
    b"\x57\xee\xd5\x80",  # submitSignatures
}


def to_bytes(s: str | bytes) -> bytes:
    # cleanup string and convert to bytes
    if isinstance(s, str):
        s = un_prefix_0x(s)

        if not is_hex_str(s):
            raise ValueError("Invalid hex string")

        s = bytes.fromhex(s)

    # "magic" detection of function signature
    if s[0:4] in SUBMISSION_METHOD_SELECTORS:
        s = s[4:]

    return s
