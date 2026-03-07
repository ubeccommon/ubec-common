#!/usr/bin/env python3
"""
deploy_legal_pages.py
=====================
Deploys canonical legal pages to /srv/ubec/legal/ and adds
location ^~ /legal  alias blocks to all relevant nginx vhosts.

Services covered:
  ubec.network              /srv/ubec/portal/
  living-labs.ubec.network  /srv/ubec/living-labs/
  iot.ubec.network          proxy vhost (FastAPI)
  learn.ubec.network        /srv/ubec/learn/

Single source of truth: /srv/ubec/legal/
Served under every domain at /legal, /privacy, /terms, /contact
without redirecting to another domain.

Usage:
  python3 deploy_legal_pages.py [--dry-run]

Requires: sudo for nginx config edits and reload.
Goethean principle: script only acts on observable facts.
Every destructive step is preceded by a backup.

License: GNU AGPL v3.0
"""

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────
LEGAL_DIR   = Path("/srv/ubec/legal")
NGINX_DIR   = Path("/etc/nginx/sites-enabled")
BACKUP_DIR  = Path("/srv/ubec/staging/backups/nginx-" +
                   datetime.now().strftime("%Y%m%d-%H%M%S"))

VHOSTS = {
    "ubec.network": {
        "path": NGINX_DIR / "ubec.network",
        # Insert before closing brace of the ssl server block
        # Portal already serves legal pages from /srv/ubec/portal/
        # — we use alias so /srv/ubec/legal/ is canonical.
        "insert_before": "    location ~ /\\.",
        "alias_block": """\
    # ── Canonical legal pages (shared across all domains) ─────────────
    location ^~ /legal  { alias /srv/ubec/legal/legal.html;   add_header Cache-Control "public, max-age=3600" always; }
    location ^~ /privacy { alias /srv/ubec/legal/privacy.html; add_header Cache-Control "public, max-age=3600" always; }
    location ^~ /terms  { alias /srv/ubec/legal/terms.html;   add_header Cache-Control "public, max-age=3600" always; }
    location ^~ /contact { alias /srv/ubec/legal/contact.html; add_header Cache-Control "public, max-age=3600" always; }

""",
    },
    "living-labs.ubec.network": {
        "path": NGINX_DIR / "living-labs.ubec.network",
        # Insert before location /
        "insert_before": "    location / {",
        "alias_block": """\
    # ── Canonical legal pages (shared across all domains) ─────────────
    location ^~ /legal   {
        alias /srv/ubec/legal/legal.html;
        default_type text/html;
        add_header Cache-Control "public, max-age=3600" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
    location ^~ /privacy {
        alias /srv/ubec/legal/privacy.html;
        default_type text/html;
        add_header Cache-Control "public, max-age=3600" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
    location ^~ /terms   {
        alias /srv/ubec/legal/terms.html;
        default_type text/html;
        add_header Cache-Control "public, max-age=3600" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
    location ^~ /contact {
        alias /srv/ubec/legal/contact.html;
        default_type text/html;
        add_header Cache-Control "public, max-age=3600" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }

""",
    },
    "iot.ubec.network": {
        "path": NGINX_DIR / "iot.ubec.network",
        # Insert before location = / (exact match landing page)
        "insert_before": "    # Landing page",
        "alias_block": """\
    # ── Canonical legal pages (shared across all domains) ─────────────
    # ^~ takes priority over the proxy location / below
    location ^~ /legal   {
        alias /srv/ubec/legal/legal.html;
        default_type text/html;
        add_header Cache-Control "public, max-age=3600" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
    location ^~ /privacy {
        alias /srv/ubec/legal/privacy.html;
        default_type text/html;
        add_header Cache-Control "public, max-age=3600" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
    location ^~ /terms   {
        alias /srv/ubec/legal/terms.html;
        default_type text/html;
        add_header Cache-Control "public, max-age=3600" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
    location ^~ /contact {
        alias /srv/ubec/legal/contact.html;
        default_type text/html;
        add_header Cache-Control "public, max-age=3600" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }

""",
    },
    "learn.ubec.network": {
        "path": NGINX_DIR / "learn.ubec.network",
        # learn has headers in server block (inheritance bug risk).
        # Insert before location / — we repeat headers in alias blocks.
        "insert_before": "    location / {",
        "alias_block": """\
    # ── Canonical legal pages (shared across all domains) ─────────────
    # Headers repeated here — learn vhost has them in server block which
    # would be silently dropped if we relied on inheritance (nginx bug).
    location ^~ /legal   {
        alias /srv/ubec/legal/legal.html;
        default_type text/html;
        add_header Cache-Control "public, max-age=3600" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
    location ^~ /privacy {
        alias /srv/ubec/legal/privacy.html;
        default_type text/html;
        add_header Cache-Control "public, max-age=3600" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
    location ^~ /terms   {
        alias /srv/ubec/legal/terms.html;
        default_type text/html;
        add_header Cache-Control "public, max-age=3600" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
    location ^~ /contact {
        alias /srv/ubec/legal/contact.html;
        default_type text/html;
        add_header Cache-Control "public, max-age=3600" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }

""",
    },
}

# Living-labs footer patches — replace .legal-footer div in each index.html
LIVING_LABS_ROOT = Path("/srv/ubec/living-labs")

FOOTER_PATCHES = {
    "en": {
        "file": LIVING_LABS_ROOT / "en/index.html",
        "old_marker": '<div class="legal-footer">',
        "new_block": """\
  <div class="legal-footer">
    <nav aria-label="Legal links">
      <a href="/legal">Imprint</a>
      <a href="/privacy">Privacy Policy</a>
      <a href="/terms">Terms of Service</a>
      <a href="/contact">Contact</a>
      <a href="https://iot.ubec.network/docs">API Docs</a>
    </nav>
    <p>UBEC Living Labs · Citizen Science Network · Müllrose, Brandenburg<br>
    <em>This project uses the services of Claude and Anthropic PBC.</em></p>
  </div>""",
    },
    "de": {
        "file": LIVING_LABS_ROOT / "de/index.html",
        "old_marker": '<div class="legal-footer">',
        "new_block": """\
  <div class="legal-footer">
    <nav aria-label="Legal links">
      <a href="/legal">Impressum</a>
      <a href="/privacy">Datenschutz</a>
      <a href="/terms">Nutzungsbedingungen</a>
      <a href="/contact">Kontakt</a>
      <a href="https://iot.ubec.network/docs">API-Dokumentation</a>
    </nav>
    <p>UBEC Living Labs · Citizen-Science-Netzwerk · Müllrose, Brandenburg<br>
    <em>Dieses Projekt wurde mit Unterstützung von Claude (Anthropic) entwickelt.</em></p>
  </div>""",
    },
    "pl": {
        "file": LIVING_LABS_ROOT / "pl/index.html",
        "old_marker": '<div class="legal-footer">',
        "new_block": """\
  <div class="legal-footer">
    <nav aria-label="Legal links">
      <a href="/legal">Nota prawna</a>
      <a href="/privacy">Polityka prywatności</a>
      <a href="/terms">Warunki korzystania</a>
      <a href="/contact">Kontakt</a>
      <a href="https://iot.ubec.network/docs">Dokumentacja API</a>
    </nav>
    <p>UBEC Living Labs · Sieć Nauki Obywatelskiej · Müllrose, Brandenburgia<br>
    <em>Projekt powstał przy wsparciu Claude (Anthropic).</em></p>
  </div>""",
    },
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def run(cmd, dry_run=False, check=True):
    print(f"  $ {cmd}")
    if not dry_run:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"  ERROR: {result.stderr.strip()}", file=sys.stderr)
            sys.exit(1)
        return result
    return None


def backup_file(path: Path, dry_run=False):
    dest = BACKUP_DIR / path.name
    print(f"  Backing up {path} → {dest}")
    if not dry_run:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)


def already_patched(path: Path, marker: str) -> bool:
    """Return True if the marker string is already in the file."""
    if not path.exists():
        return False
    return marker in path.read_text()


# ── Step 1: Create /srv/ubec/legal/ and copy files ───────────────────────────
def step_legal_dir(dry_run):
    print("\n── Step 1: Create /srv/ubec/legal/ ──────────────────────────────")
    script_dir = Path(__file__).parent
    src = script_dir / "legal"

    if not src.exists():
        print(f"  ERROR: Source directory '{src}' not found.", file=sys.stderr)
        print(f"  Expected: legal/legal.html, legal/privacy.html,", file=sys.stderr)
        print(f"            legal/terms.html, legal/contact.html", file=sys.stderr)
        sys.exit(1)

    for f in ["legal.html", "privacy.html", "terms.html", "contact.html"]:
        if not (src / f).exists():
            print(f"  ERROR: Missing source file: legal/{f}", file=sys.stderr)
            sys.exit(1)

    print(f"  Creating {LEGAL_DIR}")
    if not dry_run:
        LEGAL_DIR.mkdir(parents=True, exist_ok=True)
        for f in ["legal.html", "privacy.html", "terms.html", "contact.html"]:
            shutil.copy2(src / f, LEGAL_DIR / f)
            print(f"  Copied {f}")

    run(f"chown -R ubec:ubec {LEGAL_DIR}", dry_run)
    run(f"chmod -R 755 {LEGAL_DIR}", dry_run)
    print("  ✓ Legal directory ready")


# ── Step 2: Patch nginx vhosts ────────────────────────────────────────────────
def step_nginx(dry_run):
    print("\n── Step 2: Patch nginx vhosts ───────────────────────────────────")
    SKIP_MARKER = "# ── Canonical legal pages"

    for name, cfg in VHOSTS.items():
        vhost_path = cfg["path"]
        print(f"\n  [{name}]")

        if not vhost_path.exists():
            print(f"  SKIP — vhost file not found: {vhost_path}")
            continue

        if already_patched(vhost_path, SKIP_MARKER):
            print(f"  SKIP — already patched (marker found)")
            continue

        content = vhost_path.read_text()
        insert_before = cfg["insert_before"]

        if insert_before not in content:
            print(f"  ERROR: Insert marker not found in {vhost_path}:", file=sys.stderr)
            print(f"  Expected: '{insert_before}'", file=sys.stderr)
            sys.exit(1)

        backup_file(vhost_path, dry_run)

        new_content = content.replace(
            insert_before,
            cfg["alias_block"] + insert_before,
            1  # replace first occurrence only
        )

        print(f"  Writing patched {vhost_path}")
        if not dry_run:
            vhost_path.write_text(new_content)
        print(f"  ✓ {name} patched")

    # Test nginx config before reloading
    print("\n  Testing nginx configuration...")
    result = run("nginx -t", dry_run)
    if not dry_run and result.returncode != 0:
        print("  nginx -t FAILED. Restoring backups...", file=sys.stderr)
        for name, cfg in VHOSTS.items():
            backup = BACKUP_DIR / cfg["path"].name
            if backup.exists():
                shutil.copy2(backup, cfg["path"])
                print(f"  Restored {cfg['path']}")
        sys.exit(1)

    print("  Reloading nginx...")
    run("systemctl reload nginx", dry_run)
    print("  ✓ nginx reloaded")


# ── Step 3: Patch living-labs footers ─────────────────────────────────────────
def step_footers(dry_run):
    print("\n── Step 3: Patch living-labs .legal-footer blocks ───────────────")

    for lang, patch in FOOTER_PATCHES.items():
        fpath = patch["file"]
        print(f"\n  [{lang}] {fpath}")

        if not fpath.exists():
            print(f"  SKIP — file not found: {fpath}")
            continue

        content = fpath.read_text()
        marker = patch["old_marker"]

        if marker not in content:
            print(f"  SKIP — marker '{marker}' not found in file")
            continue

        # Find the full old block: from marker to closing </div>
        start = content.index(marker)
        # Find the matching </div> after the marker
        end = content.index("</div>", start) + len("</div>")
        old_block = content[start:end]

        if patch["new_block"].strip() == old_block.strip():
            print(f"  SKIP — already up to date")
            continue

        backup_file(fpath, dry_run)

        new_content = content[:start] + patch["new_block"] + content[end:]
        print(f"  Writing patched {fpath}")
        if not dry_run:
            fpath.write_text(new_content)
        print(f"  ✓ {lang} footer patched")


# ── Step 4: Git commit ────────────────────────────────────────────────────────
def step_git(dry_run):
    print("\n── Step 4: Git commit ───────────────────────────────────────────")
    run("cd /srv/ubec && git add -A", dry_run)
    run(
        'cd /srv/ubec && git commit -m '
        '"feat: add canonical legal pages at /srv/ubec/legal/\n\n'
        'Pages served at /legal /privacy /terms /contact on all domains\n'
        'via nginx alias blocks. No cross-domain redirect.\n'
        'Living-labs footer links updated to relative paths."',
        dry_run
    )
    run("cd /srv/ubec && git push", dry_run)
    print("  ✓ Committed and pushed")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Deploy UBEC canonical legal pages")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print actions without making any changes")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN — no files will be modified\n")

    print("=" * 60)
    print("  UBEC Legal Pages Deployment")
    print(f"  Target: {LEGAL_DIR}")
    print(f"  Backup: {BACKUP_DIR}")
    print("=" * 60)

    step_legal_dir(args.dry_run)
    step_nginx(args.dry_run)
    step_footers(args.dry_run)
    step_git(args.dry_run)

    print("\n" + "=" * 60)
    print("  Deployment complete.")
    print("  Verify:")
    print("    curl -sI https://ubec.network/legal | grep -E 'HTTP|Content-Type'")
    print("    curl -sI https://living-labs.ubec.network/legal | grep -E 'HTTP|Content-Type'")
    print("    curl -sI https://iot.ubec.network/legal | grep -E 'HTTP|Content-Type'")
    print("    curl -sI https://learn.ubec.network/legal | grep -E 'HTTP|Content-Type'")
    print("=" * 60)


if __name__ == "__main__":
    main()
