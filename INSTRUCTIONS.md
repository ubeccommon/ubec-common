## Changes in v2.0 (March 2026)

### Brand rename: UBEC Commons → UBEC DAO

**Decision:** The platform name reverts to **UBEC DAO** (short form) and
**Ubuntu Bioregional Economic Commons DAO** (full form). "UBEC Commons" is
retired as a brand name.

**Rationale:** UBEC DAO is the established name. UBEC Commons was a proposed
rebrand that was not adopted.

**Applied across:**
- `design-cdn/v1/ubec-nav.js` — fallback logo + portal service label
- All portal HTML pages (EN/DE/PL)
- All legal HTML pages (EN/DE/PL × 4 pages)
- Footer brand name: `UBEC DAO`
- Footer brand description: `Ubuntu Bioregional Economic Commons DAO — a Web 4.0...`

**Copyright line** (all footers, all pages):
```
© 2024–2026 Michel Garand · GNU AGPL v3.0 (code) · CC BY-SA 4.0 (docs) · living-labs@ubec.network
```
Rationale: UBEC DAO has no legal standing. Copyright must be held by a natural
person. Michel Garand is the sole legal copyright holder.

**Locked terminology update:**

| EN | DE | PL |
|---|---|---|
| UBEC DAO (short) | UBEC DAO | UBEC DAO |
| Ubuntu Bioregional Economic Commons DAO (full) | Ubuntu Bioregional Economic Commons DAO | Ubuntu Bioregional Economic Commons DAO |

All other locked terminology unchanged (Steward/Hüter:in/Opiekun etc.).

**Code comments and README files** retain "UBEC Commons" — these are
internal metadata, not public-facing text, and do not require updating.

---

### Nav font sizes — subtle increase (~12%)

Applied to `design-cdn/v1/ubec-design-system.css`:

| Selector | Before | After |
|---|---|---|
| `.ubec-nav__logo-name` | `0.95rem` | `1.05rem` |
| `.ubec-nav__logo-sub` | `0.63rem` | `0.70rem` |
| `.ubec-nav__link` | `0.80rem` | `0.90rem` |
| `.ubec-nav__lang` | `0.75rem` | `0.85rem` |
| `.ubec-nav__login` | `0.80rem` | `0.90rem` |

Change is live on all services via CDN — no per-service deploy required.

---

### Legal pages — multilingual EN/DE/PL deployed

**Structure on server:**
```
/srv/ubec/legal/
  en/legal.html   en/privacy.html   en/terms.html   en/contact.html
  de/legal.html   de/privacy.html   de/terms.html   de/contact.html
  pl/legal.html   pl/privacy.html   pl/terms.html   pl/contact.html
```

**nginx location blocks** in `ubec.network` vhost (and all other vhosts):
```nginx
location ^~ /en/legal    { alias /srv/ubec/legal/en/legal.html;    default_type text/html; ... }
location ^~ /en/privacy  { alias /srv/ubec/legal/en/privacy.html;  default_type text/html; ... }
location ^~ /en/terms    { alias /srv/ubec/legal/en/terms.html;    default_type text/html; ... }
location ^~ /en/contact  { alias /srv/ubec/legal/en/contact.html;  default_type text/html; ... }
# (same for /de/ and /pl/)
```

**Footer links** in portal pages use language-prefixed paths:
- `portal/en/index.html` → `/en/legal`, `/en/privacy`, `/en/terms`, `/en/contact`
- `portal/de/index.html` → `/de/legal`, `/de/privacy`, `/de/terms`, `/de/contact`
- `portal/pl/index.html` → `/pl/legal`, `/pl/privacy`, `/pl/terms`, `/pl/contact`

Internal links within legal pages also use language-prefixed paths.

**Root stubs** (`/legal`, `/privacy`, `/terms`, `/contact`) — these do NOT
exist as files. Do not rely on them. All links must use language-prefixed paths.

**TMG §5 compliance:** Impressum is complete with Michel Garand's full address,
VAT number DE415395232, and contact details. No cease-and-desist risk.

---

### Portal — multilingual EN/DE/PL deployed

**Status:** Fully operational at `ubec.network`.

```
/srv/ubec/portal/
  index.html        ← language-detect redirect (navigator.language → /en|de|pl/)
  en/index.html     ← English landing page
  de/index.html     ← German landing page
  pl/index.html     ← Polish landing page
```

All three pages use `ubec-nav.js v3` with `data-ubec-service="portal"`.
Bespoke nav HTML/CSS/JS fully retired.

**Sections on each page:** Hero · Philosophy strip (Buckminster Fuller) ·
Eight service cards · Four-element token economy · Six philosophy pillars · Footer

**Attribution text** (footer, all three pages — exact wording locked):
- EN: "This project is being developed with assistance from Claude (Anthropic PBC).
  All strategic decisions, philosophical positions, and project commitments are
  those of the author."
- DE: "Dieses Projekt wird mit Unterstützung von Claude (Anthropic PBC) entwickelt.
  Alle strategischen Entscheidungen, philosophischen Positionen und
  Projektverpflichtungen liegen beim Autor."
- PL: "Projekt jest rozwijany przy wsparciu Claude (Anthropic PBC). Wszystkie
  decyzje strategiczne, stanowiska filozoficzne i zobowiązania projektowe należą
  do autora."

---

### Service deployment status on ubec-common (v2.0)

| Service | nginx | App/files | Nav | Legal | Notes |
|---|---|---|---|---|---|
| `ubec.network` | ✅ | ✅ EN/DE/PL portal | ✅ ubec-nav.js v3 | ✅ /en/de/pl | Fully operational |
| `iot.ubec.network` | ✅ | ✅ FastAPI | ✅ ubec-nav.js v3 | ✅ | Fully operational |
| `learn.ubec.network` | ✅ | ✅ Static | ✅ | ✅ | Fully operational |
| `living-labs.ubec.network` | ✅ | ✅ EN/DE/PL | ✅ ubec-nav.js v3 | ✅ | Fully operational |
| `design.ubec.network` | ✅ | ✅ CDN | N/A | N/A | Fully operational |
| `erdpuls.ubec.network` | ❌ no vhost | templates empty | ❌ | ❌ | Needs landing page |
| `bioregional.ubec.network` | ❌ no vhost | Not migrated | ❌ | ❌ | Not started |
| `mapservice.ubec.network` | ❌ no vhost | config/README only | ❌ | ❌ | Not started |

---

### Priority queue (next sessions)

1. **Sign-in page** — `iot.ubec.network/login` (POST `/api/v1/auth/login`),
   multilingual EN/DE/PL, consistent with register page UX
2. **`erdpuls.ubec.network`** — nginx vhost + static landing page,
   `data-ubec-service="erdpuls"`
3. **Git sync** — commit all server-side changes to `ubec_dao_platform` repo:
   - `design-cdn/v1/ubec-design-system.css` (font sizes)
   - `design-cdn/v1/ubec-nav.js` (brand rename)
   - `portal/en/`, `portal/de/`, `portal/pl/` (multilingual pages)
   - `legal/en/`, `legal/de/`, `legal/pl/` (multilingual legal pages)

---

*Document maintained under CC BY-SA 4.0 · Code under GNU AGPL v3.0*
*Last updated: March 2026 · Version 2.0*
*Primary contact: living-labs@ubec.network*
