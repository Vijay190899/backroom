# Sync log: PC → laptop

Only the **PC** edits this file. Newest entry first. Tell the laptop what changed under it: contracts, new env vars, merged branches, gate results.

Entry format:

```
## <date time> · H<id> / merge of laptop/<id>
Done: what works now.
Laptop must: pull, then run these commands (`uv sync --all-packages`, `pnpm install`, ...).
Contract changes: anything the laptop's code must adapt to.
```

---

## Thu 12 Nov 2026 · two-machine mode starts
Done: M0 finished and pushed. `pnpm dev:lite` added (api + portals + web, no Docker, no database). `/health` now answers in about 1.3 s even when Postgres is down.
Laptop must: follow HANDOVER §2b, then start with task L0 (contracts) from §9.
