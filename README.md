# Pascal String Escape Decoder

Decodes Pascal and Delphi string-literal bodies containing `#$XX` hex-byte escapes, `#NNN` decimal Unicode code-point escapes, and the common named escapes (`#0`, `#9`, `#10`, `#13`) into a Python `str`.

```python
from pascal_string_escape_decoder import decode_pascal_string, PascalStringDecodeError

decode_pascal_string("line1#13#10line2")   # 'line1\r\nline2'
decode_pascal_string("price: #8364")        # 'price: €'
decode_pascal_string("tab#9here")           # 'tab\there'
```

## Why this exists

Tools that extract string literals from Pascal/Delphi source (localisation pipelines, static analysers) need to resolve the `#`-prefixed escape sequences into real characters. Doing this with ad-hoc regex tends to mis-handle bare hashes and out-of-range code points. This library provides a single focused decoder with explicit error reporting.

The scope is deliberately narrow: the input is the *body* of the literal, not the raw source token. Strip the surrounding quotes yourself before calling `decode_pascal_string`. Trying to honour both raw and stripped forms in one function creates ambiguous trailing-quote cases, so the decision was made to accept only the body.

## Edge you will hit

A `#` not followed by a digit (or `$` then a hex digit) is treated as a literal `#`. This matches the behaviour of most Delphi code generators when emitting a standalone hash they failed to escape, but means a malformed escape like `#x` silently becomes the two characters `#x`. If you need strict validation, check the decoded length against expectations or pre-scan for `#` sequences that don't match `#(\$[0-9A-Fa-f]+|[0-9]+)`.

Surrogate code points (`#55296` through `#57343`) raise `PascalStringDecodeError`, because Python's `chr` rejects them and they cannot form a valid character on their own.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

