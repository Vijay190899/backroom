# Sync log: laptop → PC

Only the **laptop** edits this file (the PC never does, so it cannot conflict). Newest entry first. One entry per finished task or branch.

Entry format:

```
## Sun 15 Nov 2026 · L12 · branch laptop/l12-deploy (from main)
Done:
- `.github/workflows/deploy-images.yml`: api and portals images, built in CI and pushed to `ghcr.io/vijay190899/backroom-{api,portals}:{sha,latest}` on `main`; PRs build only.
- `infra/deploy.sh`: `setup` (Docker, 2 GB swap, /opt/backroom), `up [tag]` (copy compose, Caddyfile and `.env.production`, generate an image override, pull, start, health check), `status`, `logs` (DECISIONS L-84).
Verify:
- The PR runs "Deploy images" (build-only); both jobs should be green.
- `bash -n infra/deploy.sh`.
- After merge, `main` pushes `:latest`. Then `infra/deploy.sh setup ubuntu@<lightsail-ip>` and `infra/deploy.sh up ubuntu@<lightsail-ip>`; expect "api healthy".
Needs from PC / owner (H8):
- Make the two GHCR packages public (or `docker login ghcr.io` on the server).
- Write `.env.production` locally (never commit it). Set `API_HOST` / `PORTALS_HOST` to real DNS names for Caddy's TLS.
- Seed the server's data.
- Vercel: import the repo with root directory `apps/web` (keep "include files outside the root directory" on, because `/bench` imports `bench/results/*.json`). Set `NEXT_PUBLIC_API_URL=https://<API_HOST>`.
- CORS on the API for the Vercel origin.
Notes:
- Nothing was deployed from the laptop: no server credentials and no Vercel account here.

## <date time> · L<id> · branch laptop/<id>-<slug>
Done: what works now.
Verify: the exact commands to check it (and what you should see).
Needs from PC: anything the PC must do to integrate (new dependency, migration, env var).
Notes: surprises, shortcuts, things left undone.
```

---

_No entries yet._
