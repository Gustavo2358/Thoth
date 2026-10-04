import re


def locate(raw: str, excerpt: str, quote: str) -> tuple[int, int]:
    if not excerpt.strip() or not quote.strip():
        raise ValueError("Empty source or learner quote")
    pattern = r"\s+".join(re.escape(t) for t in excerpt.split())
    matches = list(re.finditer(pattern, raw))
    if len(matches) != 1:
        raise ValueError("Source excerpt must identify one contiguous part of the report")
    span = matches[0].span()
    quoted = r"\s+".join(re.escape(t) for t in quote.split())
    if not re.search(quoted, raw[slice(*span)]):
        raise ValueError("Learner quote is absent from the report excerpt")
    return span
