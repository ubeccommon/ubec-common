-- ============================================================================
-- UBEC Holonic Score Verification Script
-- ============================================================================
-- Purpose: Verify that holonic scores are being properly calculated and 
--          updated regularly across all accounts
-- 
-- Version: 1.0.0
-- Date: November 29, 2025
-- 
-- Usage: psql -U ubec -d ubec -f verify_holonic_scores.sql
--    OR: psql -U ubec -d ubec < verify_holonic_scores.sql
--
-- Expected Schedule:
--   - Holonic evaluation: Every 30-60 minutes or daily at 2 AM
--   - Ubuntu metrics: Updated alongside holonic evaluation
--
-- Attribution: This project uses the services of Claude and Anthropic PBC 
--              to inform our decisions and recommendations.
-- ============================================================================

-- Set output formatting for better readability
\pset border 2
\pset format aligned
\pset null '(null)'

\echo ''
\echo '╔══════════════════════════════════════════════════════════════════════════════╗'
\echo '║           UBEC HOLONIC SCORE VERIFICATION REPORT                             ║'
\echo '║           Generated: ' :DBNAME ' @ ' `date +%Y-%m-%d\ %H:%M:%S` '                              ║'
\echo '╚══════════════════════════════════════════════════════════════════════════════╝'
\echo ''

-- ============================================================================
-- SECTION 1: TABLE EXISTENCE CHECK
-- ============================================================================
\echo '┌──────────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 1: TABLE EXISTENCE CHECK                                             │'
\echo '└──────────────────────────────────────────────────────────────────────────────┘'

SELECT 
    'holonic_metrics' as table_name,
    CASE WHEN EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'ubec_main' AND table_name = 'holonic_metrics'
    ) THEN '✅ EXISTS' ELSE '❌ MISSING' END as status,
    (SELECT COUNT(*) FROM ubec_main.holonic_metrics) as row_count,
    pg_size_pretty((SELECT pg_relation_size('ubec_main.holonic_metrics'))) as table_size
UNION ALL
SELECT 
    'ubec_holonic_metrics' as table_name,
    CASE WHEN EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'ubec_main' AND table_name = 'ubec_holonic_metrics'
    ) THEN '✅ EXISTS' ELSE '❌ MISSING' END as status,
    (SELECT COUNT(*) FROM ubec_main.ubec_holonic_metrics) as row_count,
    pg_size_pretty((SELECT pg_relation_size('ubec_main.ubec_holonic_metrics'))) as table_size
UNION ALL
SELECT 
    'stellar_accounts' as table_name,
    CASE WHEN EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'ubec_main' AND table_name = 'stellar_accounts'
    ) THEN '✅ EXISTS' ELSE '❌ MISSING' END as status,
    (SELECT COUNT(*) FROM ubec_main.stellar_accounts) as row_count,
    pg_size_pretty((SELECT pg_relation_size('ubec_main.stellar_accounts'))) as table_size;

\echo ''

-- ============================================================================
-- SECTION 2: EVALUATION FRESHNESS CHECK
-- ============================================================================
\echo '┌──────────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 2: EVALUATION FRESHNESS CHECK                                        │'
\echo '└──────────────────────────────────────────────────────────────────────────────┘'

-- Check latest evaluation timestamps
SELECT 
    'holonic_metrics' as source,
    MAX(evaluation_date) as latest_evaluation,
    NOW() - MAX(evaluation_date) as time_since_last,
    CASE 
        WHEN MAX(evaluation_date) >= NOW() - INTERVAL '1 hour' THEN '✅ FRESH (< 1 hour)'
        WHEN MAX(evaluation_date) >= NOW() - INTERVAL '6 hours' THEN '⚠️ RECENT (< 6 hours)'
        WHEN MAX(evaluation_date) >= NOW() - INTERVAL '24 hours' THEN '⚠️ STALE (< 24 hours)'
        WHEN MAX(evaluation_date) >= NOW() - INTERVAL '7 days' THEN '❌ OLD (< 7 days)'
        ELSE '❌ VERY OLD (> 7 days)'
    END as freshness_status
FROM ubec_main.holonic_metrics
UNION ALL
SELECT 
    'ubec_holonic_metrics' as source,
    MAX(calculated_at) as latest_evaluation,
    NOW() - MAX(calculated_at) as time_since_last,
    CASE 
        WHEN MAX(calculated_at) >= NOW() - INTERVAL '1 hour' THEN '✅ FRESH (< 1 hour)'
        WHEN MAX(calculated_at) >= NOW() - INTERVAL '6 hours' THEN '⚠️ RECENT (< 6 hours)'
        WHEN MAX(calculated_at) >= NOW() - INTERVAL '24 hours' THEN '⚠️ STALE (< 24 hours)'
        WHEN MAX(calculated_at) >= NOW() - INTERVAL '7 days' THEN '❌ OLD (< 7 days)'
        ELSE '❌ VERY OLD (> 7 days)'
    END as freshness_status
FROM ubec_main.ubec_holonic_metrics;

\echo ''

-- ============================================================================
-- SECTION 3: ACCOUNT COVERAGE ANALYSIS
-- ============================================================================
\echo '┌──────────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 3: ACCOUNT COVERAGE ANALYSIS                                         │'
\echo '└──────────────────────────────────────────────────────────────────────────────┘'

WITH account_stats AS (
    SELECT 
        (SELECT COUNT(DISTINCT account_id) FROM ubec_main.stellar_accounts) as total_accounts,
        (SELECT COUNT(DISTINCT account_id) FROM ubec_main.holonic_metrics) as accounts_with_holonic,
        (SELECT COUNT(DISTINCT account_id) FROM ubec_main.ubec_holonic_metrics) as accounts_with_ubuntu,
        (SELECT COUNT(DISTINCT account_id) FROM ubec_main.ubec_balances WHERE balance > 0) as accounts_with_balance
)
SELECT 
    total_accounts as "Total Accounts",
    accounts_with_balance as "Accounts with Balance",
    accounts_with_holonic as "Accounts Evaluated (holonic_metrics)",
    accounts_with_ubuntu as "Accounts Evaluated (ubec_holonic_metrics)",
    ROUND(accounts_with_holonic::numeric / NULLIF(accounts_with_balance, 0) * 100, 2) as "Holonic Coverage %",
    ROUND(accounts_with_ubuntu::numeric / NULLIF(accounts_with_balance, 0) * 100, 2) as "Ubuntu Coverage %",
    CASE 
        WHEN accounts_with_holonic >= accounts_with_balance * 0.95 THEN '✅ EXCELLENT (≥95%)'
        WHEN accounts_with_holonic >= accounts_with_balance * 0.80 THEN '⚠️ GOOD (≥80%)'
        WHEN accounts_with_holonic >= accounts_with_balance * 0.50 THEN '⚠️ PARTIAL (≥50%)'
        ELSE '❌ LOW (<50%)'
    END as coverage_status
FROM account_stats;

\echo ''

-- ============================================================================
-- SECTION 4: EVALUATION FREQUENCY ANALYSIS (Last 7 Days)
-- ============================================================================
\echo '┌──────────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 4: EVALUATION FREQUENCY ANALYSIS (Last 7 Days)                       │'
\echo '└──────────────────────────────────────────────────────────────────────────────┘'

-- Daily evaluation counts
SELECT 
    DATE(evaluation_date) as evaluation_day,
    COUNT(DISTINCT account_id) as accounts_evaluated,
    COUNT(*) as total_evaluations,
    MIN(evaluation_date)::time as first_eval_time,
    MAX(evaluation_date)::time as last_eval_time,
    CASE 
        WHEN COUNT(DISTINCT account_id) >= 400 THEN '✅'
        WHEN COUNT(DISTINCT account_id) >= 200 THEN '⚠️'
        ELSE '❌'
    END as status
FROM ubec_main.holonic_metrics
WHERE evaluation_date >= NOW() - INTERVAL '7 days'
GROUP BY DATE(evaluation_date)
ORDER BY evaluation_day DESC;

\echo ''

-- ============================================================================
-- SECTION 5: CATEGORY DISTRIBUTION VERIFICATION
-- ============================================================================
\echo '┌──────────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 5: CATEGORY DISTRIBUTION VERIFICATION                                │'
\echo '└──────────────────────────────────────────────────────────────────────────────┘'

-- Current category distribution (latest evaluation per account)
WITH latest_evaluations AS (
    SELECT DISTINCT ON (account_id)
        account_id,
        holonic_category,
        composite_score,
        evaluation_date
    FROM ubec_main.holonic_metrics
    ORDER BY account_id, evaluation_date DESC
)
SELECT 
    holonic_category as "Category",
    COUNT(*) as "Count",
    ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 2) as "Percentage",
    ROUND(AVG(composite_score)::numeric, 4) as "Avg Score",
    ROUND(MIN(composite_score)::numeric, 4) as "Min Score",
    ROUND(MAX(composite_score)::numeric, 4) as "Max Score",
    CASE holonic_category
        WHEN 'Exemplar' THEN '🌟'
        WHEN 'Integrator' THEN '🔗'
        WHEN 'Contributor' THEN '💪'
        WHEN 'Participant' THEN '👋'
        WHEN 'Observer' THEN '👀'
        ELSE '❓'
    END as icon
FROM latest_evaluations
GROUP BY holonic_category
ORDER BY 
    CASE holonic_category
        WHEN 'Exemplar' THEN 1
        WHEN 'Integrator' THEN 2
        WHEN 'Contributor' THEN 3
        WHEN 'Participant' THEN 4
        WHEN 'Observer' THEN 5
        ELSE 6
    END;

\echo ''

-- ============================================================================
-- SECTION 6: DIMENSION SCORE VALIDITY CHECK
-- ============================================================================
\echo '┌──────────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 6: DIMENSION SCORE VALIDITY CHECK                                    │'
\echo '└──────────────────────────────────────────────────────────────────────────────┘'

-- Check that all dimension scores are within valid range (0.0 - 1.0)
WITH latest_evaluations AS (
    SELECT DISTINCT ON (account_id) *
    FROM ubec_main.holonic_metrics
    ORDER BY account_id, evaluation_date DESC
),
score_checks AS (
    SELECT
        'autonomy_integration_score' as dimension,
        COUNT(*) as total,
        SUM(CASE WHEN autonomy_integration_score >= 0 AND autonomy_integration_score <= 1 THEN 1 ELSE 0 END) as valid,
        SUM(CASE WHEN autonomy_integration_score < 0 OR autonomy_integration_score > 1 THEN 1 ELSE 0 END) as invalid,
        SUM(CASE WHEN autonomy_integration_score IS NULL THEN 1 ELSE 0 END) as null_count,
        ROUND(AVG(autonomy_integration_score)::numeric, 4) as avg_score
    FROM latest_evaluations
    UNION ALL
    SELECT 'multi_scale_score', COUNT(*), 
        SUM(CASE WHEN multi_scale_score >= 0 AND multi_scale_score <= 1 THEN 1 ELSE 0 END),
        SUM(CASE WHEN multi_scale_score < 0 OR multi_scale_score > 1 THEN 1 ELSE 0 END),
        SUM(CASE WHEN multi_scale_score IS NULL THEN 1 ELSE 0 END),
        ROUND(AVG(multi_scale_score)::numeric, 4)
    FROM latest_evaluations
    UNION ALL
    SELECT 'regenerative_impact_score', COUNT(*),
        SUM(CASE WHEN regenerative_impact_score >= 0 AND regenerative_impact_score <= 1 THEN 1 ELSE 0 END),
        SUM(CASE WHEN regenerative_impact_score < 0 OR regenerative_impact_score > 1 THEN 1 ELSE 0 END),
        SUM(CASE WHEN regenerative_impact_score IS NULL THEN 1 ELSE 0 END),
        ROUND(AVG(regenerative_impact_score)::numeric, 4)
    FROM latest_evaluations
    UNION ALL
    SELECT 'network_contribution_score', COUNT(*),
        SUM(CASE WHEN network_contribution_score >= 0 AND network_contribution_score <= 1 THEN 1 ELSE 0 END),
        SUM(CASE WHEN network_contribution_score < 0 OR network_contribution_score > 1 THEN 1 ELSE 0 END),
        SUM(CASE WHEN network_contribution_score IS NULL THEN 1 ELSE 0 END),
        ROUND(AVG(network_contribution_score)::numeric, 4)
    FROM latest_evaluations
    UNION ALL
    SELECT 'ubuntu_alignment_score', COUNT(*),
        SUM(CASE WHEN ubuntu_alignment_score >= 0 AND ubuntu_alignment_score <= 1 THEN 1 ELSE 0 END),
        SUM(CASE WHEN ubuntu_alignment_score < 0 OR ubuntu_alignment_score > 1 THEN 1 ELSE 0 END),
        SUM(CASE WHEN ubuntu_alignment_score IS NULL THEN 1 ELSE 0 END),
        ROUND(AVG(ubuntu_alignment_score)::numeric, 4)
    FROM latest_evaluations
    UNION ALL
    SELECT 'composite_score', COUNT(*),
        SUM(CASE WHEN composite_score >= 0 AND composite_score <= 1 THEN 1 ELSE 0 END),
        SUM(CASE WHEN composite_score < 0 OR composite_score > 1 THEN 1 ELSE 0 END),
        SUM(CASE WHEN composite_score IS NULL THEN 1 ELSE 0 END),
        ROUND(AVG(composite_score)::numeric, 4)
    FROM latest_evaluations
)
SELECT 
    dimension as "Dimension",
    total as "Total",
    valid as "Valid",
    invalid as "Invalid",
    null_count as "Nulls",
    avg_score as "Avg Score",
    CASE 
        WHEN invalid = 0 AND null_count = 0 THEN '✅ OK'
        WHEN invalid > 0 THEN '❌ INVALID VALUES'
        WHEN null_count > 0 THEN '⚠️ NULL VALUES'
        ELSE '❓ UNKNOWN'
    END as status
FROM score_checks;

\echo ''

-- ============================================================================
-- SECTION 7: UBUNTU PRINCIPLE METRICS VERIFICATION
-- ============================================================================
\echo '┌──────────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 7: UBUNTU PRINCIPLE METRICS VERIFICATION                             │'
\echo '└──────────────────────────────────────────────────────────────────────────────┘'

-- Check Ubuntu principle coverage (should have 4 principles per account)
WITH principle_coverage AS (
    SELECT 
        account_id,
        COUNT(DISTINCT principle) as principles_count,
        MAX(calculated_at) as last_calc
    FROM ubec_main.ubec_holonic_metrics
    WHERE calculated_at >= NOW() - INTERVAL '7 days'
    GROUP BY account_id
)
SELECT 
    principles_count as "Principles Per Account",
    COUNT(*) as "Account Count",
    ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 2) as "Percentage",
    CASE 
        WHEN principles_count = 4 THEN '✅ COMPLETE'
        WHEN principles_count >= 2 THEN '⚠️ PARTIAL'
        ELSE '❌ INCOMPLETE'
    END as status
FROM principle_coverage
GROUP BY principles_count
ORDER BY principles_count DESC;

\echo ''

-- Principle-level statistics
SELECT 
    principle as "Principle",
    element as "Element",
    COUNT(*) as "Records",
    COUNT(DISTINCT account_id) as "Accounts",
    ROUND(AVG(score)::numeric, 4) as "Avg Score",
    ROUND(MIN(score)::numeric, 4) as "Min Score",
    ROUND(MAX(score)::numeric, 4) as "Max Score",
    CASE LOWER(element::text)
        WHEN 'air' THEN '🌬️ (UBEC)'
        WHEN 'water' THEN '💧 (UBECrc)'
        WHEN 'earth' THEN '🌍 (UBECgpi)'
        WHEN 'fire' THEN '🔥 (UBECtt)'
        ELSE '❓'
    END as token_mapping
FROM ubec_main.ubec_holonic_metrics
WHERE calculated_at >= NOW() - INTERVAL '7 days'
GROUP BY principle, element
ORDER BY 
    CASE principle::text
        WHEN 'diversity' THEN 1
        WHEN 'reciprocity' THEN 2
        WHEN 'mutualism' THEN 3
        WHEN 'regeneration' THEN 4
        ELSE 5
    END;

\echo ''

-- ============================================================================
-- SECTION 8: DATA CONSISTENCY CHECK
-- ============================================================================
\echo '┌──────────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 8: DATA CONSISTENCY CHECK                                            │'
\echo '└──────────────────────────────────────────────────────────────────────────────┘'

-- Check for accounts with holonic_metrics but missing ubec_holonic_metrics (or vice versa)
WITH holonic_accounts AS (
    SELECT DISTINCT account_id FROM ubec_main.holonic_metrics
    WHERE evaluation_date >= NOW() - INTERVAL '7 days'
),
ubuntu_accounts AS (
    SELECT DISTINCT account_id FROM ubec_main.ubec_holonic_metrics
    WHERE calculated_at >= NOW() - INTERVAL '7 days'
)
SELECT 
    'Accounts in holonic_metrics only' as check_type,
    COUNT(*) as count,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ OK'
        WHEN COUNT(*) < 10 THEN '⚠️ FEW MISSING'
        ELSE '❌ MANY MISSING'
    END as status
FROM holonic_accounts h
WHERE NOT EXISTS (SELECT 1 FROM ubuntu_accounts u WHERE u.account_id = h.account_id)
UNION ALL
SELECT 
    'Accounts in ubec_holonic_metrics only' as check_type,
    COUNT(*) as count,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ OK'
        WHEN COUNT(*) < 10 THEN '⚠️ FEW MISSING'
        ELSE '❌ MANY MISSING'
    END as status
FROM ubuntu_accounts u
WHERE NOT EXISTS (SELECT 1 FROM holonic_accounts h WHERE h.account_id = u.account_id)
UNION ALL
SELECT 
    'Accounts in both tables (consistent)' as check_type,
    COUNT(*) as count,
    '✅ CONSISTENT' as status
FROM holonic_accounts h
WHERE EXISTS (SELECT 1 FROM ubuntu_accounts u WHERE u.account_id = h.account_id);

\echo ''

-- ============================================================================
-- SECTION 9: SCORE CHANGE DETECTION (Recent Updates)
-- ============================================================================
\echo '┌──────────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 9: SCORE CHANGE DETECTION (Last 48 Hours)                            │'
\echo '└──────────────────────────────────────────────────────────────────────────────┘'

-- Identify accounts with significant score changes
WITH score_history AS (
    SELECT 
        account_id,
        composite_score,
        holonic_category,
        evaluation_date,
        LAG(composite_score) OVER (PARTITION BY account_id ORDER BY evaluation_date) as prev_score,
        LAG(holonic_category) OVER (PARTITION BY account_id ORDER BY evaluation_date) as prev_category
    FROM ubec_main.holonic_metrics
    WHERE evaluation_date >= NOW() - INTERVAL '48 hours'
),
changes AS (
    SELECT 
        account_id,
        composite_score as current_score,
        prev_score,
        composite_score - prev_score as score_change,
        holonic_category as current_category,
        prev_category,
        CASE WHEN holonic_category != prev_category THEN true ELSE false END as category_changed,
        evaluation_date
    FROM score_history
    WHERE prev_score IS NOT NULL
)
SELECT 
    'Accounts with score changes' as metric,
    COUNT(DISTINCT account_id) as count
FROM changes
WHERE ABS(score_change) > 0.01
UNION ALL
SELECT 
    'Accounts with category changes' as metric,
    COUNT(DISTINCT account_id) as count
FROM changes
WHERE category_changed = true
UNION ALL
SELECT 
    'Avg score change magnitude' as metric,
    ROUND(AVG(ABS(score_change))::numeric, 4) as count
FROM changes
WHERE score_change IS NOT NULL;

\echo ''

-- Top 10 accounts with largest positive score changes
\echo 'Top 10 Accounts with Largest Score Improvements (Last 48h):'
WITH score_history AS (
    SELECT 
        account_id,
        composite_score,
        evaluation_date,
        LAG(composite_score) OVER (PARTITION BY account_id ORDER BY evaluation_date) as prev_score
    FROM ubec_main.holonic_metrics
    WHERE evaluation_date >= NOW() - INTERVAL '48 hours'
)
SELECT 
    LEFT(account_id, 12) || '...' as account_id,
    ROUND(prev_score::numeric, 4) as previous_score,
    ROUND(composite_score::numeric, 4) as current_score,
    ROUND((composite_score - prev_score)::numeric, 4) as improvement,
    evaluation_date::timestamp(0) as updated_at
FROM score_history
WHERE prev_score IS NOT NULL 
  AND composite_score > prev_score
ORDER BY (composite_score - prev_score) DESC
LIMIT 10;

\echo ''

-- ============================================================================
-- SECTION 10: SCHEDULER JOB STATUS CHECK
-- ============================================================================
\echo '┌──────────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 10: SCHEDULER JOB STATUS CHECK                                       │'
\echo '└──────────────────────────────────────────────────────────────────────────────┘'

-- Check if scheduler_jobs table exists and show holonic-related jobs
-- Note: Column is 'enabled' not 'is_active' per database schema
SELECT 
    job_name as "Job Name",
    schedule_interval as "Interval",
    last_run as "Last Run",
    next_run as "Next Run",
    enabled as "Enabled",
    CASE 
        WHEN enabled = true AND last_run >= NOW() - INTERVAL '2 hours' THEN '✅ RUNNING'
        WHEN enabled = true AND last_run >= NOW() - INTERVAL '24 hours' THEN '⚠️ DELAYED'
        WHEN enabled = true THEN '❌ STALE'
        ELSE '⏸️ DISABLED'
    END as status
FROM ubec_main.scheduler_jobs
WHERE job_name ILIKE '%holonic%' 
   OR job_name ILIKE '%evaluation%'
   OR job_name ILIKE '%analytics%'
ORDER BY job_name;

\echo ''

-- ============================================================================
-- SECTION 11: SUMMARY AND RECOMMENDATIONS
-- ============================================================================
\echo '┌──────────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 11: SUMMARY AND RECOMMENDATIONS                                      │'
\echo '└──────────────────────────────────────────────────────────────────────────────┘'

WITH health_checks AS (
    SELECT 
        -- Freshness check
        CASE WHEN (SELECT MAX(evaluation_date) FROM ubec_main.holonic_metrics) >= NOW() - INTERVAL '6 hours' 
             THEN 1 ELSE 0 END as freshness_ok,
        -- Coverage check
        CASE WHEN (SELECT COUNT(DISTINCT account_id) FROM ubec_main.holonic_metrics) >= 
                  (SELECT COUNT(DISTINCT account_id) FROM ubec_main.ubec_balances WHERE balance > 0) * 0.8
             THEN 1 ELSE 0 END as coverage_ok,
        -- Validity check
        CASE WHEN NOT EXISTS (
            SELECT 1 FROM ubec_main.holonic_metrics 
            WHERE composite_score < 0 OR composite_score > 1
        ) THEN 1 ELSE 0 END as validity_ok,
        -- Consistency check
        CASE WHEN (
            SELECT COUNT(DISTINCT account_id) FROM ubec_main.holonic_metrics WHERE evaluation_date >= NOW() - INTERVAL '7 days'
        ) = (
            SELECT COUNT(DISTINCT account_id) FROM ubec_main.ubec_holonic_metrics WHERE calculated_at >= NOW() - INTERVAL '7 days'
        ) THEN 1 ELSE 0 END as consistency_ok
)
SELECT 
    CASE WHEN freshness_ok = 1 THEN '✅' ELSE '❌' END || ' Data Freshness' as "Check",
    CASE WHEN freshness_ok = 1 THEN 'Evaluations are recent' ELSE 'Evaluations are stale - check scheduler' END as "Status"
FROM health_checks
UNION ALL
SELECT 
    CASE WHEN coverage_ok = 1 THEN '✅' ELSE '❌' END || ' Account Coverage',
    CASE WHEN coverage_ok = 1 THEN 'Good coverage (≥80%)' ELSE 'Low coverage - run batch evaluation' END
FROM health_checks
UNION ALL
SELECT 
    CASE WHEN validity_ok = 1 THEN '✅' ELSE '❌' END || ' Score Validity',
    CASE WHEN validity_ok = 1 THEN 'All scores in valid range' ELSE 'Invalid scores detected - investigate' END
FROM health_checks
UNION ALL
SELECT 
    CASE WHEN consistency_ok = 1 THEN '✅' ELSE '⚠️' END || ' Table Consistency',
    CASE WHEN consistency_ok = 1 THEN 'Tables are synchronized' ELSE 'Tables may be out of sync' END
FROM health_checks;

\echo ''

-- Overall health score
WITH health_checks AS (
    SELECT 
        CASE WHEN (SELECT MAX(evaluation_date) FROM ubec_main.holonic_metrics) >= NOW() - INTERVAL '6 hours' THEN 1 ELSE 0 END +
        CASE WHEN (SELECT COUNT(DISTINCT account_id) FROM ubec_main.holonic_metrics) >= 
                  (SELECT COUNT(DISTINCT account_id) FROM ubec_main.ubec_balances WHERE balance > 0) * 0.8 THEN 1 ELSE 0 END +
        CASE WHEN NOT EXISTS (SELECT 1 FROM ubec_main.holonic_metrics WHERE composite_score < 0 OR composite_score > 1) THEN 1 ELSE 0 END +
        CASE WHEN (SELECT COUNT(DISTINCT account_id) FROM ubec_main.holonic_metrics WHERE evaluation_date >= NOW() - INTERVAL '7 days') > 0 THEN 1 ELSE 0 END
        as total_passed
)
SELECT 
    CASE total_passed
        WHEN 4 THEN '🟢 OVERALL STATUS: HEALTHY (4/4 checks passed)'
        WHEN 3 THEN '🟡 OVERALL STATUS: GOOD (3/4 checks passed)'
        WHEN 2 THEN '🟠 OVERALL STATUS: DEGRADED (2/4 checks passed)'
        ELSE '🔴 OVERALL STATUS: UNHEALTHY (' || total_passed || '/4 checks passed)'
    END as "Overall Health Status"
FROM health_checks;

\echo ''
\echo '╔══════════════════════════════════════════════════════════════════════════════╗'
\echo '║                          END OF VERIFICATION REPORT                          ║'
\echo '╚══════════════════════════════════════════════════════════════════════════════╝'
\echo ''
\echo 'Attribution: This project uses the services of Claude and Anthropic PBC'
\echo '             to inform our decisions and recommendations.'
\echo ''
