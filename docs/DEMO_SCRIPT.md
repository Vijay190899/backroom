# Demo Script — 5 minutes

**Setup before the call:** deployed URL open in a browser at 110% zoom. `/bench` in a second tab. Portals pre-warmed (skills compiled at seed 0). Chaos seed 7 verified to heal. Live-mode access code set. Local `docker compose` running as a backup.

| t | Beat | What you show | Line |
|---|---|---|---|
| 0:00 | Hook | Today: 3 cards for Hafer & Bohne | "Your homepage ends at 'Approve all'. This is what happens after the owner taps it." |
| 0:30 | Evidence | Open the Franzbrötchen margin card's evidence drawer: SQL result, invoice fact, butter +16%, margin 71% → 68% (target 70%) | "Every euro here was computed by code. The model writes the sentence, and a number guard rejects any figure that isn't in the evidence." |
| 1:00 | Act | Approve "Reorder oat milk" → Run theater: login, TOTP, cart, checkout. REPLAY badge, 2.x s, $0.000 | "It ran this before, so it compiled the run into a skill. No LLM call this time." |
| 1:40 | Break it | Chaos seed 7 (German labels, moved nav, cookie modal) → replay fails at step 4 → HEAL on Haiku → success → skill v2 diff | "The site changed. It noticed, fixed itself, and now every merchant on this portal gets the fix." |
| 2:40 | Remember | Memory: drag the time slider back 10 days → butter price fact superseded; fact provenance = invoice PDF | "Facts have validity windows, so it knows what was true when. That's what makes memory compound instead of bloat." |
| 3:20 | Learn the owner | Reject the Franzbrötchen card (€3.20 → €3.60, +12.5%) with "too steep, max 8%" → new Preference fact appears in memory → regenerate → €3.45 (+7.8%, margin still 70%), "kept under your 8% cap" | "Rejections become rules the verifier enforces. That's the second self-improvement loop." |
| 4:00 | Proof | `/bench`: learning curve (spikes at redesigns, then recovery), success under 20 chaos seeds, $/task, memory vs raw-dump accuracy and tokens | "These are measured, reproducible numbers. One command, results committed with the git SHA." |
| 4:40 | Close | `/about` architecture + model table | "Provider and models are env vars. Haiku does the work and Sonnet plans, via OpenRouter today. Switching to Opus, or going direct to Anthropic, is one line. How I'd take this to a real POS: API adapters first, browser skills for the long tail." |

## Likely questions (prepare crisp answers)
1. *How would this handle Cloudflare / bot protection on real portals?* → Legitimate sessions (persisted auth, the owner's own login), human handoff for CAPTCHAs, and partnering or APIs where possible. Evasion isn't a durable strategy.
2. *Why not browser-use / Stagehand?* → For the demo I own the loop: the skill-compilation and heal semantics are the product, and I need the metrics. In production I'd evaluate them as the explore layer.
3. *How does memory avoid going stale or contradictory?* → Bitemporal facts, supersession on (subject, predicate), confidence, provenance. The context packer only reads facts valid "as of" now.
4. *Cost at scale?* → Replay is $0. Explore is about $0.01 on Haiku. Skills are shared per portal across merchants, so marginal cost falls with every merchant added.
5. *What breaks first in production?* → Long-tail portal auth flows and silent wrong outcomes. Hence postconditions, idempotency and human handoff.
