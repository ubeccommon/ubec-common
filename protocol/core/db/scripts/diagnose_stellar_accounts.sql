-- ============================================================================
-- Diagnostic: stellar_accounts Table Population Analysis
-- ============================================================================
-- Purpose: Identify why created_at, primary_element, last_activity_at are NULL
-- ============================================================================

\echo ''
\echo '╔═══════════════════════════════════════════════════════════════════════════╗'
\echo '║         STELLAR_ACCOUNTS TABLE DIAGNOSTIC REPORT                          ║'
\echo '╚═══════════════════════════════════════════════════════════════════════════╝'
\echo ''

-- Section 1: Table Schema
\echo '┌───────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 1: TABLE SCHEMA                                                   │'
\echo '└───────────────────────────────────────────────────────────────────────────┘'

SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'ubec_main' 
  AND table_name = 'stellar_accounts'
ORDER BY ordinal_position;

\echo ''

-- Section 2: NULL Value Analysis
\echo '┌───────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 2: NULL VALUE ANALYSIS                                            │'
\echo '└───────────────────────────────────────────────────────────────────────────┘'

SELECT 
    COUNT(*) as total_accounts,
    COUNT(created_at) as has_created_at,
    COUNT(*) - COUNT(created_at) as missing_created_at,
    COUNT(primary_element) as has_primary_element,
    COUNT(*) - COUNT(primary_element) as missing_primary_element,
    COUNT(last_activity_at) as has_last_activity,
    COUNT(*) - COUNT(last_activity_at) as missing_last_activity
FROM ubec_main.stellar_accounts;

\echo ''

-- Section 3: Sample of Populated vs Unpopulated Accounts
\echo '┌───────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 3: SAMPLE ACCOUNTS (First 10)                                     │'
\echo '└───────────────────────────────────────────────────────────────────────────┘'

SELECT 
    LEFT(account_id, 12) || '...' as account_id,
    created_at,
    primary_element,
    last_activity_at
FROM ubec_main.stellar_accounts
ORDER BY account_id
LIMIT 10;

\echo ''

-- Section 4: Check if data exists in related tables
\echo '┌───────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 4: DATA SOURCES FOR MISSING FIELDS                                │'
\echo '└───────────────────────────────────────────────────────────────────────────┘'

\echo 'Checking ubec_balances for activity timestamps...'
SELECT 
    'ubec_balances' as source_table,
    COUNT(DISTINCT account_id) as accounts,
    MIN(last_modified_at) as earliest_activity,
    MAX(last_modified_at) as latest_activity
FROM ubec_main.ubec_balances;

\echo ''
\echo 'Checking stellar_transactions for created_at data...'
SELECT 
    'stellar_transactions' as source_table,
    COUNT(DISTINCT source_account) as unique_sources,
    MIN(created_at) as earliest_tx,
    MAX(created_at) as latest_tx
FROM ubec_main.stellar_transactions;

\echo ''
\echo 'Checking ubec_holonic_metrics for primary_element data...'
SELECT 
    element,
    COUNT(DISTINCT account_id) as accounts
FROM ubec_main.ubec_holonic_metrics
WHERE calculated_at >= NOW() - INTERVAL '7 days'
GROUP BY element
ORDER BY element;

\echo ''

-- Section 5: Determine Primary Element from Holonic Metrics
\echo '┌───────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 5: DERIVABLE PRIMARY ELEMENT (Highest Scoring Element)            │'
\echo '└───────────────────────────────────────────────────────────────────────────┘'

WITH element_scores AS (
    SELECT 
        account_id,
        element,
        score,
        ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY score DESC) as rank
    FROM ubec_main.ubec_holonic_metrics
    WHERE calculated_at >= NOW() - INTERVAL '7 days'
)
SELECT 
    element as derived_primary_element,
    COUNT(*) as account_count
FROM element_scores
WHERE rank = 1
GROUP BY element
ORDER BY account_count DESC;

\echo ''

-- Section 6: Determine Created At from First Transaction
\echo '┌───────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 6: DERIVABLE CREATED_AT (First Transaction Date)                  │'
\echo '└───────────────────────────────────────────────────────────────────────────┘'

WITH first_tx AS (
    SELECT 
        source_account as account_id,
        MIN(created_at) as first_transaction
    FROM ubec_main.stellar_transactions
    GROUP BY source_account
)
SELECT 
    COUNT(*) as accounts_with_tx_history,
    MIN(first_transaction) as earliest_account,
    MAX(first_transaction) as newest_account
FROM first_tx;

\echo ''

-- Section 7: Recommendations
\echo '┌───────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 7: RECOMMENDATIONS                                                │'
\echo '└───────────────────────────────────────────────────────────────────────────┘'

\echo ''
\echo 'To populate missing fields, run the following UPDATE queries:'
\echo ''
\echo '-- 1. Populate created_at from first transaction:'
\echo 'UPDATE ubec_main.stellar_accounts sa'
\echo 'SET created_at = ft.first_tx'
\echo 'FROM ('
\echo '    SELECT source_account, MIN(created_at) as first_tx'
\echo '    FROM ubec_main.stellar_transactions'
\echo '    GROUP BY source_account'
\echo ') ft'
\echo 'WHERE sa.account_id = ft.source_account'
\echo '  AND sa.created_at IS NULL;'
\echo ''
\echo '-- 2. Populate last_activity_at from balances or transactions:'
\echo 'UPDATE ubec_main.stellar_accounts sa'
\echo 'SET last_activity_at = COALESCE(b.last_modified_at, t.last_tx)'
\echo 'FROM ('
\echo '    SELECT account_id, MAX(last_modified_at) as last_modified_at'
\echo '    FROM ubec_main.ubec_balances'
\echo '    GROUP BY account_id'
\echo ') b'
\echo 'LEFT JOIN ('
\echo '    SELECT source_account, MAX(created_at) as last_tx'
\echo '    FROM ubec_main.stellar_transactions'
\echo '    GROUP BY source_account'
\echo ') t ON b.account_id = t.source_account'
\echo 'WHERE sa.account_id = b.account_id'
\echo '  AND sa.last_activity_at IS NULL;'
\echo ''
\echo '-- 3. Populate primary_element from highest holonic score:'
\echo 'UPDATE ubec_main.stellar_accounts sa'
\echo 'SET primary_element = pe.element::text'
\echo 'FROM ('
\echo '    SELECT DISTINCT ON (account_id) account_id, element'
\echo '    FROM ubec_main.ubec_holonic_metrics'
\echo '    ORDER BY account_id, score DESC'
\echo ') pe'
\echo 'WHERE sa.account_id = pe.account_id'
\echo '  AND sa.primary_element IS NULL;'
\echo ''

\echo '╔═══════════════════════════════════════════════════════════════════════════╗'
\echo '║                      END OF DIAGNOSTIC REPORT                             ║'
\echo '╚═══════════════════════════════════════════════════════════════════════════╝'
