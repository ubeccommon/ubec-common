# UBEC Database Documenter Enhancement Guide

**Version 5.0 - Complete Enterprise Edition**

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## Overview

The enhanced UBEC database documenter (v5.0) provides **complete enterprise-grade documentation** of your PostgreSQL database, including comprehensive security analysis, structural details, and operational metadata that was missing from the previous version.

## What's New in Version 5.0

### 1. **Complete User & Role Documentation**

#### Database Users
- User IDs and authentication details
- Superuser status and privileges
- Database creation permissions
- Replication capabilities
- Row-level security bypass status
- Account expiration dates
- Configuration settings
- Role memberships

#### Database Roles
- Login capabilities
- Privilege inheritance
- Role creation permissions
- Connection limits
- Role membership hierarchy
- Grant relationships

### 2. **Comprehensive Permission Analysis**

#### Schema-Level Permissions
- USAGE privileges
- CREATE privileges
- Per-user/role grants

#### Table-Level Permissions
- SELECT, INSERT, UPDATE, DELETE
- TRUNCATE, REFERENCES, TRIGGER
- Grantable privileges (WITH GRANT OPTION)
- Complete permission matrix per table

#### Row-Level Security (RLS)
- Policy names and definitions
- Policy commands (SELECT, INSERT, UPDATE, DELETE, ALL)
- Permissive vs restrictive policies
- Applicable roles
- USING expressions
- CHECK expressions

### 3. **Advanced Constraint Documentation**

#### Primary Keys
- Column composition
- Constraint names
- Index association

#### Foreign Keys
- Source and target columns
- Referenced tables and schemas
- ON UPDATE actions
- ON DELETE actions
- Complete referential integrity map

#### Unique Constraints
- Multi-column unique indexes
- Named constraints
- Implicit vs explicit definitions

#### Check Constraints
- Constraint expressions
- Column validations
- Table-level checks

### 4. **Detailed Index Analysis**

For each index:
- Index name and type (btree, gin, gist, etc.)
- Column composition
- Uniqueness property
- Primary key association
- Physical size on disk
- Full index definition (CREATE INDEX statement)

### 5. **Trigger Documentation**

Complete trigger information:
- Trigger names
- Timing (BEFORE, AFTER, INSTEAD OF)
- Events (INSERT, DELETE, UPDATE, TRUNCATE)
- Level (ROW, STATEMENT)
- Associated function names
- Full trigger definitions

### 6. **Sequence Tracking**

For all sequences:
- Start values
- Increment values
- Minimum and maximum bounds
- Cache sizes
- Cycle behavior
- Ownership relationships (table.column)

### 7. **Extension Registry**

Complete PostgreSQL extensions:
- Extension names
- Installed versions
- Schema locations
- Descriptions
- Dependencies

### 8. **Table & Column Comments**

- PostgreSQL COMMENT metadata extraction
- Table-level descriptions
- Column-level documentation
- Inline display in documentation

### 9. **Enhanced Statistics**

Per schema:
- Table counts
- View counts
- Function counts
- Total row counts
- Physical storage sizes

Database-wide:
- Total schemas analyzed
- Aggregate table/view/function counts
- Total data rows
- Total column count
- Foreign key relationship count

---

## Usage Guide

### Basic Usage

```bash
# Document all schemas with full security analysis
python ubec_schema_documenter_enhanced.py

# Document specific schemas
python ubec_schema_documenter_enhanced.py --schemas ubec_main phenomenal

# Skip security documentation (faster)
python ubec_schema_documenter_enhanced.py --no-security

# Include system schemas
python ubec_schema_documenter_enhanced.py --include-system
```

### Output Formats

```bash
# Generate markdown (default)
python ubec_schema_documenter_enhanced.py --format markdown

# Generate JSON for programmatic access
python ubec_schema_documenter_enhanced.py --format json

# Custom output filename
python ubec_schema_documenter_enhanced.py --output my_database_docs
```

### Advanced Options

```bash
# Full command with all options
python ubec_schema_documenter_enhanced.py \
  --host localhost \
  --port 5432 \
  --database ubec \
  --user ubec_app \
  --schemas ubec_main phenomenal \
  --format markdown \
  --output production_docs \
  --debug
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--host` | Database host | From .env or localhost |
| `--port` | Database port | From .env or 5432 |
| `--database` | Database name | From .env or ubec |
| `--user` | Database user | From .env or ubec_app |
| `--password` | Database password | From .env |
| `--schemas` | Specific schemas to document | Auto-discover all |
| `--include-system` | Include pg_* and information_schema | Excluded by default |
| `--no-security` | Skip user/role/permission documentation | Included by default |
| `--format` | Output format (markdown or json) | markdown |
| `--output` | Output filename (without extension) | Auto-generated timestamp |
| `--debug` | Enable debug logging | Disabled |

---

## Generated Documentation Structure

### Markdown Output

```
1. Database Overview
   - Summary statistics
   - Schema breakdown table

2. Extensions
   - Installed extensions with versions

3. Security (if enabled)
   - Database Users
     * User attributes
     * Role memberships
   - Database Roles
     * Role attributes
     * Grant relationships

4. Schemas
   For each schema:
   - Schema description
   - Statistics summary
   - Schema permissions
   
   - Sequences
     * Sequence properties
     * Ownership information
   
   - Tables
     For each table:
     * Table comments
     * Row count and size
     * Columns with types, nullability, defaults, comments
     * Primary keys
     * Foreign keys with actions
     * Unique constraints
     * Check constraints
     * Indexes with types and sizes
     * Triggers with events
     * Row-level security policies
     * Table permissions
   
   - Views
     * View names
     * View definitions (SQL)
   
   - Functions
     * Function signatures
     * Return types
     * Languages
     * Descriptions
```

### JSON Output

Complete structured data including:
- `metadata`: Generation info, PostgreSQL version
- `database_overview`: Aggregate statistics
- `extensions`: Extension registry
- `security`: Users, roles, permissions
- `schemas`: Full schema documentation
- `cross_schema_analysis`: Relationship mapping

---

## Example Output Sections

### User Documentation Example

```markdown
#### ubec_app

- **User ID:** 16385
- **Superuser:** No
- **Can Create DB:** No
- **Can Replicate:** No
- **Bypass RLS:** No
- **Member Of:** ubec_application_role
```

### Table Documentation Example

```markdown
#### holders

*Tracks UBEC token holders and their distribution compliance*

**Rows:** 643 | **Size:** 128 kB

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| account_id | text | ✗ | |
| balance | numeric(20,7) | ✗ | |
| trust_level | integer | ✓ | 0 |
| last_updated | timestamp with time zone | ✗ | CURRENT_TIMESTAMP |

**Primary Key:**
- holders_pkey: (account_id)

**Indexes:**
- PRIMARY btree: (account_id) - 48 kB
- BTREE: (balance) - 40 kB

**Row Level Security:** Disabled

**Permissions:**
- ubec_app: SELECT, INSERT, UPDATE, DELETE
- ubec_readonly: SELECT
```

### Foreign Key Example

```markdown
**Foreign Keys:**
- fk_distribution_holder: (account_id) → ubec_main.accounts(account_id)
  - ON UPDATE: CASCADE, ON DELETE: RESTRICT
```

### RLS Policy Example

```markdown
**Row Level Security:** Enabled

- **Policy:** user_own_data_only
  - **Command:** ALL
  - **Roles:** ubec_app
  - **USING:** `(account_id = current_user)`
  - **CHECK:** `(account_id = current_user)`
```

---

## Performance Considerations

### Large Databases

For databases with many tables (100+):
- Use `--schemas` to limit scope
- Consider using `--no-security` for faster generation
- JSON format is faster than markdown

### Security Documentation

Security analysis adds approximately 10-20% to generation time:
- User enumeration
- Role hierarchy resolution
- Permission matrix calculation
- RLS policy extraction

Skip with `--no-security` if not needed.

### Row Counting

Row counting can be slow on large tables:
- Uses `COUNT(*)` on each table
- Wrapped in exception handling
- Reports `NULL` if counting times out

---

## Integration with UBEC Project

### Project Compliance

The documenter follows all 12 UBEC design principles:

1. **Modular Design** - Self-contained documentation generator
2. **Service Pattern** - Can be imported as module or run standalone
3. **Service Registry** - No dependencies on other UBEC services
4. **Single Source of Truth** - Database is authoritative source
5. **Strict Async Operations** - Uses synchronous psycopg2 (appropriate for tooling)
6. **No Fallbacks** - Clean, precise queries
7. **Per-Asset Monitoring** - Tracks each table/schema individually
8. **No Duplicate Configuration** - Uses .env and DATABASE_URL
9. **Integrated Rate Limiting** - Not applicable (database queries)
10. **Clear Separation** - Analysis vs presentation separated
11. **Comprehensive Documentation** - Self-documenting with examples
12. **Method Singularity** - Each query method defined once

### Attribution

All generated documentation includes:
> "This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC."

---

## Troubleshooting

### Connection Issues

```
❌ Connection refused. Is PostgreSQL running?
```
**Solution:** Verify PostgreSQL is running and accessible

```
❌ Password authentication failed
```
**Solution:** Check `UBEC_DB_PASSWORD` in .env file

### Permission Issues

```
❌ Permission denied for schema
```
**Solution:** Connect with a user that has appropriate privileges

### Missing Data

```
No users found.
```
**Solution:** May need superuser privileges for pg_user queries

### Encoding Errors

The documenter includes comprehensive error handling for:
- Non-UTF-8 characters
- Large text fields
- Complex SQL definitions

---

## Best Practices

### 1. Regular Documentation

Generate documentation:
- After schema changes
- Before production deployments
- During security audits
- For compliance reporting

### 2. Version Control

Store documentation in git:
```bash
python ubec_schema_documenter_enhanced.py --output docs/database_schema
git add docs/database_schema.md
git commit -m "Update database documentation"
```

### 3. Automated Generation

Add to CI/CD pipeline:
```yaml
# .github/workflows/document.yml
- name: Generate Database Documentation
  run: |
    python ubec_schema_documenter_enhanced.py \
      --format markdown \
      --output artifacts/database_docs
```

### 4. Security Review

Use security documentation for:
- Access control audits
- Privilege minimization
- Compliance verification
- Security policy validation

### 5. Performance Analysis

Use statistics for:
- Growth tracking
- Index optimization
- Partition planning
- Capacity planning

---

## Comparison: v4.0 vs v5.0

| Feature | v4.0 | v5.0 |
|---------|------|------|
| Tables | ✓ | ✓ |
| Views | ✓ | ✓ |
| Functions | ✓ | ✓ |
| Basic columns | ✓ | ✓ |
| **Users** | ✗ | ✓ |
| **Roles** | ✗ | ✓ |
| **Schema permissions** | ✗ | ✓ |
| **Table permissions** | ✗ | ✓ |
| **Row-level security** | ✗ | ✓ |
| **Primary keys** | Partial | ✓ |
| **Foreign keys** | Partial | ✓ |
| **Unique constraints** | ✗ | ✓ |
| **Check constraints** | ✗ | ✓ |
| **Detailed indexes** | ✗ | ✓ |
| **Triggers** | ✗ | ✓ |
| **Sequences** | ✗ | ✓ |
| **Extensions** | Basic | ✓ |
| **Comments** | ✗ | ✓ |
| **Index sizes** | ✗ | ✓ |
| **FK actions** | ✗ | ✓ |

---

## Support & Contribution

### Reporting Issues

For bugs or feature requests:
1. Check existing documentation
2. Verify database connectivity
3. Enable `--debug` for detailed logs
4. Include PostgreSQL version
5. Provide sample output

### Future Enhancements

Potential additions:
- Materialized view documentation
- Partition table hierarchy
- Foreign data wrappers
- Publication/subscription (replication)
- Table inheritance trees
- Performance statistics integration
- Dependency graph visualization
- Change detection (diff between runs)

---

## Conclusion

Version 5.0 provides enterprise-grade database documentation suitable for:
- **Production audits** - Complete security and structure analysis
- **Compliance reporting** - Full permission and access documentation
- **Team onboarding** - Comprehensive reference material
- **Change management** - Baseline for tracking modifications
- **Performance tuning** - Index and constraint analysis
- **Security reviews** - RLS policy and privilege verification

The enhanced documenter is production-ready and fully aligned with UBEC protocol design principles.

---

**Generated:** 2025-11-17  
**Version:** 5.0 - Complete Enterprise Edition  
**Compatibility:** PostgreSQL 12+  
**Python:** 3.8+
