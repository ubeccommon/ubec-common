#!/usr/bin/env bash
#
# 00_preflight_check.sh — UBEC Protocol Suite production preflight check
#
# Purpose:
#   READ-ONLY inspection of a target server to report exactly which resources
#   are available before attempting a production install. Makes NO changes.
#   Run this first, review the PASS/FAIL summary, then run install_ubec.sh.
#
# Usage:
#   bash 00_preflight_check.sh
#
# Exit codes:
#   0  all mandatory checks passed
#   1  one or more mandatory checks failed
#
# Design principle alignment:
#   #4 Single source of truth  — reports facts only, changes nothing
#   #6 No sync fallbacks        — no silent defaults; every gap is reported
#   #11 Comprehensive docs      — self-documenting output
#
# License (code): GNU Affero General Public License v3.0
#
# Attribution:
#   This project uses the services of Claude and Anthropic PBC to inform our
#   decisions and recommendations. This project was made possible with the
#   assistance of Claude and Anthropic PBC.

set -uo pipefail

# --- Requirements (edit only if your standards change) -----------------------
REQUIRED_PY_MAJOR=3
REQUIRED_PY_MINOR=11          # Python 3.11+
REQUIRED_PG_MAJOR=15          # PostgreSQL 15+
REQUIRED_RAM_MB=4096          # 4 GB minimum (8 GB recommended)
RECOMMENDED_RAM_MB=8192
REQUIRED_DISK_MB=5120         # 5 GB free on install target
INSTALL_TARGET="/opt"        # where /opt/ubec will live
STELLAR_HOST="horizon.stellar.org"
GIT_HOST="github.com"

# --- Output helpers ----------------------------------------------------------
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

green()  { printf '\033[0;32m%s\033[0m\n' "$*"; }
red()    { printf '\033[0;31m%s\033[0m\n' "$*"; }
yellow() { printf '\033[0;33m%s\033[0m\n' "$*"; }

ok()   { green  "  [ PASS ] $*"; PASS_COUNT=$((PASS_COUNT+1)); }
bad()  { red    "  [ FAIL ] $*"; FAIL_COUNT=$((FAIL_COUNT+1)); }
warn() { yellow "  [ WARN ] $*"; WARN_COUNT=$((WARN_COUNT+1)); }
info() { printf '  [ INFO ] %s\n' "$*"; }
head() { printf '\n=== %s ===\n' "$*"; }

# --- 1. Operating system -----------------------------------------------------
head "Operating System"
if [[ -r /etc/os-release ]]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    info "Detected: ${PRETTY_NAME:-unknown}"
    if [[ "${ID:-}" == "ubuntu" ]]; then
        case "${VERSION_ID:-}" in
            24.04|22.04) ok "Ubuntu ${VERSION_ID} (supported)";;
            *) warn "Ubuntu ${VERSION_ID:-?} — install targets 22.04/24.04 LTS; proceed with care";;
        esac
    else
        warn "Non-Ubuntu distro (${ID:-?}) — package steps in the installer assume apt/Ubuntu"
    fi
    info "Kernel: $(uname -r)   Arch: $(uname -m)"
else
    bad "/etc/os-release not readable — cannot identify OS"
fi

# --- 2. Privileges -----------------------------------------------------------
head "Privileges"
if [[ "$(id -u)" -eq 0 ]]; then
    ok "Running as root"
elif command -v sudo >/dev/null 2>&1; then
    ok "sudo available ($(command -v sudo)) — installer will use it"
else
    bad "Not root and sudo not found — installer needs elevated privileges"
fi

# --- 3. Python ---------------------------------------------------------------
head "Python"
PY_BIN=""
for cand in python3.11 python3; do
    if command -v "$cand" >/dev/null 2>&1; then PY_BIN="$cand"; break; fi
done
if [[ -n "$PY_BIN" ]]; then
    PV=$("$PY_BIN" -c 'import sys;print("%d.%d.%d"%sys.version_info[:3])' 2>/dev/null)
    PMAJ=$("$PY_BIN" -c 'import sys;print(sys.version_info[0])' 2>/dev/null)
    PMIN=$("$PY_BIN" -c 'import sys;print(sys.version_info[1])' 2>/dev/null)
    info "Found $PY_BIN -> Python ${PV}"
    if (( PMAJ > REQUIRED_PY_MAJOR || (PMAJ == REQUIRED_PY_MAJOR && PMIN >= REQUIRED_PY_MINOR) )); then
        ok "Python ${PV} meets >= ${REQUIRED_PY_MAJOR}.${REQUIRED_PY_MINOR}"
    else
        bad "Python ${PV} is below required ${REQUIRED_PY_MAJOR}.${REQUIRED_PY_MINOR}"
    fi
    if "$PY_BIN" -m venv --help >/dev/null 2>&1; then
        ok "venv module available"
    else
        bad "venv module missing — install python3.11-venv"
    fi
else
    bad "No python3 interpreter found"
fi

# --- 4. PostgreSQL -----------------------------------------------------------
head "PostgreSQL"
if command -v psql >/dev/null 2>&1; then
    PG_RAW=$(psql --version 2>/dev/null | awk '{print $3}')
    PG_MAJ=${PG_RAW%%.*}
    info "psql client: ${PG_RAW}"
    if [[ -n "$PG_MAJ" ]] && (( PG_MAJ >= REQUIRED_PG_MAJOR )); then
        ok "PostgreSQL client ${PG_RAW} meets >= ${REQUIRED_PG_MAJOR}"
    else
        warn "PostgreSQL client ${PG_RAW} below ${REQUIRED_PG_MAJOR} (DB may be on another host)"
    fi
else
    warn "psql not found — OK only if the database runs on a separate host"
fi
if command -v pg_isready >/dev/null 2>&1; then
    if pg_isready -q >/dev/null 2>&1; then
        ok "Local PostgreSQL server is accepting connections"
    else
        info "pg_isready: no local server responding (expected if DB is remote)"
    fi
fi

# --- 5. System packages ------------------------------------------------------
head "Build / System Packages"
for pkg_cmd in "git:git" "gcc:build-essential" "pg_config:libpq-dev"; do
    cmd=${pkg_cmd%%:*}; pkg=${pkg_cmd##*:}
    if command -v "$cmd" >/dev/null 2>&1; then
        ok "$cmd present (package: $pkg)"
    else
        warn "$cmd missing — installer will apt-install '$pkg'"
    fi
done

# --- 6. Memory ---------------------------------------------------------------
head "Memory"
if [[ -r /proc/meminfo ]]; then
    MEM_KB=$(awk '/MemTotal/{print $2}' /proc/meminfo)
    MEM_MB=$(( MEM_KB / 1024 ))
    info "Total RAM: ${MEM_MB} MB"
    if (( MEM_MB >= RECOMMENDED_RAM_MB )); then
        ok "RAM ${MEM_MB} MB meets recommended ${RECOMMENDED_RAM_MB} MB"
    elif (( MEM_MB >= REQUIRED_RAM_MB )); then
        warn "RAM ${MEM_MB} MB meets minimum but below recommended ${RECOMMENDED_RAM_MB} MB"
    else
        bad "RAM ${MEM_MB} MB below minimum ${REQUIRED_RAM_MB} MB"
    fi
else
    warn "/proc/meminfo unreadable — cannot verify RAM"
fi

# --- 7. Disk -----------------------------------------------------------------
head "Disk"
if DF_AVAIL_MB=$(df -Pm "$INSTALL_TARGET" 2>/dev/null | awk 'NR==2{print $4}'); then
    info "Free on ${INSTALL_TARGET}: ${DF_AVAIL_MB} MB"
    if (( DF_AVAIL_MB >= REQUIRED_DISK_MB )); then
        ok "Disk ${DF_AVAIL_MB} MB free meets >= ${REQUIRED_DISK_MB} MB"
    else
        bad "Disk ${DF_AVAIL_MB} MB free below required ${REQUIRED_DISK_MB} MB"
    fi
else
    warn "Could not read free space on ${INSTALL_TARGET}"
fi

# --- 8. Network reachability -------------------------------------------------
head "Network"
check_host() {
    local host="$1" port="$2" label="$3"
    if command -v nc >/dev/null 2>&1; then
        if nc -z -w5 "$host" "$port" >/dev/null 2>&1; then ok "$label reachable ($host:$port)"; else bad "$label unreachable ($host:$port)"; fi
    elif command -v curl >/dev/null 2>&1; then
        if curl -sS --connect-timeout 5 -o /dev/null "https://$host" >/dev/null 2>&1; then ok "$label reachable (https://$host)"; else bad "$label unreachable (https://$host)"; fi
    else
        warn "Neither nc nor curl present — cannot test $label"
    fi
}
check_host "$STELLAR_HOST" 443 "Stellar Horizon"
check_host "$GIT_HOST" 443 "GitHub"

# --- Summary -----------------------------------------------------------------
head "Summary"
printf '  PASS: %s   WARN: %s   FAIL: %s\n' "$PASS_COUNT" "$WARN_COUNT" "$FAIL_COUNT"
echo
if (( FAIL_COUNT > 0 )); then
    red "Preflight FAILED — resolve the FAIL items above before installing."
    exit 1
else
    if (( WARN_COUNT > 0 )); then
        yellow "Preflight passed with warnings — review WARN items, then proceed."
    else
        green "Preflight passed cleanly — safe to run install_ubec.sh."
    fi
    exit 0
fi
