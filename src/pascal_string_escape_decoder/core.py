from __future__ import annotations


class PascalStringDecodeError(ValueError):
    """Raised when a Pascal/Delphi string literal cannot be decoded.

    Subclassing ValueError keeps the public exception hierarchy narrow: callers
    that already catch ValueError for input-validation continue to work, while
    those that want precise diagnostics can catch this subclass explicitly.
    """


def _decode_hex_byte(raw: str) -> str:
    value = int(raw, 16)
    if value < 0 or value > 0xFF:
        raise PascalStringDecodeError(f"hex byte out of range: #{raw}")
    return chr(value)


def _decode_code_point(raw: str) -> str:
    value = int(raw, 10)
    if value < 0 or value > 0x10FFFF:
        raise PascalStringDecodeError(f"code point out of range: #{raw}")
    if 0xD800 <= value <= 0xDFFF:
        raise PascalStringDecodeError(f"invalid code point: #{raw}")
    try:
        return chr(value)
    except ValueError as exc:
        # Python's chr rejects surrogates (0xD800..0xDFFF) with ValueError.
        # Re-raise as our own type so the caller sees one error class.
        raise PascalStringDecodeError(f"invalid code point: #{raw}") from exc


_NAMED_ESCAPES = {
    "#0": "\x00",
    "#10": "\n",
    "#13": "\r",
    "#9": "\t",
}


def _decode_escape(text: str, i: int) -> tuple[str, int]:
    """Decode the escape starting at text[i] (a '#').

    Returns (decoded_string, next_index). Two forms are recognised:

      #$XX  - a single byte in hexadecimal, e.g. #$FF, #$41.
      #NNN  - a decimal Unicode code point, e.g. #65, #8364.

    The leading '#' is consumed. After the optional '$', we read the longest
    run of ASCII digits (hex digits for the $ form) so that '#$1A' decodes to
    one character rather than stopping at the first digit. If the run is empty
    we treat the bare '#' as a literal '#', which matches how many Delphi code
    generators emit a standalone hash that they failed to escape.
    """
    assert text[i] == "#"
    j = i + 1
    if j < len(text) and text[j] == "$":
        j += 1
        start = j
        while j < len(text) and text[j] in "0123456789abcdefABCDEF":
            j += 1
        if j == start:
            return "#", j
        return _decode_hex_byte(text[start:j]), j

    start = j
    while j < len(text) and text[j].isdigit():
        j += 1
    if j == start:
        return "#", i + 1
    raw = text[start:j]
    if raw in _NAMED_ESCAPES:
        return _NAMED_ESCAPES[raw], j
    return _decode_code_point(raw), j


def decode_pascal_string(text: str) -> str:
    """Decode a Pascal/Delphi string literal into a Python ``str``.

    Recognises ``#$XX`` hex-byte escapes (e.g. ``#$FF``), ``#NNN`` decimal
    Unicode code-point escapes (e.g. ``#8364``), and the most common named
    escapes (``#0``, ``#9``, ``#10``, ``#13``). Everything else, including
    doubled single quotes which Delphi uses as an in-string literal quote, is
    left verbatim.

    The input is the *body* of the string literal: the surrounding quotes are
    not expected and, if present, are treated as literal characters. This is a
    deliberate scope decision — callers almost always strip the outer quotes
    before decoding, and handling both raw-source and stripped forms in one
    function leads to ambiguous cases (e.g. a trailing single quote that could
    be a closing delimiter or a literal character). Keeping the decoder focused
    on the body removes that ambiguity.

    Raises :class:`PascalStringDecodeError` for out-of-range byte or code-point
    values.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str")

    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "#":
            decoded, i = _decode_escape(text, i)
            out.append(decoded)
        else:
            out.append(ch)
            i += 1
    return "".join(out)
