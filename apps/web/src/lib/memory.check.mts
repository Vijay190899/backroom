// Checks the memory page's day logic (run by `pnpm contracts`): days are Bonn days.
import assert from "node:assert/strict";

import type { GraphFact } from "./contracts.ts";
import { dayOf, describeValue, endOfDay, validAt } from "./memory.ts";

const fact = (from: string, to: string | null = null): GraphFact => ({
  id: "f",
  subject_id: "s",
  predicate: "p",
  object_id: null,
  value: 1,
  valid_from: from,
  valid_to: to,
  confidence: 1,
});

// The butter price changed at midnight in Bonn on 6 Nov: 23:00 UTC on 5 Nov.
const newPrice = fact("2026-11-05T23:00:00Z");
const oldPrice = fact("2026-05-24T00:00:00Z", "2026-11-05T23:00:00Z");
const nov5 = dayOf(Date.parse("2026-11-05T12:00:00Z"));
const nov6 = dayOf(Date.parse("2026-11-06T12:00:00Z"));
assert.equal(validAt(newPrice, endOfDay(nov5)), false, "as of 5 Nov the new price is not true yet");
assert.equal(validAt(oldPrice, endOfDay(nov5)), true, "as of 5 Nov the old price still holds");
assert.equal(validAt(newPrice, endOfDay(nov6)), true, "as of 6 Nov the new price holds");
assert.equal(dayOf(Date.parse(newPrice.valid_from)), nov6, "the change's tick sits on 6 Nov");
// Summer time (+2 h): midnight in Bonn on 1 Jul is 22:00 UTC on 30 Jun.
const july = fact("2026-06-30T22:00:00Z");
assert.equal(validAt(july, endOfDay(dayOf(Date.parse("2026-06-30T12:00:00Z")))), false);
assert.equal(validAt(july, endOfDay(dayOf(Date.parse("2026-07-01T12:00:00Z")))), true);
console.log("ok    memory days are Bonn days (winter and summer)");

assert.equal(describeValue({ source: "archive", tmax_c: 11.1, precip_mm: 0.3 }), "11.1 °C, 0.3 mm rain (archive)");
assert.equal(describeValue({ weekdays: ["tue", "fri"], supplier: "grainline" }), "Tue and Fri, supplier grainline");
assert.equal(describeValue({ max_price_increase_pct: 8 }), "rises of at most 8%");
assert.equal(describeValue(3.5), "3.5");
console.log("ok    fact values read as words, not JSON");
