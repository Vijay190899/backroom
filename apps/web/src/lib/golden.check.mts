// Checks the committed golden runs (run by `pnpm contracts`): every recording parses with the
// same schemas the app uses, is marked recorded, and has every frame it names (PRD F7).
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { goldenFrameSchema, runEventSchema } from "./contracts.ts";

const root = join(import.meta.dirname, "..", "..", "public", "golden");
const names = JSON.parse(readFileSync(join(root, "index.json"), "utf8")) as string[];
assert.ok(names.length >= 4, "the demo's four recordings are committed");
for (const name of names) {
  const events = runEventSchema.array().parse(JSON.parse(readFileSync(join(root, name, "events.json"), "utf8")));
  const frames = goldenFrameSchema.array().parse(JSON.parse(readFileSync(join(root, name, "frames.json"), "utf8")));
  const first = events[0];
  const last = events.at(-1);
  assert.ok(first?.type === "run.started" && first.recorded, `${name}: starts as a recorded run`);
  assert.ok(last?.type === "run.finished" && last.status === "succeeded", `${name}: ends succeeded`);
  assert.deepEqual(events.map((e) => e.seq), events.map((_, i) => i + 1), `${name}: seq 1..n without gaps`);
  assert.ok(frames.length > 0, `${name}: has frames`);
  for (const f of frames) {
    assert.ok(existsSync(join(root, name, "frames", f.file)), `${name}: ${f.file} exists`);
    assert.ok(f.after_seq >= 0 && f.after_seq <= events.length, `${name}: ${f.file} follows a real event`);
  }
}
console.log(`ok    ${names.length} golden runs parse, are marked recorded and have their frames`);
