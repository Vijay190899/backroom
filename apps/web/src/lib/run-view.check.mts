/**
 * Run-view check: folding the committed sample run gives the numbers the theater shows.
 * Run: `pnpm -C apps/web contracts` (part of `pnpm check`).
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import { runEventSchema } from "./contracts.ts";
import { describeChange, foldRun, gapMs } from "./run-view.ts";

const events = runEventSchema.array().parse(JSON.parse(readFileSync(new URL("../fixtures/run-events.json", import.meta.url), "utf8")));

// Mid-run: after the first heal (seq 16), before the second.
const mid = foldRun(events.slice(0, 16));
assert.equal(mid.mode, "replay");
assert.equal(mid.skillVersion, 2);
const signIn = mid.steps.find((s) => s.index === 3)!;
assert.equal(signIn.state, "healed");
assert.deepEqual(signIn.heal?.rungs.map((r) => `${r.rung}:${r.ok}`), ["fallback:false", "healer:true"]);
assert.deepEqual(signIn.heal?.target, { role: "button", name: "Anmelden" });
assert.deepEqual(signIn.heal?.inserted.map((i) => i.target?.name), ["Alle akzeptieren"]);
assert.equal(mid.totals.llm_calls, 1);
assert.equal(mid.path, "/grainline/login");
console.log("ok    mid-run heal folds (Sign in → Anmelden, cookie banner inserted, v2)");

// While healing: the mode flips and the step shows it.
const healing = foldRun(events.slice(0, 12));
assert.equal(healing.mode, "heal");
assert.equal(healing.steps.find((s) => s.index === 3)?.state, "healing");
console.log("ok    healing state");

// The whole run.
const done = foldRun(events);
assert.equal(done.finished?.status, "succeeded");
assert.equal(done.steps.length, 11);
assert.equal(done.steps.filter((s) => s.state === "healed").length, 2);
assert.equal(done.totals.llm_calls, 2);
assert.equal(done.totals.usd, 0.0031);
assert.equal(done.elapsedMs, 15680);
assert.equal(done.path, "/grainline/checkout");
assert.equal(done.chaosSeed, 7);
const secondHeal = events.findLast((e) => e.type === "heal.succeeded");
assert.ok(secondHeal?.type === "heal.succeeded");
assert.equal(describeChange(secondHeal.changes[0]), "‘Add to cart’ → ‘In den Warenkorb’");
console.log("ok    finished run: 11 steps, 2 heals, 2 model calls, $0.0031, 15.68 s");

// Pacing: a 5 s locator timeout is clipped; 2× halves the gap.
const timeout = events.findIndex((e) => e.type === "step.finished" && e.duration_ms === 5000);
assert.equal(gapMs(events, timeout, 1), 900);
assert.equal(gapMs(events, timeout, 2), 450);
console.log("ok    pacing clips waits");

// A run that fails mid-step: nothing keeps spinning once it is over.
const upToSignIn = events.slice(0, 8); // step 3 ("Sign in") has started, not finished
const failedEnd = runEventSchema.parse({
  seq: 99, run_id: "run_demo_seed7", ts: "2026-11-13T07:31:06Z", type: "run.finished", status: "failed",
  summary: "Stopped", result: {}, undo_available: false, skill_version: 1,
  totals: { elapsed_ms: 6000, steps: 4, llm_calls: 0, tokens_in: 0, tokens_out: 0, cache_read_tokens: 0, usd: 0 },
});
assert.equal(foldRun([...upToSignIn, failedEnd]).steps.at(-1)?.state, "failed");
console.log("ok    a failed run settles its running step");

// Asking for a person clears once the agent moves on.
const ask = runEventSchema.parse({ seq: 9, run_id: "run_demo_seed7", ts: "2026-11-13T07:31:01Z", type: "ask_human", reason: "Captcha", step_index: 3 });
assert.equal(foldRun([...upToSignIn, ask]).askHuman?.reason, "Captcha");
const next = runEventSchema.parse({ seq: 10, run_id: "run_demo_seed7", ts: "2026-11-13T07:31:02Z", type: "step.started", index: 4, intent: "Retry", action: "click", target: null, value: null, mode: "replay" });
assert.equal(foldRun([...upToSignIn, ask, next]).askHuman, null);
console.log("ok    ask_human clears when the run moves on");

// Secrets never survive the fold, even if a stream carried a value.
const leaky = runEventSchema.parse({ ...events[3], value: "hunter2" });
assert.equal(foldRun([events[0], leaky]).steps[0].value, null);
assert.equal(done.heals, 2);
console.log("ok    secret values dropped; heals counted from events");
