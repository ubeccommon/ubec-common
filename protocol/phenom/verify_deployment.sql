-- ============================================================================
-- Quick Verification Queries for Phenomenal Schema
-- Run these in psql to verify successful deployment
-- ============================================================================

-- Connect to ubec database
-- \c ubec

-- Set search path
SET search_path TO phenomenal, public;

-- ============================================================================
-- 1. CHECK TABLES
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'CHECKING TABLES'
\echo '===================================================================='

SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='phenomenal' AND columns.table_name=tables.table_name) as column_count
FROM information_schema.tables
WHERE table_schema = 'phenomenal' 
    AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- ============================================================================
-- 2. CHECK VIEWS
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'CHECKING VIEWS'
\echo '===================================================================='

SELECT table_name as view_name
FROM information_schema.views
WHERE table_schema = 'phenomenal'
ORDER BY table_name;

-- ============================================================================
-- 3. CHECK FUNCTIONS
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'CHECKING FUNCTIONS'
\echo '===================================================================='

SELECT 
    routine_name as function_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'phenomenal'
ORDER BY routine_name;

-- ============================================================================
-- 4. CHECK TRIGGERS
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'CHECKING TRIGGERS'
\echo '===================================================================='

SELECT 
    trigger_name,
    event_object_table as table_name,
    action_timing,
    event_manipulation
FROM information_schema.triggers
WHERE trigger_schema = 'phenomenal'
ORDER BY event_object_table, trigger_name;

-- ============================================================================
-- 5. CHECK CUSTOM TYPES
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'CHECKING CUSTOM TYPES'
\echo '===================================================================='

SELECT 
    typname as type_name,
    typtype as type_kind
FROM pg_type
WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'phenomenal')
ORDER BY typname;

-- ============================================================================
-- 6. CHECK INDEXES
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'CHECKING INDEXES (First 20)'
\echo '===================================================================='

SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'phenomenal'
ORDER BY tablename, indexname
LIMIT 20;

-- ============================================================================
-- 7. TEST FUNCTION EXECUTION
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'TESTING FUNCTION EXECUTION'
\echo '===================================================================='

-- Test calculate_gravitational_mass (should return 0 for non-existent entity)
SELECT phenomenal.calculate_gravitational_mass('account', 999999) as test_mass_calculation;

-- ============================================================================
-- 8. CHECK MATERIALIZED VIEW
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'CHECKING MATERIALIZED VIEW'
\echo '===================================================================='

SELECT 
    schemaname,
    matviewname,
    matviewowner,
    definition IS NOT NULL as has_definition
FROM pg_matviews
WHERE schemaname = 'phenomenal';

-- ============================================================================
-- 9. TABLE SIZE SUMMARY
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'TABLE SIZES'
\echo '===================================================================='

SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'phenomenal'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- ============================================================================
-- 10. FINAL SUMMARY
-- ============================================================================
\echo ''
\echo '===================================================================='
\echo 'DEPLOYMENT SUMMARY'
\echo '===================================================================='

SELECT 
    'Tables' as component,
    COUNT(*) as count
FROM information_schema.tables
WHERE table_schema = 'phenomenal' AND table_type = 'BASE TABLE'

UNION ALL

SELECT 
    'Views' as component,
    COUNT(*) as count
FROM information_schema.views
WHERE table_schema = 'phenomenal'

UNION ALL

SELECT 
    'Functions' as component,
    COUNT(*) as count
FROM information_schema.routines
WHERE routine_schema = 'phenomenal'

UNION ALL

SELECT 
    'Triggers' as component,
    COUNT(*) as count
FROM information_schema.triggers
WHERE trigger_schema = 'phenomenal'

UNION ALL

SELECT 
    'Indexes' as component,
    COUNT(*) as count
FROM pg_indexes
WHERE schemaname = 'phenomenal';

\echo ''
\echo '===================================================================='
\echo '✅ Verification Complete!'
\echo '===================================================================='
\echo 'If you see tables, views, functions, and triggers listed above,'
\echo 'your phenomenal schema is successfully deployed!'
\echo ''
