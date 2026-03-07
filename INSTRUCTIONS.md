---

## Changes in v1.8 (March 2026)

### ubec-nav.js upgraded to v3

**Previous behaviour (v1/v2):** Lang buttons were unstyled, no service identity in logo,
no login button. Each service implemented its own workaround header (`ll-header` on
living-labs).

**v3 behaviour (current):**
- Logo area renders the **active service identity** (icon + name + subtitle) from
  `data-ubec-service` attribute on `<html>` — not a generic "UBEC Commons" text
- Service links list **excludes** the active service (no self-link)
- Language switcher is right-aligned via `margin-left: auto` on `.ubec-nav__lang-switcher`
- **Login button** at far right — `https://iot.ubec.network/login` — label localised
  by current language: EN → "Sign in", DE → "Anmelden", PL → "Zaloguj"
- Falls back to "Sign in" on services with no lang prefix (portal, hub)

**SUBTITLES map** (canonical — do not rename):
```javascript
'portal':      'Bioregional Commons'
'protocol':    'Bioregional Protocol Network'
'maps':        'Bioregional GIS'
'living-labs': 'Citizen Science Network'
'hub':         'Central API & IoT Integration'
'erdpuls':     'Flagship Living Lab · Müllrose'
'open':        'Developer Commons'
'learn':       'Pattern Language of Place'
```

**Login architecture note:** The login button points to `iot.ubec.network/login`.
The Hub holds the single steward identity store. RBAC (roles/permissions per service)
is already in the Hub schema. Phase 2 SSO (`auth.ubec.network`) will issue tokens
that all services validate — stewards log in once and permissions determine access
across all services. Do not create per-service login flows.

---

### ll-header pattern — RETIRED

The `ll-header` (Living Labs secondary sticky header) has been removed. It was a
workaround for the unstyled lang buttons in ubec-nav.js v1/v2. With v3 the universal
nav handles service identity and language switching in a single bar.

**Do not reintroduce `ll-header` on any service.** If a service needs a secondary
contextual header (e.g. a sub-nav for sections), use a distinct class name and do
not duplicate the language switcher.

---

### design.ubec.network CDN — nginx cache headers fix

The `design.ubec.network` nginx vhost had `add_header` directives split between the
`server` block (security headers) and the `location /v1/` block (cache + CORS). This
triggered the nginx inheritance override bug — parent `server` block headers were
silently dropped.

**Fixed in v1.8:** All headers consolidated into `location /v1/`:
```nginx
location /v1/ {
    expires 1h;
    add_header Cache-Control "public, max-age=3600, must-revalidate" always;
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, OPTIONS" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    gzip on;
    gzip_types text/css application/javascript;
}
```

`must-revalidate` added to `Cache-Control` — forces browsers to revalidate after 1h
rather than serving indefinitely stale copies.

---

### ubec-design-system.css — rebuilt clean (v1.8)

The CDN CSS had accumulated conflicting duplicate rules through multiple append
operations during the living-labs nav session. This caused cascade order bugs where
old `.ubec-nav__logo` styles (font-style: italic, wrong colour) overrode new ones.

**Lesson:** Never append nav/component styles to the CDN CSS incrementally across
sessions. The CSS must be rebuilt as a complete authoritative file when structural
changes are needed.

**Current canonical structure** (391 lines):
1. Reset
2. Design tokens (`:root` — full palette, typography, spacing, layout vars)
3. Dark mode overrides
4. Base element styles
5. Button components (`.btn-primary`, `.btn-secondary`, `.btn-ghost`)
6. Token status indicators (`.ubec-token`, pulse animation)
7. Universal Navigation Bar v3 (single clean block — no duplicates)
8. Nav login button (`.ubec-nav__login`)

The canonical source of truth for this file is `INSTRUCTIONS.md §3` (color palette,
typography) combined with the nav spec in `§3.4`. Rebuild from those sections if
the file is ever lost or corrupted — do not reconstruct from memory.

---

### living-labs.ubec.network — nav migration completed (v1.8)

**Status:** Fully operational. One unified nav bar on all three language pages.

- `data-ubec-service="living-labs"` confirmed on `<html>` in all three pages
- `ll-header` HTML removed from EN/DE/PL pages
- `body { padding-top: 68px; }` (matches nav height of 68px)
- Empty `<style></style>` block present in EN page — harmless, can be removed

**Remaining living-labs work:**
- `/en/register.html`, `/de/register.html`, `/pl/register.html` — steward
  registration form (POST to `https://iot.ubec.network/api/v1/auth/register`)
- `/en/impressum.html`, `/de/impressum.html`, `/pl/impressum.html` — legal pages
  (German TMG §5 compliance — incomplete Impressum is liable to cease-and-desist)

---

### Service deployment status on ubec-common (v1.8)

| Service | nginx vhost | App/files | Nav status |
|---|---|---|---|
| `ubec.network` | ✅ | Static HTML `/srv/ubec/portal/` | Bespoke nav (not ubec-nav.js) |
| `iot.ubec.network` | ✅ | FastAPI `/srv/ubec/hub/` + static landing | ✅ ubec-nav.js v3 |
| `learn.ubec.network` | ✅ | Static HTML `/srv/ubec/learn/` | Previously fixed |
| `living-labs.ubec.network` | ✅ | Static HTML `/srv/ubec/living-labs/` (EN/DE/PL) | ✅ ubec-nav.js v3 |
| `design.ubec.network` | ✅ | CDN `/srv/ubec/design-cdn/` | N/A |
| `analytics.ubec.network` | ✅ | Plausible | N/A |
| `auth.ubec.network` | ✅ | Placeholder | N/A |
| `erdpuls.ubec.network` | ❌ no vhost | Python app `/srv/ubec/erdpuls/` — `templates/` empty | Needs landing page |
| `bioregional.ubec.network` | ❌ no vhost | Not migrated to this server | Not started |
| `mapservice.ubec.network` | ❌ no vhost | Only `config/README/static` present | Not started |

---

*This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.*
*Document maintained under CC BY-SA 4.0 · Code under GNU AGPL v3.0*
*Last updated: March 2026 · Version 1.8*
*Primary contact: living-labs@ubec.network*
