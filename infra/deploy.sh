#!/usr/bin/env bash
# Deploy the backend to one small server (AWS Lightsail, 2 GB) by pulling images built in CI
# (.github/workflows/deploy-images.yml). Nothing is built on the server.
#
#   infra/deploy.sh setup  user@host          # once: security updates, Docker, swap, /opt/backroom
#   infra/deploy.sh up     user@host [tag]    # copy compose + Caddyfile + env + data, pull, start
#   infra/deploy.sh reset  user@host          # the demo's starting point (pnpm demo:reset --relearn)
#   infra/deploy.sh status user@host          # containers and the API health check
#   infra/deploy.sh logs   user@host [svc]    # follow logs
#
# The server's environment comes from a local, git-ignored file (ENV_FILE, default
# .env.production). It is copied with mode 600 and never printed. Images default to
# ghcr.io/vijay190899/backroom-{api,portals}:latest; set IMAGE_PREFIX to change the owner.
# data/out (built by `pnpm seed`) is shipped and mounted read-only, so the server runs on the
# same data as the benchmarks; learned skills live in a volume and survive redeploys.
set -euo pipefail

cmd="${1:-}"; host="${2:-}"
[[ -n "$cmd" && -n "$host" ]] || { sed -n '4,9p' "$0"; exit 2; }
here="$(cd "$(dirname "$0")" && pwd)"
dir=/opt/backroom
prefix="${IMAGE_PREFIX:-ghcr.io/vijay190899/backroom}"
ssh_() { ssh -o BatchMode=yes -o ConnectTimeout=10 "$host" "$@"; }
compose="docker compose -f docker-compose.yml -f docker-compose.images.yml --profile deploy"

case "$cmd" in
  setup)
    ssh_ 'bash -s' <<'REMOTE'
set -euo pipefail
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get -y -qq upgrade
if ! command -v docker >/dev/null; then
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER"
fi
# 2 GB of RAM: a swap file keeps Chromium from being OOM-killed under load.
if ! sudo swapon --show | grep -q /swapfile; then
  sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
  sudo mkswap /swapfile && sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
fi
sudo mkdir -p /opt/backroom && sudo chown "$USER" /opt/backroom
# SSH: keys only (Lightsail's default), and no root login at all.
printf 'PermitRootLogin no\nPasswordAuthentication no\nKbdInteractiveAuthentication no\n' \
  | sudo tee /etc/ssh/sshd_config.d/10-backroom.conf >/dev/null
sudo sshd -t && sudo systemctl reload ssh
if [ -f /var/run/reboot-required ]; then echo "setup done; a reboot is required: sudo reboot"; else echo "setup done"; fi
REMOTE
    ;;

  up)
    tag="${3:-latest}"
    env_file="${ENV_FILE:-$here/../.env.production}"
    [[ -f "$env_file" ]] || { echo "missing $env_file (the server's .env; see .env.example)" >&2; exit 1; }
    # Refuse to ship an environment that would run open or keyless.
    for key in OPENROUTER_API_KEY DEMO_ACCESS_CODE PORTALS_ADMIN_TOKEN WEB_ORIGIN API_HOST; do
      value="$(tr -d '\r' < "$env_file" | grep -E "^$key=" | tail -1 | cut -d= -f2-)"
      if [[ -z "$value" || "$value" == "change-me" ]]; then
        echo "$env_file: $key is empty or change-me" >&2; exit 1
      fi
    done
    data="$here/../data/out"
    [[ -f "$data/manifest.json" ]] || { echo "missing data/out (run: pnpm seed)" >&2; exit 1; }
    scp -q "$here/docker-compose.yml" "$here/Caddyfile" "$host:$dir/"
    tr -d '\r' < "$env_file" | ssh_ "umask 077 && cat > $dir/.env"  # LF only, never printed
    tar -C "$data/.." -czf - out | ssh_ "rm -rf $dir/data/out && mkdir -p $dir/data && tar -C $dir/data -xzf -"
    # Point the deploy services at the CI images instead of local builds; mount the data
    # (read-only) and keep the learned skills in a volume.
    ssh_ "chmod 600 $dir/.env && cat > $dir/docker-compose.images.yml" <<YAML
services:
  api:
    image: $prefix-api:$tag
    pull_policy: always
    volumes:
      - ./data/out:/app/data/out:ro
      - skills:/app/var/skills
  portals:
    image: $prefix-portals:$tag
    pull_policy: always
volumes:
  skills:
YAML
    ssh_ "cd $dir && sed -i 's#env_file: ../.env#env_file: .env#; s#context: ..#context: .#' docker-compose.yml \
      && $compose pull api portals \
      && $compose up -d --no-build --remove-orphans \
      && docker image prune -f >/dev/null"
    "$0" status "$host"
    ;;

  reset)
    # Clears runs and briefs, re-seeds memory, relearns the skills at seed 0 (about $0.01).
    ssh_ "cd $dir && $compose exec -T api uv run --no-sync python -m backroom_api.demo reset --relearn"
    ;;

  status)
    ssh_ "cd $dir && $compose ps"
    for i in $(seq 1 30); do
      if ssh_ "cd $dir && $compose exec -T api \
          python -c 'import urllib.request,sys; sys.exit(0 if urllib.request.urlopen(\"http://localhost:8000/health\").status == 200 else 1)'" 2>/dev/null; then
        echo "api healthy"; exit 0
      fi
      sleep 2
    done
    echo "api not healthy after 60 s; try: $0 logs $host api" >&2; exit 1
    ;;

  logs)
    ssh -t "$host" "cd $dir && $compose logs -f --tail 200 ${3:-}"
    ;;

  *) sed -n '4,9p' "$0"; exit 2 ;;
esac
