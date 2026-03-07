# UBEC Legal Pages — Deployment Package

## Contents

```
deploy_legal_pages.py   ← deployment script (run this)
legal/
  legal.html            ← Impressum (DE authoritative + EN)
  privacy.html          ← Privacy Policy / Datenschutzerklärung
  terms.html            ← Terms of Service / Nutzungsbedingungen
  contact.html          ← Contact / Kontakt (mailto fallback)
```

## What the script does

1. Creates `/srv/ubec/legal/` and copies the four HTML files into it
2. Adds `location ^~ /legal|privacy|terms|contact` alias blocks to:
   - `/etc/nginx/sites-enabled/ubec.network`
   - `/etc/nginx/sites-enabled/living-labs.ubec.network`
   - `/etc/nginx/sites-enabled/iot.ubec.network`
   - `/etc/nginx/sites-enabled/learn.ubec.network`
3. Updates the `.legal-footer` div in living-labs EN/DE/PL index pages
   to use relative paths (`/legal`, `/privacy` etc.) — no cross-domain redirect
4. Runs `nginx -t` before reloading — auto-restores backups if test fails
5. Commits and pushes everything to git

Backups of all modified files are saved to `/srv/ubec/staging/backups/nginx-TIMESTAMP/`

## Prerequisites

- Script must run as a user with `sudo`-equivalent rights to edit
  `/etc/nginx/sites-enabled/` and reload nginx
- The `legal/` directory must be in the same folder as the script
- Git remote must be configured (`git push` will run automatically)

## Usage

```bash
# Upload this package to /srv/ubec on ubec-common, then:
cd /srv/ubec

# Dry run first — no changes made, just prints what would happen
sudo python3 deploy_legal_pages.py --dry-run

# Full deployment
sudo python3 deploy_legal_pages.py
```

## Verify after deployment

```bash
curl -sI https://ubec.network/legal          | grep -E 'HTTP|Content-Type'
curl -sI https://living-labs.ubec.network/legal | grep -E 'HTTP|Content-Type'
curl -sI https://iot.ubec.network/legal      | grep -E 'HTTP|Content-Type'
curl -sI https://learn.ubec.network/legal    | grep -E 'HTTP|Content-Type'
```

All four should return `HTTP/2 200` and `content-type: text/html`.

## Updating legal content in future

Edit the files in `/srv/ubec/legal/` directly. No nginx changes needed.
Commit and push:

```bash
cd /srv/ubec
git add legal/
git commit -m "docs(legal): update privacy policy — [describe change]"
git push
```

## Architecture note

`/srv/ubec/legal/` is the single canonical source.
nginx `alias` directives serve the same files under every domain.
Visitors never leave their domain to read legal pages.
No symlinks. No file duplication. One update propagates everywhere instantly.
