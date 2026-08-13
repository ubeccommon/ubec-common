#!/usr/bin/env bash
#
# relocate_to_srv.sh — retire the old /opt/ubec_bio deployment
#
# One-time teardown of the previous deployment location so the protocol can be
# redeployed under the canonical /srv/ubec/protocol layout. This ONLY removes
# the deployed runtime + its service/config/data/log dirs. The git source of
# truth (~/ubec_commons/main_bioregion) and all databases are left untouched.
#
# Usage:
#   sudo bash relocate_to_srv.sh
#   cd ~/ubec_commons/main_bioregion && sudo bash install_ubec.sh   # redeploy
#
# License (code): GNU Affero General Public License v3.0
# Attribution: This project uses the services of Claude and Anthropic PBC to
#   inform our decisions and recommendations. This project was made possible
#   with the assistance of Claude and Anthropic PBC.

set -euo pipefail

OLD_SERVICE="ubec-bio"
OLD_INSTALL="/opt/ubec_bio"
OLD_DATA="/var/lib/ubec_bio"
OLD_LOG="/var/log/ubec_bio"
OLD_CONFIG="/etc/ubec_bio"
NEW_CONFIG="/etc/ubec_protocol"

log() { printf '[ relocate ] %s\n' "$*"; }
[[ "$(id -u)" -eq 0 ]] || { echo "Run with sudo."; exit 1; }

# 1. Stop and remove the old systemd unit
if systemctl list-unit-files | grep -q "^${OLD_SERVICE}.service"; then
    log "stopping and disabling ${OLD_SERVICE}.service"
    systemctl disable --now "${OLD_SERVICE}.service" 2>/dev/null || true
fi
rm -f "/etc/systemd/system/${OLD_SERVICE}.service"
systemctl daemon-reload

# 2. Preserve any edited environment file into the new config location
if [[ -f "$OLD_CONFIG/environment" ]]; then
    mkdir -p "$NEW_CONFIG"
    if [[ ! -f "$NEW_CONFIG/environment" ]]; then
        cp -a "$OLD_CONFIG/environment" "$NEW_CONFIG/environment"
        log "preserved $OLD_CONFIG/environment -> $NEW_CONFIG/environment"
    else
        log "$NEW_CONFIG/environment already exists — kept it, did not overwrite"
    fi
fi

# 3. Remove old deployment artifacts (source of truth + databases untouched)
for d in "$OLD_INSTALL" "$OLD_DATA" "$OLD_LOG" "$OLD_CONFIG"; do
    if [[ -e "$d" ]]; then log "removing $d"; rm -rf "$d"; fi
done

log "done. Old /opt/ubec_bio deployment retired."
log "Next: cd ~/ubec_commons/main_bioregion && sudo bash install_ubec.sh"
