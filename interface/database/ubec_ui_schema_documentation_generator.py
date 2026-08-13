#!/usr/bin/env python3
"""
================================================================================
Database Schema Documentation Generator for UBEC Protocol
================================================================================
UBEC DAO Protocol - GNU General Public License v3.0

This script creates a comprehensive documentation of your database schema,
serving as the single source of truth for your database structure.

The documentation includes:
- Complete table structures with all columns and their properties
- Relationships between tables (foreign keys)
- Indexes for performance optimization
- Constraints that ensure data integrity
- Triggers and their purposes
- PostGIS spatial data documentation
- Admin authentication structure
- Four Elements token documentation
- Best practices and usage notes

Supported Schemas:
    - ubec_main: Core protocol tables (tokens, holonic, distributions, admin)
    - phenomenal: Spatial/mapping data (bioregions, POIs, ecoregions)
    - ubec_ui: UI interface data (applications, sessions)

Philosophy:
    "I am because we are" - Ubuntu Philosophy

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.

Author: UBEC DAO Protocol
Version: 2.0.0
License: GPL-3.0
"""

import psycopg2
import json
import os
import sys
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import argparse
from pathlib import Path

# Try to import python-dotenv for loading .env files
try:
    from dotenv import load_dotenv
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables only.")
    print("To install: pip install python-dotenv")
    load_dotenv = None

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================================================================================
# Constants
# ================================================================================

VERSION = "2.0.0"
DEFAULT_SCHEMAS = ["ubec_main", "phenomenal", "ubec_ui"]
DEFAULT_DATABASE = "ubec"
GENERATOR_NAME = "UBEC Protocol Schema Documenter"

# UBEC Protocol specific tables
UBEC_CORE_TABLES = {
    # ubec_main schema
    'stellar_accounts': 'Stellar blockchain account data mirror',
    'stellar_transactions': 'Transaction history from Stellar network',
    'stellar_operations': 'Individual operations within transactions',
    'ubec_balances': 'Current token balances for all four elements',
    'ubec_balance_history': 'Historical balance changes over time',
    'ubec_air_metrics': '🜁 Air (UBEC) token metrics - Diversity',
    'ubec_water_flows': '🜄 Water (UBECrc) flow tracking - Reciprocity',
    'ubec_earth_distributions': '🜃 Earth (UBECgpi) distributions - Mutualism',
    'ubec_fire_transformations': '🜂 Fire (UBECtt) transformations - Regeneration',
    'ubec_holonic_metrics': 'Ubuntu principle evaluation scores',
    'ubec_distributions': 'Token distribution records (65/30/5 model)',
    'beneficiary_applications': 'Applications to become UBEC beneficiaries',
    'admin_users': 'Admin user authentication and authorization',
    'admin_sessions': 'Admin session management',
    'admin_audit_log': 'Admin action audit trail',
    'email_queue': 'Outbound email queue',
    # phenomenal schema
    'bioregion_boundaries': 'Community-submitted bioregion polygons',
    'points_of_interest': 'Points of interest within bioregions',
    'ecoregions': 'WWF Ecoregions2017 reference data',
    'watersheds': 'FEOW HydroSHEDS watershed boundaries',
    # ubec_ui schema
    'applications': 'UI beneficiary application submissions',
    'sessions': 'UI session tracking',
}

# The Four Elements
UBEC_ELEMENTS = {
    'air': {'symbol': '🜁', 'token': 'UBEC', 'principle': 'Diversity'},
    'water': {'symbol': '🜄', 'token': 'UBECrc', 'principle': 'Reciprocity'},
    'earth': {'symbol': '🜃', 'token': 'UBECgpi', 'principle': 'Mutualism'},
    'fire': {'symbol': '🜂', 'token': 'UBECtt', 'principle': 'Regeneration'},
}

# Holonic categories
HOLONIC_CATEGORIES = {
    'observer': {'level': 1, 'description': 'Initial participation'},
    'participant': {'level': 2, 'description': 'Active member'},
    'contributor': {'level': 3, 'description': 'Regular contributor'},
    'steward': {'level': 4, 'description': 'Community steward'},
    'exemplar': {'level': 5, 'description': 'Ubuntu exemplar'},
}

# ================================================================================
# Environment Configuration
# ================================================================================

def find_and_load_env_file() -> bool:
    """Search for and load .env file."""
    if load_dotenv is None:
        return False
        
    paths_to_check = [
        Path.cwd() / '.env',
        Path.cwd().parent / '.env',
    ]
    
    for env_path in paths_to_check:
        if env_path.exists():
            logger.info(f"Found .env at: {env_path}")
            load_dotenv(env_path)
            return True
    return False


def get_database_config() -> Dict[str, Any]:
    """Get database configuration from environment variables."""
    find_and_load_env_file()
    
    # Support both UI_DB_* and DB_* patterns (matching ui_db_connection.py)
    config = {
        'host': os.getenv('UI_DB_HOST', os.getenv('DB_HOST', 'localhost')),
        'port': int(os.getenv('UI_DB_PORT', os.getenv('DB_PORT', '5432'))),
        'database': os.getenv('UI_DB_NAME', os.getenv('DB_NAME', DEFAULT_DATABASE)),
        'user': os.getenv('UI_DB_USER', os.getenv('DB_USER', 'postgres')),
        'password': os.getenv('UI_DB_PASSWORD', os.getenv('DB_PASSWORD', ''))
    }
    
    if not config['password']:
        raise ValueError("Database password not configured. Set UI_DB_PASSWORD or DB_PASSWORD.")
    
    return config


# ================================================================================
# Schema Documenter Class
# ================================================================================

class SchemaDocumenter:
    """Comprehensive schema documentation generator for UBEC Protocol."""
    
    def __init__(self, connection_params: Dict[str, Any], schemas: List[str] = None):
        self.connection_params = connection_params
        self.schemas = schemas or DEFAULT_SCHEMAS
        self.conn = None
        self.documentation = {
            'metadata': {},
            'schemas': {},
            'admin': {},
            'summary': {}
        }
        
    def connect(self) -> None:
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.conn.autocommit = True
            logger.info("Connected to database")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise
            
    def disconnect(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Disconnected from database")
            
    def generate_documentation(self) -> Dict[str, Any]:
        """Generate complete schema documentation."""
        logger.info(f"Documenting schemas: {', '.join(self.schemas)}")
        
        self._document_metadata()
        
        for schema in self.schemas:
            if self._schema_exists(schema):
                logger.info(f"Documenting: {schema}")
                self._document_schema(schema)
            else:
                logger.warning(f"Schema '{schema}' not found")
        
        self._document_admin_structure()
        self._generate_summary()
        
        return self.documentation
    
    def _schema_exists(self, schema_name: str) -> bool:
        """Check if schema exists."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = %s)
        """, (schema_name,))
        exists = cursor.fetchone()[0]
        cursor.close()
        return exists
        
    def _document_metadata(self) -> None:
        """Document database metadata."""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT version()")
        pg_version = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT pg_database_size(current_database()),
                   pg_size_pretty(pg_database_size(current_database()))
        """)
        db_size = cursor.fetchone()
        
        # Check PostGIS
        cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis')")
        has_postgis = cursor.fetchone()[0]
        
        postgis_version = None
        if has_postgis:
            try:
                cursor.execute("SELECT PostGIS_Version()")
                postgis_version = cursor.fetchone()[0]
            except:
                pass
        
        self.documentation['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'documented_schemas': self.schemas,
            'database_name': self.connection_params.get('database'),
            'database_version': pg_version,
            'database_size': {'bytes': db_size[0], 'human_readable': db_size[1]},
            'extensions': {'postgis': has_postgis, 'postgis_version': postgis_version},
            'documentation_version': VERSION,
            'generator': GENERATOR_NAME,
            'elements': UBEC_ELEMENTS,
            'holonic_categories': HOLONIC_CATEGORIES
        }
        cursor.close()
        
    def _document_schema(self, schema_name: str) -> None:
        """Document all objects in a schema."""
        schema_doc = {
            'tables': {},
            'indexes': {},
            'triggers': {},
            'functions': [],
            'spatial_tables': [],
            'relationships': []
        }
        
        self._document_tables(schema_name, schema_doc)
        self._document_indexes(schema_name, schema_doc)
        self._document_triggers(schema_name, schema_doc)
        self._document_functions(schema_name, schema_doc)
        self._document_relationships(schema_name, schema_doc)
        
        if self.documentation['metadata']['extensions']['postgis']:
            self._document_spatial_tables(schema_name, schema_doc)
        
        self.documentation['schemas'][schema_name] = schema_doc
        
    def _document_tables(self, schema_name: str, schema_doc: Dict) -> None:
        """Document all tables in schema."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT t.table_name, obj_description(c.oid) as comment
            FROM information_schema.tables t
            JOIN pg_class c ON c.relname = t.table_name
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE t.table_schema = %s AND t.table_type = 'BASE TABLE' AND n.nspname = %s
            ORDER BY t.table_name
        """, (schema_name, schema_name))
        
        tables = cursor.fetchall()
        logger.info(f"  Found {len(tables)} tables")
        
        for table_name, table_comment in tables:
            # Get columns
            cursor.execute("""
                SELECT c.column_name, c.data_type, c.udt_name, c.character_maximum_length,
                       c.numeric_precision, c.numeric_scale, c.is_nullable, c.column_default
                FROM information_schema.columns c
                WHERE c.table_schema = %s AND c.table_name = %s
                ORDER BY c.ordinal_position
            """, (schema_name, table_name))
            
            columns = []
            for col in cursor.fetchall():
                columns.append({
                    'name': col[0],
                    'data_type': self._format_data_type(col[1], col[2], col[3], col[4], col[5]),
                    'nullable': col[6] == 'YES',
                    'default': col[7],
                    'is_spatial': col[2] in ('geometry', 'geography')
                })
            
            # Get constraints
            cursor.execute("""
                SELECT con.conname, con.contype, pg_get_constraintdef(con.oid)
                FROM pg_constraint con
                JOIN pg_namespace nsp ON nsp.oid = con.connamespace
                WHERE nsp.nspname = %s AND con.conrelid = (
                    SELECT oid FROM pg_class WHERE relname = %s 
                    AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s)
                )
            """, (schema_name, table_name, schema_name))
            
            constraint_map = {'p': 'PRIMARY KEY', 'u': 'UNIQUE', 'c': 'CHECK', 'f': 'FOREIGN KEY'}
            constraints = [{'name': c[0], 'type': constraint_map.get(c[1], c[1]), 'definition': c[2]} 
                          for c in cursor.fetchall()]
            
            # Get stats
            try:
                cursor.execute(f"""
                    SELECT COUNT(*), pg_size_pretty(pg_total_relation_size('{schema_name}.{table_name}'))
                    FROM {schema_name}.{table_name}
                """)
                stats = cursor.fetchone()
            except:
                stats = (0, 'Unknown')
            
            schema_doc['tables'][table_name] = {
                'schema': schema_name,
                'comment': table_comment,
                'ubec_description': UBEC_CORE_TABLES.get(table_name),
                'category': self._categorize_table(table_name, schema_name),
                'columns': columns,
                'constraints': constraints,
                'statistics': {'row_count': stats[0], 'total_size': stats[1]},
                'is_ubec_core': table_name in UBEC_CORE_TABLES,
                'has_spatial_columns': any(c['is_spatial'] for c in columns)
            }
        cursor.close()
        
    def _categorize_table(self, table_name: str, schema_name: str) -> str:
        """Categorize table by purpose."""
        if schema_name == 'phenomenal':
            return 'spatial'
        elif 'admin' in table_name:
            return 'admin'
        elif 'stellar' in table_name:
            return 'blockchain'
        elif 'holonic' in table_name:
            return 'holonic'
        elif 'distribution' in table_name:
            return 'distribution'
        elif any(e in table_name for e in ['air', 'water', 'earth', 'fire']):
            return 'element'
        elif 'ubec_' in table_name:
            return 'protocol'
        elif 'email' in table_name:
            return 'email'
        elif 'application' in table_name or 'session' in table_name:
            return 'ui'
        return 'other'
        
    def _format_data_type(self, data_type, udt_name, char_len, num_prec, num_scale) -> str:
        """Format data type string."""
        if udt_name in ('geometry', 'geography'):
            return udt_name
        if data_type == 'character varying' and char_len:
            return f"varchar({char_len})"
        if data_type == 'numeric' and num_prec:
            return f"numeric({num_prec},{num_scale})" if num_scale else f"numeric({num_prec})"
        if data_type == 'ARRAY':
            return f"{udt_name}[]"
        return data_type
            
    def _document_relationships(self, schema_name: str, schema_doc: Dict) -> None:
        """Document foreign key relationships."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT tc.table_name, kcu.column_name, ccu.table_name, ccu.column_name,
                       tc.constraint_name, rc.delete_rule
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
                JOIN information_schema.referential_constraints rc ON rc.constraint_name = tc.constraint_name
                WHERE tc.table_schema = %s AND tc.constraint_type = 'FOREIGN KEY'
            """, (schema_name,))
            
            schema_doc['relationships'] = [
                {'from_table': r[0], 'from_column': r[1], 'to_table': r[2], 
                 'to_column': r[3], 'constraint_name': r[4], 'delete_rule': r[5]}
                for r in cursor.fetchall()
            ]
        except Exception as e:
            logger.warning(f"Could not document relationships: {e}")
            schema_doc['relationships'] = []
        cursor.close()
            
    def _document_indexes(self, schema_name: str, schema_doc: Dict) -> None:
        """Document indexes."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT indexname, tablename, indexdef FROM pg_indexes
            WHERE schemaname = %s ORDER BY tablename
        """, (schema_name,))
        
        indexes_by_table = {}
        for idx in cursor.fetchall():
            table = idx[1]
            if table not in indexes_by_table:
                indexes_by_table[table] = []
            indexes_by_table[table].append({
                'name': idx[0],
                'definition': idx[2],
                'is_primary': idx[0].endswith('_pkey'),
                'is_spatial': 'gist' in idx[2].lower()
            })
        schema_doc['indexes'] = indexes_by_table
        cursor.close()
        
    def _document_triggers(self, schema_name: str, schema_doc: Dict) -> None:
        """Document triggers."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT trigger_name, event_object_table, event_manipulation, action_timing
            FROM information_schema.triggers WHERE trigger_schema = %s
        """, (schema_name,))
        
        triggers_by_table = {}
        for trg in cursor.fetchall():
            table = trg[1]
            if table not in triggers_by_table:
                triggers_by_table[table] = []
            triggers_by_table[table].append({
                'name': trg[0], 'event': trg[2], 'timing': trg[3]
            })
        schema_doc['triggers'] = triggers_by_table
        cursor.close()
        
    def _document_functions(self, schema_name: str, schema_doc: Dict) -> None:
        """Document functions."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT p.proname, pg_get_function_result(p.oid), pg_get_function_arguments(p.oid)
                FROM pg_proc p
                JOIN pg_namespace n ON n.oid = p.pronamespace
                WHERE n.nspname = %s AND p.prokind IN ('f', 'p')
            """, (schema_name,))
            schema_doc['functions'] = [
                {'name': f[0], 'return_type': f[1], 'arguments': f[2]}
                for f in cursor.fetchall()
            ]
        except:
            schema_doc['functions'] = []
        cursor.close()
            
    def _document_spatial_tables(self, schema_name: str, schema_doc: Dict) -> None:
        """Document PostGIS spatial tables."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT f_table_name, f_geometry_column, coord_dimension, srid, type
                FROM geometry_columns WHERE f_table_schema = %s
            """, (schema_name,))
            schema_doc['spatial_tables'] = [
                {'table_name': s[0], 'geometry_column': s[1], 'dimensions': s[2], 
                 'srid': s[3], 'geometry_type': s[4]}
                for s in cursor.fetchall()
            ]
        except:
            schema_doc['spatial_tables'] = []
        cursor.close()
            
    def _document_admin_structure(self) -> None:
        """Document admin users."""
        cursor = self.conn.cursor()
        admin_info = {'users': [], 'tables_exist': False}
        
        try:
            cursor.execute("""
                SELECT id, username, email, role, is_active, last_login_at
                FROM ubec_main.admin_users ORDER BY id
            """)
            admin_info['tables_exist'] = True
            admin_info['users'] = [
                {'id': u[0], 'username': u[1], 'email': u[2], 'role': u[3],
                 'is_active': u[4], 'last_login_at': u[5].isoformat() if u[5] else None}
                for u in cursor.fetchall()
            ]
        except:
            pass
        
        self.documentation['admin'] = admin_info
        cursor.close()

    def _generate_summary(self) -> None:
        """Generate summary statistics."""
        total_tables = total_columns = total_indexes = total_triggers = 0
        total_functions = total_relationships = spatial_tables = 0
        tables_by_schema = {}
        tables_by_category = {}
        
        for schema_name, schema_doc in self.documentation['schemas'].items():
            tables = schema_doc.get('tables', {})
            tables_by_schema[schema_name] = len(tables)
            total_tables += len(tables)
            
            for table_info in tables.values():
                total_columns += len(table_info.get('columns', []))
                cat = table_info.get('category', 'other')
                tables_by_category[cat] = tables_by_category.get(cat, 0) + 1
                if table_info.get('has_spatial_columns'):
                    spatial_tables += 1
            
            total_indexes += sum(len(i) for i in schema_doc.get('indexes', {}).values())
            total_triggers += sum(len(t) for t in schema_doc.get('triggers', {}).values())
            total_functions += len(schema_doc.get('functions', []))
            total_relationships += len(schema_doc.get('relationships', []))
            spatial_tables += len(schema_doc.get('spatial_tables', []))
        
        ubec_core = sum(1 for s in self.documentation['schemas'].values() 
                       for t in s.get('tables', {}).values() if t.get('is_ubec_core'))
        
        self.documentation['summary'] = {
            'total_schemas': len(self.documentation['schemas']),
            'total_tables': total_tables,
            'total_columns': total_columns,
            'total_relationships': total_relationships,
            'total_indexes': total_indexes,
            'total_triggers': total_triggers,
            'total_functions': total_functions,
            'ubec_core_tables': ubec_core,
            'spatial_tables': spatial_tables,
            'tables_by_schema': tables_by_schema,
            'tables_by_category': tables_by_category
        }
        
    def save_documentation(self, output_format: str = 'markdown', output_file: str = None) -> str:
        """Save documentation to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext_map = {'markdown': 'md', 'json': 'json', 'html': 'html'}
        
        if not output_file:
            output_file = f"database/ubec_ui_schema_documentation_{timestamp}.{ext_map.get(output_format, 'md')}"
        
        if output_format == 'markdown':
            self._save_markdown(output_file)
        elif output_format == 'json':
            self._save_json(output_file)
        elif output_format == 'html':
            self._save_html(output_file)
            
        return output_file
            
    def _save_markdown(self, filename: str) -> None:
        """Save as Markdown."""
        meta = self.documentation['metadata']
        summary = self.documentation['summary']
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# UBEC Protocol - Database Schema Documentation\n\n")
            f.write("> **Single Source of Truth** | *\"I am because we are\"*\n\n---\n\n")
            
            # Metadata
            f.write("## Metadata\n\n")
            f.write(f"| Property | Value |\n|----------|-------|\n")
            f.write(f"| Generated | {meta['generated_at']} |\n")
            f.write(f"| Database | `{meta['database_name']}` |\n")
            f.write(f"| Size | {meta['database_size']['human_readable']} |\n")
            f.write(f"| PostGIS | {'✅ ' + str(meta['extensions']['postgis_version']) if meta['extensions']['postgis'] else '❌'} |\n\n")
            
            # Four Elements
            f.write("## The Four Elements\n\n")
            f.write("| Element | Symbol | Token | Principle |\n|---------|--------|-------|----------|\n")
            for e, info in UBEC_ELEMENTS.items():
                f.write(f"| {e.title()} | {info['symbol']} | {info['token']} | {info['principle']} |\n")
            f.write("\n")
            
            # Summary
            f.write("## Summary\n\n")
            f.write(f"| Metric | Count |\n|--------|-------|\n")
            for key in ['total_schemas', 'total_tables', 'total_columns', 'total_relationships', 
                       'total_indexes', 'spatial_tables', 'ubec_core_tables']:
                f.write(f"| {key.replace('_', ' ').title()} | {summary[key]} |\n")
            f.write("\n")
            
            # Schemas
            for schema_name, schema_doc in self.documentation['schemas'].items():
                f.write(f"---\n\n## Schema: `{schema_name}`\n\n")
                
                for table_name, info in sorted(schema_doc['tables'].items()):
                    badges = ""
                    if info.get('is_ubec_core'): badges += " 🏛️"
                    if info.get('has_spatial_columns'): badges += " 🗺️"
                    
                    f.write(f"### {table_name}{badges}\n\n")
                    if info.get('ubec_description'):
                        f.write(f"> {info['ubec_description']}\n\n")
                    
                    stats = info['statistics']
                    f.write(f"**Category:** `{info['category']}` | **Rows:** {stats['row_count']:,} | **Size:** {stats['total_size']}\n\n")
                    
                    f.write("| Column | Type | Nullable | Default |\n|--------|------|----------|--------|\n")
                    for col in info['columns']:
                        null = '✓' if col['nullable'] else '✗'
                        default = str(col['default'])[:25] if col['default'] else '-'
                        spatial = ' 🗺️' if col.get('is_spatial') else ''
                        f.write(f"| `{col['name']}`{spatial} | {col['data_type']} | {null} | {default} |\n")
                    f.write("\n")
                
                # Relationships
                if schema_doc.get('relationships'):
                    f.write(f"### Relationships\n\n")
                    f.write("| From | → | To | On Delete |\n|------|---|----|-----------|\n")
                    for r in schema_doc['relationships']:
                        f.write(f"| `{r['from_table']}.{r['from_column']}` | → | `{r['to_table']}.{r['to_column']}` | {r['delete_rule']} |\n")
                    f.write("\n")
                
                # Spatial
                if schema_doc.get('spatial_tables'):
                    f.write(f"### Spatial Data\n\n")
                    f.write("| Table | Column | Type | SRID |\n|-------|--------|------|------|\n")
                    for s in schema_doc['spatial_tables']:
                        f.write(f"| `{s['table_name']}` | {s['geometry_column']} | {s['geometry_type']} | {s['srid']} |\n")
                    f.write("\n")
            
            # Admin
            admin = self.documentation.get('admin', {})
            if admin.get('users'):
                f.write("---\n\n## Admin Users\n\n")
                f.write("| Username | Email | Role | Active |\n|----------|-------|------|--------|\n")
                for u in admin['users']:
                    active = '✅' if u['is_active'] else '❌'
                    f.write(f"| `{u['username']}` | {u['email']} | {u['role']} | {active} |\n")
                f.write("\n")
            
            f.write("---\n\n*Generated by UBEC Protocol Schema Documenter*\n")
            f.write("*This project uses the services of Claude and Anthropic PBC.*\n")
        
        print(f"\n✅ Saved: {filename}")
        
    def _save_json(self, filename: str) -> None:
        """Save as JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.documentation, f, indent=2, default=str, ensure_ascii=False)
        print(f"\n✅ Saved: {filename}")
        
    def _save_html(self, filename: str) -> None:
        """Save as HTML."""
        meta = self.documentation['metadata']
        summary = self.documentation['summary']
        
        html = f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8"><title>UBEC Schema Documentation</title>
<style>
:root {{ --primary: #667eea; --bg: #f5f7fa; }}
body {{ font-family: system-ui, sans-serif; background: var(--bg); margin: 0; padding: 20px; }}
.container {{ max-width: 1200px; margin: 0 auto; }}
h1 {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
.card {{ background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #eee; }}
th {{ background: var(--bg); }}
.elements {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
.element {{ padding: 20px; border-radius: 8px; text-align: center; color: white; }}
.air {{ background: #87CEEB; }} .water {{ background: #4A90E2; }}
.earth {{ background: #8BC34A; }} .fire {{ background: #FF6B6B; }}
code {{ background: #e8e8e8; padding: 2px 6px; border-radius: 3px; }}
</style></head><body>
<div class="container">
<h1>🌍 UBEC Protocol Schema<br><small>"I am because we are"</small></h1>

<div class="elements">
<div class="element air"><div style="font-size:2em">🜁</div><b>Air (UBEC)</b><div>Diversity</div></div>
<div class="element water"><div style="font-size:2em">🜄</div><b>Water (UBECrc)</b><div>Reciprocity</div></div>
<div class="element earth"><div style="font-size:2em">🜃</div><b>Earth (UBECgpi)</b><div>Mutualism</div></div>
<div class="element fire"><div style="font-size:2em">🜂</div><b>Fire (UBECtt)</b><div>Regeneration</div></div>
</div>

<div class="card">
<h2>Summary</h2>
<table>
<tr><th>Schemas</th><th>Tables</th><th>Columns</th><th>Relationships</th><th>Indexes</th><th>Spatial</th></tr>
<tr><td>{summary['total_schemas']}</td><td>{summary['total_tables']}</td><td>{summary['total_columns']}</td>
<td>{summary['total_relationships']}</td><td>{summary['total_indexes']}</td><td>{summary['spatial_tables']}</td></tr>
</table>
</div>

<div class="card">
<h2>Metadata</h2>
<table>
<tr><td>Generated</td><td>{meta['generated_at']}</td></tr>
<tr><td>Database</td><td><code>{meta['database_name']}</code></td></tr>
<tr><td>Size</td><td>{meta['database_size']['human_readable']}</td></tr>
<tr><td>PostGIS</td><td>{'✅ ' + str(meta['extensions']['postgis_version']) if meta['extensions']['postgis'] else '❌'}</td></tr>
</table>
</div>

<div style="text-align:center;color:#666;margin-top:40px">
<p>Generated by UBEC Protocol Schema Documenter v{VERSION}</p>
</div>
</div></body></html>"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n✅ Saved: {filename}")


# ================================================================================
# Main Entry Point
# ================================================================================

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate database schema documentation for UBEC Protocol'
    )
    
    try:
        env_config = get_database_config()
    except ValueError as e:
        print(f"\n❌ {e}")
        print("\nSet environment variables: UI_DB_HOST, UI_DB_PORT, UI_DB_NAME, UI_DB_USER, UI_DB_PASSWORD")
        return 1
    
    parser.add_argument('--host', default=env_config['host'])
    parser.add_argument('--port', type=int, default=env_config['port'])
    parser.add_argument('--database', default=env_config['database'])
    parser.add_argument('--user', default=env_config['user'])
    parser.add_argument('--password', default=env_config['password'])
    parser.add_argument('--schemas', nargs='+', default=DEFAULT_SCHEMAS)
    parser.add_argument('--format', choices=['markdown', 'json', 'html'], default='markdown')
    parser.add_argument('--output', '-o')
    parser.add_argument('--debug', action='store_true')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("\n" + "=" * 60)
    print("  🌍 UBEC Protocol Schema Documenter")
    print("     \"I am because we are\"")
    print("=" * 60)
    print(f"\n🔗 {args.host}:{args.port}/{args.database}")
    print(f"📦 Schemas: {', '.join(args.schemas)}\n")
    
    conn_params = {
        'host': args.host, 'port': args.port, 'database': args.database,
        'user': args.user, 'password': args.password
    }
    
    documenter = SchemaDocumenter(conn_params, args.schemas)
    
    try:
        documenter.connect()
        documenter.generate_documentation()
        output_file = documenter.save_documentation(args.format, args.output)
        
        summary = documenter.documentation['summary']
        print(f"\n📊 Summary: {summary['total_tables']} tables, {summary['total_columns']} columns")
        print(f"   {summary['total_relationships']} relationships, {summary['spatial_tables']} spatial")
        print("\n✨ Documentation complete!\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    finally:
        documenter.disconnect()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
