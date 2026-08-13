#!/usr/bin/env bash
#
# install_ubec.sh — UBEC Protocol Suite: deploy a bioregion node
#
# Model (matches the project's dev -> prod migration pattern):
#   SRC_DIR   = git working tree  (single source of truth, where GitHub lives)
#   INSTALL_DIR = deployed runtime copy (systemd runs from here; no .git)
#
# The script: ensures the repo in SRC_DIR (clone/pull), deploys a clean copy to
# INSTALL_DIR, builds a Python venv + installs dependencies, writes the config
# file (single source of truth), and installs a systemd unit. Idempotent.
#
# Usage:
#   bash 00_preflight_check.sh
#   sudo bash install_ubec.sh                 # first run may stop to add a deploy key
#   sudo nano /etc/ubec_bio/environment       # real credentials
#   sudo systemctl enable --now ubec-bio.service
#
# License (code): GNU Affero General Public License v3.0
# License (docs): Creative Commons BY-SA 4.0
#
# Attribution:
#   This project uses the services of Claude and Anthropic PBC to inform our
#   decisions and recommendations. This project was made possible with the
#   assistance of Claude and Anthropic PBC.

set -euo pipefail

# =============================================================================
# CONFIG
# =============================================================================
REPO_URL="${REPO_URL:-git@github.com:ubeccommon/ubec_main.git}"  # private repo
REPO_REF="${REPO_REF:-main}"

SERVICE_USER="${SERVICE_USER:-${SUDO_USER:-ubec}}"   # owns SRC_DIR + runs the service
SERVICE_NAME="${SERVICE_NAME:-ubec-protocol}"

# Source of truth (git working tree). Defaults to the service user's home.
SERVICE_HOME="$(getent passwd "$SERVICE_USER" | cut -d: -f6)"
SRC_DIR="${SRC_DIR:-$SERVICE_HOME/ubec_commons/main_bioregion}"

# Deployed runtime + supporting dirs (canonical /srv/ubec/{service}/ layout).
INSTALL_DIR="${INSTALL_DIR:-/srv/ubec/protocol}"
DATA_DIR="${DATA_DIR:-/var/lib/ubec_protocol}"
LOG_DIR="${LOG_DIR:-/var/log/ubec_protocol}"
CONFIG_DIR="${CONFIG_DIR:-/etc/ubec_protocol}"

PY_BIN="${PY_BIN:-auto}"                 # 'auto' = pick python3.11+ on PATH
REQUIRED_PY_MINOR=11

# Files never copied from the git tree into the runtime deployment
DEPLOY_EXCLUDES=(.git venv __pycache__ '*.pyc' logs reports backups .env .ssh .checkout)

# Auth for the PRIVATE repo:
#   (A) SSH deploy key [default] — keep the git@ URL. First run prints a public
#       key to add under: repo > Settings > Deploy keys (read-only). Re-run.
#   (B) HTTPS + PAT — set REPO_URL=https://github.com/ubeccommon/ubec_main.git
#       and configure a git credential helper for '$SERVICE_USER'.
# =============================================================================

# --- Logging + error trap ----------------------------------------------------
log() { printf '\033[0;34m[ %(%H:%M:%S)T ] %s\033[0m\n' -1 "$*"; }
die() { printf '\033[0;31m[ FATAL ] %s\033[0m\n' "$*" >&2; exit 1; }
trap 'die "Aborted at line $LINENO (command: $BASH_COMMAND)"' ERR

# --- Elevation ---------------------------------------------------------------
if [[ "$(id -u)" -eq 0 ]]; then SUDO=""; else
    command -v sudo >/dev/null 2>&1 || die "Run as root or install sudo."
    SUDO="sudo"
fi
# Run a command as the service user, whether we started as root or via sudo.
# (When already root, $SUDO is empty; 'sudo -u' flags would be misparsed, so use
#  runuser instead and set HOME explicitly for ~/.ssh, ~/.gitconfig resolution.)
run_as_service() {
    if [[ -z "$SUDO" ]]; then
        runuser -u "$SERVICE_USER" -- env HOME="$SERVICE_HOME" bash -c "$1"
    else
        $SUDO -u "$SERVICE_USER" -H bash -c "$1"
    fi
}

# =============================================================================
# Phase 0 — Validate
# =============================================================================
log "Phase 0: validating inputs"
[[ -n "$REPO_URL" ]] || die "REPO_URL is not set."
[[ -n "$SERVICE_HOME" ]] || die "Cannot resolve home for user '$SERVICE_USER'. Set SERVICE_USER."
id "$SERVICE_USER" >/dev/null 2>&1 || die "User '$SERVICE_USER' does not exist."
[[ -r /etc/os-release ]] || die "Cannot read /etc/os-release."
# shellcheck disable=SC1091
. /etc/os-release
[[ "${ID:-}" == "ubuntu" ]] || die "This installer targets Ubuntu (found: ${ID:-unknown})."

py_ok() { command -v "$1" >/dev/null 2>&1 && \
          [[ "$("$1" -c 'import sys;print(sys.version_info[1])' 2>/dev/null)" =~ ^[0-9]+$ ]] && \
          (( $("$1" -c 'import sys;print(sys.version_info[0])') == 3 && \
             $("$1" -c 'import sys;print(sys.version_info[1])') >= REQUIRED_PY_MINOR )); }
if [[ "$PY_BIN" == "auto" ]]; then
    PY_BIN=""
    for cand in python3.13 python3.12 python3.11 python3; do
        if py_ok "$cand"; then PY_BIN="$cand"; break; fi
    done
    [[ -n "$PY_BIN" ]] || die "No python3 >= 3.${REQUIRED_PY_MINOR} on PATH. Set PY_BIN."
else
    py_ok "$PY_BIN" || die "$PY_BIN missing or below 3.${REQUIRED_PY_MINOR}."
fi
PY_VER=$("$PY_BIN" -c 'import sys;print("%d.%d"%sys.version_info[:2])')
log "  service user : $SERVICE_USER (home: $SERVICE_HOME)"
log "  source (git) : $SRC_DIR"
log "  install (run): $INSTALL_DIR"
log "  python       : $PY_BIN ($PY_VER)"

# =============================================================================
# Phase 1 — System packages
# =============================================================================
log "Phase 1: installing system packages"
VENV_PKG="python${PY_VER}-venv"
if ! apt-cache show "$VENV_PKG" >/dev/null 2>&1; then
    log "  '$VENV_PKG' unavailable — using python3-venv metapackage"
    VENV_PKG="python3-venv"
fi
$SUDO apt-get update -y
$SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git build-essential libpq-dev rsync "$VENV_PKG"

# =============================================================================
# Phase 2 — Confirm service user (already exists as login user 'ubec')
# =============================================================================
log "Phase 2: service user"
log "  using existing user '$SERVICE_USER' — no creation needed"

# =============================================================================
# Phase 3 — SSH deploy key (only for SSH URLs)
# =============================================================================
GIT_ENV=""
if [[ "$REPO_URL" == git@* || "$REPO_URL" == ssh://* ]]; then
    log "Phase 3: SSH deploy key for '$SERVICE_USER'"
    SSH_DIR="$SERVICE_HOME/.ssh"
    KEY="$SSH_DIR/id_ed25519_ubec"
    KNOWN="$SSH_DIR/known_hosts"
    CFG="$SSH_DIR/config"
    run_as_service "mkdir -p '$SSH_DIR' && chmod 700 '$SSH_DIR'"
    if ! $SUDO test -f "$KEY"; then
        run_as_service "ssh-keygen -t ed25519 -N '' -C 'ubec-bio-deploy@$(hostname)' -f '$KEY'"
        log "  generated deploy key"
    fi
    run_as_service "ssh-keyscan -t ed25519,rsa github.com >> '$KNOWN' 2>/dev/null; sort -u '$KNOWN' -o '$KNOWN'; chmod 644 '$KNOWN'"

    # Standard, robust approach: pin the deploy key to github.com in ssh config.
    # After this, a plain 'ssh -T git@github.com' and 'git clone git@...' both use
    # the key automatically — no -i or GIT_SSH_COMMAND needed anywhere.
    if ! run_as_service "grep -q '# ubec-bio-deploy' '$CFG' 2>/dev/null"; then
        run_as_service "cat >> '$CFG' <<'SSHCFG'

# ubec-bio-deploy (managed by install_ubec.sh)
Host github.com
    HostName github.com
    User git
    IdentityFile $KEY
    IdentitiesOnly yes
SSHCFG
chmod 600 '$CFG'"
        log "  wrote ssh config entry pinning the deploy key to github.com"
    fi

    # Auth check now matches exactly what git will do (plain ssh via config).
    if run_as_service "ssh -o BatchMode=yes -T git@github.com 2>&1 | grep -q 'successfully authenticated'"; then
        log "  GitHub accepts the deploy key"
    else
        echo
        echo "==================================================================="
        echo " ACTION REQUIRED — GitHub is not yet accepting this key."
        echo " Add it as a READ-ONLY deploy key, then re-run this script:"
        echo "   github.com/ubeccommon/ubec_main > Settings > Deploy keys > Add"
        echo "   (leave 'Allow write access' UNCHECKED)"
        echo "-------------------------------------------------------------------"
        $SUDO cat "$KEY.pub"
        echo "-------------------------------------------------------------------"
        echo " Verify manually with:"
        echo "   sudo -u $SERVICE_USER ssh -T git@github.com"
        echo " Then:  sudo bash install_ubec.sh"
        echo "==================================================================="
        exit 0
    fi
fi

# =============================================================================
# Phase 4 — Ensure repo in SRC_DIR (source of truth)
# =============================================================================
log "Phase 4: syncing git working tree at $SRC_DIR (ref: $REPO_REF)"
run_as_service "mkdir -p '$SRC_DIR'"
if $SUDO test -d "$SRC_DIR/.git"; then
    log "  existing repo — fetch + hard reset to origin/$REPO_REF"
    run_as_service "cd '$SRC_DIR' && git remote set-url origin '$REPO_URL' && $GIT_ENV git fetch --all --tags --prune && git checkout '$REPO_REF' && git reset --hard 'origin/$REPO_REF'"
else
    log "  adopting $SRC_DIR as a checkout (untracked files preserved)"
    run_as_service "cd '$SRC_DIR' && git init -q && (git remote add origin '$REPO_URL' 2>/dev/null || git remote set-url origin '$REPO_URL') && $GIT_ENV git fetch --depth 1 origin '$REPO_REF' && git checkout -f -B '$REPO_REF' FETCH_HEAD"
fi
$SUDO test -f "$SRC_DIR/main.py" || die "main.py not found in $SRC_DIR — wrong repo or ref?"
$SUDO test -f "$SRC_DIR/requirements.txt" || die "requirements.txt not found in $SRC_DIR. Add the generated requirements.txt to the repo root, then re-run."

# =============================================================================
# Phase 5 — Deploy clean copy to INSTALL_DIR
# =============================================================================
log "Phase 5: deploying runtime copy to $INSTALL_DIR"
for d in "$INSTALL_DIR" "$DATA_DIR" "$LOG_DIR" "$CONFIG_DIR"; do $SUDO mkdir -p "$d"; done
RSYNC_ARGS=(-a --delete)
for ex in "${DEPLOY_EXCLUDES[@]}"; do RSYNC_ARGS+=(--exclude "$ex"); done
$SUDO rsync "${RSYNC_ARGS[@]}" "$SRC_DIR"/ "$INSTALL_DIR"/
$SUDO chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR" "$DATA_DIR" "$LOG_DIR"
$SUDO chmod 750 "$INSTALL_DIR" "$DATA_DIR" "$LOG_DIR" "$CONFIG_DIR"

# =============================================================================
# Phase 6 — Python venv + dependencies (in INSTALL_DIR)
# =============================================================================
log "Phase 6: virtualenv + dependencies"
if ! $SUDO test -x "$INSTALL_DIR/venv/bin/python"; then
    run_as_service "$PY_BIN -m venv '$INSTALL_DIR/venv'"
    log "  created venv"
fi
run_as_service "'$INSTALL_DIR/venv/bin/pip' install --upgrade pip"
run_as_service "'$INSTALL_DIR/venv/bin/pip' install -r '$INSTALL_DIR/requirements.txt'"
run_as_service "'$INSTALL_DIR/venv/bin/python' -c 'import stellar_sdk, asyncpg, fastapi; print(\"deps OK — stellar-sdk\", stellar_sdk.__version__)'"

# =============================================================================
# Phase 7 — Config file (single source of truth)
# =============================================================================
log "Phase 7: $CONFIG_DIR/environment"
if $SUDO test -f "$CONFIG_DIR/environment"; then
    log "  environment file present — left untouched"
elif $SUDO test -f "$SRC_DIR/env.example"; then
    $SUDO cp "$SRC_DIR/env.example" "$CONFIG_DIR/environment"
    log "  seeded from env.example — EDIT real credentials"
elif $SUDO test -f "$SRC_DIR/.env.example"; then
    $SUDO cp "$SRC_DIR/.env.example" "$CONFIG_DIR/environment"
    log "  seeded from .env.example — EDIT real credentials"
else
    $SUDO tee "$CONFIG_DIR/environment" >/dev/null <<EOF
# UBEC bioregion production environment — fill in real values.
UBEC_ENV=production
UBEC_BASE_DIR=$INSTALL_DIR
UBEC_DATA_DIR=$DATA_DIR
UBEC_LOG_DIR=$LOG_DIR
UBEC_CONFIG_DIR=$CONFIG_DIR
LOG_LEVEL=INFO
LOG_FILE=$LOG_DIR/ubec.log
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ubec_protocol
DB_USER=ubec_admin
DB_PASSWORD=CHANGE_ME
DB_SCHEMA=ubec_main
STELLAR_NETWORK=PUBLIC
STELLAR_HORIZON_URL=https://horizon.stellar.org
EOF
    log "  wrote template — EDIT real credentials"
fi
$SUDO chown root:"$SERVICE_USER" "$CONFIG_DIR/environment"
$SUDO chmod 640 "$CONFIG_DIR/environment"

# =============================================================================
# Phase 8 — systemd unit
# =============================================================================
log "Phase 8: systemd unit '$SERVICE_NAME.service'"
$SUDO tee "/etc/systemd/system/$SERVICE_NAME.service" >/dev/null <<EOF
[Unit]
Description=UBEC Protocol (bioregional.ubec.network)
After=network-online.target postgresql.service
Wants=network-online.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$CONFIG_DIR/environment
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/main.py
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=$DATA_DIR $LOG_DIR

[Install]
WantedBy=multi-user.target
EOF
$SUDO systemctl daemon-reload
log "  unit installed (not started)"

# =============================================================================
# Done
# =============================================================================
cat <<EOF

===================================================================
 Bioregion node deployed
===================================================================
 Source (git)  : $SRC_DIR        (edit + git pull here)
 Runtime        : $INSTALL_DIR    (deployed copy; do not edit directly)
 Service user   : $SERVICE_USER
 Config         : $CONFIG_DIR/environment   (edit real credentials!)
 Logs / Data    : $LOG_DIR  /  $DATA_DIR

 NEXT STEPS:
   1. sudo nano $CONFIG_DIR/environment
   2. Initialise DB schema if fresh (confirm the real path in the repo), e.g.:
        psql -U ubec_admin -d ubec -f $INSTALL_DIR/database/schema/ubec_main_schema.sql
   3. sudo systemctl enable --now $SERVICE_NAME.service
   4. systemctl status $SERVICE_NAME.service ; journalctl -u $SERVICE_NAME -f

 To redeploy after 'git pull' in $SRC_DIR: just re-run  sudo bash install_ubec.sh
===================================================================
EOF
