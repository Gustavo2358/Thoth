"""Only whitespace normalization is allowed; no fuzzy matching or invented quotes."""
import re


def normalized(text: str) -> str:
    return " ".join(text.split())


def locate(raw: str, span: str) -> tuple[int, int]:
    # Match tokens literally, allowing only runs of whitespace to vary.
    tokens = re.split(r"\s+", span.strip())
    if not tokens or not tokens[0]:
        raise ValueError("empty source span")
    matches = list(re.finditer(r"\s+".join(re.escape(t) for t in tokens), raw))
    if len(matches) != 1:
        raise ValueError("source span absent or ambiguous; supply a larger unique span")
    return matches[0].span()


def validate(raw: str, span: str, utterance: str, correction: str | None = None,
             comment: str | None = None) -> tuple[int, int]:
    start, end = locate(raw, span)
    source = normalized(raw[start:end])
    for name, value in (("learner utterance", utterance), ("correction", correction),
                        ("teacher comment", comment)):
        if value is not None and normalized(value) not in source:
            raise ValueError(f"{name} absent from source span")
    return start, end
