"""Skill registry: every version of every skill, as JSON files under `var/skills/`.

    var/skills/<skill id>/v<N>.json

A file store keeps H3 independent of the database (H4 can mirror it into Postgres for the
Skills page). Versions are immutable once written, except for `stats`, which the runner
updates after each run. `latest` is the highest version number.
"""

import re
from datetime import UTC, datetime
from pathlib import Path

from backroom_api.config import REPO_ROOT
from backroom_api.skills.schema import Skill, SkillDiff, SkillStats

DEFAULT_ROOT = REPO_ROOT / "var" / "skills"
_ID_RE = re.compile(r"^[a-z]+\.[a-z_]+$")


class SkillStore:
    def __init__(self, root: Path = DEFAULT_ROOT) -> None:
        self.root = root

    def _dir(self, skill_id: str) -> Path:
        if not _ID_RE.fullmatch(skill_id):
            raise ValueError(f"bad skill id: {skill_id!r}")
        return self.root / skill_id

    def versions(self, skill_id: str) -> list[int]:
        folder = self._dir(skill_id)
        if not folder.exists():
            return []
        numbered = (re.fullmatch(r"v(\d+)\.json", p.name) for p in folder.glob("v*.json"))
        return sorted(int(m.group(1)) for m in numbered if m)

    def get(self, skill_id: str, version: int) -> Skill | None:
        path = self._dir(skill_id) / f"v{version}.json"
        if not path.exists():
            return None
        return Skill.model_validate_json(path.read_text(encoding="utf-8"))

    def latest(self, skill_id: str) -> Skill | None:
        versions = self.versions(skill_id)
        return self.get(skill_id, versions[-1]) if versions else None

    def save(self, skill: Skill) -> None:
        folder = self._dir(skill.id)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"v{skill.version}.json"
        if path.exists():
            raise FileExistsError(
                f"{skill.id} v{skill.version} already exists (versions are immutable)"
            )
        path.write_text(skill.model_dump_json(indent=2), encoding="utf-8")

    def record_run(
        self, skill_id: str, version: int, *, ok: bool, wall_ms: int, usd: float
    ) -> None:
        """Fold one run into the version's running stats."""
        skill = self.get(skill_id, version)
        if skill is None:
            return
        s = skill.stats
        runs = s.runs + 1

        def mean(old: float | None, new: float) -> float:
            return new if old is None else (old * s.runs + new) / runs

        stats = SkillStats(
            runs=runs,
            successes=s.successes + int(ok),
            mean_latency_ms=mean(s.mean_latency_ms, wall_ms),
            mean_usd=mean(s.mean_usd, usd),
            last_run_at=datetime.now(UTC),
        )
        path = self._dir(skill_id) / f"v{version}.json"
        path.write_text(
            skill.model_copy(update={"stats": stats}).model_dump_json(indent=2), "utf-8"
        )

    def save_diff(self, diff: SkillDiff) -> None:
        """The exact changes a heal made (the generic differ can mislabel a healed block)."""
        path = self._dir(diff.skill_id) / f"v{diff.to_version}.diff.json"
        path.write_text(diff.model_dump_json(indent=2), encoding="utf-8")

    def get_diff(self, skill_id: str, to_version: int) -> SkillDiff | None:
        path = self._dir(skill_id) / f"v{to_version}.diff.json"
        if path.exists():
            return SkillDiff.model_validate_json(path.read_text(encoding="utf-8"))
        old, new = self.get(skill_id, to_version - 1), self.get(skill_id, to_version)
        if old is None or new is None:
            return None
        from backroom_api.skills.diff import diff_skills

        return diff_skills(old, new)

    def delete(self, skill_id: str) -> None:
        """Forget a skill entirely (the next run is a cold explore)."""
        folder = self._dir(skill_id)
        if folder.exists():
            for p in folder.glob("v*.json"):
                p.unlink()
