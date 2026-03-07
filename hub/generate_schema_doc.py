#!/usr/bin/env python3
"""
Script: generate_schema_doc.py
Service: hub (iot.ubec.network)
Purpose: Introspect the ubec_hub PostgreSQL schema and produce a Markdown
         document suitable for uploading to the project knowledge base.
         Run this whenever the schema changes to keep documentation current.

Usage:
    cd /srv/ubec/hub
    source .venv/bin/activate
    python3 generate_schema_doc.py

    # Optional: write to specific output file
    python3 generate_schema_doc.py --output /tmp/ubec_hub_schema.md

Output: ubec_hub_schema_doc.md (in current directory by default)

License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import argparse
import sys
from datetime import datetime, timezone
from typing import Any

import psycopg2
import psycopg2.extras

# ── Connection — reads same .env as the application ──────────────────────────

def load_env(path: str = ".env") -> dict[str, str]:
    """Parse .env file into a dict. No external dependencies."""
    env: dict[str, str] = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                env[key.strip()] = val.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env


def get_connection(env: dict[str, str]):
    return psycopg2.connect(
        host     = env.get("DB_HOST", "127.0.0.1"),
        port     = int(env.get("DB_PORT", "5432")),
        dbname   = env.get("DB_NAME", "ubec_hub"),
        user     = env.get("DB_USER", "ubec_hub_app"),
        password = env.get("DB_PASSWORD", ""),
        options  = "-c search_path=ubec_hub,public",
    )


SCHEMA = "ubec_hub"

# ── Queries ───────────────────────────────────────────────────────────────────

SQL_TABLES = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = %s
  AND table_type = 'BASE TABLE'
ORDER BY table_name;
"""

SQL_COLUMNS = """
SELECT
    c.column_name,
    c.data_type,
    c.character_maximum_length,
    c.numeric_precision,
    c.numeric_scale,
    c.is_nullable,
    c.column_default,
    c.udt_name
FROM information_schema.columns c
WHERE c.table_schema = %s
  AND c.table_name   = %s
ORDER BY c.ordinal_position;
"""

SQL_CONSTRAINTS = """
SELECT
    con.conname                        AS name,
    con.contype                        AS type,
    pg_get_constraintdef(con.oid)      AS definition
FROM pg_constraint con
JOIN pg_namespace  nsp ON nsp.oid = con.connamespace
JOIN pg_class      cls ON cls.oid = con.conrelid
WHERE nsp.nspname = %s
  AND cls.relname = %s
ORDER BY con.contype, con.conname;
"""

SQL_INDEXES = """
SELECT
    i.relname                          AS index_name,
    ix.indisunique                     AS is_unique,
    ix.indisprimary                    AS is_primary,
    array_agg(a.attname ORDER BY k.pos) AS columns,
    pg_get_expr(ix.indpred, ix.indrelid) AS predicate
FROM pg_index     ix
JOIN pg_class     t  ON t.oid  = ix.indrelid
JOIN pg_class     i  ON i.oid  = ix.indexrelid
JOIN pg_namespace n  ON n.oid  = t.relnamespace
JOIN LATERAL unnest(ix.indkey) WITH ORDINALITY AS k(attnum, pos)
     ON TRUE
JOIN pg_attribute a  ON a.attrelid = t.oid AND a.attnum = k.attnum
WHERE n.nspname = %s
  AND t.relname = %s
GROUP BY i.relname, ix.indisunique, ix.indisprimary,
         ix.indpred, ix.indrelid
ORDER BY ix.indisprimary DESC, i.relname;
"""

SQL_FOREIGN_KEYS = """
SELECT
    kcu.column_name                    AS from_column,
    ccu.table_name                     AS to_table,
    ccu.column_name                    AS to_column,
    rc.delete_rule,
    rc.update_rule,
    tc.constraint_name
FROM information_schema.table_constraints        tc
JOIN information_schema.key_column_usage         kcu
     ON tc.constraint_name = kcu.constraint_name
     AND tc.table_schema   = kcu.table_schema
JOIN information_schema.referential_constraints  rc
     ON rc.constraint_name   = tc.constraint_name
     AND rc.constraint_schema = tc.table_schema
JOIN information_schema.constraint_column_usage  ccu
     ON ccu.constraint_name = rc.unique_constraint_name
     AND ccu.table_schema   = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema    = %s
  AND tc.table_name      = %s
ORDER BY kcu.column_name;
"""

SQL_ENUMS = """
SELECT
    t.typname                          AS enum_name,
    array_agg(e.enumlabel ORDER BY e.enumsortorder) AS values
FROM pg_type     t
JOIN pg_enum     e ON e.enumtypid = t.oid
JOIN pg_namespace n ON n.oid = t.typnamespace
WHERE n.nspname = %s
GROUP BY t.typname
ORDER BY t.typname;
"""

SQL_ROW_COUNTS = """
SELECT
    schemaname,
    relname AS tablename,
    n_live_tup AS row_count
FROM pg_stat_user_tables
WHERE schemaname = %s
ORDER BY relname;
"""

SQL_FUNCTIONS = """
SELECT
    p.proname                           AS name,
    pg_get_function_arguments(p.oid)    AS arguments,
    pg_get_function_result(p.oid)       AS return_type,
    l.lanname                           AS language
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
JOIN pg_language  l ON l.oid = p.prolang
WHERE n.nspname = %s
  AND p.prokind = 'f'
ORDER BY p.proname;
"""


# ── Formatters ────────────────────────────────────────────────────────────────

CONSTRAINT_TYPES = {
    "p": "PRIMARY KEY",
    "u": "UNIQUE",
    "c": "CHECK",
    "f": "FOREIGN KEY",
    "x": "EXCLUSION",
}


def fmt_col_type(row: dict[str, Any]) -> str:
    dt   = row["data_type"]
    udt  = row["udt_name"]
    clen = row["character_maximum_length"]
    np   = row["numeric_precision"]
    ns   = row["numeric_scale"]

    if dt == "character varying":
        return f"varchar({clen})" if clen else "varchar"
    if dt == "character":
        return f"char({clen})" if clen else "char"
    if dt == "numeric":
        if np and ns:
            return f"numeric({np},{ns})"
        if np:
            return f"numeric({np})"
        return "numeric"
    if dt == "ARRAY":
        return f"{udt.lstrip('_')}[]"
    if dt == "USER-DEFINED":
        return udt
    return dt


def nullable(row: dict[str, Any]) -> str:
    return "" if row["is_nullable"] == "YES" else " NOT NULL"


def default(row: dict[str, Any]) -> str:
    d = row["column_default"]
    if d is None:
        return ""
    # Truncate long defaults (e.g. uuid_generate_v4())
    if len(d) > 40:
        d = d[:37] + "..."
    return f" DEFAULT {d}"


# ── Document builder ──────────────────────────────────────────────────────────

def build_doc(cur) -> str:
    lines: list[str] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Header
    lines += [
        "# UBEC Hub — Database Schema Documentation",
        "",
        f"> **Schema:** `{SCHEMA}`  ",
        f"> **Generated:** {now}  ",
        "> **Source:** `generate_schema_doc.py`  ",
        "> Upload this file to project knowledge to keep AI sessions current.",
        "",
        "---",
        "",
    ]

    # Enum types
    cur.execute(SQL_ENUMS, (SCHEMA,))
    enums = cur.fetchall()
    if enums:
        lines += ["## Enum Types", ""]
        for e in enums:
            vals = ", ".join(f"`{v}`" for v in e["values"])
            lines.append(f"- **`{e['enum_name']}`** → {vals}")
        lines += ["", "---", ""]

    # Row counts
    cur.execute(SQL_ROW_COUNTS, (SCHEMA,))
    row_counts = {r["tablename"]: r["row_count"] for r in cur.fetchall()}

    # Tables
    cur.execute(SQL_TABLES, (SCHEMA,))
    tables = [r["table_name"] for r in cur.fetchall()]

    lines += [
        "## Tables",
        "",
        f"**Total tables:** {len(tables)}",
        "",
        "| Table | Rows |",
        "|-------|-----:|",
    ]
    for t in tables:
        lines.append(f"| `{t}` | {row_counts.get(t, 0):,} |")
    lines += ["", "---", ""]

    # Per-table detail
    lines.append("## Table Details")
    lines.append("")

    for table in tables:
        rows = row_counts.get(table, 0)
        lines += [f"### `{table}`", "", f"*{rows:,} rows*", "", "**Columns:**", ""]
        lines += [
            "| Column | Type | Nullable | Default |",
            "|--------|------|----------|---------|",
        ]

        cur.execute(SQL_COLUMNS, (SCHEMA, table))
        for col in cur.fetchall():
            col_type = fmt_col_type(col)
            null_str = "yes" if col["is_nullable"] == "YES" else "**no**"
            def_str  = col["column_default"] or ""
            # Truncate long defaults
            if len(def_str) > 35:
                def_str = def_str[:32] + "..."
            lines.append(f"| `{col['column_name']}` | `{col_type}` | {null_str} | `{def_str}` |")

        # Foreign keys
        cur.execute(SQL_FOREIGN_KEYS, (SCHEMA, table))
        fks = cur.fetchall()
        if fks:
            lines += ["", "**Foreign keys:**", ""]
            for fk in fks:
                lines.append(
                    f"- `{fk['from_column']}` → `{SCHEMA}.{fk['to_table']}.{fk['to_column']}`"
                    f"  (ON DELETE {fk['delete_rule']})"
                )

        # Indexes (skip primary key — already obvious)
        cur.execute(SQL_INDEXES, (SCHEMA, table))
        idxs = [r for r in cur.fetchall() if not r["is_primary"]]
        if idxs:
            lines += ["", "**Indexes:**", ""]
            for idx in idxs:
                uniq = " UNIQUE" if idx["is_unique"] else ""
                cols = ", ".join(idx["columns"])
                pred = f" WHERE {idx['predicate']}" if idx["predicate"] else ""
                lines.append(f"- `{idx['index_name']}`{uniq} on (`{cols}`){pred}")

        # Check / unique constraints (not FK, not PK)
        cur.execute(SQL_CONSTRAINTS, (SCHEMA, table))
        for con in cur.fetchall():
            if con["type"] in ("p", "f"):
                continue
            ctype = CONSTRAINT_TYPES.get(con["type"], con["type"])
            lines.append(f"- **{ctype}** `{con['name']}`: `{con['definition']}`")

        lines += ["", "---", ""]

    # Functions / triggers
    cur.execute(SQL_FUNCTIONS, (SCHEMA,))
    funcs = cur.fetchall()
    if funcs:
        lines += ["## Functions", ""]
        lines += [
            "| Function | Arguments | Returns | Language |",
            "|----------|-----------|---------|----------|",
        ]
        for f in funcs:
            lines.append(
                f"| `{f['name']}` | {f['arguments'] or '—'} | "
                f"`{f['return_type']}` | {f['language']} |"
            )
        lines += ["", "---", ""]

    # Footer
    lines += [
        "",
        "*This project uses the services of Claude and Anthropic PBC to inform our*",
        "*decisions and recommendations.*",
        f"*Generated by generate_schema_doc.py · {now}*",
    ]

    return "\n".join(lines) + "\n"


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ubec_hub schema documentation")
    parser.add_argument(
        "--output", "-o",
        default="ubec_hub_schema_doc.md",
        help="Output Markdown file (default: ubec_hub_schema_doc.md)",
    )
    parser.add_argument(
        "--env", "-e",
        default=".env",
        help="Path to .env file (default: .env)",
    )
    args = parser.parse_args()

    print(f"Connecting to database…")
    env = load_env(args.env)

    try:
        conn = get_connection(env)
    except psycopg2.OperationalError as exc:
        print(f"ERROR: Could not connect to database: {exc}", file=sys.stderr)
        sys.exit(1)

    with conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            print(f"Introspecting schema `{SCHEMA}`…")
            doc = build_doc(cur)

    conn.close()

    with open(args.output, "w") as f:
        f.write(doc)

    lines = doc.count("\n")
    print(f"✓ Written to: {args.output}  ({lines} lines)")
    print(f"  Upload to project knowledge as: ubec_hub_schema_doc.md")


if __name__ == "__main__":
    main()
