# Sync log: laptop → PC

Only the **laptop** edits this file (the PC never does, so it cannot conflict). Newest entry first. One entry per finished task or branch.

Entry format:

```
## <date time> · L<id> · branch laptop/<id>-<slug>
Done: what works now.
Verify: the exact commands to check it (and what you should see).
Needs from PC: anything the PC must do to integrate (new dependency, migration, env var).
Notes: surprises, shortcuts, things left undone.
```

---

## Thu 12 Nov 2026 15:20 · L10 · branch laptop/l10-llm-probe
Done: `pnpm probe:llm` on OpenRouter (worker anthropic/claude-haiku-5.5, SDK 2.8.0): all 6 checks pass (basic, effort, strict_tools, structured_outputs, prompt_cache, streaming). Total $0.0020. `LLM_CAPS_OFF` stays empty; no DECISIONS entry needed. Closes the last M0 gate item.
Verify: `cat bench/results/provider_probe.json` (every check `"ok": true`), or rerun `pnpm probe:llm` with the key in `.env`.
Needs from PC: merge only; adds `bench/results/provider_probe.json` (PC-owned path, written as L10 specifies). Update HANDOVER §1 to mark the M0 gate closed.
Notes: laptop setup per §2b done; `pnpm check` green on macOS (20 passed).
