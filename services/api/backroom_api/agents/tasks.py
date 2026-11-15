"""The tasks Backroom can carry out (CONTRACTS §4): goal, parameters, and how success is proved.

A task's `goal` is what the explore agent is told; its `postconditions` are what the code
checks afterwards against the portal's own state. The agent never decides that a run
succeeded: it can only say it is finished.
"""

from dataclasses import dataclass, field
from typing import Any

from backroom_api.contracts.common import Portal, SkillTask
from backroom_api.skills.schema import Postcondition


@dataclass(frozen=True)
class TaskSpec:
    task: SkillTask
    portal: Portal
    goal: str  # formatted with the params
    start_path: str
    params_schema: dict[str, Any]
    postconditions: list[Postcondition]
    default_params: dict[str, Any] = field(default_factory=dict[str, Any])

    def goal_for(self, params: dict[str, Any]) -> str:
        return self.goal.format(**params)


TASKS: dict[str, TaskSpec] = {
    "grainline.reorder_item": TaskSpec(
        task="grainline.reorder_item",
        portal="grainline",
        start_path="/grainline/login",
        goal=(
            "Order {qty} cartons of the product with SKU {sku} from Grainline Wholesale and "
            "place the order. Sign in first. Find the product by searching for its exact SKU "
            "code so that only one product row is left, set the quantity, add it to the cart, "
            "check out, and place the order. Finish when the order confirmation is visible."
        ),
        params_schema={
            "type": "object",
            "properties": {"sku": {"type": "string"}, "qty": {"type": "integer", "minimum": 1}},
            "required": ["sku", "qty"],
        },
        postconditions=[
            Postcondition(kind="portal_state", value="orders.last.status", equals="placed"),
            Postcondition(kind="portal_state", value="orders.last.lines.0.sku", equals="{{sku}}"),
            Postcondition(kind="portal_state", value="orders.last.lines.0.qty", equals="{{qty}}"),
        ],
        default_params={"sku": "OAT-1L", "qty": 24},
    ),
    "tilldesk.change_price": TaskSpec(
        task="tilldesk.change_price",
        portal="tilldesk",
        start_path="/tilldesk/login",
        goal=(
            "Change the price of the menu item with id {item_id} to {price_eur} EUR in "
            "TillDesk and publish the menu so the new price is live. Sign in first. Then open "
            "the item's edit page directly with action `goto` and the path "
            "/tilldesk/menu/{item_id}/edit (do not click through the menu list), set the price, "
            "save, go back to the menu page and use the Publish control there."
        ),
        params_schema={
            "type": "object",
            "properties": {
                "item_id": {"type": "string"},
                "price_eur": {"type": "number", "exclusiveMinimum": 0},
            },
            "required": ["item_id", "price_eur"],
        },
        postconditions=[
            Postcondition(
                kind="portal_state",
                value="items.{{item_id}}.published_price_eur",
                equals="{{price_eur}}",
            )
        ],
        default_params={"item_id": "franzbroetchen", "price_eur": 3.45},
    ),
}
