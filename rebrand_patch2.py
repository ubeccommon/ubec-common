#!/usr/bin/env python3
"""
rebrand_patch2.py — second pass for files missed in first run
Patches:
  - /srv/ubec/portal/legal.html, terms.html, privacy.html, contact.html
  - /srv/ubec/portal/index.html  (redirect stub title)
  - aria-label in portal/en, de, pl index.html (service card self-link)
License: GNU AGPL v3.0
"""

import re
import pathlib
import datetime

BASE  = pathlib.Path('/srv/ubec')
SHORT = 'UBEC DAO'
FULL  = 'Ubuntu Bioregional Economic Commons DAO'


def replace_safe(text, old, new):
    """Replace old→new except when immediately preceded by = / ' "."""
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


def patch(text):
    # Page title
    text = re.sub(r'—\s*UBEC Commons(<)', f'— {SHORT}\\1', text)

    # footer__brand-name
    text = re.sub(
        r'(<div class="footer__brand-name">)UBEC Commons(</div>)',
        f'\\1{SHORT}\\2', text
    )

    # footer__brand-desc expansion
    text = re.sub(
        r'(<p class="footer__brand-desc">\s*)A Web 4\.0',
        f'\\1{FULL} — a Web 4.0', text, count=1
    )

    # Copyright
    text = re.sub(
        r'©\s*(?:2024[–-])?2026\s*UBEC Commons',
        '© 2024–2026 Michel Garand', text
    )

    # Specific body phrases
    text = text.replace('UBEC Commons living-lab initiative', f'{SHORT} living-lab initiative')
    text = text.replace('UBEC Commons Living-Lab-Initiative', f'{SHORT} Living-Lab-Initiative')
    text = text.replace('grant UBEC Commons a', f'grant {SHORT} a')
    text = text.replace('UBEC Commons eine nicht-exklusive', f'{SHORT} eine nicht-exklusive')
    text = text.replace('UBEC Commons ist eine', f'{SHORT} ist eine')
    text = text.replace('UBEC Commons is a', f'{SHORT} is a')
    text = text.replace('any UBEC Commons service', f'any {SHORT} service')

    # aria-label on portal self-link cards
    text = re.sub(
        r'aria-label="UBEC Commons Portal —',
        f'aria-label="{SHORT} Portal —', text
    )

    # Redirect stub title
    text = re.sub(
        r'<title>UBEC Commons\s*—\s*Redirect',
        f'<title>{SHORT} — Redirect', text
    )

    # All remaining safe replacements
    text = replace_safe(text, 'UBEC Commons', SHORT)

    return text


FILES = [
    'portal/legal.html',
    'portal/terms.html',
    'portal/privacy.html',
    'portal/contact.html',
    'portal/index.html',
    'portal/en/index.html',
    'portal/de/index.html',
    'portal/pl/index.html',
]

def main():
    print("rebrand_patch2.py — second pass")
    print("=" * 40)
    changed, skipped, missing = [], [], []

    for rel in FILES:
        p = BASE / rel
        if not p.exists():
            print(f"  ! NOT FOUND: {rel}"); missing.append(rel); continue
        orig = p.read_text(encoding='utf-8')
        new  = patch(orig)
        if new == orig:
            print(f"  ~ no change: {rel}"); skipped.append(rel)
        else:
            p.write_text(new, encoding='utf-8')
            print(f"  ✓ patched:   {rel}"); changed.append(rel)

    print(f"\n  Changed: {len(changed)}  Skipped: {len(skipped)}  Missing: {len(missing)}")
    print(f"\nDone — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nFinal verify:")
    print("  grep -r 'UBEC Commons' /srv/ubec/portal /srv/ubec/legal /srv/ubec/design-cdn \\")
    print("    --include='*.html' --include='*.js'")

if __name__ == '__main__':
    main()
