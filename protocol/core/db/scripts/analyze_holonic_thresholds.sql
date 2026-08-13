-- ============================================================================
-- UBEC Holonic Category Threshold Analysis and Adjustment
-- ============================================================================
-- Purpose: Analyze current score distribution and propose adjusted thresholds
--          for a more diverse category distribution in early-stage ecosystem
--
-- Version: 1.0.0
-- Date: November 30, 2025
--
-- Current Thresholds (designed for mature ecosystem):
--   Observer:    0.0 - 0.2
--   Participant: 0.2 - 0.4
--   Contributor: 0.4 - 0.6
--   Integrator:  0.6 - 0.8
--   Exemplar:    0.8 - 1.0
--
-- Problem: Early-stage ecosystem has most scores < 0.2, so everyone is "Observer"
--
-- Attribution: This project uses the services of Claude and Anthropic PBC
-- ============================================================================

\echo ''
\echo '╔═══════════════════════════════════════════════════════════════════════════╗'
\echo '║       HOLONIC CATEGORY THRESHOLD ANALYSIS & ADJUSTMENT                    ║'
\echo '╚═══════════════════════════════════════════════════════════════════════════╝'
\echo ''

-- ============================================================================
-- SECTION 1: Current Score Distribution Analysis
-- ============================================================================
\echo '┌───────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 1: CURRENT SCORE DISTRIBUTION                                     │'
\echo '└───────────────────────────────────────────────────────────────────────────┘'

-- Get latest scores for each account
WITH latest_scores AS (
    SELECT DISTINCT ON (account_id)
        account_id,
        composite_score,
        holonic_category
    FROM ubec_main.holonic_metrics
    ORDER BY account_id, evaluation_date DESC
)
SELECT 
    MIN(composite_score) as min_score,
    PERCENTILE_CONT(0.10) WITHIN GROUP (ORDER BY composite_score) as p10,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY composite_score) as p25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY composite_score) as median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY composite_score) as p75,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY composite_score) as p90,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY composite_score) as p95,
    MAX(composite_score) as max_score,
    AVG(composite_score) as avg_score,
    COUNT(*) as total_accounts
FROM latest_scores;

\echo ''

-- Score histogram
\echo '┌───────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 2: SCORE HISTOGRAM (Current Distribution)                         │'
\echo '└───────────────────────────────────────────────────────────────────────────┘'

WITH latest_scores AS (
    SELECT DISTINCT ON (account_id)
        account_id,
        composite_score
    FROM ubec_main.holonic_metrics
    ORDER BY account_id, evaluation_date DESC
),
score_buckets AS (
    SELECT 
        CASE 
            WHEN composite_score < 0.05 THEN '0.00-0.05'
            WHEN composite_score < 0.10 THEN '0.05-0.10'
            WHEN composite_score < 0.15 THEN '0.10-0.15'
            WHEN composite_score < 0.20 THEN '0.15-0.20'
            WHEN composite_score < 0.25 THEN '0.20-0.25'
            WHEN composite_score < 0.30 THEN '0.25-0.30'
            WHEN composite_score < 0.35 THEN '0.30-0.35'
            WHEN composite_score < 0.40 THEN '0.35-0.40'
            WHEN composite_score < 0.50 THEN '0.40-0.50'
            ELSE '0.50+'
        END as score_range,
        composite_score
    FROM latest_scores
)
SELECT 
    score_range,
    COUNT(*) as accounts,
    ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 1) as percentage,
    REPEAT('█', (COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 50)::int) as bar
FROM score_buckets
GROUP BY score_range
ORDER BY score_range;

\echo ''

-- ============================================================================
-- SECTION 3: Current Category Distribution (With Current Thresholds)
-- ============================================================================
\echo '┌───────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 3: CURRENT CATEGORY DISTRIBUTION (Original Thresholds)            │'
\echo '└───────────────────────────────────────────────────────────────────────────┘'

WITH latest_scores AS (
    SELECT DISTINCT ON (account_id)
        account_id,
        composite_score,
        holonic_category
    FROM ubec_main.holonic_metrics
    ORDER BY account_id, evaluation_date DESC
)
SELECT 
    holonic_category as "Category",
    COUNT(*) as "Count",
    ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 1) as "Percentage",
    ROUND(MIN(composite_score)::numeric, 4) as "Min Score",
    ROUND(MAX(composite_score)::numeric, 4) as "Max Score"
FROM latest_scores
GROUP BY holonic_category
ORDER BY 
    CASE holonic_category
        WHEN 'Exemplar' THEN 1
        WHEN 'Integrator' THEN 2
        WHEN 'Contributor' THEN 3
        WHEN 'Participant' THEN 4
        WHEN 'Observer' THEN 5
    END;

\echo ''
\echo 'Current Thresholds: Observer(<0.2), Participant(0.2-0.4), Contributor(0.4-0.6), Integrator(0.6-0.8), Exemplar(>0.8)'
\echo ''

-- ============================================================================
-- SECTION 4: Proposed New Thresholds (Percentile-Based)
-- ============================================================================
\echo '┌───────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 4: PROPOSED NEW THRESHOLDS (Early-Stage Ecosystem)                │'
\echo '└───────────────────────────────────────────────────────────────────────────┘'

\echo ''
\echo 'OPTION A: Percentile-Based Thresholds (Relative to Current Network)'
\echo '=================================================================='
\echo 'Goal: Create natural distribution based on actual network performance'
\echo ''

WITH latest_scores AS (
    SELECT DISTINCT ON (account_id)
        composite_score
    FROM ubec_main.holonic_metrics
    ORDER BY account_id, evaluation_date DESC
)
SELECT 
    'Observer' as category,
    '0.0' as "From",
    ROUND(PERCENTILE_CONT(0.40) WITHIN GROUP (ORDER BY composite_score)::numeric, 3)::text as "To (P40)",
    '~40%' as target_pct
FROM latest_scores
UNION ALL
SELECT 
    'Participant',
    ROUND(PERCENTILE_CONT(0.40) WITHIN GROUP (ORDER BY composite_score)::numeric, 3)::text,
    ROUND(PERCENTILE_CONT(0.70) WITHIN GROUP (ORDER BY composite_score)::numeric, 3)::text,
    '~30%'
FROM latest_scores
UNION ALL
SELECT 
    'Contributor',
    ROUND(PERCENTILE_CONT(0.70) WITHIN GROUP (ORDER BY composite_score)::numeric, 3)::text,
    ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY composite_score)::numeric, 3)::text,
    '~20%'
FROM latest_scores
UNION ALL
SELECT 
    'Integrator',
    ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY composite_score)::numeric, 3)::text,
    ROUND(PERCENTILE_CONT(0.97) WITHIN GROUP (ORDER BY composite_score)::numeric, 3)::text,
    '~7%'
FROM latest_scores
UNION ALL
SELECT 
    'Exemplar',
    ROUND(PERCENTILE_CONT(0.97) WITHIN GROUP (ORDER BY composite_score)::numeric, 3)::text,
    '1.0',
    '~3%'
FROM latest_scores;

\echo ''
\echo 'OPTION B: Fixed Early-Stage Thresholds (Lower Boundaries)'
\echo '========================================================='
\echo 'Goal: Lower all boundaries to match early-stage ecosystem'
\echo ''

SELECT 
    'Observer' as category,
    '0.0 - 0.05' as score_range,
    'Holding tokens, minimal activity' as description
UNION ALL SELECT 'Participant', '0.05 - 0.12', 'Some activity, beginning engagement'
UNION ALL SELECT 'Contributor', '0.12 - 0.22', 'Regular participation, building network'
UNION ALL SELECT 'Integrator', '0.22 - 0.32', 'Active contributor, strong connections'
UNION ALL SELECT 'Exemplar', '0.32+', 'Top performers, leading by example';

\echo ''

-- ============================================================================
-- SECTION 5: Preview New Distribution with Option B Thresholds
-- ============================================================================
\echo '┌───────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 5: PREVIEW - Distribution with OPTION B Thresholds                │'
\echo '└───────────────────────────────────────────────────────────────────────────┘'

WITH latest_scores AS (
    SELECT DISTINCT ON (account_id)
        account_id,
        composite_score
    FROM ubec_main.holonic_metrics
    ORDER BY account_id, evaluation_date DESC
),
new_categories AS (
    SELECT 
        account_id,
        composite_score,
        CASE 
            WHEN composite_score >= 0.32 THEN 'Exemplar'
            WHEN composite_score >= 0.22 THEN 'Integrator'
            WHEN composite_score >= 0.12 THEN 'Contributor'
            WHEN composite_score >= 0.05 THEN 'Participant'
            ELSE 'Observer'
        END as new_category
    FROM latest_scores
)
SELECT 
    new_category as "Category",
    COUNT(*) as "Count",
    ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 1) as "Percentage",
    ROUND(MIN(composite_score)::numeric, 4) as "Min Score",
    ROUND(MAX(composite_score)::numeric, 4) as "Max Score",
    CASE new_category
        WHEN 'Exemplar' THEN '🌟'
        WHEN 'Integrator' THEN '🔗'
        WHEN 'Contributor' THEN '💪'
        WHEN 'Participant' THEN '👋'
        WHEN 'Observer' THEN '👀'
    END as icon
FROM new_categories
GROUP BY new_category
ORDER BY 
    CASE new_category
        WHEN 'Exemplar' THEN 1
        WHEN 'Integrator' THEN 2
        WHEN 'Contributor' THEN 3
        WHEN 'Participant' THEN 4
        WHEN 'Observer' THEN 5
    END;

\echo ''

-- ============================================================================
-- SECTION 6: Side-by-Side Comparison
-- ============================================================================
\echo '┌───────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 6: SIDE-BY-SIDE COMPARISON                                        │'
\echo '└───────────────────────────────────────────────────────────────────────────┘'

WITH latest_scores AS (
    SELECT DISTINCT ON (account_id)
        account_id,
        composite_score,
        holonic_category as current_category
    FROM ubec_main.holonic_metrics
    ORDER BY account_id, evaluation_date DESC
),
with_new AS (
    SELECT 
        composite_score,
        current_category,
        CASE 
            WHEN composite_score >= 0.32 THEN 'Exemplar'
            WHEN composite_score >= 0.22 THEN 'Integrator'
            WHEN composite_score >= 0.12 THEN 'Contributor'
            WHEN composite_score >= 0.05 THEN 'Participant'
            ELSE 'Observer'
        END as new_category
    FROM latest_scores
)
SELECT 
    'Current' as threshold_set,
    SUM(CASE WHEN current_category = 'Observer' THEN 1 ELSE 0 END) as "👀 Observer",
    SUM(CASE WHEN current_category = 'Participant' THEN 1 ELSE 0 END) as "👋 Participant",
    SUM(CASE WHEN current_category = 'Contributor' THEN 1 ELSE 0 END) as "💪 Contributor",
    SUM(CASE WHEN current_category = 'Integrator' THEN 1 ELSE 0 END) as "🔗 Integrator",
    SUM(CASE WHEN current_category = 'Exemplar' THEN 1 ELSE 0 END) as "🌟 Exemplar"
FROM with_new
UNION ALL
SELECT 
    'Option B (New)',
    SUM(CASE WHEN new_category = 'Observer' THEN 1 ELSE 0 END),
    SUM(CASE WHEN new_category = 'Participant' THEN 1 ELSE 0 END),
    SUM(CASE WHEN new_category = 'Contributor' THEN 1 ELSE 0 END),
    SUM(CASE WHEN new_category = 'Integrator' THEN 1 ELSE 0 END),
    SUM(CASE WHEN new_category = 'Exemplar' THEN 1 ELSE 0 END)
FROM with_new;

\echo ''

-- ============================================================================
-- SECTION 7: SQL to Update Categories (RUN ONLY AFTER REVIEW)
-- ============================================================================
\echo '┌───────────────────────────────────────────────────────────────────────────┐'
\echo '│ SECTION 7: UPDATE SCRIPT (Run separately after review)                    │'
\echo '└───────────────────────────────────────────────────────────────────────────┘'

\echo ''
\echo 'To apply Option B thresholds, run the following UPDATE:'
\echo ''
\echo '-- OPTION B: Early-Stage Ecosystem Thresholds'
\echo '-- Observer:    0.00 - 0.05'
\echo '-- Participant: 0.05 - 0.12'
\echo '-- Contributor: 0.12 - 0.22'
\echo '-- Integrator:  0.22 - 0.32'
\echo '-- Exemplar:    0.32+'
\echo ''
\echo 'UPDATE ubec_main.holonic_metrics'
\echo 'SET holonic_category = CASE'
\echo '    WHEN composite_score >= 0.32 THEN ''Exemplar'''
\echo '    WHEN composite_score >= 0.22 THEN ''Integrator'''
\echo '    WHEN composite_score >= 0.12 THEN ''Contributor'''
\echo '    WHEN composite_score >= 0.05 THEN ''Participant'''
\echo '    ELSE ''Observer'''
\echo 'END;'
\echo ''
\echo 'NOTE: You will also need to update the ubec_holonic_evaluator.py thresholds'
\echo '      to ensure future evaluations use the new boundaries.'
\echo ''

\echo '╔═══════════════════════════════════════════════════════════════════════════╗'
\echo '║                      END OF ANALYSIS                                      ║'
\echo '╚═══════════════════════════════════════════════════════════════════════════╝'
