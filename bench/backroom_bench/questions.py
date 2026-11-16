"""B3's question set: 30 questions about Hafer & Bohne, each with SQL ground truth over the
seeded data (data/out/*.parquet). Answers are graded within ±1% (PRD §9); counts and
names must match exactly. The SQL is the truth; no model ever writes it."""

from dataclasses import dataclass
from typing import Literal

Kind = Literal["number", "count", "text"]
# Fixed before any real B3 run, from what memory is built to hold (ARCHITECTURE §7,
# memory/writers.py): menu prices, recipes, ingredient prices from invoices, suppliers, staff,
# holidays, weather and the owner's rules. Sales, transactions, orders, stock, the rota and
# wages are analytics: detectors compute them with SQL over DuckDB, and the memory graph
# never stores them. B3 reports accuracy on all 30 and per scope.
Scope = Literal["memory", "analytics"]
MEMORY_SCOPE = frozenset({"q01", "q02", "q03", "q04", "q07", "q08", "q09", "q22", "q23", "q24"})


@dataclass(frozen=True)
class Question:
    id: str
    text: str
    sql: str
    kind: Kind = "number"

    @property
    def scope(self) -> Scope:
        return "memory" if self.id in MEMORY_SCOPE else "analytics"


Q = Question
OCT = "date between '2026-10-01' and '2026-10-31'"

QUESTIONS: tuple[Question, ...] = (
    Q(
        "q01",
        "What does a Franzbrötchen cost on the menu, in euros?",
        "select price_eur from menu where item_id = 'franzbroetchen'",
    ),
    Q(
        "q02",
        "What does an oat latte cost on the menu, in euros?",
        "select price_eur from menu where item_id = 'oat-latte'",
    ),
    Q(
        "q03",
        "How many grams of butter go into one Franzbrötchen?",
        "select amount * 1000 from recipes where item_id = 'franzbroetchen' and sku = 'BUTTER-1KG'",
    ),
    Q("q04", "How many items are on the menu?", "select count(*) from menu", "count"),
    Q(
        "q05",
        "How many orders were placed with Grainline in total?",
        "select count(distinct order_id) from grainline_orders",
        "count",
    ),
    Q(
        "q06",
        "How many 1-litre cartons of oat milk were ordered from Grainline in October 2026?",
        "select sum(qty) from grainline_orders where sku = 'OAT-1L' and order_date between '2026-10-01' and '2026-10-31'",
        "count",
    ),
    Q(
        "q07",
        "What was the most recent unit price paid for a 1 kg block of butter at Grainline, in euros?",
        "select unit_price_eur from grainline_orders where sku = 'BUTTER-1KG' order by order_date desc limit 1",
    ),
    Q(
        "q08",
        "What was the first unit price paid for a 1 kg block of butter at Grainline, in euros?",
        "select unit_price_eur from grainline_orders where sku = 'BUTTER-1KG' order by order_date asc limit 1",
    ),
    Q(
        "q09",
        "By what percentage did Grainline's butter price change between the first and the most recent order?",
        "select (l.p - f.p) / f.p * 100 from (select unit_price_eur p from grainline_orders where sku = 'BUTTER-1KG' order by order_date asc limit 1) f, (select unit_price_eur p from grainline_orders where sku = 'BUTTER-1KG' order by order_date desc limit 1) l",
    ),
    Q(
        "q10",
        "How many days after ordering was Grainline order GW-10474 delivered?",
        "select max(delivery_date - order_date) from grainline_orders where order_id = 'GW-10474'",
        "count",
    ),
    Q(
        "q11",
        "What was total revenue in October 2026, in euros?",
        f"select sum(revenue_eur) from sales where {OCT}",
    ),
    Q(
        "q12",
        "How many Franzbrötchen were sold in October 2026?",
        f"select sum(qty) from sales where item_id = 'franzbroetchen' and {OCT}",
        "count",
    ),
    Q(
        "q13",
        "What was revenue on Saturday 7 November 2026, in euros?",
        "select sum(revenue_eur) from sales where date = '2026-11-07'",
    ),
    Q(
        "q14",
        "How many transactions were there on 7 November 2026?",
        "select count(distinct transaction_id) from sales where date = '2026-11-07'",
        "count",
    ),
    Q(
        "q15",
        "What was the average revenue per day in September 2026, in euros?",
        "select sum(revenue_eur) / count(distinct date) from sales where date between '2026-09-01' and '2026-09-30'",
    ),
    Q(
        "q16",
        "Which item sold the most units in the 28 days to 12 November 2026? Give its menu name.",
        "select m.name from sales s join menu m using (item_id) where s.date between '2026-10-16' and '2026-11-12' group by m.name order by sum(s.qty) desc limit 1",
        "text",
    ),
    Q(
        "q17",
        "At which hour of the day are the most units sold, over the whole period?",
        "select hour from sales group by hour order by sum(qty) desc limit 1",
        "count",
    ),
    Q(
        "q18",
        "How many litres of oat milk were in stock at closing on 12 November 2026?",
        "select closing from inventory where sku = 'OAT-1L' and date = '2026-11-12'",
    ),
    Q(
        "q19",
        "How many litres of oat milk were used per day on average over the 14 days to 12 November 2026?",
        "select avg(used) from inventory where sku = 'OAT-1L' and date between '2026-10-30' and '2026-11-12'",
    ),
    Q(
        "q20",
        "How many staff hours were rostered in the week of 2 to 8 November 2026?",
        "select sum(hours) from rota where date between '2026-11-02' and '2026-11-08'",
    ),
    Q(
        "q21",
        "What did staff cost in October 2026, in euros?",
        f"select sum(cost_eur) from rota where {OCT}",
    ),
    Q(
        "q22",
        "How many different people appear on the rota?",
        "select count(distinct staff_id) from rota",
        "count",
    ),
    Q(
        "q23",
        "How many public holidays fall in the data period?",
        "select count(*) from holidays",
        "count",
    ),
    Q(
        "q24",
        "What is the name of the first public holiday in the data period?",
        "select name from holidays order by date limit 1",
        "text",
    ),
    Q(
        "q25",
        "What share of October 2026 revenue came from oat lattes, in percent?",
        f"select sum(case when item_id = 'oat-latte' then revenue_eur else 0 end) / sum(revenue_eur) * 100 from sales where {OCT}",
    ),
    Q(
        "q26",
        "How much was spent at Grainline on orders placed in October 2026, in euros?",
        "select sum(qty * unit_price_eur) from grainline_orders where order_date between '2026-10-01' and '2026-10-31'",
    ),
    Q(
        "q27",
        "How many Grainline orders included coffee beans?",
        "select count(distinct order_id) from grainline_orders where sku = 'BEANS-1KG'",
        "count",
    ),
    Q(
        "q28",
        "On average, how many 1-litre cartons of milk were in a Grainline order line for milk?",
        "select avg(qty) from grainline_orders where sku = 'MILK-1L'",
    ),
    Q(
        "q29",
        "How many units did the average transaction contain in October 2026?",
        f"select sum(qty) / count(distinct transaction_id) from sales where {OCT}",
    ),
    Q(
        "q30",
        "On which day of the week is average daily revenue highest? Give the English day name.",
        "select dayname(date) from (select date, sum(revenue_eur) r from sales group by date) group by dayname(date) order by avg(r) desc limit 1",
        "text",
    ),
)
