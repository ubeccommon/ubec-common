---

## Changes in v1.9 (March 2026)

### ubec.network portal — multilingual redesign decision

**Context:** The portal at `ubec.network` has been a single-language (English only)
bespoke static page with its own hand-rolled nav, styles inlined in `<head>`, and no
language switching. It is the public face of the entire ecosystem. As of v1.8 every
other service either uses ubec-nav.js v3 or is the CDN itself.

**Decision:** Replace the existing `portal/index.html` with a multilingual structure
matching the pattern used by `living-labs.ubec.network`:

```
/srv/ubec/portal/
  index.html          ← redirect to /en/ (or browser-language detection)
  en/index.html       ← English landing page
  de/index.html       ← German landing page
  pl/index.html       ← Polish landing page
```

**Nav:** Retire the bespoke portal nav. The portal will use ubec-nav.js v3 with
`data-ubec-service="portal"` on `<html>`, `<nav id="ubec-nav">` in body, and
`body { padding-top: 68px; }`. The bespoke `.nav`, `.nav__links`, `.nav__hamburger`,
`.nav__mobile` CSS and JS can be removed entirely from the portal once migrated.

**Root redirect (`index.html`):** A minimal HTML file with a `<meta http-equiv="refresh">`
and a JS `navigator.language` fallback. Redirects to `/en/`, `/de/`, or `/pl/` based
on browser language. If language cannot be determined, defaults to `/en/`.

**Content:** All existing content sections are preserved and translated:
- Hero (title, tagline, description, two CTA buttons)
- Buckminster Fuller philosophy strip
- Ecosystem section (eight service cards)
- Four-element token economy section
- Philosophy pillars section (five pillars)
- Footer (three-column: brand + Services + Legal)

All copy is translated into German and Polish. The English version is the canonical
source. German and Polish translations are factually accurate renderings — not
machine-translated paraphrases. Key terminology is locked:
  - "Steward" → DE: "Hüter:in", PL: "Opiekun/Opiekunka"
  - "Bioregional" (one word) → DE: "bioregional", PL: "bioregionalny"
  - "Regenerative" → DE: "regenerativ", PL: "regeneratywny"
  - "Commons" → DE: "Gemeingut" or "Commons" (context-dependent), PL: "dobra wspólne" or "Commons"

**Legal pages:** The portal already has `/srv/ubec/legal/` with canonical legal pages.
The per-language footers link to these pages. The footer legal links use the canonical
paths (not per-language duplicates).

**File size constraint:** Each language page should be a single self-contained HTML
file. Service-local styles go in `<style>` in `<head>`. The CDN provides the design
tokens and nav. No external JS beyond ubec-nav.js.

---

### Service deployment status on ubec-common (v1.9)

| Service | nginx vhost | App/files | Nav status | Legal |
|---|---|---|---|---|
| `ubec.network` | ✅ | Static HTML `/srv/ubec/portal/` | 🔄 Bespoke → ubec-nav.js v3 migration pending | ✅ |
| `iot.ubec.network` | ✅ | FastAPI `/srv/ubec/hub/` + static landing | ✅ ubec-nav.js v3 | ✅ |
| `learn.ubec.network` | ✅ | Static HTML `/srv/ubec/learn/` | ✅ Previously fixed | ✅ |
| `living-labs.ubec.network` | ✅ | Static HTML `/srv/ubec/living-labs/` EN/DE/PL | ✅ ubec-nav.js v3 | ✅ |
| `design.ubec.network` | ✅ | CDN `/srv/ubec/design-cdn/` | N/A | N/A |
| `analytics.ubec.network` | ✅ | Plausible | N/A | N/A |
| `auth.ubec.network` | ✅ | Placeholder | N/A | N/A |
| `erdpuls.ubec.network` | ❌ no vhost | Python app `/srv/ubec/erdpuls/` — templates empty | ❌ | ❌ |
| `bioregional.ubec.network` | ❌ no vhost | Not migrated | ❌ | ❌ |
| `mapservice.ubec.network` | ❌ no vhost | Only config/README/static present | ❌ | ❌ |

---

### Completed this session (v1.9)

- **Steward registration pages** deployed: `living-labs.ubec.network/{en,de,pl}/register.html`
  - POST to `https://iot.ubec.network/api/v1/auth/register`
  - Fields: email, password (8–128), gdpr_consent (required), full_name (optional),
    display_name (optional), preferred_language (auto-set per page)
  - On success: redirect to `/{lang}/welcome.html`
  - 409 Conflict → localised "email already exists" message
  - Password strength bar (5-step visual, colour-coded)
- **Welcome stubs** deployed: `living-labs.ubec.network/{en,de,pl}/welcome.html`
  - Placeholder onboarding pages — direct steward to Hub login
  - Marked as "coming in a future release"

---

*This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.*
*Document maintained under CC BY-SA 4.0 · Code under GNU AGPL v3.0*
*Last updated: March 2026 · Version 1.9*
*Primary contact: living-labs@ubec.network*
