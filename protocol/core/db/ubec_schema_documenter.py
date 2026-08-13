#!/usr/bin/env python3
"""
UBEC Protocol Suite - Comprehensive Multi-Schema Database Documentation Generator
Enhanced Edition with Complete Security, Permission, and Structure Analysis

This project uses the services of Claude and Anthropic PBC to inform our 
decisions and recommendations. This project was made possible with the 
assistance of Claude and Anthropic PBC.

Generates comprehensive documentation across ALL aspects of the UBEC database:
- Auto-discovers all available schemas
- Documents all tables with columns, data types, and constraints
- Documents views, functions, triggers, and sequences
- Documents database users, roles, and permissions
- Documents indexes, foreign keys, and check constraints
- Documents row-level security policies
- Documents PostgreSQL extensions and configurations
- Cross-schema relationship tracking
- Complete security audit information

Version: 5.0.1 - Complete Enterprise Edition (Patched)
Date: November 17, 2025
"""

import psycopg2
import psycopg2.extras
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
import logging
import argparse
from pathlib import Path

# Try to import python-dotenv
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# UBEC Protocol Constants
ELEMENTS = {
    'air': {'symbol': '🜁', 'token': 'UBEC', 'principle': 'Diversity', 'role': 'Gateway & Universal Access'},
    'water': {'symbol': '🜄', 'token': 'UBECrc', 'principle': 'Reciprocity', 'role': 'Flow & Exchange'},
    'earth': {'symbol': '🜃', 'token': 'UBECgpi', 'principle': 'Mutualism', 'role': 'Stability & Value'},
    'fire': {'symbol': '🜂', 'token': 'UBECtt', 'principle': 'Regeneration', 'role': 'Transformation & Action'}
}

# Known schema descriptions
SCHEMA_DESCRIPTIONS = {
    'ubec_main': 'Four-Element Protocol - Primary operational schema for UBEC token management',
    'phenomenal': 'Phenomenological Quantum Gravity Schema - Advanced analytics and network topology',
    'topology': 'PostGIS Topology Schema - Spatial network topology and geometric relationships',
    'public': 'PostgreSQL default schema - PostGIS extensions and shared utilities'
}


def find_and_load_env_file():
    """Search for and load .env file from common locations."""
    if load_dotenv is None:
        logger.warning("python-dotenv not available, using system environment variables")
        return False
        
    current_path = Path.cwd()
    paths_to_check = [
        current_path / '.env',
        current_path.parent / '.env',
        current_path.parent.parent / '.env',
        Path('/home/triag/UBEC/projects/UBEC') / '.env',
    ]
    
    for env_path in paths_to_check:
        if env_path.exists():
            logger.info(f"Loading .env from: {env_path}")
            load_dotenv(env_path)
            return True
    
    logger.warning("No .env file found")
    return False


def get_database_config():
    """Get database configuration from environment with UBEC-specific fallbacks."""
    find_and_load_env_file()
    
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        logger.info(f"Found DATABASE_URL, parsing connection string")
        config = parse_database_url(database_url)
        logger.info(f"Parsed config: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
        return config
    
    config = {
        'host': os.environ.get('UBEC_DB_HOST') or os.environ.get('DB_HOST') or 'localhost',
        'port': int(os.environ.get('UBEC_DB_PORT') or os.environ.get('DB_PORT') or 5432),
        'database': os.environ.get('UBEC_DB_NAME') or os.environ.get('DB_NAME') or 'ubec',
        'user': os.environ.get('UBEC_DB_USER') or os.environ.get('DB_USER') or 'ubec_app',
        'password': os.environ.get('UBEC_DB_PASSWORD') or os.environ.get('DB_PASSWORD')
    }
    
    if not config['password']:
        logger.warning("No password found - attempting peer authentication")
    
    logger.info(f"Database config: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
    
    return config


def parse_database_url(url: str) -> Dict[str, Any]:
    """Parse DATABASE_URL connection string."""
    from urllib.parse import urlparse, unquote
    
    parsed = urlparse(url)
    
    config = {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/') if parsed.path else 'ubec',
        'user': unquote(parsed.username) if parsed.username else 'ubec_app',
    }
    
    if parsed.password:
        config['password'] = unquote(parsed.password)
    
    return config


class UBECComprehensiveDocumenter:
    """Comprehensive multi-schema database documentation generator with security analysis."""
    
    def __init__(self, connection_params: Dict[str, Any], 
                 schemas: Optional[List[str]] = None,
                 exclude_system_schemas: bool = True,
                 include_security: bool = True):
        """
        Initialize comprehensive documenter.
        
        Args:
            connection_params: Database connection parameters
            schemas: Specific schemas to document (None = auto-discover all)
            exclude_system_schemas: Exclude pg_* and information_schema
            include_security: Include user/role/permission documentation
        """
        self.connection_params = connection_params
        self.requested_schemas = schemas
        self.exclude_system_schemas = exclude_system_schemas
        self.include_security = include_security
        self.conn = None
        self.discovered_schemas = []
        self.documentation = {
            'metadata': {},
            'database_overview': {},
            'security': {
                'users': {},
                'roles': {},
                'schema_permissions': {},
                'table_permissions': {},
                'row_level_security': {}
            },
            'extensions': {},
            'schemas': {},
            'cross_schema_analysis': {
                'total_tables': 0,
                'total_relationships': 0,
                'schema_dependencies': []
            }
        }
        
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.conn.autocommit = True
            logger.info("Connected to UBEC database successfully")
        except psycopg2.OperationalError as e:
            if "password authentication failed" in str(e):
                logger.error("Password authentication failed. Check UBEC_DB_PASSWORD in .env")
            elif "Connection refused" in str(e):
                logger.error("Connection refused. Is PostgreSQL running?")
            elif "does not exist" in str(e):
                logger.error(f"Database '{self.connection_params['database']}' does not exist.")
            else:
                logger.error(f"Connection error: {e}")
            raise
            
    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def discover_schemas(self) -> List[str]:
        """Discover all available schemas in the database."""
        cursor = self.conn.cursor()
        
        try:
            query = """
                SELECT s.schema_name, 
                       COUNT(t.table_name) as table_count
                FROM information_schema.schemata s
                LEFT JOIN information_schema.tables t ON s.schema_name = t.table_schema
                WHERE s.schema_name NOT IN ('pg_toast', 'pg_catalog')
                GROUP BY s.schema_name
                ORDER BY s.schema_name
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            schemas = []
            for schema_name, table_count in results:
                if self.exclude_system_schemas:
                    if schema_name.startswith('pg_') or schema_name == 'information_schema':
                        logger.debug(f"Excluding system schema: {schema_name}")
                        continue
                
                if self.requested_schemas and schema_name not in self.requested_schemas:
                    logger.debug(f"Skipping non-requested schema: {schema_name}")
                    continue
                
                schemas.append(schema_name)
                logger.info(f"Discovered schema: {schema_name} ({table_count} tables)")
            
            self.discovered_schemas = schemas
            return schemas
            
        finally:
            cursor.close()
    
    def get_database_users(self) -> Dict[str, Any]:
        """Get all database users and their attributes."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            query = """
                SELECT 
                    usename as username,
                    usesysid as user_id,
                    usecreatedb as can_create_db,
                    usesuper as is_superuser,
                    userepl as can_replicate,
                    usebypassrls as bypass_rls,
                    valuntil as valid_until,
                    useconfig as config_settings
                FROM pg_user
                ORDER BY usename
            """
            
            cursor.execute(query)
            users = {}
            
            for row in cursor.fetchall():
                username = row['username']
                users[username] = {
                    'user_id': row['user_id'],
                    'can_create_db': row['can_create_db'],
                    'is_superuser': row['is_superuser'],
                    'can_replicate': row['can_replicate'],
                    'bypass_rls': row['bypass_rls'],
                    'valid_until': str(row['valid_until']) if row['valid_until'] else None,
                    'config_settings': row['config_settings'],
                    'member_of': []
                }
            
            # Get role memberships
            membership_query = """
                SELECT 
                    u.usename as username,
                    r.rolname as role_name
                FROM pg_user u
                JOIN pg_auth_members m ON u.usesysid = m.member
                JOIN pg_roles r ON m.roleid = r.oid
                ORDER BY u.usename, r.rolname
            """
            
            cursor.execute(membership_query)
            for row in cursor.fetchall():
                username = row['username']
                if username in users:
                    users[username]['member_of'].append(row['role_name'])
            
            logger.info(f"Documented {len(users)} database users")
            return users
            
        finally:
            cursor.close()
    
    def get_database_roles(self) -> Dict[str, Any]:
        """Get all database roles and their attributes."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            query = """
                SELECT 
                    rolname as role_name,
                    rolsuper as is_superuser,
                    rolinherit as inherit_privileges,
                    rolcreaterole as can_create_role,
                    rolcreatedb as can_create_db,
                    rolcanlogin as can_login,
                    rolreplication as can_replicate,
                    rolbypassrls as bypass_rls,
                    rolconnlimit as connection_limit,
                    rolvaliduntil as valid_until
                FROM pg_roles
                WHERE rolname NOT LIKE 'pg_%'
                ORDER BY rolname
            """
            
            cursor.execute(query)
            roles = {}
            
            for row in cursor.fetchall():
                role_name = row['role_name']
                roles[role_name] = {
                    'is_superuser': row['is_superuser'],
                    'inherit_privileges': row['inherit_privileges'],
                    'can_create_role': row['can_create_role'],
                    'can_create_db': row['can_create_db'],
                    'can_login': row['can_login'],
                    'can_replicate': row['can_replicate'],
                    'bypass_rls': row['bypass_rls'],
                    'connection_limit': row['connection_limit'],
                    'valid_until': str(row['valid_until']) if row['valid_until'] else None,
                    'granted_to': []
                }
            
            # Get members of each role
            membership_query = """
                SELECT 
                    r1.rolname as role_name,
                    r2.rolname as member_name
                FROM pg_roles r1
                JOIN pg_auth_members m ON r1.oid = m.roleid
                JOIN pg_roles r2 ON m.member = r2.oid
                WHERE r1.rolname NOT LIKE 'pg_%'
                ORDER BY r1.rolname, r2.rolname
            """
            
            cursor.execute(membership_query)
            for row in cursor.fetchall():
                role_name = row['role_name']
                if role_name in roles:
                    roles[role_name]['granted_to'].append(row['member_name'])
            
            logger.info(f"Documented {len(roles)} database roles")
            return roles
            
        finally:
            cursor.close()
    
    def get_schema_permissions(self, schema_name: str) -> Dict[str, List[str]]:
        """Get permissions granted on a schema."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            query = """
                SELECT 
                    n.nspname as schema_name,
                    r.rolname as grantee,
                    p.privilege_type
                FROM information_schema.usage_privileges p
                JOIN pg_namespace n ON p.object_schema = n.nspname
                JOIN pg_roles r ON p.grantee = r.rolname
                WHERE n.nspname = %s
                ORDER BY r.rolname, p.privilege_type
            """
            
            cursor.execute(query, (schema_name,))
            permissions = {}
            
            for row in cursor.fetchall():
                grantee = row['grantee']
                priv = row['privilege_type']
                
                if grantee not in permissions:
                    permissions[grantee] = []
                permissions[grantee].append(priv)
            
            return permissions
            
        finally:
            cursor.close()
    
    def get_table_permissions(self, schema_name: str, table_name: str) -> Dict[str, List[str]]:
        """Get permissions granted on a specific table."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            query = """
                SELECT 
                    grantee,
                    privilege_type,
                    is_grantable
                FROM information_schema.table_privileges
                WHERE table_schema = %s AND table_name = %s
                ORDER BY grantee, privilege_type
            """
            
            cursor.execute(query, (schema_name, table_name))
            permissions = {}
            
            for row in cursor.fetchall():
                grantee = row['grantee']
                priv = row['privilege_type']
                grantable = row['is_grantable'] == 'YES'
                
                if grantee not in permissions:
                    permissions[grantee] = []
                
                priv_str = priv
                if grantable:
                    priv_str += " (GRANT)"
                    
                permissions[grantee].append(priv_str)
            
            return permissions
            
        finally:
            cursor.close()
    
    def get_row_level_security(self, schema_name: str, table_name: str) -> Dict[str, Any]:
        """Get row-level security policies for a table."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            query = """
                SELECT 
                    polname as policy_name,
                    polcmd as command,
                    polpermissive as is_permissive,
                    polroles::regrole[] as roles,
                    pg_get_expr(polqual, polrelid) as using_expression,
                    pg_get_expr(polwithcheck, polrelid) as check_expression
                FROM pg_policy
                JOIN pg_class ON pg_policy.polrelid = pg_class.oid
                JOIN pg_namespace ON pg_class.relnamespace = pg_namespace.oid
                WHERE pg_namespace.nspname = %s AND pg_class.relname = %s
                ORDER BY polname
            """
            
            cursor.execute(query, (schema_name, table_name))
            policies = []
            
            for row in cursor.fetchall():
                policy = {
                    'name': row['policy_name'],
                    'command': row['command'],
                    'permissive': row['is_permissive'],
                    'roles': [str(r) for r in row['roles']] if row['roles'] else [],
                    'using': row['using_expression'],
                    'check': row['check_expression']
                }
                policies.append(policy)
            
            return {'enabled': len(policies) > 0, 'policies': policies}
            
        except Exception as e:
            logger.debug(f"No RLS policies for {schema_name}.{table_name}: {e}")
            return {'enabled': False, 'policies': []}
        finally:
            cursor.close()
    
    def get_table_indexes(self, schema_name: str, table_name: str) -> List[Dict[str, Any]]:
        """Get all indexes for a table with detailed information."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            query = """
                SELECT 
                    i.relname as index_name,
                    a.attname as column_name,
                    ix.indisunique as is_unique,
                    ix.indisprimary as is_primary,
                    am.amname as index_type,
                    pg_get_indexdef(ix.indexrelid) as index_definition,
                    pg_size_pretty(pg_relation_size(i.oid)) as index_size
                FROM pg_index ix
                JOIN pg_class t ON ix.indrelid = t.oid
                JOIN pg_class i ON ix.indexrelid = i.oid
                JOIN pg_namespace n ON t.relnamespace = n.oid
                JOIN pg_am am ON i.relam = am.oid
                LEFT JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                WHERE n.nspname = %s AND t.relname = %s
                ORDER BY i.relname, a.attnum
            """
            
            cursor.execute(query, (schema_name, table_name))
            
            indexes = {}
            for row in cursor.fetchall():
                index_name = row['index_name']
                if index_name not in indexes:
                    indexes[index_name] = {
                        'columns': [],
                        'unique': row['is_unique'],
                        'primary': row['is_primary'],
                        'type': row['index_type'],
                        'definition': row['index_definition'],
                        'size': row['index_size']
                    }
                if row['column_name']:
                    indexes[index_name]['columns'].append(row['column_name'])
            
            return list(indexes.values())
            
        finally:
            cursor.close()
    
    def get_table_constraints(self, schema_name: str, table_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all constraints for a table."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            constraints = {
                'check': [],
                'unique': [],
                'foreign_key': [],
                'primary_key': []
            }
            
            # Check constraints
            check_query = """
                SELECT 
                    con.conname as constraint_name,
                    pg_get_constraintdef(con.oid) as definition
                FROM pg_constraint con
                JOIN pg_class rel ON con.conrelid = rel.oid
                JOIN pg_namespace nsp ON rel.relnamespace = nsp.oid
                WHERE nsp.nspname = %s 
                AND rel.relname = %s 
                AND con.contype = 'c'
                ORDER BY con.conname
            """
            
            cursor.execute(check_query, (schema_name, table_name))
            for row in cursor.fetchall():
                constraints['check'].append({
                    'name': row['constraint_name'],
                    'definition': row['definition']
                })
            
            # Unique constraints
            unique_query = """
                SELECT 
                    con.conname as constraint_name,
                    array_agg(att.attname ORDER BY u.attposition) as columns
                FROM pg_constraint con
                JOIN pg_class rel ON con.conrelid = rel.oid
                JOIN pg_namespace nsp ON rel.relnamespace = nsp.oid
                JOIN LATERAL unnest(con.conkey) WITH ORDINALITY AS u(attnum, attposition) ON TRUE
                JOIN pg_attribute att ON att.attrelid = rel.oid AND att.attnum = u.attnum
                WHERE nsp.nspname = %s 
                AND rel.relname = %s 
                AND con.contype = 'u'
                GROUP BY con.conname
                ORDER BY con.conname
            """
            
            cursor.execute(unique_query, (schema_name, table_name))
            for row in cursor.fetchall():
                constraints['unique'].append({
                    'name': row['constraint_name'],
                    'columns': row['columns']
                })
            
            # Foreign key constraints
            fk_query = """
                SELECT 
                    con.conname as constraint_name,
                    array_agg(att.attname ORDER BY u.attposition) as columns,
                    nspf.nspname as foreign_schema,
                    clf.relname as foreign_table,
                    array_agg(attf.attname ORDER BY u.attposition) as foreign_columns,
                    con.confupdtype as on_update,
                    con.confdeltype as on_delete
                FROM pg_constraint con
                JOIN pg_class rel ON con.conrelid = rel.oid
                JOIN pg_namespace nsp ON rel.relnamespace = nsp.oid
                JOIN pg_class clf ON con.confrelid = clf.oid
                JOIN pg_namespace nspf ON clf.relnamespace = nspf.oid
                JOIN LATERAL unnest(con.conkey) WITH ORDINALITY AS u(attnum, attposition) ON TRUE
                JOIN pg_attribute att ON att.attrelid = rel.oid AND att.attnum = u.attnum
                JOIN LATERAL unnest(con.confkey) WITH ORDINALITY AS uf(attnum, attposition) ON u.attposition = uf.attposition
                JOIN pg_attribute attf ON attf.attrelid = clf.oid AND attf.attnum = uf.attnum
                WHERE nsp.nspname = %s 
                AND rel.relname = %s 
                AND con.contype = 'f'
                GROUP BY con.conname, nspf.nspname, clf.relname, con.confupdtype, con.confdeltype
                ORDER BY con.conname
            """
            
            cursor.execute(fk_query, (schema_name, table_name))
            
            action_codes = {
                'a': 'NO ACTION',
                'r': 'RESTRICT',
                'c': 'CASCADE',
                'n': 'SET NULL',
                'd': 'SET DEFAULT'
            }
            
            for row in cursor.fetchall():
                constraints['foreign_key'].append({
                    'name': row['constraint_name'],
                    'columns': row['columns'],
                    'references': f"{row['foreign_schema']}.{row['foreign_table']}",
                    'foreign_columns': row['foreign_columns'],
                    'on_update': action_codes.get(row['on_update'], 'UNKNOWN'),
                    'on_delete': action_codes.get(row['on_delete'], 'UNKNOWN')
                })
            
            # Primary key
            pk_query = """
                SELECT 
                    con.conname as constraint_name,
                    array_agg(att.attname ORDER BY u.attposition) as columns
                FROM pg_constraint con
                JOIN pg_class rel ON con.conrelid = rel.oid
                JOIN pg_namespace nsp ON rel.relnamespace = nsp.oid
                JOIN LATERAL unnest(con.conkey) WITH ORDINALITY AS u(attnum, attposition) ON TRUE
                JOIN pg_attribute att ON att.attrelid = rel.oid AND att.attnum = u.attnum
                WHERE nsp.nspname = %s 
                AND rel.relname = %s 
                AND con.contype = 'p'
                GROUP BY con.conname
            """
            
            cursor.execute(pk_query, (schema_name, table_name))
            for row in cursor.fetchall():
                constraints['primary_key'].append({
                    'name': row['constraint_name'],
                    'columns': row['columns']
                })
            
            return constraints
            
        finally:
            cursor.close()
    
    def get_table_triggers(self, schema_name: str, table_name: str) -> List[Dict[str, Any]]:
        """Get all triggers for a table."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            query = """
                SELECT 
                    tgname as trigger_name,
                    pg_get_triggerdef(t.oid) as trigger_definition,
                    CASE tgtype & 1 WHEN 1 THEN 'ROW' ELSE 'STATEMENT' END as level,
                    CASE 
                        WHEN tgtype & 2 = 2 THEN 'BEFORE'
                        WHEN tgtype & 64 = 64 THEN 'INSTEAD OF'
                        ELSE 'AFTER'
                    END as timing,
                    array_to_string(ARRAY[
                        CASE WHEN tgtype & 4 = 4 THEN 'INSERT' END,
                        CASE WHEN tgtype & 8 = 8 THEN 'DELETE' END,
                        CASE WHEN tgtype & 16 = 16 THEN 'UPDATE' END,
                        CASE WHEN tgtype & 32 = 32 THEN 'TRUNCATE' END
                    ]::text[], ' OR ') as events,
                    p.proname as function_name
                FROM pg_trigger t
                JOIN pg_class c ON t.tgrelid = c.oid
                JOIN pg_namespace n ON c.relnamespace = n.oid
                JOIN pg_proc p ON t.tgfoid = p.oid
                WHERE n.nspname = %s 
                AND c.relname = %s
                AND NOT t.tgisinternal
                ORDER BY tgname
            """
            
            cursor.execute(query, (schema_name, table_name))
            triggers = []
            
            for row in cursor.fetchall():
                triggers.append({
                    'name': row['trigger_name'],
                    'timing': row['timing'],
                    'events': row['events'],
                    'level': row['level'],
                    'function': row['function_name'],
                    'definition': row['trigger_definition']
                })
            
            return triggers
            
        finally:
            cursor.close()
    
    def get_sequences(self, schema_name: str) -> List[Dict[str, Any]]:
        """Get all sequences in a schema."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            query = """
                SELECT 
                    c.relname as sequence_name,
                    s.seqstart as start_value,
                    s.seqincrement as increment,
                    s.seqmax as max_value,
                    s.seqmin as min_value,
                    s.seqcache as cache_size,
                    s.seqcycle as cycles,
                    d.objid,
                    d.refobjid,
                    ct.relname as owned_by_table,
                    a.attname as owned_by_column
                FROM pg_class c
                JOIN pg_namespace n ON c.relnamespace = n.oid
                JOIN pg_sequence s ON s.seqrelid = c.oid
                LEFT JOIN pg_depend d ON d.objid = c.oid AND d.deptype = 'a'
                LEFT JOIN pg_class ct ON d.refobjid = ct.oid
                LEFT JOIN pg_attribute a ON a.attrelid = ct.oid AND a.attnum = d.refobjsubid
                WHERE n.nspname = %s
                AND c.relkind = 'S'
                ORDER BY c.relname
            """
            
            cursor.execute(query, (schema_name,))
            sequences = []
            
            for row in cursor.fetchall():
                seq = {
                    'name': row['sequence_name'],
                    'start': row['start_value'],
                    'increment': row['increment'],
                    'max': row['max_value'],
                    'min': row['min_value'],
                    'cache': row['cache_size'],
                    'cycle': row['cycles']
                }
                
                if row['owned_by_table']:
                    seq['owned_by'] = f"{row['owned_by_table']}.{row['owned_by_column']}"
                
                sequences.append(seq)
            
            return sequences
            
        finally:
            cursor.close()
    
    def get_extensions(self) -> Dict[str, Any]:
        """Get installed PostgreSQL extensions."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            query = """
                SELECT 
                    e.extname as name,
                    e.extversion as version,
                    n.nspname as schema,
                    d.description
                FROM pg_extension e
                JOIN pg_namespace n ON e.extnamespace = n.oid
                LEFT JOIN pg_description d ON d.objoid = e.oid
                ORDER BY e.extname
            """
            
            cursor.execute(query)
            extensions = {}
            
            for row in cursor.fetchall():
                extensions[row['name']] = {
                    'version': row['version'],
                    'schema': row['schema'],
                    'description': row['description']
                }
            
            logger.info(f"Found {len(extensions)} installed extensions")
            return extensions
            
        finally:
            cursor.close()
    
    def get_table_comments(self, schema_name: str, table_name: str) -> Dict[str, Optional[str]]:
        """Get comments on table and its columns."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            comments = {'table': None, 'columns': {}}
            
            # Table comment
            table_query = """
                SELECT obj_description(c.oid) as comment
                FROM pg_class c
                JOIN pg_namespace n ON c.relnamespace = n.oid
                WHERE n.nspname = %s AND c.relname = %s
            """
            
            cursor.execute(table_query, (schema_name, table_name))
            row = cursor.fetchone()
            if row and row['comment']:
                comments['table'] = row['comment']
            
            # Column comments
            column_query = """
                SELECT 
                    a.attname as column_name,
                    col_description(c.oid, a.attnum) as comment
                FROM pg_class c
                JOIN pg_namespace n ON c.relnamespace = n.oid
                JOIN pg_attribute a ON a.attrelid = c.oid
                WHERE n.nspname = %s 
                AND c.relname = %s
                AND a.attnum > 0
                AND NOT a.attisdropped
                AND col_description(c.oid, a.attnum) IS NOT NULL
            """
            
            cursor.execute(column_query, (schema_name, table_name))
            for row in cursor.fetchall():
                comments['columns'][row['column_name']] = row['comment']
            
            return comments
            
        finally:
            cursor.close()
    
    def document_schema(self, schema_name: str) -> Dict[str, Any]:
        """Generate comprehensive documentation for a single schema."""
        logger.info(f"Documenting schema: {schema_name}")
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        schema_doc = {
            'name': schema_name,
            'description': SCHEMA_DESCRIPTIONS.get(schema_name, ''),
            'tables': {},
            'views': {},
            'functions': [],
            'sequences': [],
            'permissions': {},
            'statistics': {
                'table_count': 0,
                'view_count': 0,
                'function_count': 0,
                'total_rows': 0,
                'total_size': '0 bytes'
            }
        }
        
        try:
            # Get schema permissions
            schema_doc['permissions'] = self.get_schema_permissions(schema_name)
            
            # Get sequences
            schema_doc['sequences'] = self.get_sequences(schema_name)
            
            # Get tables
            tables_query = """
                SELECT 
                    table_name,
                    pg_size_pretty(pg_total_relation_size(quote_ident(table_schema)||'.'||quote_ident(table_name))) as size
                FROM information_schema.tables
                WHERE table_schema = %s
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            
            cursor.execute(tables_query, (schema_name,))
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table['table_name']
                logger.info(f"  Documenting table: {schema_name}.{table_name}")
                
                table_doc = {
                    'columns': [],
                    'row_count': 0,
                    'size': table['size'],
                    'indexes': [],
                    'constraints': {},
                    'triggers': [],
                    'permissions': {},
                    'row_level_security': {},
                    'comments': {}
                }
                
                # Get columns
                columns_query = """
                    SELECT 
                        column_name,
                        data_type,
                        character_maximum_length,
                        numeric_precision,
                        numeric_scale,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                """
                
                cursor.execute(columns_query, (schema_name, table_name))
                for col in cursor.fetchall():
                    column_info = {
                        'name': col['column_name'],
                        'type': col['data_type'],
                        'nullable': col['is_nullable'] == 'YES',
                        'default': col['column_default']
                    }
                    
                    if col['character_maximum_length']:
                        column_info['max_length'] = col['character_maximum_length']
                    if col['numeric_precision']:
                        column_info['precision'] = col['numeric_precision']
                    if col['numeric_scale']:
                        column_info['scale'] = col['numeric_scale']
                    
                    table_doc['columns'].append(column_info)
                
                # Get row count (safely)
                try:
                    count_query = f"SELECT COUNT(*) as count FROM {schema_name}.{table_name}"
                    cursor.execute(count_query)
                    table_doc['row_count'] = cursor.fetchone()['count']
                except Exception as e:
                    logger.warning(f"Could not get row count for {schema_name}.{table_name}: {e}")
                    table_doc['row_count'] = None
                
                # Get additional details
                table_doc['indexes'] = self.get_table_indexes(schema_name, table_name)
                table_doc['constraints'] = self.get_table_constraints(schema_name, table_name)
                table_doc['triggers'] = self.get_table_triggers(schema_name, table_name)
                table_doc['permissions'] = self.get_table_permissions(schema_name, table_name)
                table_doc['row_level_security'] = self.get_row_level_security(schema_name, table_name)
                table_doc['comments'] = self.get_table_comments(schema_name, table_name)
                
                schema_doc['tables'][table_name] = table_doc
                schema_doc['statistics']['table_count'] += 1
                if table_doc['row_count']:
                    schema_doc['statistics']['total_rows'] += table_doc['row_count']
            
            # Get views
            views_query = """
                SELECT 
                    table_name as view_name,
                    view_definition
                FROM information_schema.views
                WHERE table_schema = %s
                ORDER BY table_name
            """
            
            cursor.execute(views_query, (schema_name,))
            for view in cursor.fetchall():
                schema_doc['views'][view['view_name']] = {
                    'definition': view['view_definition']
                }
                schema_doc['statistics']['view_count'] += 1
            
            # Get functions
            functions_query = """
                SELECT 
                    p.proname as function_name,
                    pg_get_function_arguments(p.oid) as arguments,
                    pg_get_function_result(p.oid) as return_type,
                    l.lanname as language,
                    d.description
                FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                JOIN pg_language l ON p.prolang = l.oid
                LEFT JOIN pg_description d ON d.objoid = p.oid
                WHERE n.nspname = %s
                AND p.prokind = 'f'
                ORDER BY p.proname
            """
            
            cursor.execute(functions_query, (schema_name,))
            for func in cursor.fetchall():
                schema_doc['functions'].append({
                    'name': func['function_name'],
                    'arguments': func['arguments'],
                    'return_type': func['return_type'],
                    'language': func['language'],
                    'description': func['description']
                })
                schema_doc['statistics']['function_count'] += 1
            
            # Get total schema size
            size_query = """
                SELECT pg_size_pretty(SUM(pg_total_relation_size(quote_ident(schemaname)||'.'||quote_ident(tablename)))::bigint) as size
                FROM pg_tables
                WHERE schemaname = %s
            """
            
            cursor.execute(size_query, (schema_name,))
            result = cursor.fetchone()
            if result and result['size']:
                schema_doc['statistics']['total_size'] = result['size']
            
            return schema_doc
            
        finally:
            cursor.close()
    
    def generate_documentation(self):
        """Generate complete database documentation."""
        logger.info("Starting comprehensive documentation generation")
        
        # Metadata
        self.documentation['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'database': self.connection_params['database'],
            'host': self.connection_params['host'],
            'port': self.connection_params['port'],
            'generator_version': '5.0.1'
        }
        
        # Get PostgreSQL version
        cursor = self.conn.cursor()
        cursor.execute("SELECT version()")
        self.documentation['metadata']['postgresql_version'] = cursor.fetchone()[0]
        cursor.close()
        
        # Get extensions
        self.documentation['extensions'] = self.get_extensions()
        
        # Security documentation
        if self.include_security:
            logger.info("Documenting security (users, roles, permissions)")
            self.documentation['security']['users'] = self.get_database_users()
            self.documentation['security']['roles'] = self.get_database_roles()
        
        # Discover and document schemas
        schemas = self.discover_schemas()
        
        # Database overview
        overview = {
            'schemas': {},
            'totals': {
                'tables': 0,
                'views': 0,
                'functions': 0,
                'rows': 0,
                'columns': 0,
                'relationships': 0
            }
        }
        
        for schema_name in schemas:
            schema_doc = self.document_schema(schema_name)
            self.documentation['schemas'][schema_name] = schema_doc
            
            # Update overview
            overview['schemas'][schema_name] = {
                'tables': schema_doc['statistics']['table_count'],
                'views': schema_doc['statistics']['view_count'],
                'functions': schema_doc['statistics']['function_count'],
                'rows': schema_doc['statistics']['total_rows'],
                'size': schema_doc['statistics']['total_size']
            }
            
            overview['totals']['tables'] += schema_doc['statistics']['table_count']
            overview['totals']['views'] += schema_doc['statistics']['view_count']
            overview['totals']['functions'] += schema_doc['statistics']['function_count']
            overview['totals']['rows'] += schema_doc['statistics']['total_rows']
            
            # Count columns and relationships
            for table_doc in schema_doc['tables'].values():
                overview['totals']['columns'] += len(table_doc['columns'])
                overview['totals']['relationships'] += len(table_doc['constraints'].get('foreign_key', []))
        
        self.documentation['database_overview'] = overview
        
        logger.info("Documentation generation complete")
    
    def save_documentation(self, format: str = 'markdown', output_filename: Optional[str] = None):
        """Save documentation in specified format."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Use .md extension for markdown files
        file_ext = 'md' if format == 'markdown' else format
        
        if output_filename:
            filename = f"{output_filename}.{file_ext}"
        else:
            filename = f"current_ubec_comprehensive_database_documentation_{timestamp}.{file_ext}"
        
        if format == 'markdown':
            self._save_as_markdown(filename)
        elif format == 'json':
            self._save_as_json(filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _save_as_markdown(self, filename: str):
        """Save as markdown file with comprehensive formatting."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Header
                f.write("# UBEC Protocol Suite - Comprehensive Database Documentation\n\n")
                f.write("*This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations.*\n\n")
                
                metadata = self.documentation['metadata']
                f.write(f"**Generated:** {metadata['generated_at']}\n\n")
                f.write(f"**Database:** {metadata['database']}\n\n")
                f.write(f"**PostgreSQL Version:** {metadata['postgresql_version']}\n\n")
                f.write("---\n\n")
                
                # Table of Contents
                f.write("## Table of Contents\n\n")
                f.write("1. [Database Overview](#database-overview)\n")
                f.write("2. [Extensions](#extensions)\n")
                if self.include_security:
                    f.write("3. [Security](#security)\n")
                    f.write("   - [Database Users](#database-users)\n")
                    f.write("   - [Database Roles](#database-roles)\n")
                f.write("4. [Schemas](#schemas)\n")
                for schema_name in self.documentation['schemas'].keys():
                    f.write(f"   - [{schema_name}](#{schema_name.replace('_', '-')})\n")
                f.write("\n---\n\n")
                
                # Database Overview
                f.write("## Database Overview\n\n")
                overview = self.documentation['database_overview']
                
                f.write("### Summary Statistics\n\n")
                f.write(f"- **Total Schemas:** {len(overview['schemas'])}\n")
                f.write(f"- **Total Tables:** {overview['totals']['tables']}\n")
                f.write(f"- **Total Views:** {overview['totals']['views']}\n")
                f.write(f"- **Total Functions:** {overview['totals']['functions']}\n")
                f.write(f"- **Total Rows:** {overview['totals']['rows']:,}\n")
                f.write(f"- **Total Columns:** {overview['totals']['columns']:,}\n")
                f.write(f"- **Total Foreign Keys:** {overview['totals']['relationships']}\n\n")
                
                f.write("### Schema Summary\n\n")
                f.write("| Schema | Tables | Views | Functions | Rows | Size |\n")
                f.write("|--------|--------|-------|-----------|------|------|\n")
                for schema_name, schema_info in sorted(overview['schemas'].items()):
                    f.write(f"| {schema_name} | {schema_info['tables']} | {schema_info['views']} | "
                           f"{schema_info['functions']} | {schema_info['rows']:,} | {schema_info['size']} |\n")
                f.write("\n---\n\n")
                
                # Extensions
                f.write("## Extensions\n\n")
                extensions = self.documentation['extensions']
                if extensions:
                    f.write("| Extension | Version | Schema | Description |\n")
                    f.write("|-----------|---------|--------|-------------|\n")
                    for name, ext in sorted(extensions.items()):
                        desc = ext['description'] or 'N/A'
                        f.write(f"| {name} | {ext['version']} | {ext['schema']} | {desc} |\n")
                else:
                    f.write("No extensions installed.\n")
                f.write("\n---\n\n")
                
                # Security section
                if self.include_security:
                    f.write("## Security\n\n")
                    
                    # Users
                    f.write("### Database Users\n\n")
                    users = self.documentation['security']['users']
                    if users:
                        for username, user_info in sorted(users.items()):
                            f.write(f"#### {username}\n\n")
                            f.write(f"- **User ID:** {user_info['user_id']}\n")
                            f.write(f"- **Superuser:** {'Yes' if user_info['is_superuser'] else 'No'}\n")
                            f.write(f"- **Can Create DB:** {'Yes' if user_info['can_create_db'] else 'No'}\n")
                            f.write(f"- **Can Replicate:** {'Yes' if user_info['can_replicate'] else 'No'}\n")
                            f.write(f"- **Bypass RLS:** {'Yes' if user_info['bypass_rls'] else 'No'}\n")
                            if user_info['valid_until']:
                                f.write(f"- **Valid Until:** {user_info['valid_until']}\n")
                            if user_info['member_of']:
                                f.write(f"- **Member Of:** {', '.join(user_info['member_of'])}\n")
                            f.write("\n")
                    else:
                        f.write("No users found.\n\n")
                    
                    # Roles
                    f.write("### Database Roles\n\n")
                    roles = self.documentation['security']['roles']
                    if roles:
                        for role_name, role_info in sorted(roles.items()):
                            f.write(f"#### {role_name}\n\n")
                            f.write(f"- **Can Login:** {'Yes' if role_info['can_login'] else 'No'}\n")
                            f.write(f"- **Superuser:** {'Yes' if role_info['is_superuser'] else 'No'}\n")
                            f.write(f"- **Inherit Privileges:** {'Yes' if role_info['inherit_privileges'] else 'No'}\n")
                            f.write(f"- **Can Create Role:** {'Yes' if role_info['can_create_role'] else 'No'}\n")
                            f.write(f"- **Can Create DB:** {'Yes' if role_info['can_create_db'] else 'No'}\n")
                            if role_info['granted_to']:
                                f.write(f"- **Granted To:** {', '.join(role_info['granted_to'])}\n")
                            f.write("\n")
                    else:
                        f.write("No roles found.\n\n")
                    
                    f.write("---\n\n")
                
                # Schemas
                f.write("## Schemas\n\n")
                
                for schema_name, schema_doc in self.documentation['schemas'].items():
                    logger.info(f"Writing schema documentation for: {schema_name}")
                    
                    try:
                        f.write(f"## {schema_name}\n\n")
                        
                        if schema_doc.get('description'):
                            f.write(f"*{schema_doc['description']}*\n\n")
                        
                        # Schema statistics
                        stats = schema_doc['statistics']
                        f.write(f"**Tables:** {stats['table_count']} | ")
                        f.write(f"**Views:** {stats['view_count']} | ")
                        f.write(f"**Functions:** {stats['function_count']} | ")
                        f.write(f"**Total Rows:** {stats['total_rows']:,} | ")
                        f.write(f"**Size:** {stats['total_size']}\n\n")
                        
                        # Schema permissions
                        if schema_doc.get('permissions'):
                            f.write("### Schema Permissions\n\n")
                            for grantee, privs in sorted(schema_doc['permissions'].items()):
                                f.write(f"- **{grantee}:** {', '.join(privs)}\n")
                            f.write("\n")
                        
                        # Sequences
                        if schema_doc.get('sequences'):
                            f.write("### Sequences\n\n")
                            for seq in schema_doc['sequences']:
                                f.write(f"#### {seq['name']}\n\n")
                                f.write(f"- **Start:** {seq['start']}\n")
                                f.write(f"- **Increment:** {seq['increment']}\n")
                                f.write(f"- **Min:** {seq['min']}, **Max:** {seq['max']}\n")
                                f.write(f"- **Cache:** {seq['cache']}\n")
                                if seq.get('owned_by'):
                                    f.write(f"- **Owned By:** {seq['owned_by']}\n")
                                f.write("\n")
                        
                        # Tables
                        if schema_doc['tables']:
                            try:
                                logger.info(f"  Writing {len(schema_doc['tables'])} tables for {schema_name}")
                                f.write("### Tables\n\n")
                                
                                for table_name in sorted(schema_doc['tables'].keys()):
                                    try:
                                        table_doc = schema_doc['tables'][table_name]
                                        f.write(f"#### {table_name}\n\n")
                                        
                                        # Table comment
                                        if table_doc['comments'].get('table'):
                                            f.write(f"*{table_doc['comments']['table']}*\n\n")
                                        
                                        # Table stats
                                        row_count = table_doc['row_count']
                                        row_str = f"{row_count:,}" if row_count is not None else "N/A"
                                        f.write(f"**Rows:** {row_str} | **Size:** {table_doc['size']}\n\n")
                                        
                                        # Columns
                                        f.write("**Columns:**\n\n")
                                        f.write("| Column | Type | Nullable | Default |\n")
                                        f.write("|--------|------|----------|----------|\n")
                                        for col in table_doc['columns']:
                                            col_type = col['type']
                                            if col.get('max_length'):
                                                col_type += f"({col['max_length']})"
                                            elif col.get('precision'):
                                                if col.get('scale'):
                                                    col_type += f"({col['precision']},{col['scale']})"
                                                else:
                                                    col_type += f"({col['precision']})"
                                            
                                            nullable = "✓" if col['nullable'] else "✗"
                                            default = col['default'] or ""
                                            
                                            # Check for column comment
                                            comment = table_doc['comments']['columns'].get(col['name'])
                                            col_name = col['name']
                                            if comment:
                                                col_name += f" *({comment})*"
                                            
                                            f.write(f"| {col_name} | {col_type} | {nullable} | {default} |\n")
                                        f.write("\n")
                                        
                                        # Constraints
                                        constraints = table_doc['constraints']
                                        
                                        if constraints.get('primary_key'):
                                            f.write("**Primary Key:**\n")
                                            for pk in constraints['primary_key']:
                                                f.write(f"- {pk['name']}: ({', '.join(pk['columns'])})\n")
                                            f.write("\n")
                                        
                                        if constraints.get('foreign_key'):
                                            f.write("**Foreign Keys:**\n")
                                            for fk in constraints['foreign_key']:
                                                f.write(f"- {fk['name']}: ({', '.join(fk['columns'])}) → "
                                                       f"{fk['references']}({', '.join(fk['foreign_columns'])})\n")
                                                f.write(f"  - ON UPDATE: {fk['on_update']}, ON DELETE: {fk['on_delete']}\n")
                                            f.write("\n")
                                        
                                        if constraints.get('unique'):
                                            f.write("**Unique Constraints:**\n")
                                            for uc in constraints['unique']:
                                                f.write(f"- {uc['name']}: ({', '.join(uc['columns'])})\n")
                                            f.write("\n")
                                        
                                        if constraints.get('check'):
                                            f.write("**Check Constraints:**\n")
                                            for cc in constraints['check']:
                                                f.write(f"- {cc['name']}: {cc['definition']}\n")
                                            f.write("\n")
                                        
                                        # Indexes
                                        if table_doc['indexes']:
                                            f.write("**Indexes:**\n")
                                            for idx in table_doc['indexes']:
                                                idx_type = []
                                                if idx['primary']:
                                                    idx_type.append('PRIMARY')
                                                if idx['unique']:
                                                    idx_type.append('UNIQUE')
                                                idx_type.append(idx['type'].upper())
                                                
                                                type_str = ' '.join(idx_type)
                                                f.write(f"- {type_str}: ({', '.join(idx['columns'])}) - {idx['size']}\n")
                                            f.write("\n")
                                        
                                        # Triggers
                                        if table_doc['triggers']:
                                            f.write("**Triggers:**\n")
                                            for trg in table_doc['triggers']:
                                                f.write(f"- **{trg['name']}:** {trg['timing']} {trg['events']} {trg['level']}\n")
                                                f.write(f"  - Calls: {trg['function']}\n")
                                            f.write("\n")
                                        
                                        # Row Level Security
                                        rls = table_doc['row_level_security']
                                        if rls['enabled']:
                                            f.write("**Row Level Security:** Enabled\n\n")
                                            for policy in rls['policies']:
                                                f.write(f"- **Policy:** {policy['name']}\n")
                                                f.write(f"  - **Command:** {policy['command']}\n")
                                                f.write(f"  - **Roles:** {', '.join(policy['roles']) if policy['roles'] else 'ALL'}\n")
                                                if policy['using']:
                                                    f.write(f"  - **USING:** `{policy['using']}`\n")
                                                if policy['check']:
                                                    f.write(f"  - **CHECK:** `{policy['check']}`\n")
                                            f.write("\n")
                                        
                                        # Table permissions
                                        if table_doc['permissions']:
                                            f.write("**Permissions:**\n")
                                            for grantee, privs in sorted(table_doc['permissions'].items()):
                                                f.write(f"- **{grantee}:** {', '.join(privs)}\n")
                                            f.write("\n")
                                        
                                        f.write("---\n\n")
                                        
                                    except Exception as e:
                                        logger.error(f"Error writing table {table_name}: {e}")
                                        f.write(f"\n*Error documenting table {table_name}: {e}*\n\n")
                                        
                            except Exception as e:
                                logger.error(f"Error writing tables section for {schema_name}: {e}")
                                f.write(f"\n*Error documenting tables: {e}*\n\n")
                        
                        # Views
                        if schema_doc['views']:
                            try:
                                logger.info(f"  Writing {len(schema_doc['views'])} views for {schema_name}")
                                f.write("### Views\n\n")
                                for view_name in sorted(schema_doc['views'].keys()):
                                    try:
                                        f.write(f"#### {view_name}\n\n")
                                        f.write("```sql\n")
                                        view_def = schema_doc['views'][view_name]['definition']
                                        if view_def:
                                            safe_def = view_def.encode('utf-8', errors='replace').decode('utf-8')
                                            f.write(safe_def[:1000])
                                            if len(safe_def) > 1000:
                                                f.write("\n...\n")
                                        f.write("\n```\n\n")
                                    except Exception as e:
                                        logger.error(f"Error writing view {view_name}: {e}")
                                        f.write(f"\n*Error documenting view {view_name}: {e}*\n\n")
                            except Exception as e:
                                logger.error(f"Error writing views section for {schema_name}: {e}")
                                f.write(f"\n*Error documenting views: {e}*\n\n")
                        
                        # Functions
                        if schema_doc['functions']:
                            try:
                                logger.info(f"  Writing {len(schema_doc['functions'])} functions for {schema_name}")
                                f.write("### Functions\n\n")
                                for func in schema_doc['functions']:
                                    try:
                                        f.write(f"#### {func['name']}({func['arguments']})\n\n")
                                        f.write(f"- **Returns:** {func['return_type']}\n")
                                        f.write(f"- **Language:** {func['language']}\n")
                                        if func.get('description'):
                                            f.write(f"- **Description:** {func['description']}\n")
                                        f.write("\n")
                                    except Exception as e:
                                        logger.error(f"Error writing function {func.get('name', 'unknown')}: {e}")
                                        f.write(f"\n*Error documenting function: {e}*\n\n")
                            except Exception as e:
                                logger.error(f"Error writing functions section for {schema_name}: {e}")
                                f.write(f"\n*Error documenting functions: {e}*\n\n")
                        
                        f.write("---\n\n")
                        logger.info(f"Completed documentation for schema: {schema_name}")
                        
                    except Exception as e:
                        logger.error(f"Error documenting schema {schema_name}: {e}")
                        f.write(f"\n## ERROR: Could not complete documentation for schema `{schema_name}`\n\n")
                        f.write(f"Error: {e}\n\n")
                        f.write("---\n\n")
            
            print(f"\n✅ Comprehensive documentation saved to: {filename}\n")
            logger.info(f"Successfully saved to {filename}")
            
        except Exception as e:
            logger.error(f"Fatal error saving markdown: {e}")
            print(f"\n❌ Error saving documentation: {e}\n")
            raise

    def _save_as_json(self, filename: str):
        """Save as JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.documentation, f, indent=2, default=str)
        
        print(f"\n✅ Comprehensive documentation saved to: {filename}\n")
        logger.info(f"Saved to {filename}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive multi-schema UBEC database documentation with security analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Document ALL schemas with security
  python ubec_schema_documenter_enhanced.py
  
  # Document specific schemas
  python ubec_schema_documenter_enhanced.py --schemas ubec_main phenomenal
  
  # Include system schemas
  python ubec_schema_documenter_enhanced.py --include-system
  
  # Skip security documentation
  python ubec_schema_documenter_enhanced.py --no-security
  
  # Generate JSON format
  python ubec_schema_documenter_enhanced.py --format json
  
  # Custom output file
  python ubec_schema_documenter_enhanced.py --output complete_ubec_docs
        """
    )
    
    # Get default config
    try:
        env_config = get_database_config()
    except Exception as e:
        print(f"\n❌ Configuration Error: {e}\n")
        return 1
    
    # Arguments
    parser.add_argument('--host', default=env_config['host'],
                       help='Database host')
    parser.add_argument('--port', type=int, default=env_config['port'],
                       help='Database port')
    parser.add_argument('--database', default=env_config['database'],
                       help='Database name')
    parser.add_argument('--user', default=env_config['user'],
                       help='Database user')
    parser.add_argument('--password', default=env_config.get('password'),
                       help='Database password')
    parser.add_argument('--schemas', nargs='+',
                       help='Specific schemas to document (default: auto-discover all)')
    parser.add_argument('--include-system', action='store_true',
                       help='Include system schemas (pg_*, information_schema)')
    parser.add_argument('--no-security', action='store_true',
                       help='Skip security documentation (users, roles, permissions)')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown',
                       help='Output format')
    parser.add_argument('--output', help='Output filename (without extension)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    conn_params = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user
    }
    
    if args.password:
        conn_params['password'] = args.password
    
    print(f"\n🜁 🜄 🜃 🜂 UBEC Comprehensive Multi-Schema Documentation Generator v5.0.1")
    print(f"=" * 70)
    print(f"Database: {conn_params['database']}@{conn_params['host']}:{conn_params['port']}")
    print(f"User: {conn_params['user']}")
    if args.schemas:
        print(f"Schemas: {', '.join(args.schemas)}")
    else:
        print(f"Schemas: Auto-discover all")
    print(f"Security: {'Disabled' if args.no_security else 'Enabled'}")
    print(f"=" * 70 + "\n")
    
    documenter = UBECComprehensiveDocumenter(
        conn_params, 
        schemas=args.schemas,
        exclude_system_schemas=not args.include_system,
        include_security=not args.no_security
    )
    
    try:
        documenter.connect()
        documenter.generate_documentation()
        documenter.save_documentation(args.format, args.output)
        
        # Print summary
        overview = documenter.documentation['database_overview']
        print(f"\n📊 Documentation Summary:")
        print(f"   Schemas: {len(overview['schemas'])}")
        print(f"   Tables: {overview['totals']['tables']}")
        print(f"   Rows: {overview['totals']['rows']:,}")
        print(f"   Columns: {overview['totals']['columns']:,}")
        print(f"   Views: {overview['totals']['views']}")
        print(f"   Functions: {overview['totals']['functions']}")
        print(f"   Relationships: {overview['totals']['relationships']}\n")
        
        # Schema breakdown
        print(f"📋 Schemas Documented:")
        for schema_name, schema_info in overview['schemas'].items():
            print(f"   • {schema_name}: {schema_info['tables']} tables, {schema_info['rows']:,} rows")
        
        if documenter.include_security:
            security = documenter.documentation['security']
            print(f"\n🔒 Security Summary:")
            print(f"   Users: {len(security['users'])}")
            print(f"   Roles: {len(security['roles'])}")
        
        print(f"\n✅ Comprehensive documentation complete!\n")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
        
    finally:
        documenter.disconnect()


if __name__ == "__main__":
    sys.exit(main())
