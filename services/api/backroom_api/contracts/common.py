"""Small types shared by every contract module."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

Portal = Literal["grainline", "tilldesk", "localboard"]
# How a run (or one step of it) is being executed. Shown as the mode badge.
Mode = Literal["explore", "replay", "heal"]
# What a number in the evidence measures. The number guard formats by unit.
Unit = Literal["eur", "eur_per_kg", "eur_per_l", "pct", "count", "days", "hours", "mm", "g", "ml"]
CandidateKind = Literal["stockout", "margin_erosion", "weather_demand"]
# Skill tasks the planner can bind an action card to: "<portal>.<verb>".
SkillTask = Literal[
    "grainline.reorder_item",
    "grainline.download_invoice",
    "tilldesk.change_price",
    "localboard.post_special",
]


class Contract(BaseModel):
    """Base for every contract model: unknown fields are an error, so drift between
    the two machines fails a test instead of passing silently."""

    model_config = ConfigDict(extra="forbid")
