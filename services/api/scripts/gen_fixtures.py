"""Regenerate the shared fixtures (apps/web/src/fixtures/*.json) from the pydantic
contracts, so they stay valid by construction (docs/CONTRACTS.md §9).

Run: `uv run python services/api/scripts/gen_fixtures.py`
"""

import json
import sys
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pydantic import BaseModel

from backroom_api.contracts.api import (
    ActionCard,
    Brief,
    GraphFact,
    GraphNode,
    GuardResult,
    MemoryGraph,
    SkillSummary,
    SkillVersions,
)
from backroom_api.contracts.candidate import Evidence, EvidenceNumber
from backroom_api.contracts.common import Unit
from backroom_api.contracts.events import (
    CostTick,
    HealAttempt,
    HealStarted,
    HealSucceeded,
    ModeChanged,
    RunEvent,
    RunFinished,
    RunStarted,
    RunTotals,
    StepFinished,
    StepStarted,
    run_events_adapter,
)
from backroom_api.skills.schema import (
    CssFallback,
    Expect,
    LabelFallback,
    Locator,
    Postcondition,
    Skill,
    SkillDiff,
    SkillStats,
    Step,
    StepChange,
    TextFallback,
)

REPO = Path(__file__).resolve().parents[3]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "apps" / "web" / "src" / "fixtures"
NOW = datetime(2026, 11, 13, 7, 30, tzinfo=UTC)


def n(key: str, value: float, unit: Unit, label: str) -> EvidenceNumber:
    return EvidenceNumber(key=key, value=value, unit=unit, label=label)


def ok_guard() -> GuardResult:
    return GuardResult(passed=True, regenerations=0)


# --- brief ---------------------------------------------------------------------------
cards = [
    ActionCard(
        id="act_oat_reorder",
        candidate_id="stockout:ingredient:oat-milk:2026-11-13",
        kind="stockout",
        rank=2,
        title="Reorder oat milk",
        impact_eur_weekly=730.80,
        why=(
            "Oat milk runs out in 2 days at this week's pace; 28 cartons for €44.52 cover "
            "7 days and protect about €730.80 of oat lattes a week."
        ),
        evidence=[
            Evidence(
                id="ev_oat_velocity",
                kind="sql",
                label="Oat milk use, last 7 days",
                sql="select day, litres from oat_milk_use where day >= :as_of - 7 order by day",
                columns=["day", "litres"],
                rows=[["2026-11-06", 5.9], ["2026-11-07", 7.4], ["2026-11-08", 6.1]],
                synthetic=True,
            ),
            Evidence(
                id="ev_oat_stock", kind="fact", label="Stock on hand", fact_ids=["f_oat_stock"]
            ),
        ],
        numbers=[
            n("days_left", 2, "days", "Days of stock left"),
            n("qty", 28, "count", "Cartons to order"),
            n("cover_days", 7, "days", "Days the order covers"),
            n("order_total_eur", 44.52, "eur", "Order total"),
            n("impact_eur_weekly", 730.80, "eur", "Weekly sales of items that need it"),
        ],
        task="grainline.reorder_item",
        portal="grainline",
        params={"sku": "OAT-1L", "qty": 28},
        executable=True,
        status="proposed",
        preference_note="Scheduled for Friday, your next Grainline order day",
        copy_source="llm",
        guard=ok_guard(),
    ),
    ActionCard(
        id="act_franz_price",
        candidate_id="margin_erosion:product:franzbroetchen:2026-11-13",
        kind="margin_erosion",
        rank=1,
        title="Fix Franzbrötchen margin",
        impact_eur_weekly=86.80,
        why=(
            "Butter is up 16%, so a Franzbrötchen now costs €1.02 to make and its margin fell "
            "from 71% to 68%, under your 70% target; €3.20 → €3.60 brings it to 72%."
        ),
        evidence=[
            Evidence(
                id="ev_butter_invoice",
                kind="invoice",
                label="Grainline invoice INV-204118: butter €8.24/kg",
                fact_ids=["f_butter_price_2"],
            ),
            Evidence(
                id="ev_franz_cost",
                kind="sql",
                label="Franzbrötchen unit cost",
                sql="select ingredient, cost_eur from unit_cost where product = 'franzbroetchen'",
                columns=["ingredient", "before_eur", "after_eur"],
                rows=[["butter", 0.55, 0.64], ["flour", 0.21, 0.21], ["other", 0.17, 0.17]],
            ),
        ],
        numbers=[
            n("driver_increase_pct", 16.1, "pct", "Butter price change"),
            n("driver_cost_before_eur", 0.55, "eur", "Butter per Franzbrötchen, before"),
            n("unit_cost_before_eur", 0.93, "eur", "Unit cost before"),
            n("unit_cost_after_eur", 1.02, "eur", "Unit cost now"),
            n("margin_before_pct", 71, "pct", "Margin before"),
            n("margin_after_pct", 68, "pct", "Margin now"),
            n("margin_target_pct", 70, "pct", "Target margin"),
            n("price_now_eur", 3.20, "eur", "Current price"),
            n("price_new_eur", 3.60, "eur", "Proposed price"),
            n("price_increase_pct", 12.5, "pct", "Price change"),
            n("margin_new_pct", 72, "pct", "Margin at new price"),
            n("impact_eur_weekly", 86.80, "eur", "Weekly margin recovered"),
        ],
        task="tilldesk.change_price",
        portal="tilldesk",
        params={"item_id": "franzbroetchen", "price_eur": 3.60},
        executable=True,
        status="proposed",
        copy_source="llm",
        guard=ok_guard(),
    ),
    ActionCard(
        id="act_rainy_saturday",
        candidate_id="weather_demand:business:hafer-und-bohne:2026-11-13",
        kind="weather_demand",
        rank=3,
        title="Rainy Saturday: trim one shift",
        impact_eur_weekly=58.00,
        why=(
            "Saturday's forecast is 9 mm of rain and rainy Saturdays bring 14% fewer guests; "
            "trimming one 4-hour afternoon shift saves €58.00."
        ),
        evidence=[
            Evidence(
                id="ev_rain_history",
                kind="chart",
                label="Saturday footfall, rain vs dry",
                columns=["weather", "avg_transactions"],
                rows=[["dry", 412], ["rain", 354]],
                synthetic=True,
            )
        ],
        numbers=[
            n("rain_mm", 9, "mm", "Forecast rain"),
            n("footfall_change_pct", -14, "pct", "Footfall on rainy Saturdays"),
            n("shift_hours", 4, "hours", "Shift length"),
            n("impact_eur_weekly", 58.00, "eur", "Labour saved"),
        ],
        task=None,
        portal=None,
        executable=False,
        status="proposed",
        copy_source="template",
        guard=GuardResult(passed=True, regenerations=1),
    ),
]
brief = Brief(id="brief_2026-11-13", generated_at=NOW, as_of=NOW, cards=cards, cached=True)

# After Lena rejects the +12.5% rise with "too steep, max 8%" (PRD F4, DEMO_SCRIPT 3:20).
franz = cards[1]
capped = franz.model_copy(
    update={
        "id": "act_franz_price_capped",
        "why": (
            "Butter is up 16%, so a Franzbrötchen now costs €1.02 to make and its margin fell "
            "to 68%; €3.20 → €3.45 (+7.8%) brings it back to your 70% target."
        ),
        "numbers": [
            *(
                x
                for x in franz.numbers
                if x.key
                not in {
                    "price_new_eur",
                    "price_increase_pct",
                    "margin_new_pct",
                    "impact_eur_weekly",
                }
            ),
            n("price_new_eur", 3.45, "eur", "Proposed price"),
            n("price_increase_pct", 7.8, "pct", "Price change"),
            n("margin_new_pct", 70, "pct", "Margin at new price"),
            n("max_price_increase_pct", 8, "pct", "Your cap on price rises"),
            n("impact_eur_weekly", 54.25, "eur", "Weekly margin recovered"),
        ],
        "impact_eur_weekly": 54.25,
        "params": {"item_id": "franzbroetchen", "price_eur": 3.45},
        "preference_note": "Kept under your 8% cap",
    }
)
ActionCard.model_validate(capped.model_dump())
brief_after_reject = Brief(
    id="brief_2026-11-13_r1",
    generated_at=NOW + timedelta(minutes=4),
    as_of=NOW,
    cards=[cards[0], capped, cards[2]],
    cached=False,
)

# --- skill v1 / v2 ---------------------------------------------------------------------


def reorder_steps(sign_in: str, add_to_cart: str) -> list[Step]:
    return [
        Step(
            intent="Open the Grainline login page",
            action="goto",
            value_template="/grainline/login",
            expect=Expect(url_pattern="^/grainline/login$"),
        ),
        Step(
            intent="Enter the account email",
            action="fill_secret",
            target=Locator(role="textbox", name="Email"),
            fallbacks=[LabelFallback(label="Email"), CssFallback(css="input[name=email]")],
            value_template="{{secret:grainline_user}}",
        ),
        Step(
            intent="Enter the password",
            action="fill_secret",
            target=Locator(role="textbox", name="Password"),
            fallbacks=[CssFallback(css="input[name=password]")],
            value_template="{{secret:grainline_password}}",
        ),
        Step(
            intent="Sign in",
            action="click",
            target=Locator(role="button", name=sign_in),
            expect=Expect(url_pattern="^/grainline/login/totp$"),
        ),
        Step(
            intent="Enter the authenticator code",
            action="totp",
            target=Locator(role="textbox", name="Authentication code"),
            fallbacks=[CssFallback(css="input[name=code]")],
            value_template="{{secret:grainline_totp}}",
        ),
        Step(
            intent="Confirm the code",
            action="click",
            target=Locator(role="button", name="Verify"),
            expect=Expect(url_pattern="^/grainline/$"),
        ),
        Step(
            intent="Open the catalog search",
            action="goto",
            value_template="/grainline/catalog?q={{sku}}",
            expect=Expect(text="{{sku}}"),
        ),
        Step(
            intent="Set the quantity",
            action="fill",
            target=Locator(role="spinbutton", name="Quantity"),
            value_template="{{qty}}",
        ),
        Step(
            intent="Add the item to the cart",
            action="click",
            target=Locator(role="button", name=add_to_cart),
            fallbacks=[CssFallback(css="form[action$='/cart/add'] [type=submit]")],
        ),
        Step(
            intent="Go to checkout",
            action="goto",
            value_template="/grainline/checkout",
            expect=Expect(url_pattern="^/grainline/checkout$"),
        ),
        Step(
            intent="Place the order",
            action="click",
            target=Locator(role="button", name="Place order"),
            expect=Expect(url_pattern="^/grainline/orders/GW-\\d{5}$"),
        ),
    ]


params_schema = {
    "type": "object",
    "properties": {
        "sku": {"type": "string", "pattern": "^[A-Z0-9-]+$"},
        "qty": {"type": "integer", "minimum": 1, "maximum": 200},
    },
    "required": ["sku", "qty"],
    "additionalProperties": False,
}
post = [
    Postcondition(kind="portal_state", value="orders.last.status", equals="placed"),
    Postcondition(kind="portal_state", value="orders.last.lines.0.sku", equals="{{sku}}"),
]
v1 = Skill(
    id="grainline.reorder_item",
    task="grainline.reorder_item",
    portal="grainline",
    version=1,
    params_schema=params_schema,
    steps=reorder_steps("Sign in", "Add to cart"),
    postconditions=post,
    stats=SkillStats(runs=6, successes=6, mean_latency_ms=2410, mean_usd=0.0),
    created_at=NOW - timedelta(hours=20),
)
DISMISS_BANNER = Step(
    intent="Accept the cookie banner",
    action="click",
    target=Locator(role="button", name="Alle akzeptieren"),
    fallbacks=[TextFallback(text="Alle akzeptieren")],
)
SIGN_IN_V1 = {"role": "button", "name": "Sign in"}
ADD_V1 = {"role": "button", "name": "Add to cart"}
# Heals by v1 step index -> the changes that heal produced (indices in v2).
heals: dict[int, list[StepChange]] = {
    3: [
        StepChange(
            op="insert", step_index=3, field="step", before=None, after=DISMISS_BANNER.model_dump()
        ),
        StepChange(
            step_index=4,
            field="target",
            before=SIGN_IN_V1,
            after={"role": "button", "name": "Anmelden"},
        ),
    ],
    8: [
        StepChange(
            step_index=9,
            field="target",
            before=ADD_V1,
            after={"role": "button", "name": "In den Warenkorb"},
        )
    ],
}
changes = [c for cs in heals.values() for c in cs]
v2_steps = reorder_steps("Anmelden", "In den Warenkorb")
v2_steps.insert(3, DISMISS_BANNER)
v2 = v1.model_copy(
    update={
        "version": 2,
        "parent_version": 1,
        "heal_note": "Seed 7: cookie banner and German labels; added a dismiss step, healed 2",
        "steps": v2_steps,
        "stats": SkillStats(runs=1, successes=1, mean_latency_ms=9120, mean_usd=0.0031),
        "created_at": NOW + timedelta(minutes=2),
    }
)
Skill.model_validate(v2.model_dump())
versions = SkillVersions(
    skill_id=v1.id,
    versions=[v1, v2],
    diffs=[SkillDiff(skill_id=v1.id, from_version=1, to_version=2, changes=changes)],
)
summaries = [
    SkillSummary(
        id=v1.id,
        task="grainline.reorder_item",
        portal="grainline",
        latest_version=2,
        runs=7,
        success_rate=1.0,
        mean_latency_ms=3369,
        mean_usd=0.00044,
        updated_at=v2.created_at,
    ),
    SkillSummary(
        id="tilldesk.change_price",
        task="tilldesk.change_price",
        portal="tilldesk",
        latest_version=1,
        runs=3,
        success_rate=1.0,
        mean_latency_ms=1980,
        mean_usd=0.0,
        updated_at=NOW - timedelta(hours=18),
    ),
]

# --- run events: warm replay at seed 7, heals steps 3 and 8 -------------------------------
RUN_ID = "run_demo_seed7"


class Clock:
    """Hands out seq numbers and timestamps for the fixture run."""

    def __init__(self) -> None:
        self.seq = 0
        self.t = NOW + timedelta(minutes=1)

    def tick(self, ms: int = 0) -> tuple[int, datetime]:
        self.seq += 1
        self.t += timedelta(milliseconds=ms)
        return self.seq, self.t


clock = Clock()
tot = RunTotals(
    elapsed_ms=0, steps=0, llm_calls=0, tokens_in=0, tokens_out=0, cache_read_tokens=0, usd=0.0
)
events: list[RunEvent] = []

seq, ts = clock.tick()
events.append(
    RunStarted(
        seq=seq,
        run_id=RUN_ID,
        ts=ts,
        action_id="act_oat_reorder",
        task="grainline.reorder_item",
        portal="grainline",
        mode="replay",
        skill_version=1,
        chaos_seed=7,
    )
)
PARAMS = {"sku": "OAT-1L", "qty": "28"}
offset = 0  # v2 has one extra step once the first heal inserted it
for v1_index, step in enumerate(v1.steps):
    i = v1_index + offset
    if step.action in ("fill_secret", "totp"):
        value = None
    else:
        value = step.value_template
        for key, param in PARAMS.items():
            value = value and value.replace("{{" + key + "}}", param)
    seq, ts = clock.tick(40)
    events.append(
        StepStarted(
            seq=seq,
            run_id=RUN_ID,
            ts=ts,
            index=i,
            intent=step.intent,
            action=step.action,
            target=step.target,
            value=value,
            mode="replay",
        )
    )
    heal = heals.get(v1_index)
    if heal is None:
        dur = 180 + 20 * i
        tot = tot.model_copy(update={"elapsed_ms": tot.elapsed_ms + dur, "steps": tot.steps + 1})
        seq, ts = clock.tick(dur)
        events.append(
            StepFinished(
                seq=seq,
                run_id=RUN_ID,
                ts=ts,
                index=i,
                ok=True,
                duration_ms=dur,
                llm_calls=0,
                tokens_in=0,
                tokens_out=0,
                usd=0.0,
            )
        )
        continue
    fail = f"locator not found: button '{heal[-1].before['name']}'"
    seq, ts = clock.tick(5000)
    events.append(
        StepFinished(
            seq=seq,
            run_id=RUN_ID,
            ts=ts,
            index=i,
            ok=False,
            duration_ms=5000,
            llm_calls=0,
            tokens_in=0,
            tokens_out=0,
            usd=0.0,
            error=fail,
        )
    )
    seq, ts = clock.tick(5)
    events.append(
        ModeChanged(seq=seq, run_id=RUN_ID, ts=ts, from_mode="replay", to_mode="heal", reason=fail)
    )
    seq, ts = clock.tick(5)
    events.append(HealStarted(seq=seq, run_id=RUN_ID, ts=ts, step_index=i, failure=fail))
    seq, ts = clock.tick(120)
    events.append(
        HealAttempt(seq=seq, run_id=RUN_ID, ts=ts, step_index=i, rung="fallback", ok=False)
    )
    seq, ts = clock.tick(1400)
    events.append(
        HealAttempt(
            seq=seq,
            run_id=RUN_ID,
            ts=ts,
            step_index=i,
            rung="healer",
            model="claude-haiku-5-5",
            ok=True,
        )
    )
    tot = RunTotals(
        elapsed_ms=tot.elapsed_ms + 6530,
        steps=tot.steps + 1,
        llm_calls=tot.llm_calls + 1,
        tokens_in=tot.tokens_in + 4210,
        tokens_out=tot.tokens_out + 96,
        cache_read_tokens=tot.cache_read_tokens + 3100,
        usd=round(tot.usd + 0.00155, 5),
    )
    seq, ts = clock.tick(10)
    events.append(
        HealSucceeded(seq=seq, run_id=RUN_ID, ts=ts, step_index=i, new_version=2, changes=heal)
    )
    offset += sum(c.op == "insert" for c in heal) - sum(c.op == "delete" for c in heal)
    seq, ts = clock.tick(5)
    events.append(CostTick(seq=seq, run_id=RUN_ID, ts=ts, totals=tot, skill_version=2))
    seq, ts = clock.tick(5)
    events.append(
        ModeChanged(
            seq=seq,
            run_id=RUN_ID,
            ts=ts,
            from_mode="heal",
            to_mode="replay",
            reason="healed; continuing on v2",
        )
    )
seq, ts = clock.tick(10)
events.append(CostTick(seq=seq, run_id=RUN_ID, ts=ts, totals=tot, skill_version=2))
seq, ts = clock.tick(20)
events.append(
    RunFinished(
        seq=seq,
        run_id=RUN_ID,
        ts=ts,
        status="succeeded",
        summary="Order GW-10482 placed, 28 \u00d7 1L oat milk, €44.52, arrives Mon",
        result={"order_id": "GW-10482", "total_eur": 44.52},
        undo_available=True,
        skill_version=2,
        totals=tot,
    )
)

# Round-trip through the adapter: the fixture must parse exactly as the API would send it.
run_events_adapter.validate_python([e.model_dump() for e in events])

# --- memory graph (as of now) --------------------------------------------------------------
day = timedelta(days=1)
nodes = [
    GraphNode(id="business:hafer-und-bohne", type="business", name="Hafer & Bohne"),
    GraphNode(id="supplier:grainline", type="supplier", name="Grainline Wholesale"),
    GraphNode(id="ingredient:butter", type="ingredient", name="Butter"),
    GraphNode(id="ingredient:oat-milk", type="ingredient", name="Oat milk"),
    GraphNode(id="product:franzbroetchen", type="product", name="Franzbrötchen"),
    GraphNode(
        id="preference:grainline-order-days",
        type="preference",
        name="Order from Grainline on Tue/Fri",
    ),
]
facts = [
    GraphFact(
        id="f_butter_price_1",
        subject_id="ingredient:butter",
        predicate="unit_price_eur_per_kg",
        object_id=None,
        value=7.10,
        valid_from=NOW - 60 * day,
        valid_to=NOW - 9 * day,
        confidence=1.0,
    ),
    GraphFact(
        id="f_butter_price_2",
        subject_id="ingredient:butter",
        predicate="unit_price_eur_per_kg",
        object_id=None,
        value=8.24,
        valid_from=NOW - 9 * day,
        valid_to=None,
        confidence=0.97,
    ),
    GraphFact(
        id="f_butter_supplier",
        subject_id="ingredient:butter",
        predicate="supplied_by",
        object_id="supplier:grainline",
        valid_from=NOW - 60 * day,
        valid_to=None,
        confidence=1.0,
    ),
    GraphFact(
        id="f_oat_supplier",
        subject_id="ingredient:oat-milk",
        predicate="supplied_by",
        object_id="supplier:grainline",
        valid_from=NOW - 60 * day,
        valid_to=None,
        confidence=1.0,
    ),
    GraphFact(
        id="f_franz_butter",
        subject_id="product:franzbroetchen",
        predicate="uses_ingredient",
        object_id="ingredient:butter",
        value={"grams": 77.5},
        valid_from=NOW - 60 * day,
        valid_to=None,
        confidence=1.0,
    ),
    GraphFact(
        id="f_franz_price",
        subject_id="product:franzbroetchen",
        predicate="menu_price_eur",
        object_id=None,
        value=3.20,
        valid_from=NOW - 60 * day,
        valid_to=None,
        confidence=1.0,
    ),
    GraphFact(
        id="f_order_days",
        subject_id="business:hafer-und-bohne",
        predicate="has_preference",
        object_id="preference:grainline-order-days",
        value={"weekdays": ["tue", "fri"], "supplier": "supplier:grainline"},
        valid_from=NOW - 45 * day,
        valid_to=None,
        confidence=0.9,
    ),
]
graph = MemoryGraph(as_of=NOW, nodes=nodes, facts=facts)


def dump(name: str, obj: BaseModel | Sequence[BaseModel]) -> None:
    if isinstance(obj, BaseModel):
        data = obj.model_dump(mode="json")
    else:
        data = [o.model_dump(mode="json") for o in obj]
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


OUT.mkdir(parents=True, exist_ok=True)
dump("brief.json", brief)
dump("brief-after-reject.json", brief_after_reject)
dump("skill-versions.json", versions)
dump("skills.json", summaries)
dump("run-events.json", events)
dump("memory-graph.json", graph)
print("wrote", sorted(p.name for p in OUT.iterdir()))
