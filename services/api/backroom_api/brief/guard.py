"""The number guard (PRD §8.4 step 4, CONTRACTS §6): deterministic, no LLM.

Every number written in a card's copy must equal a number in the card's evidence:

- A number with d decimals matches a value v when it equals round_half_up(|v|, d).
  Money keeps its cents: a euro amount is written with two decimals (or none, when the
  value is whole), so "€13" can't stand in for €13.08.
- Units must agree. "€x" matches a euro value, "€x/kg" or "€x/l" a per-kg or per-litre
  price, "x%" a percentage, and a bare number followed by a unit word ("2 days",
  "4-hour") only that unit; any other bare number matches a non-euro, non-percent value.
- A sign written in the copy (plus or minus) must agree with the value's sign.
- Number words ("two", "dozen") are numbers too; fractions in words ("half") never match.
- Digits inside SKUs, order and invoice ids and protected names don't count.
- Clock times and numeric dates are never in the evidence, so they always fail.

What the guard can't see: whether a correct number is used for the right thing ("margin
70%" when 70% is the target, not the margin) or the right direction ("14% more" when
sales fell 14%). The planner prompt carries those rules; the guard proves no number is
invented.
"""

import re
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from backroom_api.analytics.pricing import round_half_up
from backroom_api.contracts.candidate import EvidenceNumber

EURO_UNITS = frozenset({"eur", "eur_per_kg", "eur_per_l"})
PCT_UNITS = frozenset({"pct"})
MAX_DECIMALS = 6
# Ids whose digits are not quantities: SKUs (OAT-1L, CUP-12OZ-50), orders, invoices.
_IDS = re.compile(r"\b(?:GW-\d+|INV-\d+|[A-Z]{2,}(?:-[A-Z0-9]+)+)\b")
_NUMBER = re.compile(
    r"(?P<euro_pre>(?:€|EUR)\s?)?"
    r"(?P<sign>[+\-\u2212])?"  # plus, hyphen-minus or the minus sign
    r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
    r"(?P<suffix>\s?(?:%|€|EUR\b))?"
    r"(?P<per>\s?/\s?(?:kg|l)\b)?"
    r"(?P<word>[\s-]?(?:days?|hours?|mm|ml|g)\b)?",
    re.IGNORECASE,
)
_CLOCK = re.compile(r"\b\d{1,2}:\d{2}\b")
_WORDS = {
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "dozen": 12,
    "twenty": 20,
    "hundred": 100,
    "thousand": 1000,
}
_FRACTIONS = {"half": 0.5, "quarter": 0.25, "third": 1 / 3, "½": 0.5, "¼": 0.25, "¾": 0.75}
_WORD_RE = re.compile(
    r"\b(" + "|".join(_WORDS) + r")\b|(" + "|".join(_FRACTIONS) + ")", re.IGNORECASE
)
_UNIT_WORDS = {
    "day": "days",
    "days": "days",
    "hour": "hours",
    "hours": "hours",
    "mm": "mm",
    "ml": "ml",
    "g": "g",
}


@dataclass(frozen=True)
class Found:
    text: str  # as written, e.g. "€3.20"
    value: float
    decimals: int
    kind: str  # "eur", "eur_per_kg", "eur_per_l", "pct", "plain", "clock", "fraction"
    unit: str | None = None  # for a plain number followed by a unit word
    sign: int = 0  # +1 / -1 when the copy wrote a sign, else 0


def extract(text: str, protected: Iterable[str] = ()) -> list[Found]:
    """Every number in `text` with its written precision, unit and sign."""
    for phrase in sorted(protected, key=len, reverse=True):
        if phrase:
            text = re.sub(re.escape(phrase), " ", text, flags=re.IGNORECASE)
    text = _IDS.sub(" ", text)
    found = [Found(c, float("nan"), 0, "clock") for c in _CLOCK.findall(text)]
    text = _CLOCK.sub(" ", text)
    for m in _NUMBER.finditer(text):
        raw = m.group("num").replace(",", "")
        decimals = len(raw.split(".")[1]) if "." in raw else 0
        suffix = (m.group("suffix") or "").strip().upper()
        per = (m.group("per") or "").replace(" ", "").lower()
        if m.group("euro_pre") or suffix in ("€", "EUR"):
            kind = {"/kg": "eur_per_kg", "/l": "eur_per_l"}.get(per, "eur")
        elif suffix == "%":
            kind = "pct"
        else:
            kind = "plain"
        word = (m.group("word") or "").strip(" -").lower()
        sign = {"+": 1, "-": -1, "\u2212": -1}.get(m.group("sign") or "", 0)
        found.append(
            Found(
                m.group(0).strip(),
                float(raw),
                decimals,
                kind,
                _UNIT_WORDS.get(word) if kind == "plain" else None,
                sign,
            )
        )
    for m in _WORD_RE.finditer(text):
        if m.group(1):
            found.append(Found(m.group(0), float(_WORDS[m.group(1).lower()]), 0, "plain"))
        else:
            found.append(Found(m.group(0), _FRACTIONS[m.group(2).lower()], 0, "fraction"))
    return found


def _rounds_to(value: float, decimals: int, written: float) -> bool:
    if decimals > MAX_DECIMALS:
        return False
    try:
        return round_half_up(abs(value), decimals) == written
    except InvalidOperation:
        return False


def _matches(found: Found, number: EvidenceNumber) -> bool:
    if found.kind in ("clock", "fraction"):
        return False
    if found.sign and number.value and (found.sign > 0) != (number.value > 0):
        return False
    if found.kind.startswith("eur"):
        if number.unit != found.kind:
            return False
        whole = Decimal(str(abs(number.value))) == Decimal(str(abs(number.value))).to_integral()
        if found.decimals not in ((0, 2) if whole else (2,)):
            return False
    elif found.kind == "pct":
        if number.unit not in PCT_UNITS:
            return False
    else:  # plain
        if number.unit in EURO_UNITS | PCT_UNITS:
            return False
        if found.unit is not None and number.unit != found.unit:
            return False
    return _rounds_to(number.value, found.decimals, found.value)


def unmatched(
    texts: Iterable[str | None], numbers: list[EvidenceNumber], protected: Iterable[str] = ()
) -> list[str]:
    """The numbers in `texts` that no evidence value backs (empty means the copy passes)."""
    protected = list(protected)
    bad: list[str] = []
    for text in texts:
        for f in extract(text or "", protected):
            if not any(_matches(f, n) for n in numbers):
                bad.append(f.text)
    return bad


# --- formatting the planner may copy verbatim ------------------------------------------------


def _short(value: float) -> str:
    """1 decimal at most, never exponent notation: 4 -> "4", 5.47 -> "5.5"."""
    text = f"{round_half_up(value, 1):.1f}"
    return text[:-2] if text.endswith(".0") else text


def display(number: EvidenceNumber) -> str:
    """How a value should be written so the guard accepts it."""
    v = number.value
    if number.unit in EURO_UNITS:
        suffix = {"eur_per_kg": "/kg", "eur_per_l": "/l"}.get(number.unit, "")
        return f"€{abs(v):,.2f}{suffix}"
    if number.unit == "pct":
        return f"{_short(abs(v))}%"
    unit = {"days": " days", "mm": " mm", "hours": " hours", "g": " g", "ml": " ml"}
    return _short(v) + unit.get(number.unit, "")
