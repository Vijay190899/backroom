#!/usr/bin/env bash
# Deploy the backend to one small server (AWS Lightsail, 2 GB) by pulling images built in CI
# (.github/workflows/deploy-images.yml). Nothing is built on the server.
#
#   infra/deploy.sh setup  user@host          # once: Docker, swap, /opt/backroom
#   infra/deploy.sh up     user@host [tag]    # copy compose + Caddyfile + env, pull, start
#   infra/deploy.sh status user@host          # containers and the API health check
#   infra/deploy.sh logs   user@host [svc]    # follow logs
#
# The server's environment comes from a local, git-ignored file (ENV_FILE, default
# .env.production). It is copied with mode 600 and never printed. Images default to
# ghcr.io/vijay190899/backroom-{api,portals}:latest; set IMAGE_PREFIX to change the owner.
set -euo pipefail

cmd="${1:-}"; host="${2:-}"
[[ -n "$cmd" && -n "$host" ]] || { sed -n '4,8p' "$0"; exit 2; }
here="$(cd "$(dirname "$0")" && pwd)"
dir=/opt/backroom
prefix="${IMAGE_PREFIX:-ghcr.io/vijay190899/backroom}"
ssh_() { ssh -o BatchMode=yes -o ConnectTimeout=10 "$host" "$@"; }

case "$cmd" in
  setup)
    ssh_ 'bash -s' <<'REMOTE'
set -euo pipefail
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
echo "setup done (log out and back in once so the docker group applies)"
REMOTE
    ;;

  up)
    tag="${3:-latest}"
    env_file="${ENV_FILE:-$here/../.env.production}"
    [[ -f "$env_file" ]] || { echo "missing $env_file (the server's .env; see .env.example)" >&2; exit 1; }
    scp -q "$here/docker-compose.yml" "$here/Caddyfile" "$host:$dir/"
    scp -q "$env_file" "$host:$dir/.env"
    # Point the deploy services at the CI images instead of local builds.
    ssh_ "chmod 600 $dir/.env && cat > $dir/docker-compose.images.yml" <<YAML
services:
  api:
    image: $prefix-api:$tag
    pull_policy: always
  portals:
    image: $prefix-portals:$tag
    pull_policy: always
YAML
    ssh_ "cd $dir && sed -i 's#env_file: ../.env#env_file: .env#; s#context: ..#context: .#' docker-compose.yml \
      && docker compose -f docker-compose.yml -f docker-compose.images.yml --profile deploy pull api portals \
      && docker compose -f docker-compose.yml -f docker-compose.images.yml --profile deploy up -d --no-build --remove-orphans \
      && docker image prune -f >/dev/null"
    "$0" status "$host"
    ;;

  status)
    ssh_ "cd $dir && docker compose -f docker-compose.yml -f docker-compose.images.yml --profile deploy ps"
    for i in $(seq 1 30); do
      if ssh_ "cd $dir && docker compose -f docker-compose.yml -f docker-compose.images.yml --profile deploy exec -T api \
          python -c 'import urllib.request,sys; sys.exit(0 if urllib.request.urlopen(\"http://localhost:8000/health\").status == 200 else 1)'" 2>/dev/null; then
        echo "api healthy"; exit 0
      fi
      sleep 2
    done
    echo "api not healthy after 60 s; try: $0 logs $host api" >&2; exit 1
    ;;

  logs)
    ssh_ -t "cd $dir && docker compose -f docker-compose.yml -f docker-compose.images.yml --profile deploy logs -f --tail 200 ${3:-}"
    ;;

  *) sed -n '4,8p' "$0"; exit 2 ;;
esac
