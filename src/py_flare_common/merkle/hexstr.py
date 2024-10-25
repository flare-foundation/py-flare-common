import string


def un_prefix_0x(s: str) -> str:
    return s.removeprefix("0x")


def prefix_0x(s: str) -> str:
    return "0x" + un_prefix_0x(s)


def is_hex_str(s: str):
    s = un_prefix_0x(s)
    return all(c in string.hexdigits for c in s)
