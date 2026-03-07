# UBEC Living Labs

> Citizen science, senseBox IoT stewardship

**Domain:** `living-labs.ubec.network`
**Stack:** static
**License:** CC BY-SA 4.0

*"I am because we are. Place. Protocol. Planet."*

---

## Quick start

```bash
cp .env.example .env
# Edit .env — fill in required values
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Service role

Citizen science, senseBox IoT stewardship. See [INSTRUCTIONS.md](../../INSTRUCTIONS.md) for the full
platform architecture and design system specification.

## Design system

Styles and the universal nav bar are loaded from:

```
https://design.ubec.network/v1/ubec-design-system.css
https://design.ubec.network/v1/ubec-nav.js
```

A local fallback copy lives at `static/ubec/`.

## Attribution

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
