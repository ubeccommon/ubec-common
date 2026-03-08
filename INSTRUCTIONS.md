# INSTRUCTIONS.md — UBEC Commons
## Single Source of Truth for Design, Architecture, Philosophy & Coding Decisions

> **This document is the canonical reference for all UBEC development sessions.**
> Read it at the start of every session involving infrastructure, code, or design.
> Every decision recorded here supersedes memory, prior conversation, or inference.

**Version:** 2.1  
**Last updated:** March 2026  
**License:** CC BY-SA 4.0 (documentation) · GNU AGPL v3.0 (code)  
**Contact:** living-labs@ubec.network

*This project is being developed with assistance from Claude (Anthropic PBC).
All strategic decisions, philosophical positions, and project commitments are
those of the author — Michel Garand.*

---

## Table of Contents

1. [Core Rules — Always Apply](#1-core-rules--always-apply)
2. [Project Overview](#2-project-overview)
3. [Design System](#3-design-system)
4. [Philosophical Foundations](#4-philosophical-foundations)
5. [Token Economy](#5-token-economy)
6. [Server Infrastructure](#6-server-infrastructure)
7. [nginx — Rules & Patterns](#7-nginx--rules--patterns)
8. [Static Pages — Multilingual Pattern](#8-static-pages--multilingual-pattern)
9. [Hub API — Endpoints & Auth](#9-hub-api--endpoints--auth)
10. [Hub Static Pages — Deployed State](#10-hub-static-pages--deployed-state)
11. [Legal & Compliance](#11-legal--compliance)
12. [Service Deployment Status](#12-service-deployment-status)
13. [Priority Queue](#13-priority-queue)
14. [Changelog](#14-changelog)

---

## 1. Core Rules — Always Apply

These rules are non-negotiable. They apply in every session regardless of context.

**1.1 Reason from facts only (Goethean principle)**
Never guess or infer missing information. If something is unclear or absent,
stop and ask. Do not fabricate API responses, file contents, or server state.
Observe first; conclude only from what is directly verifiable.

**1.2 Coding is an exact science**
Only propose what can actually be executed in the current phase.
Never assume an API endpoint exists — check `/docs` or `/openapi.json` first.
Never assume a file is in place — check with `ls` or `cat` first.

**1.3 Language**
All code is Python unless the service requires otherwise (HTML/CSS/JS for
static pages, nginx config for infrastructure).

**1.4 Infrastructure must be EU-hosted**
Approved providers: Hetzner, OVH, IONOS, Exoscale, STACKIT.
Prohibited: AWS, GCP, Azure, Cloudflare (CDN or proxy), DigitalOcean, Heroku.
**Cloudflare proxying is permanently prohibited.** It rewrites nginx responses,
injects scripts, obfuscates email addresses, and truncates JavaScript.
DNS must always be grey-clouded (direct). Do not re-enable Cloudflare.

**1.5 Font provider is Bunny Fonts — never Google Fonts**
All font imports use `https://fonts.bunny.net` exclusively.
Google Fonts transfers visitor IP addresses to US servers — GDPR violation.
```html
<link rel="preconnect" href="https://fonts.bunny.net">
<link href="https://fonts.bunny.net/css?family=dm-serif-display:400,400i|dm-sans:300,400,500,600,300i,400i|jetbrains-mono:400,500&display=swap" rel="stylesheet">
```

**1.6 Vocabulary — locked terms**
- "Stewards" not "users"
- "Regenerative" not "sustainable"
- "Bioregional" (one word, never hyphenated)
- "Commons" as noun and value
- "Hüter:in" (DE) / "Opiekun/Opiekunka" (PL) for steward

**1.7 No CDN fallbacks**
`design.ubec.network` is trusted first-party infrastructure. Do not add
`onerror` attributes to `<link>` or `<script>` tags loading from it.
The `UBEC_Server_Technical_Specifications.md` fallback guidance is superseded
by this rule — it was written before the CDN was stabilised.
```html
<!-- CORRECT -->
<link rel="stylesheet" href="https://design.ubec.network/v1/ubec-design-system.css">
<script defer src="https://design.ubec.network/v1/ubec-nav.js"></script>

<!-- WRONG — do not add onerror -->
<link rel="stylesheet" href="..." onerror="this.onerror=null;this.href='...'">
```

**1.8 Attribution — locked wording**
Footer of every service must include:
- EN: "This project is being developed with assistance from Claude (Anthropic PBC). All strategic decisions, philosophical positions, and project commitments are those of the author."
- DE: "Dieses Projekt wird mit Unterstützung von Claude (Anthropic PBC) entwickelt. Alle strategischen Entscheidungen, philosophischen Positionen und Projektverpflichtungen liegen beim Autor."
- PL: "Projekt jest rozwijany przy wsparciu Claude (Anthropic PBC). Wszystkie decyzje strategiczne, stanowiska filozoficzne i zobowiązania projektowe należą do autora."

---

## 2. Project Overview

**UBEC Commons** (Ubuntu Bioregional Economic Commons) is a Web 4.0 bioregional
DAO protocol network based in Müllrose, Brandenburg, Germany, anchored in
the Schlaubetal nature park.

The platform connects small farms, citizen scientists, educators, artists, and
communities through regenerative economics and blockchain-backed token systems
on the Stellar network.

### 2.1 Eight Services

| Service | Domain | Type | Status |
|---|---|---|---|
| Portal | `ubec.network` | Static HTML | ✅ Fully operational |
| Protocol | `bioregional.ubec.network` | Python app | ❌ Not migrated |
| Maps | `mapservice.ubec.network` | PHP/Mapbender | ❌ Not migrated |
| Living Labs | `living-labs.ubec.network` | Static HTML | ✅ Fully operational |
| Hub | `iot.ubec.network` | FastAPI + Static | ✅ Fully operational |
| Erdpuls | `erdpuls.ubec.network` | Python app | ❌ Needs landing page |
| Open | `ubeccommon.github.io` | GitHub Pages | External |
| Learn | `learn.ubec.network` | Static HTML | ✅ Fully operational |

All services share the design system CDN at `design.ubec.network`.

### 2.2 Sub-brand Names

| Service | Sub-brand |
|---|---|
| ubec.network | UBEC DAO |
| bioregional.ubec.network | UBEC Protocol |
| mapservice.ubec.network | UBEC Maps |
| living-labs.ubec.network | UBEC Living Labs |
| iot.ubec.network | UBEC Hub |
| erdpuls.ubec.network | Erdpuls by UBEC |
| ubeccommon.github.io | UBEC Open |
| learn.ubec.network | UBEC Learn |

### 2.3 Code Repository

`https://github.com/ubeccommon/ubec_dao_platform`  
License: GNU AGPL v3.0 (code) · CC BY-SA 4.0 (documentation)

---

## 3. Design System

### 3.1 CDN

```
https://design.ubec.network/v1/ubec-design-system.css
https://design.ubec.network/v1/ubec-nav.js
```

Served from `/srv/ubec/design-cdn/v1/` on ubec-common.
Cache: `public, max-age=3600, must-revalidate`.
CORS: `Access-Control-Allow-Origin: *` (first-party CDN, all UBEC domains).

### 3.2 Colour Palette

```css
:root {
  /* Four-element tokens */
  --color-air:            #A8D5E8;
  --color-water:          #5B9E9E;
  --color-earth:          #C4974A;
  --color-fire:           #E8834A;

  /* Commons greens */
  --color-commons:        #5A8A6A;
  --color-commons-dark:   #3D6B52;
  --color-commons-light:  #EAF4EE;

  /* Warm peach tones */
  --color-peach:          #F2C9B0;
  --color-peach-deep:     #D4956A;
  --color-peach-light:    #FBF0E8;

  /* Devotion (blue-grey) */
  --color-devotion:       #7A9FBA;
  --color-devotion-dark:  #4A6B8A;
  --color-devotion-light: #EBF1F7;

  /* Ochre / gold */
  --color-ochre:          #D4A84B;
  --color-ochre-light:    #FBF3E0;

  /* Warm neutrals (parchment → bark) */
  --color-parchment:      #FBF6EE;
  --color-linen:          #F2EBE0;
  --color-sand:           #E5D9CC;
  --color-clay:           #9E8070;
  --color-humus:          #5C3D2A;
  --color-bark:           #3A2418;

  /* Status */
  --color-status-ok:      #40916C;
}
```

Anthroposophical/Waldorf lazure tradition: warm, breathing, living tones.
Never harsh corporate colours. The palette must feel like parchment, soil, water.

### 3.3 Typography

```css
:root {
  --font-display: 'DM Serif Display', Georgia, serif;
  --font-body:    'DM Sans', 'Helvetica Neue', sans-serif;
  --font-mono:    'JetBrains Mono', 'Fira Code', monospace;
}
```

Loaded from Bunny Fonts (see §1.5). Never from Google Fonts.

### 3.4 Universal Navigation Bar (ubec-nav.js v3)

**HTML required on every page:**
```html
<html lang="en" data-ubec-service="hub">  <!-- set service name -->
<body>
  <nav id="ubec-nav" aria-label="UBEC DAO navigation"></nav>
  <!-- rest of page -->
```

**Body offset:** `body { padding-top: 68px; }` — nav height is 68px.

**Nav height CSS variable:** `--nav-height: 64px` in `:root` (visual height);
actual computed height with border is 68px. Use `padding-top: 68px` on body.

**Service names for `data-ubec-service`:**
`portal` · `hub` · `living-labs` · `protocol` · `maps` · `erdpuls` · `learn`

**Login button on authenticated pages:** hide via polling —
```js
(function hideNavLogin() {
  var btn = document.querySelector('.ubec-nav__login');
  if (btn) { btn.style.display = 'none'; }
  else { setTimeout(hideNavLogin, 50); }
})();
```

**Do not reintroduce `ll-header`** or any bespoke nav on any service.
If a secondary contextual header is needed, use a distinct class name.

### 3.5 CDN nginx — Headers Rule

All headers consolidated into `location /v1/` — never split between `server`
block and `location` block (nginx inheritance override bug: parent `server`
block headers are silently dropped when a child `location` also uses
`add_header`).

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

### 3.6 ubec-design-system.css — Canonical Structure

Current file: 391 lines. Structure (do not append incrementally — rebuild
as a complete authoritative file when structural changes are needed):

1. Reset
2. Design tokens (`:root` — full palette, typography, spacing, layout vars)
3. Dark mode overrides
4. Base element styles
5. Button components (`.btn-primary`, `.btn-secondary`, `.btn-ghost`)
6. Token status indicators (`.ubec-token`, pulse animation)
7. Universal Navigation Bar v3 (single clean block — no duplicates)
8. Nav login button (`.ubec-nav__login`)

**Nav font sizes (current — set in v1.9):**

| Selector | Size |
|---|---|
| `.ubec-nav__logo-name` | `1.05rem` |
| `.ubec-nav__logo-sub` | `0.70rem` |
| `.ubec-nav__link` | `0.90rem` |
| `.ubec-nav__lang` | `0.85rem` |
| `.ubec-nav__login` | `0.90rem` |

---

## 4. Philosophical Foundations

These are operational design constraints, not decorative references.
Every feature, data structure, and API decision is legible through at least
one of these frameworks.

**Ubuntu Philosophy** — "I am because we are"
The foundational ethics of the ecosystem. Personhood is constituted through
relationship. Collective governance over individual extraction.

**Christopher Alexander — Pattern Language & Living Structure**
The OER repository (UBEC Learn) is structured as a genuine Pattern Language
of Place. The platform unfolds through organic growth, not imposed structure.

**Edward T. Hall — Proxemics & The Hidden Dimension**
Data visibility is governed by proxemic zones: intimate / personal / social /
public. The `proxemic_zone` field in the observations schema implements this
directly. The map is a proxemic diagram.

**Goethean Science — Phenomenological Observation**
Reason only from observable facts. Never guess missing information.
The 13 Questions to the Soil embody Goethe's tender empiricism — stewards
observe phenomena first, interpret second. This is also the AI collaboration
rule: no inference without evidence.

**Rudolf Steiner — Anthroposophical Colour Theory & Waldorf Lazure**
The colour palette (§3.2) is warm, breathing, and living — peach-blossom,
living sage, ochre gold. Not harsh corporate tones. Colours carry meaning
and mood; the palette is a philosophical statement.

**Buckminster Fuller — Systems Thinking**
The portal's philosophy strip references Fuller. The eight-service ecosystem
is understood as an integrated system, not a collection of independent sites.
Comprehensive anticipatory design.

---

## 5. Token Economy

Four-element system on the Stellar blockchain.

| Token | Element | Colour | Role |
|---|---|---|---|
| UBEC | Air | `#A8D5E8` | Gateway — universal access, entry to the network |
| UBECrc | Water | `#5B9E9E` | Reciprocity — earned through observations and citizen science |
| UBECgpi | Earth | `#C4974A` | Stability — store of value, documentation anchor |
| UBECtt | Fire | `#E8834A` | Transformation — governance activation, collective action |

`stellar.toml` is live at `https://ubec.network/.well-known/stellar.toml`.
Passing all checks at `stellar.sui.li` (CORS + `text/plain` headers correct).

Hub is the reward engine: every verified observation triggers UBECrc rewards.
Token balance panels on the steward dashboard are Phase 2 placeholders.

---

## 6. Server Infrastructure

### 6.1 Current Server

```
Provider:   Hetzner Cloud
Plan:       CPX42
Hostname:   ubec-common
IP:         49.13.167.206
OS:         Ubuntu (latest LTS)
Web server: nginx/1.24.0
Database:   PostgreSQL 16
SSH user:   ubec (on server) / farmer (on client machine: schiff)
```

### 6.2 File Layout

```
/srv/ubec/
  portal/                   ← ubec.network webroot
    index.html              ← language-detect redirect
    en/index.html           ← English
    de/index.html           ← German
    pl/index.html           ← Polish
  hub/
    static/                 ← iot.ubec.network static files
      index.html            ← language-detect redirect
      en/index.html         ← EN landing
      de/index.html         ← DE landing
      pl/index.html         ← PL landing
      login.html            ← EN login
      en/login.html
      de/login.html
      pl/login.html
      en/dashboard.html     ← Steward personal dashboard
      de/dashboard.html
      pl/dashboard.html
  living-labs/              ← living-labs.ubec.network webroot
    index.html              ← language-detect redirect
    en/index.html
    de/index.html
    pl/index.html
    en/register.html
    de/register.html
    pl/register.html
    en/welcome.html
    de/welcome.html
    pl/welcome.html
  learn/                    ← learn.ubec.network webroot
  design-cdn/
    v1/
      ubec-design-system.css
      ubec-nav.js
  legal/                    ← shared legal pages (all services)
    en/legal.html   en/privacy.html   en/terms.html   en/contact.html
    de/legal.html   de/privacy.html   de/terms.html   de/contact.html
    pl/legal.html   pl/privacy.html   pl/terms.html   pl/contact.html
```

### 6.3 nginx Config Files

```
/etc/nginx/sites-enabled/
  ubec.network
  iot.ubec.network
  design.ubec.network
  living-labs.ubec.network
  learn.ubec.network
  analytics.ubec.network
  auth.ubec.network
```

### 6.4 TLS Certificates

Let's Encrypt / Certbot. Main cert:
```
/etc/letsencrypt/live/ubec.network/fullchain.pem
/etc/letsencrypt/live/ubec.network/privkey.pem
```
Valid to 2026-05-31. Covers `ubec.network` and subdomains.

### 6.5 Hub FastAPI

```
Bind:      127.0.0.1:8003
Webroot:   /srv/ubec/hub/
Version:   2.0.0
API docs:  https://iot.ubec.network/docs
OpenAPI:   https://iot.ubec.network/openapi.json
DB:        PostgreSQL 16, database: ubec_hub
```

### 6.6 Analytics

Self-hosted Plausible CE at `analytics.ubec.network`.
Cookieless, EU-hosted, no consent required under GDPR legitimate interest.
Integration script per service:
```html
<script defer data-domain="service.ubec.network"
        src="https://analytics.ubec.network/js/script.js"></script>
```

---

## 7. nginx — Rules & Patterns

### 7.1 The `add_header` Inheritance Bug

**Rule:** All `add_header` directives in a given `server` block must be
consolidated into a single `location` block. Headers in a parent `server`
block are **silently dropped** when any child `location` block also uses
`add_header`.

**Pattern:** Put all security headers + cache headers together in `location /`:
```nginx
location / {
    proxy_pass http://127.0.0.1:8003;
    # ...proxy headers...
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options           "SAMEORIGIN"                          always;
    add_header X-Content-Type-Options    "nosniff"                             always;
    add_header Referrer-Policy           "strict-origin-when-cross-origin"     always;
    add_header Permissions-Policy        "geolocation=(), camera=(), microphone=()" always;
    add_header Content-Security-Policy   "..." always;
}
```

### 7.2 `.well-known` Ordering

`location ~ /\.` (deny-all regex) matches before prefix locations.
Use `location ^~ /.well-known/` to prevent regex evaluation:
```nginx
location ^~ /.well-known/ {
    root /var/www/certbot;
    allow all;
}
```
Or use a negative lookahead: `location ~ /\.(?!well-known)`.

### 7.3 `alias` vs `root` + `try_files`

**Rule:** Never use `alias` with a file path inside a `location = /path/`
block (with trailing slash) — it causes a 500 error.

```nginx
# WRONG — causes 500
location = /en/ {
    alias /srv/ubec/hub/static/en/index.html;
}

# CORRECT — use root + try_files
location = /en/ {
    root /srv/ubec/hub/static;
    try_files /en/index.html =404;
    default_type text/html;
    add_header Cache-Control "no-cache" always;
}
```

`alias` **does** work correctly for `location = /path` (no trailing slash),
e.g. `location = /en/login { alias /srv/ubec/hub/static/en/login.html; }`.

### 7.4 Duplicate TLS Directives

`ssl_protocols` and `ssl_prefer_server_ciphers` in vhost configs conflict
with global `nginx.conf` settings. Keep TLS directives only in global config.

### 7.5 All Services Use `/srv/ubec/` Webroots

Not `/var/www/`. All paths begin `/srv/ubec/{service}/`.

### 7.6 Standard Security Headers

Applied to every `location /` or equivalent serving block:
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options           "SAMEORIGIN"                          always;
add_header X-Content-Type-Options    "nosniff"                             always;
add_header Referrer-Policy           "strict-origin-when-cross-origin"     always;
add_header Permissions-Policy        "geolocation=(), camera=(), microphone=()" always;
```

CSP varies per service. Hub CSP:
```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://design.ubec.network https://analytics.ubec.network https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://design.ubec.network https://fonts.bunny.net https://cdn.jsdelivr.net; font-src https://fonts.bunny.net; img-src 'self' data:; connect-src 'self' https://analytics.ubec.network;" always;
```

---

## 8. Static Pages — Multilingual Pattern

This pattern is used by `ubec.network`, `living-labs.ubec.network`, and
`iot.ubec.network`. All new services must follow it.

### 8.1 File Structure

```
/srv/ubec/{service}/
  index.html      ← language-detect redirect only (no content)
  en/index.html   ← full English page
  de/index.html   ← full German page
  pl/index.html   ← full Polish page
```

### 8.2 Language-Detect Redirect (`index.html`)

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>UBEC Hub</title>
  <script>
    var lang = (navigator.language || navigator.userLanguage || 'en').toLowerCase().slice(0,2);
    var map = { de: '/de/', pl: '/pl/' };
    window.location.replace(map[lang] || '/en/');
  </script>
  <noscript><meta http-equiv="refresh" content="0;url=/en/"></noscript>
</head>
<body></body>
</html>
```

### 8.3 nginx Location Blocks

```nginx
location = / {
    root /srv/ubec/{service}/static;  # or portal/
    try_files /index.html =404;
    add_header Cache-Control "no-cache" always;
    # + all security headers
}
location = /en/ {
    root /srv/ubec/{service}/static;
    try_files /en/index.html =404;
    default_type text/html;
    add_header Cache-Control "no-cache" always;
}
location = /de/ {
    root /srv/ubec/{service}/static;
    try_files /de/index.html =404;
    default_type text/html;
    add_header Cache-Control "no-cache" always;
}
location = /pl/ {
    root /srv/ubec/{service}/static;
    try_files /pl/index.html =404;
    default_type text/html;
    add_header Cache-Control "no-cache" always;
}
```

### 8.4 Language Switcher in Hero

Each language page includes an inline lang switcher near the hero CTA:
```html
<p class="hero__lang">
  <a href="/en/" hreflang="en" aria-current="true">EN</a> ·
  <a href="/de/" hreflang="de">DE</a> ·
  <a href="/pl/" hreflang="pl">PL</a>
</p>
```
The `aria-current="true"` attribute is on the current language link only.

### 8.5 Footer Legal Links

Footer links use language-prefixed paths. Root stubs (`/legal`, `/privacy`,
`/terms`, `/contact`) do not exist — never link to them:
```
/en/legal   /en/privacy   /en/terms   /en/contact
/de/legal   /de/privacy   /de/terms   /de/contact
/pl/legal   /pl/privacy   /pl/terms   /pl/contact
```

Legal files are shared across services, served from `/srv/ubec/legal/`.

### 8.6 Footer Structure — Locked

Three-column dark footer (background: `var(--color-bark)`):
- Column 1 (2fr): brand name (italic serif) + brand description
- Column 2 (1fr): Services — links to all 8 UBEC services
- Column 3 (1fr): service-local links (docs, health, legal, privacy, terms, contact)

Copyright line: `© 2024–2026 Michel Garand · CC BY-SA 4.0 · GNU AGPL v3.0`
Attribution line: Claude/Anthropic attribution (see §1.8).

### 8.7 Page Template — Head

```html
<!DOCTYPE html>
<!-- License: CC BY-SA 4.0 · This project uses the services of Claude and Anthropic PBC. -->
<html lang="en" data-ubec-service="hub">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>…</title>
  <meta name="description" content="…">
  <meta name="robots" content="index, follow">
  <link rel="preconnect" href="https://fonts.bunny.net">
  <link href="https://fonts.bunny.net/css?family=dm-serif-display:400,400i|dm-sans:300,400,500,600,300i,400i|jetbrains-mono:400,500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://design.ubec.network/v1/ubec-design-system.css">
  <script defer src="https://design.ubec.network/v1/ubec-nav.js"></script>
  <script defer data-domain="iot.ubec.network" src="https://analytics.ubec.network/js/script.js"></script>
  <style>
    /* service-local styles only */
  </style>
</head>
<body>
  <nav id="ubec-nav" aria-label="UBEC DAO navigation"></nav>
  <!-- page content -->
</body>
</html>
```

---

## 9. Hub API — Endpoints & Auth

### 9.1 Authentication

JWT Bearer tokens. Token name: `ubec_access_token`.
Storage: `localStorage` (stay signed in) or `sessionStorage` (session only).
Read pattern: `localStorage.getItem('ubec_access_token') || sessionStorage.getItem('ubec_access_token')`

Auth endpoints:
```
POST /api/v1/auth/register    ← steward registration
POST /api/v1/auth/login       ← returns access_token
GET  /api/v1/auth/me          ← StewardDetailResponse
GET  /api/v1/auth/me/permissions  ← {steward_id, roles[], permissions[]}
POST /api/v1/auth/logout
```

### 9.2 StewardDetailResponse Fields

```
email, full_name, display_name, preferred_language,
stellar_public_key, is_active, email_verified,
created_at, updated_at, roles[]
```

### 9.3 Observations

```
POST /api/v1/observations/
GET  /api/v1/observations?steward_id={id}&per_page=5&page=1
```

ObservationListOut: `observations[], total, page, per_page, pages`

Observation fields: `id, activity_id, steward_id, observed_at, location,
location_note, proxemic_zone, qualitative_notes, device_id, language,
is_validated, validated_by, validated_at, created_at, updated_at`

### 9.4 Roles & Permissions

Permissions format: `"category:action"` strings, e.g. `"observations:create"`,
`"activities:manage"`, `"stewards:manage"`.

Roles (4 in database): check live via `GET /api/v1/auth/me/permissions`.

### 9.5 Phase 2 Endpoints (not yet implemented)

- Token balances / `token_rewards` table
- Device registry (`GET /api/v1/devices/`)
- Map data pipeline (`/api/v1/maps/`)

**Always verify endpoint existence against `/openapi.json` before coding.**

---

## 10. Hub Static Pages — Deployed State

### 10.1 Full File Layout

```
/srv/ubec/hub/static/
  index.html              ← language-detect redirect
  en/
    index.html            ← EN landing page
    login.html            ← EN login (→ /en/dashboard on success)
    dashboard.html        ← Steward personal dashboard (EN)
  de/
    index.html            ← DE landing page
    login.html            ← DE login (→ /de/dashboard on success)
    dashboard.html        ← Steward personal dashboard (DE)
  pl/
    index.html            ← PL landing page
    login.html            ← PL login (→ /pl/dashboard on success)
    dashboard.html        ← Steward personal dashboard (PL)
  login.html              ← EN login (root alias, same as en/login.html)
```

### 10.2 nginx vhost — Location Block Summary

```nginx
# /.well-known/
location ^~ /.well-known/ { ... }

# Root redirect
location = / {
    root /srv/ubec/hub/static;
    try_files /index.html =404;
    add_header Cache-Control "no-cache" always;
    # + all security headers + CSP
}

# Multilingual landing pages
location = /en/ { root /srv/ubec/hub/static; try_files /en/index.html =404; ... }
location = /de/ { root /srv/ubec/hub/static; try_files /de/index.html =404; ... }
location = /pl/ { root /srv/ubec/hub/static; try_files /pl/index.html =404; ... }

# Legal (shared)
location ^~ /legal    { alias /srv/ubec/legal/legal.html; ... }
location ^~ /privacy  { alias /srv/ubec/legal/privacy.html; ... }
location ^~ /terms    { alias /srv/ubec/legal/terms.html; ... }
location ^~ /contact  { alias /srv/ubec/legal/contact.html; ... }
location ^~ /en/legal { alias /srv/ubec/legal/en/legal.html; ... }
# ... (de, pl same pattern)

# Login pages
location = /login    { alias /srv/ubec/hub/static/login.html; ... }
location = /de/login { alias /srv/ubec/hub/static/de/login.html; ... }
location = /pl/login { alias /srv/ubec/hub/static/pl/login.html; ... }

# Dashboards
location = /en/dashboard { alias /srv/ubec/hub/static/en/dashboard.html; ... }
location = /de/dashboard { alias /srv/ubec/hub/static/de/dashboard.html; ... }
location = /pl/dashboard { alias /srv/ubec/hub/static/pl/dashboard.html; ... }

# FastAPI proxy (everything else)
location / {
    proxy_pass http://127.0.0.1:8003;
    # proxy headers + security headers
}
```

### 10.3 Steward Dashboard — Panels

1. Status strip (account status, roles count, observations total, language)
2. Recent Observations (live, last 5 via API)
3. Permissions (roles + permissions grouped by category prefix)
4. Token Balances (Phase 2 placeholder — 4 element cards)
5. Connected Devices (Phase 2 placeholder)
6. Steward Profile (8 fields)

**Auth guard:** reads token → if missing, redirect to `/xx/login`.
On 401 response: clear token + redirect to `/xx/login`.
On load: `GET /api/v1/auth/me/permissions` — if no management permission,
stay on personal dashboard (management dashboard gate, §13 priority 1).

---

## 11. Legal & Compliance

### 11.1 TMG §5 Compliance (German Impressum)

Impressum is complete with Michel Garand's full address, VAT number
DE415395232, and contact details. No cease-and-desist risk.
Incomplete Impressum under German TMG §5 is liable to cease-and-desist.

### 11.2 Legal Page Locations

Shared across all services, served from `/srv/ubec/legal/`:
```
en/legal.html   en/privacy.html   en/terms.html   en/contact.html
de/legal.html   de/privacy.html   de/terms.html   de/contact.html
pl/legal.html   pl/privacy.html   pl/terms.html   pl/contact.html
```

Root stubs (`/legal`, `/privacy`, `/terms`, `/contact`) do not exist.
All links must use language-prefixed paths.

### 11.3 GDPR

- All personal data stored on EU infrastructure (Hetzner DE)
- Analytics: self-hosted Plausible (cookieless, no consent required)
- Fonts: Bunny Fonts (EU-hosted, no IP transfer to US)
- No Google Fonts, no Cloudflare, no US-hosted third-party services
- nginx access logs must anonymise IPs (last octet zeroed)
- Application logs: never log raw IPs, tokens, passwords, or PII

### 11.4 Stellar.toml

```
https://ubec.network/.well-known/stellar.toml
```
Passing all checks at `stellar.sui.li`.
CORS headers: `Access-Control-Allow-Origin: *`
Content-Type: `text/plain`

---

## 12. Service Deployment Status

### Current State (v2.1 — March 2026)

| Service | nginx | App/files | Nav | Legal | Notes |
|---|---|---|---|---|---|
| `ubec.network` | ✅ | ✅ EN/DE/PL portal | ✅ ubec-nav.js v3 | ✅ /en/de/pl | Fully operational |
| `iot.ubec.network` | ✅ | ✅ FastAPI + EN/DE/PL static | ✅ ubec-nav.js v3 | ✅ /en/de/pl | Fully operational |
| `learn.ubec.network` | ✅ | ✅ Static | ✅ | ✅ | Fully operational |
| `living-labs.ubec.network` | ✅ | ✅ EN/DE/PL + register/welcome | ✅ ubec-nav.js v3 | ✅ | Fully operational |
| `design.ubec.network` | ✅ | ✅ CDN v1 | N/A | N/A | Fully operational |
| `analytics.ubec.network` | ✅ | ✅ Plausible CE | N/A | N/A | Fully operational |
| `auth.ubec.network` | ✅ | Placeholder | N/A | N/A | Placeholder only |
| `erdpuls.ubec.network` | ❌ no vhost | Python app, templates empty | ❌ | ❌ | Needs landing page |
| `bioregional.ubec.network` | ❌ no vhost | Not migrated from old server | ❌ | ❌ | Not started |
| `mapservice.ubec.network` | ❌ no vhost | config/README only | ❌ | ❌ | Not started |

**Old server IP:** `3.121.60.104` (still running bioregional + mapservice).

### Hub Pages Detail

| Path | File | Status |
|---|---|---|
| `/` | `static/index.html` | ✅ lang-detect redirect |
| `/en/` | `static/en/index.html` | ✅ EN landing |
| `/de/` | `static/de/index.html` | ✅ DE landing |
| `/pl/` | `static/pl/index.html` | ✅ PL landing |
| `/login` | `static/login.html` | ✅ EN login |
| `/de/login` | `static/de/login.html` | ✅ DE login |
| `/pl/login` | `static/pl/login.html` | ✅ PL login |
| `/en/dashboard` | `static/en/dashboard.html` | ✅ personal dashboard |
| `/de/dashboard` | `static/de/dashboard.html` | ✅ personal dashboard |
| `/pl/dashboard` | `static/pl/dashboard.html` | ✅ personal dashboard |
| `/en/manage` | not yet built | ❌ next priority |
| `/de/manage` | not yet built | ❌ next priority |
| `/pl/manage` | not yet built | ❌ next priority |

---

## 13. Priority Queue

Work items in order. Do not start item N+1 before item N is deployed and
verified. Check every API endpoint against `/openapi.json` before coding.

### 1. Management Dashboard (current priority)

**Paths:** `/en/manage`, `/de/manage`, `/pl/manage`
**Gate:** requires `stewards:manage` permission OR `admin` role.
Redirect to `/xx/dashboard` if authenticated but not authorised.
Redirect to `/xx/login` if unauthenticated.

**Panels to build (confirm endpoints exist first):**
- Steward list — paginated, role badges, active/inactive toggle
  → `GET /api/v1/stewards/` (confirm exists)
- Role assignment — assign/revoke roles per steward
  → `PATCH /api/v1/stewards/{id}/roles` (confirm exists)
- Observation validation queue — `is_validated = false` items
  → `GET /api/v1/observations?is_validated=false` (confirm filter exists)
- Device registry — `GET /api/v1/devices/` (confirm exists)
- Token reward log — Phase 2 data, may be empty placeholder

**Before writing any HTML:** run
```bash
curl -s https://iot.ubec.network/openapi.json | python3 -m json.tool | grep '"path"'
```
and check permissions with a live admin token.

**nginx additions needed (×3):**
```nginx
location = /en/manage {
    root /srv/ubec/hub/static;
    try_files /en/manage.html =404;
    default_type text/html;
    add_header Cache-Control "no-cache" always;
}
```

### 2. `erdpuls.ubec.network` Landing Page

nginx vhost + EN/DE/PL static landing, `data-ubec-service="erdpuls"`.
Python app is at `/srv/ubec/erdpuls/` — templates are empty.
Landing page is static HTML only (same pattern as portal).
Content: place-based (Müllrose, Schlaubetal), crowdfunding model, workshops.

### 3. `bioregional.ubec.network` Migration

nginx vhost + migrate Python app from old server `3.121.60.104`.
Check what is running there before migrating.

### 4. `mapservice.ubec.network` Migration

nginx vhost + migrate PHP/Mapbender from old server.
Requires PostGIS extension on PostgreSQL 16.

### 5. Git Sync

Commit all server-side changes to `ubec_dao_platform` repo:
- `design-cdn/v1/ubec-design-system.css` (font sizes updated v1.9)
- `design-cdn/v1/ubec-nav.js` (brand rename)
- `portal/en/`, `portal/de/`, `portal/pl/`
- `hub/static/` (all landing, login, dashboard pages)
- `legal/en/`, `legal/de/`, `legal/pl/`

---

## 14. Changelog

| Version | Date | Summary |
|---|---|---|
| 1.0–1.7 | 2025 | Initial platform build, CDN setup, nav v1–v2 |
| 1.8 | Mar 2026 | CDN headers fix, ubec-design-system.css rebuild, living-labs nav migration |
| 1.9 | Mar 2026 | Nav font sizes, legal pages EN/DE/PL, portal multilingual, living-labs register/welcome pages |
| 2.0 | Mar 2026 | Steward deployment status table, login pages, steward dashboard |
| 2.1 | Mar 2026 | Hub multilingual landing pages (EN/DE/PL), nginx alias→root fix, management dashboard in priority queue, full INSTRUCTIONS.md rewrite as single canonical document |

---

*Document maintained under CC BY-SA 4.0 · Code under GNU AGPL v3.0*
*Version 2.1 · March 2026 · living-labs@ubec.network*
