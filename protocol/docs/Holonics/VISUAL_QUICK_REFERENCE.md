# UBEC Holonic Evaluator v3.0.0 - Visual Quick Reference

**Attribution:** This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    UBEC HOLONIC EVALUATOR v3.0.0                        │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  UBUNTU PRINCIPLE CALCULATION ENGINE                             │  │
│  │                                                                    │  │
│  │  ┌───────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────┐│  │
│  │  │ DIVERSITY │  │ RECIPROCITY  │  │  MUTUALISM   │  │REGENERA-││  │
│  │  │   (Air)   │  │   (Water)    │  │   (Earth)    │  │TION(Fire)││  │
│  │  │   UBEC    │  │   UBECrc     │  │   UBECgpi    │  │  UBECtt  ││  │
│  │  └─────┬─────┘  └──────┬───────┘  └──────┬───────┘  └────┬────┘│  │
│  │        │                │                  │                │     │  │
│  │        └────────────────┴──────────────────┴────────────────┘     │  │
│  │                              │                                     │  │
│  │                              ▼                                     │  │
│  │                    ┌───────────────────┐                          │  │
│  │                    │ UBUNTU ALIGNMENT  │                          │  │
│  │                    │      SCORE        │                          │  │
│  │                    │  (Weighted Avg)   │                          │  │
│  │                    └───────────────────┘                          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  5-DIMENSIONAL HOLONIC EVALUATION                                │  │
│  │                                                                    │  │
│  │  • Autonomy Integration      (derived from ubuntu metrics)       │  │
│  │  • Multi-Scale Participation (derived from ubuntu metrics)       │  │
│  │  • Regenerative Impact       (derived from ubuntu metrics)       │  │
│  │  • Network Contribution      (derived from ubuntu metrics)       │  │
│  │  • Ubuntu Alignment          (from principle calculations)       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                          ┌─────────────────┐
                          │    DATABASE     │
                          │   PERSISTENCE   │
                          └─────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
        ┌────────────────────┐         ┌────────────────────────┐
        │ holonic_metrics    │         │ ubec_holonic_metrics   │
        │                    │         │                        │
        │ • composite_score  │         │ • element              │
        │ • ubuntu_alignment │         │ • principle            │
        │ • 5 dimension      │         │ • score                │
        │   scores           │         │ • health_status        │
        │ • category         │         │ • assessment_details   │
        │ • raw_metrics      │         │ • calculation_method   │
        └────────────────────┘         └────────────────────────┘
                                                    │
                                                    ▼
                                        ┌─────────────────────┐
                                        │   API SERVICE       │
                                        │  (reads metrics)    │
                                        └─────────────────────┘
```

---

## Data Flow Diagram

```
Daily Evaluation Cycle (Scheduled at 2 AM)
═══════════════════════════════════════════

STEP 1: Load Account Data
┌─────────────────────────────────────┐
│  SELECT account_id                  │
│  FROM account_balances              │
│  WHERE asset_code = 'UBEC'          │
└──────────────┬──────────────────────┘
               │
               ▼
STEP 2: Calculate Ubuntu Principles (Per Account)
┌────────────────────────────────────────────────────────────────┐
│  FOR EACH account:                                             │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ Diversity        │  │ Reciprocity      │                   │
│  │ • Query UBEC     │  │ • Query UBECrc   │                   │
│  │   balance        │  │   transactions   │                   │
│  │ • Count partners │  │ • Calculate flow │                   │
│  │ • Count txs      │  │ • Measure balance│                   │
│  │ Score: 0.65      │  │ Score: 0.72      │                   │
│  └──────────────────┘  └──────────────────┘                   │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ Mutualism        │  │ Regeneration     │                   │
│  │ • Query UBECgpi  │  │ • Query UBECtt   │                   │
│  │   holdings       │  │   activity       │                   │
│  │ • Check age      │  │ • Count txs      │                   │
│  │ • Measure stable │  │ • Sum volume     │                   │
│  │ Score: 0.58      │  │ Score: 0.43      │                   │
│  └──────────────────┘  └──────────────────┘                   │
└────────────────────────────────────────────────────────────────┘
               │
               ▼
STEP 3: Store Ubuntu Principle Metrics
┌─────────────────────────────────────────────────────────────┐
│  INSERT INTO ubec_holonic_metrics                           │
│  VALUES (account_id, 'Air', 'diversity', 0.65, ...)        │
│  VALUES (account_id, 'Water', 'reciprocity', 0.72, ...)    │
│  VALUES (account_id, 'Earth', 'mutualism', 0.58, ...)      │
│  VALUES (account_id, 'Fire', 'regeneration', 0.43, ...)    │
└─────────────────────────────────────────────────────────────┘
               │
               ▼
STEP 4: Calculate Ubuntu Alignment Score
┌─────────────────────────────────────────────────────────────┐
│  ubuntu_alignment = (0.65 * 0.25) +  // diversity          │
│                      (0.72 * 0.25) +  // reciprocity        │
│                      (0.58 * 0.25) +  // mutualism          │
│                      (0.43 * 0.25)    // regeneration       │
│                   = 0.595                                   │
└─────────────────────────────────────────────────────────────┘
               │
               ▼
STEP 5: Calculate Other Dimensions & Composite
┌─────────────────────────────────────────────────────────────┐
│  autonomy_score = diversity * 0.7 + mutualism * 0.3        │
│  multi_scale = diversity * 0.5 + reciprocity * 0.5         │
│  regenerative = regeneration * 0.7 + mutualism * 0.3       │
│  network = reciprocity * 0.6 + diversity * 0.4             │
│  ubuntu = ubuntu_alignment (from step 4)                   │
│                                                             │
│  composite_score = (autonomy * 0.20) +                     │
│                    (multi_scale * 0.20) +                  │
│                    (regenerative * 0.20) +                 │
│                    (network * 0.20) +                      │
│                    (ubuntu * 0.20)                         │
└─────────────────────────────────────────────────────────────┘
               │
               ▼
STEP 6: Store Complete Evaluation
┌─────────────────────────────────────────────────────────────┐
│  INSERT INTO holonic_metrics                                │
│  VALUES (account_id,                                        │
│          autonomy_score,                                    │
│          multi_scale_score,                                 │
│          regenerative_score,                                │
│          network_score,                                     │
│          ubuntu_alignment,                                  │
│          composite_score,                                   │
│          holonic_category,                                  │
│          raw_metrics)                                       │
└─────────────────────────────────────────────────────────────┘
               │
               ▼
           ┌───────┐
           │ DONE  │
           └───────┘
```

---

## API Request Flow

```
User → API Request: GET /api/v1/holonic-scores?limit=1
═════════════════════════════════════════════════════════

┌─────────────────────────────────┐
│  1. API Receives Request        │
│     Rate limit: 100/min check   │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  2. Query Main Holonic Metrics                          │
│                                                           │
│  SELECT account_id, composite_score, ubuntu_alignment,  │
│         autonomy_integration_score, ...                  │
│  FROM holonic_metrics                                    │
│  WHERE evaluation_date >= CURRENT_DATE - 30 days        │
│  ORDER BY composite_score DESC                           │
│  LIMIT 1                                                 │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  3. Query Ubuntu Principle Metrics                      │
│                                                           │
│  SELECT                                                  │
│    MAX(CASE WHEN principle = 'diversity'                │
│        THEN score END) as diversity,                     │
│    MAX(CASE WHEN principle = 'reciprocity'              │
│        THEN score END) as reciprocity_health,            │
│    MAX(CASE WHEN principle = 'mutualism'                │
│        THEN score END) as mutualism_capacity,            │
│    MAX(CASE WHEN principle = 'regeneration'             │
│        THEN score END) as regeneration                   │
│  FROM ubec_holonic_metrics                               │
│  WHERE account_id = $1                                   │
│    AND calculated_at >= NOW() - INTERVAL '24 hours'     │
│  GROUP BY account_id                                     │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  4. Combine Data & Format Response                      │
│                                                           │
│  {                                                       │
│    "account_id": "GB...",                                │
│    "composite_score": 0.595,                             │
│    "holonic_category": "contributor",                    │
│    "dimensions": {                                       │
│      "autonomy_integration": 0.63,                       │
│      "multi_scale_participation": 0.68,                  │
│      "regenerative_impact": 0.48,                        │
│      "network_contribution": 0.69,                       │
│      "ubuntu_alignment": 0.595                           │
│    },                                                    │
│    "ubuntu_principles": {                                │
│      "diversity": 0.65,                                  │
│      "reciprocity_health": 0.72,                         │
│      "mutualism_capacity": 0.58,                         │
│      "regeneration": 0.43                                │
│    }                                                     │
│  }                                                       │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  5. Return JSON Response        │
│     Status: 200 OK               │
│     Time: ~5-10ms                │
└─────────────────────────────────┘
```

---

## Score Calculation Visual

```
UBUNTU PRINCIPLE SCORES
═══════════════════════

Diversity (Air/UBEC)
────────────────────
┌─────────────────────────────────────────┐
│  Balance:    3,200 UBEC                 │
│  Partners:   12 unique                  │
│  Txs:        23 in 90 days              │
├─────────────────────────────────────────┤
│  Participation: 3200/5000 * 0.4 = 0.26  │
│  Diversity:     12/20     * 0.3 = 0.18  │
│  Activity:      23/30     * 0.3 = 0.23  │
├─────────────────────────────────────────┤
│  TOTAL SCORE: 0.67                      │
│  ████████████████▌░░░░░ 67%             │
└─────────────────────────────────────────┘

Reciprocity (Water/UBECrc)
──────────────────────────
┌─────────────────────────────────────────┐
│  Transactions: 45 in 90 days            │
│  Sent:         2,400 UBECrc             │
│  Received:     2,100 UBECrc             │
├─────────────────────────────────────────┤
│  Activity: 45/50   * 0.4 = 0.36         │
│  Balance:  0.875   * 0.6 = 0.53         │
│    (2100/2400 = 0.875)                  │
├─────────────────────────────────────────┤
│  TOTAL SCORE: 0.89                      │
│  ██████████████████████░ 89%            │
└─────────────────────────────────────────┘

Mutualism (Earth/UBECgpi)
─────────────────────────
┌─────────────────────────────────────────┐
│  Holdings:  8,500 UBECgpi               │
│  Age:       287 days                    │
│  Volatility: 125 (stddev)               │
├─────────────────────────────────────────┤
│  Balance:    8500/10000 * 0.5 = 0.43    │
│  Stability:  287/365    * 0.3 = 0.24    │
│  Consistency:            * 0.2 = 0.17   │
│    (1 - 125/8500 = 0.985)               │
├─────────────────────────────────────────┤
│  TOTAL SCORE: 0.84                      │
│  █████████████████████░░ 84%            │
└─────────────────────────────────────────┘

Regeneration (Fire/UBECtt)
──────────────────────────
┌─────────────────────────────────────────┐
│  Transactions: 8 in 90 days             │
│  Volume:       2,100 UBECtt             │
│  Active days:  15                       │
├─────────────────────────────────────────┤
│  Transform:  8/20    * 0.5 = 0.20       │
│  Volume:     2100/5000 * 0.3 = 0.13     │
│  Consistent: 15/30   * 0.2 = 0.10       │
├─────────────────────────────────────────┤
│  TOTAL SCORE: 0.43                      │
│  ███████████░░░░░░░░░░░░ 43%            │
└─────────────────────────────────────────┘

UBUNTU ALIGNMENT SCORE
══════════════════════
┌─────────────────────────────────────────┐
│  Diversity:     0.67 × 0.25 = 0.168     │
│  Reciprocity:   0.89 × 0.25 = 0.223     │
│  Mutualism:     0.84 × 0.25 = 0.210     │
│  Regeneration:  0.43 × 0.25 = 0.108     │
├─────────────────────────────────────────┤
│  UBUNTU ALIGNMENT: 0.709                │
│  ████████████████████░░░ 71%            │
└─────────────────────────────────────────┘
```

---

## Health Status Determination

```
Score Range → Health Status
════════════════════════════

0.8 ────────────┐
                │  HEALTHY
0.6 ────────────┤  ✅ "System functioning well"
                │
0.4 ────────────┤  DEGRADED
                │  ⚠️  "Attention needed"
0.3 ────────────┤
                │  UNHEALTHY
0.0 ────────────┘  ❌ "Critical issues"

Example Accounts:
┌──────────────────────────────────────────┐
│ Account A:                               │
│   Diversity:    0.85 → ✅ HEALTHY       │
│   Reciprocity:  0.72 → ✅ HEALTHY       │
│   Mutualism:    0.45 → ⚠️  DEGRADED     │
│   Regeneration: 0.28 → ❌ UNHEALTHY     │
└──────────────────────────────────────────┘
```

---

## Database Table Relationships

```
holonic_metrics                ubec_holonic_metrics
═══════════════                ════════════════════

┌─────────────────┐           ┌──────────────────┐
│ account_id (PK) │◄──────────┤ account_id       │
│ evaluation_date │           │ element          │
│ composite_score │           │ principle        │
│ ubuntu_alignment│           │ score            │
│ autonomy_score  │           │ health_status    │
│ multi_scale     │           │ details (JSONB)  │
│ regenerative    │           │ calculated_at    │
│ network         │           │                  │
│ category        │           │ 4 rows per       │
│ raw_metrics     │           │ account per day  │
│                 │           │                  │
│ 1 row per       │           │ (Air/diversity   │
│ account per day │           │  Water/reciprocity│
│                 │           │  Earth/mutualism │
│                 │           │  Fire/regeneration│
└─────────────────┘           └──────────────────┘
        │                              ▲
        │                              │
        │         Both tables are      │
        └──────  populated daily ──────┘
                    at 2 AM
```

---

## Performance Comparison

```
API Response Time (per account)
════════════════════════════════

v2.3.2 (Old - Calculate On-Demand)
┌─────────────────────────────────────────────────┐
│                                                   │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 100-200ms                 │
│                                                   │
└─────────────────────────────────────────────────┘

v3.0.0 (New - Read from Database)
┌─────────────────────────────────────────────────┐
│                                                   │
│  ▓ 5-10ms                                        │
│                                                   │
└─────────────────────────────────────────────────┘

                    20x FASTER ⚡


Batch Evaluation Time (500 accounts)
════════════════════════════════════

v2.3.2 (Old)
┌────────────────────────────────────────┐
│ Not applicable - no batch evaluation   │
└────────────────────────────────────────┘

v3.0.0 (New)
┌────────────────────────────────────────┐
│ 75 seconds (once per day at 2 AM)     │
│ ▓▓▓▓▓▓▓▓░░░░░░░░ ~1.25 minutes        │
└────────────────────────────────────────┘
```

---

## Directory Structure

```
/srv/ubec/
├── core/
│   ├── holonic/
│   │   ├── ubec_holonic_evaluator.py     ← v3.0.0 (NEW)
│   │   └── ubec_holonic_evaluator.py.v2.3.2.backup
│   └── ...
├── services/
│   └── api/
│       └── api_service.py                ← Update to v2.3.1
├── utilities/
│   └── service_health_check.py
└── main.py

/docs/
├── HOLONIC_EVALUATOR_V3_DOCUMENTATION.md
├── IMPLEMENTATION_CHECKLIST.md
├── OPTION_B_COMPLETE_SUMMARY.md
└── VISUAL_QUICK_REFERENCE.md            ← This file
```

---

## Quick Command Reference

```bash
# Check if table exists
psql -U ubec -d ubec -c "
  SELECT EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_schema = 'ubec_main'
    AND table_name = 'ubec_holonic_metrics'
  );"

# Run single account evaluation (Python)
python -c "
from core.holonic.ubec_holonic_evaluator import create_holonic_evaluator
evaluator = await create_holonic_evaluator(db, config)
metrics = await evaluator.evaluate_account('GB...', save_to_db=True)
print(f'Score: {metrics.ubuntu_alignment_score}')
"

# Run batch evaluation
python -c "
result = await evaluator.evaluate_all_accounts(max_accounts=500)
print(f'Evaluated: {result[\"evaluated_count\"]} accounts')
"

# Check stored metrics
psql -U ubec -d ubec -c "
  SELECT principle, COUNT(*) as count
  FROM ubec_main.ubec_holonic_metrics
  WHERE calculated_at >= CURRENT_DATE
  GROUP BY principle;
"

# Test API endpoint
curl "http://localhost:8000/api/v1/holonic-scores?limit=1" | \
  jq '.accounts[0].ubuntu_principles'

# Monitor evaluation logs
tail -f /var/log/ubec/holonic_evaluator.log | \
  grep "Evaluation complete"
```

---

## Traffic Light Status Indicators

```
System Status Check
═══════════════════

Database Table Exists?
  ✅ ubec_main.ubec_holonic_metrics exists
  ✅ ubec_main.holonic_metrics exists
  ✅ Both tables have data
  
Evaluator Health?
  ✅ Service initialized
  ✅ Database connection working
  ✅ Weights sum to 1.0
  ✅ Error rate < 5%
  
API Integration?
  ✅ Endpoints returning data
  ✅ Response times < 10ms
  ✅ Ubuntu metrics present
  ✅ No calculation methods in API
  
Scheduled Jobs?
  ✅ Daily evaluation at 2 AM
  ✅ Health checks every 5 minutes
  ✅ Last evaluation successful
  ✅ All accounts evaluated

Data Quality?
  ✅ Scores in 0.0-1.0 range
  ✅ Health status determined
  ✅ Assessment details complete
  ✅ No missing data

═══════════════════
ALL SYSTEMS GO! 🚀
═══════════════════
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-10  
**For**: UBEC Protocol Holonic Evaluator v3.0.0

---

Attribution: This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.
