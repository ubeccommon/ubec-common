# design.ubec.network — Shared Design System CDN

Serves `ubec-design-system.css` and `ubec-nav.js` to all UBEC services.

- Versioned at `/v1/` and `/v2/`
- CORS: `Access-Control-Allow-Origin: *`
- Cache: `public, max-age=3600`
- **Highest availability target in the ecosystem** — every service depends on it.

See UBEC_Server_Technical_Specifications.md §10 for Nginx config.

License: CC BY-SA 4.0
