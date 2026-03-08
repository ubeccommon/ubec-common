#!/usr/bin/env python3
"""
rebrand_ubec_dao.py — UBEC Commons → UBEC DAO brand rename
===========================================================
License: GNU AGPL v3.0
This project uses the services of Claude and Anthropic PBC.
"""

import re
import pathlib
import datetime

BASE      = pathlib.Path('/srv/ubec')
FULL_NAME = 'Ubuntu Bioregional Economic Commons DAO'
SHORT     = 'UBEC DAO'

HTML_FILES = [
    'portal/en/index.html',
    'portal/de/index.html',
    'portal/pl/index.html',
    'legal/en/legal.html',
    'legal/en/privacy.html',
    'legal/en/terms.html',
    'legal/en/contact.html',
    'legal/de/legal.html',
    'legal/de/privacy.html',
    'legal/de/terms.html',
    'legal/de/contact.html',
    'legal/pl/legal.html',
    'legal/pl/privacy.html',
    'legal/pl/terms.html',
    'legal/pl/contact.html',
    'legal/legal.html',
    'legal/privacy.html',
    'legal/terms.html',
    'legal/contact.html',
    'hub/templates/index.html',
    'living-labs/en/index.html',
    'living-labs/de/index.html',
    'living-labs/pl/index.html',
]

JS_FILES = [
    'design-cdn/v1/ubec-nav.js',
]


def replace_safe(text, old, new):
    """Replace `old` with `new` only when not inside an HTML attribute value
    (i.e. not immediately preceded by = / ' ")."""
    parts = text.split(old)
    result = [parts[0]]
    for part in parts[1:]:
        prev = result[-1]
        if prev and prev[-1] in ('=', '/', "'", '"'):
            result.append(old)
        else:
            result.append(new)
        result.append(part)
    return ''.join(result)


def patch_js(text):
    text = text.replace("UBEC\\u00a0Commons", "UBEC\\u00a0DAO")
    text = text.replace("label: 'UBEC Commons'", "label: 'UBEC DAO'")
    return text


def patch_html(text):
    # 1. Page title
    text = re.sub(r'—\s*UBEC Commons(<)', f'— {SHORT}\\1', text)

    # 2. footer__brand-name
    text = re.sub(
        r'(<div class="footer__brand-name">)UBEC Commons(</div>)',
        f'\\1{SHORT}\\2', text
    )

    # 3. footer__brand-desc — expand first "A Web 4.0" to include full name
    text = re.sub(
        r'(<p class="footer__brand-desc">\s*)A Web 4\.0',
        f'\\1{FULL_NAME} — a Web 4.0',
        text, count=1
    )

    # 4. Copyright line
    text = re.sub(
        r'©\s*(?:2024[–-])?2026\s*UBEC Commons',
        '© 2024–2026 Michel Garand',
        text
    )

    # 5. Specific body-text phrases
    text = text.replace('UBEC Commons living-lab initiative', f'{SHORT} living-lab initiative')
    text = text.replace('grant UBEC Commons a', f'grant {SHORT} a')

    # 6. All remaining "UBEC Commons" — safe replacement (skips attribute values)
    text = replace_safe(text, 'UBEC Commons', SHORT)

    return text


def main():
    print("rebrand_ubec_dao.py — UBEC Commons → UBEC DAO")
    print("=" * 48)

    changed, skipped, missing = [], [], []

    print("\n[JS]")
    for rel in JS_FILES:
        p = BASE / rel
        if not p.exists():
            print(f"  ! NOT FOUND: {rel}"); missing.append(rel); continue
        orig = p.read_text(encoding='utf-8')
        new  = patch_js(orig)
        if new == orig:
            print(f"  ~ no change: {rel}"); skipped.append(rel)
        else:
            p.write_text(new, encoding='utf-8')
            print(f"  ✓ patched:   {rel}"); changed.append(rel)

    print("\n[HTML]")
    for rel in HTML_FILES:
        p = BASE / rel
        if not p.exists():
            print(f"  ! NOT FOUND: {rel}"); missing.append(rel); continue
        orig = p.read_text(encoding='utf-8')
        new  = patch_html(orig)
        if new == orig:
            print(f"  ~ no change: {rel}"); skipped.append(rel)
        else:
            p.write_text(new, encoding='utf-8')
            print(f"  ✓ patched:   {rel}"); changed.append(rel)

    print(f"\n{'─'*48}")
    print(f"  Changed : {len(changed)}")
    print(f"  Skipped : {len(skipped)}")
    print(f"  Missing : {len(missing)}  (not deployed yet — not an error)")
    print(f"\nDone — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nVerify:")
    print("  grep -r 'UBEC Commons' /srv/ubec/portal /srv/ubec/legal /srv/ubec/design-cdn")

if __name__ == '__main__':
    main()
