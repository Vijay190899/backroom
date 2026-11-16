"""B5, the number guard: every number a brief displays must be backed by evidence.

Two measurements. `summarize` reads the guard verdicts of every brief generated during
the bench (`card.guard`): how often the model's copy passed first time, after its one
regeneration, or fell back to template copy. `verify` re-checks the displayed copy of any
briefs with the same guard, independently of what the pipeline recorded.
"""

from collections.abc import Sequence
from typing import Any

from backroom_api.brief import guard
from backroom_api.contracts.api import Brief
from backroom_bench.results import rate


def summarize(briefs: Sequence[Brief]) -> dict[str, Any]:
    cards = [c for b in briefs for c in b.cards]
    first = sum(c.guard.passed and c.guard.regenerations == 0 for c in cards)
    second = sum(c.guard.passed and c.guard.regenerations == 1 for c in cards)
    template = sum(not c.guard.passed for c in cards)
    return {
        "briefs": len(briefs),
        "cards": len(cards),
        "model_copy_passed_first_try": rate(first, len(cards)),
        "model_copy_passed_after_regeneration": rate(second, len(cards)),
        "template_fallbacks": template,
        "regenerations": sum(c.guard.regenerations for c in cards),
    }


def verify(briefs: Sequence[Brief]) -> dict[str, Any]:
    """Re-run the guard on what each card displays (title, why, and the code-written
    preference note) against its numbers."""
    checked = 0
    failures: list[dict[str, Any]] = []
    for b in briefs:
        for c in b.cards:
            shown = [c.title, c.why, *([c.preference_note] if c.preference_note else [])]
            found = sum(len(guard.extract(t)) for t in shown)
            bad = guard.unmatched(shown, c.numbers)
            checked += found
            if bad:
                failures.append({"brief": b.id, "card": c.id, "unbacked": bad})
    return {
        "numbers_checked": checked,
        "unbacked": sum(len(f["unbacked"]) for f in failures),
        "verified": rate(checked - sum(len(f["unbacked"]) for f in failures), checked),
        "failures": failures,
        "target": {"verified": 1.0},
    }
