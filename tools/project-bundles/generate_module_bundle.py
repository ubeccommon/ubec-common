#!/usr/bin/env python3
"""
generate_module_bundle.py — produce the paste/upload bundle for a UBEC module's
Claude Project.

What it CAN do: generate everything you paste/upload into a Project —
  <MODULE>_PROJECT_INSTRUCTIONS.md  (paste into the Project's custom-instructions box)
  <MODULE>_MODULE_SPEC.md           (spec skeleton — infra facts filled, state = TODO)
  <MODULE>_KICKOFF_PROMPT.md        (first message for a new conversation)
  SETUP.md                          (the manual click-checklist)

What it CANNOT do: create the Project, upload files, or start a chat — those are
Claude.ai app actions with no public API. SETUP.md lists those manual steps.

The spec deliberately leaves CURRENT STATE / OPEN THREADS as TODO markers: infra
facts are pre-filled from modules.yaml, but live state must be verified in the
first session (don't ship a spec that claims an unverified state).

Usage:
    python3 generate_module_bundle.py --module erdpuls
    python3 generate_module_bundle.py --all
    python3 generate_module_bundle.py --module hub --config modules.yaml --out bundles
"""
from __future__ import annotations
import argparse, os, sys, datetime

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: PyYAML.  Install with:  pip install pyyaml --break-system-packages")

TODO = "TODO_VERIFY"


def mark(v):
    """Render a value, flagging TODO_VERIFY visibly."""
    s = str(v)
    return f"⚠️ **{s}** — verify from live before relying" if TODO in s else s


def bullets(items):
    return "\n".join(f"- {x}" for x in items) if items else "- (none)"


def project_instructions(g, m) -> str:
    return f"""# Project Instructions — {m['name']}
<!-- Paste this into the Project's "custom instructions" box. It is the persistent
     system prompt for every conversation in the {m['name']} Project. -->

You are working on **{m['name']}** (`{m['subdomain']}`), a module of {g['project']}.

## First action, every session
Read the module spec (`{m['id'].upper().replace('-','_')}_MODULE_SPEC.md`) and the shared
`INSTRUCTIONS.md` — both in this Project's knowledge base. `{g['instructions_file']}` is the
single source of truth (tracked in {g['monorepo']['remote']}); the Project copies are read
references and must be re-uploaded when they change. Verify live state before proposing.

## Core rules (always)
{bullets(g['rules'])}

## Deploy discipline (deploy-by-pull)
{bullets(g['deploy_model'])}

## Session ritual
{bullets(g['session_ritual'])}

## Truth hierarchy
{g['truth_hierarchy']}

## Module facts
- Subdomain: {m['subdomain']}  ·  Type: {m['type']}
- Repo: {mark(m['repo'])}
- Source of truth (edit here): {mark(m['source_of_truth'])}
- Live (deploy target): {mark(m['live_path'])}
- Service: {mark(m['service'])}  ·  Port: {mark(m['port'])}
- Stack: {mark(m['stack'])}  ·  DB: {mark(m['db'])}
- Server: {g['server']['provider']} · {g['server']['host']} · {g['server']['ip']} · user {g['server']['user']}
- Design CDN: {g['design_cdn']}  ·  Fonts: {g['fonts']}
{("- NOTE: " + m['note']) if m.get('note') else ""}

{g['copyright']}
"""


def module_spec(g, m) -> str:
    today = datetime.date.today().isoformat()
    return f"""# Module Spec — {m['name']}
**Project:** {g['project']}
**Module:** {m['name']} — `{m['subdomain']}`
**Purpose:** canonical current-state spec + open threads. Seed for the Project knowledge
base. Read at session start; update at session close. **Truth: git repo > spec > chat.**
**Last updated:** {today} (SKELETON — populate CURRENT STATE from live in first session)

{("> NOTE: " + m['note']) if m.get('note') else ""}

## YOUR FIRST ACTION
Read this spec, then the shared `INSTRUCTIONS.md`. Inspect the live repo/service and
verify state before proposing — never guess; confirm with `ls`/`cat`/`git log`.

## CORE RULES
{bullets(g['rules'])}

## PLATFORM CONTEXT
- Server: {g['server']['provider']} · `{g['server']['host']}` · `{g['server']['ip']}` · user `{g['server']['user']}` · {g['server']['stack']}
- Repo: {mark(m['repo'])}
- Source of truth (edit here): {mark(m['source_of_truth'])}
- Live (deploy target): {mark(m['live_path'])}
- Service: {mark(m['service'])}  ·  Port: {mark(m['port'])}
- Stack: {mark(m['stack'])}  ·  DB: {mark(m['db'])}
- Design CDN: {g['design_cdn']}  ·  Fonts: {g['fonts']}

## GIT / DEPLOY MODEL (deploy-by-pull)
{bullets(g['deploy_model'])}

## CURRENT STATE  ⚠️ TODO — populate from the live repo/service in the first session
- Architecture / routes: TODO
- Design/shell: TODO
- Database: TODO
- i18n / languages: TODO
- Recent changes landed: TODO
- Config/env gotchas: TODO

## LOCKED DECISIONS
- TODO (record decisions here as they're made)

## OPEN THREADS (priority order)
1. TODO — verify and record outstanding work

## NOT IN SCOPE
- TODO

## CONNECTIONS
{bullets(m.get('connections', []))}

---
{g['copyright']}
*Developed with Claude (Anthropic PBC)*
"""


def kickoff_prompt(g, m) -> str:
    return f"""# Kickoff Prompt — {m['name']}
<!-- Paste this as the FIRST message of a new conversation in the {m['name']} Project. -->

Start a session on **{m['name']}** (`{m['subdomain']}`).

1. Read `{m['id'].upper().replace('-','_')}_MODULE_SPEC.md` and `INSTRUCTIONS.md` from the
   Project knowledge base.
2. Before proposing anything, verify live state — inspect the repo
   ({mark(m['repo'])}) and, if applicable, the running service
   ({mark(m['service'])} on port {mark(m['port'])}). Reason from facts; if the spec's
   CURRENT STATE is still TODO, reconstruct it from the live repo first and offer to
   populate the spec.
3. Then we'll work on: **<STATE THE ONE TASK FOR THIS SESSION>**.

Follow the deploy-by-pull model (edit in source of truth → push → pull to live) and
end the session by updating the spec + committing.
"""


def setup_md(g, modules) -> str:
    lines = [
        "# SETUP — creating UBEC module Projects (manual steps)",
        "",
        "Project creation, knowledge upload, and starting a chat are Claude.ai app actions —",
        "there is no API for them. This generator produces the files; the steps below are the",
        "clicks. Do them once per module.",
        "",
        "## Per module",
        "1. Claude.ai → **Projects → Create Project**, name it e.g. `UBEC — <Module>`.",
        "2. Open the Project → **custom instructions** → paste `<MODULE>_PROJECT_INSTRUCTIONS.md`.",
        "3. Project → **knowledge base** → upload TWO files:",
        f"   - the canonical `{g['instructions_file']}` (single source of truth — pull the",
        "     current copy from the server; do not fork it), and",
        "   - `<MODULE>_MODULE_SPEC.md` (this bundle).",
        "4. Start a new chat in the Project with `<MODULE>_KICKOFF_PROMPT.md` as the first message.",
        "",
        "## Keep it from rotting",
        "- Re-upload `INSTRUCTIONS.md` to each Project whenever the canonical file changes",
        "  (the knowledge base is a snapshot, not a live link).",
        "- End every session by updating the module spec and re-uploading it.",
        "- The git repo is ground truth; the spec is a decision log; the chat is scratch.",
        "",
        "## Modules in this registry",
    ]
    for m in modules:
        lines.append(f"- **{m['name']}** (`{m['subdomain']}`) — bundle in `bundles/{m['id']}/`")
    lines += ["", g['copyright']]
    return "\n".join(lines)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  wrote {path}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="modules.yaml")
    ap.add_argument("--out", default="bundles")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--module", help="module id (e.g. erdpuls)")
    grp.add_argument("--all", action="store_true")
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config, encoding="utf-8"))
    g, modules = cfg["global"], cfg["modules"]
    by_id = {m["id"]: m for m in modules}

    if args.module:
        if args.module not in by_id:
            sys.exit(f"Unknown module '{args.module}'. Known: {', '.join(by_id)}")
        targets = [by_id[args.module]]
    else:
        targets = modules

    for m in targets:
        MID = m["id"].upper().replace("-", "_")
        d = os.path.join(args.out, m["id"])
        print(f"[{m['id']}]")
        write(os.path.join(d, f"{MID}_PROJECT_INSTRUCTIONS.md"), project_instructions(g, m))
        write(os.path.join(d, f"{MID}_MODULE_SPEC.md"), module_spec(g, m))
        write(os.path.join(d, f"{MID}_KICKOFF_PROMPT.md"), kickoff_prompt(g, m))

    write(os.path.join(args.out, "SETUP.md"), setup_md(g, modules))
    print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
