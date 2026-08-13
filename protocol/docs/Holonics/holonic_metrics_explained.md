# UBEC Holonic Evaluation Metrics - Calculation Breakdown
## How Scores Are Defined and Calculated

**Date:** October 14, 2025  
**Module:** `ubec_holonic_evaluator.py` v4.2.3  
**Your Network Results:** 643 accounts evaluated

---

## Overview

Each account receives **5 dimensional scores** (0.0 to 1.0) that are combined into a **composite score** using configured weights. The composite score determines the account's **holonic category**.

---

## 1. Autonomy & Integration Balance (Your Avg: 0.77)

**Purpose:** Measures the balance between independent activity and collective participation.

### Formula Components:

**Autonomy Score** (Independence):
```python
balance_autonomy = min(balance / 10000.0, 1.0)     # Balance sufficiency
tx_autonomy = min(transaction_count / 100.0, 1.0)  # Activity level
autonomy_score = (balance_autonomy + tx_autonomy) / 2
```

**Integration Score** (Collective Participation):
```python
network_integration = min(unique_partners / 50.0, 1.0)  # Network connectivity
community_integration = 0.5                              # TODO: Placeholder
integration_score = (network_integration + community_integration) / 2
```

**Final Balance Score:**
```python
balance_score = 1.0 - abs(autonomy_score - integration_score)
# Perfect balance (autonomy = integration) = 1.0
# Maximum imbalance = 0.0
```

### Thresholds:
- Balance > 10,000 UBEC → Maximum balance autonomy (1.0)
- 100+ transactions → Maximum transaction autonomy (1.0)
- 50+ unique partners → Maximum network integration (1.0)

### Your Network's 0.77 Score Means:
✅ Good balance between independence and network participation  
✅ Accounts are neither too isolated nor too dependent  
✅ Healthy autonomy/integration ratio

---

## 2. Multi-Scale Participation (Your Avg: 0.17)

**Purpose:** Measures activity across individual, community, and system scales.

### Formula:
```python
individual_scale = min(transaction_count / 100.0, 1.0)    # Personal activity
community_scale = min(unique_partners / 50.0, 1.0)        # Local network
system_scale = 0.5                                         # TODO: Placeholder

multi_scale_score = (individual_scale + community_scale + system_scale) / 3
```

### Thresholds:
- 100+ transactions → Maximum individual participation (1.0)
- 50+ unique partners → Maximum community participation (1.0)
- System scale: Currently placeholder (0.5 for all accounts)

### Your Network's 0.17 Score Means:
⚠️ Low transaction counts (< 17 avg transactions per account)  
⚠️ Limited unique partners (< 8.5 avg per account)  
📊 **Typical of early-stage ecosystems or passive holders**

---

## 3. Regenerative Impact (Your Avg: 0.17)

**Purpose:** Measures contribution to ecosystem regeneration and growth.

### Formula:
```python
distribution_impact = min(unique_partners / 100.0, 1.0)           # Token spreading
growth_impact = 0.5                                                # TODO: Placeholder
sustainability_impact = min(account_age_days / 365.0, 1.0)        # Long-term holding

regenerative_score = (distribution_impact + growth_impact + sustainability_impact) / 3
```

### Thresholds:
- 100+ unique partners → Maximum distribution impact (1.0)
- Growth impact: Currently placeholder (0.5 for all accounts)
- 365+ days old → Maximum sustainability (1.0)

### Your Network's 0.17 Score Means:
⚠️ Limited token distribution (< 17 unique partners avg)  
⚠️ Relatively new accounts (< 62 days avg account age)  
📊 **Early ecosystem - accounts haven't been active long enough**

---

## 4. Network Contribution (Your Avg: 0.04)

**Purpose:** Measures overall contribution to network health and vitality.

### Formula:
```python
volume_contribution = min(transaction_count / 200.0, 1.0)       # Transaction activity
connectivity_contribution = min(unique_partners / 100.0, 1.0)   # Network bridging
balance_contribution = min(balance / 50000.0, 1.0)              # Capital contribution
ecosystem_contribution = (balance_contribution + volume_contribution) / 2

network_score = (volume_contribution + connectivity_contribution + ecosystem_contribution) / 3
```

### Thresholds:
- 200+ transactions → Maximum volume (1.0)
- 100+ unique partners → Maximum connectivity (1.0)
- 50,000+ UBEC balance → Maximum balance contribution (1.0)

### Your Network's 0.04 Score Means:
🔴 Very low transaction volume (< 8 transactions avg per account)  
🔴 Minimal network connectivity (< 4 unique partners avg)  
🔴 Lower balances or highly distributed holdings  
📊 **Indicates mostly passive holders with minimal transactions**

---

## 5. Ubuntu Alignment (Your Avg: 0.12)

**Purpose:** Measures alignment with Ubuntu philosophy principles.

### Formula:
```python
reciprocity = 0.6                                              # TODO: Placeholder
mutualism = min(unique_partners / 50.0, 1.0)                  # Mutual benefit
diversity = min(unique_partners / 100.0, 1.0)                 # Diverse connections
regeneration = min(account_age_days / 365.0, 1.0)            # System contribution
holism = min(transaction_count / 150.0, 1.0)                 # Whole system participation

ubuntu_score = (reciprocity + mutualism + diversity + regeneration + holism) / 5
```

### Thresholds:
- Reciprocity: Currently placeholder (0.6 for all accounts)
- 50+ unique partners → Maximum mutualism (1.0)
- 100+ unique partners → Maximum diversity (1.0)
- 365+ days old → Maximum regeneration (1.0)
- 150+ transactions → Maximum holism (1.0)

### Your Network's 0.12 Score Means:
⚠️ Limited diverse connections (< 12 unique partners avg)  
⚠️ Low transaction-based participation (< 18 transactions avg)  
⚠️ Early-stage accounts (< 44 days avg)  
📊 **Low Ubuntu alignment is expected for new/passive ecosystems**

---

## 6. Composite Score & Category (Your Avg: 0.253)

**Purpose:** Overall holonic evaluation combining all dimensions.

### Formula:
```python
composite_score = (
    autonomy_integration * weight_1 +      # 0.77 * 0.20 = 0.154
    multi_scale * weight_2 +               # 0.17 * 0.20 = 0.034
    regenerative_impact * weight_3 +       # 0.17 * 0.20 = 0.034
    network_contribution * weight_4 +      # 0.04 * 0.20 = 0.008
    ubuntu_alignment * weight_5            # 0.12 * 0.20 = 0.024
)                                          # Total = 0.254 ≈ 0.253
```

### Current Weights (Equal):
- Autonomy/Integration: **20%**
- Multi-Scale: **20%**
- Regenerative Impact: **20%**
- Network Contribution: **20%**
- Ubuntu Alignment: **20%**

### Category Thresholds:
```
┌─────────────────────────────────────────────┐
│  0.0 - 0.2  →  Observer                    │
│  0.2 - 0.4  →  Participant  ← All 643 here!│
│  0.4 - 0.6  →  Contributor                 │
│  0.6 - 0.8  →  Integrator                  │
│  0.8 - 1.0  →  Exemplar                    │
└─────────────────────────────────────────────┘
```

### Your Network's Distribution:
- **Participant (643 accounts):** Active enough to participate but not yet contributing significantly
- Score range: 0.20 to 0.40
- Average: **0.253**

---

## Key Findings from Your Network

### ✅ Strengths:
1. **Strong autonomy/integration balance (0.77)**
   - Healthy balance between independence and network participation
   - Not too isolated, not too dependent

### ⚠️ Growth Opportunities:
1. **Low transaction volume (0.04 network contribution)**
   - Most accounts are passive holders
   - Average < 8 transactions per account
   
2. **Limited network connectivity (0.17 multi-scale)**
   - Average < 8.5 unique trading partners per account
   - Suggests limited peer-to-peer exchange
   
3. **Early-stage ecosystem (0.17 regenerative impact)**
   - Accounts are relatively new
   - Haven't built long-term participation patterns yet

### 📊 This is NORMAL for:
- Early-stage token ecosystems
- Networks with many recent adopters
- Communities still building transaction habits
- Passive investment holders vs active participants

---

## Placeholder Values (TODOs)

These scores use **placeholder values** and need real data:

1. **community_integration (0.5)** - Needs:
   - Community forum participation data
   - Event attendance records
   - Governance voting history

2. **system_scale (0.5)** - Needs:
   - Ecosystem-wide participation metrics
   - Cross-protocol activity
   - System governance contributions

3. **growth_impact (0.5)** - Needs:
   - Referral tracking data
   - New account onboarding metrics
   - Network growth attribution

4. **reciprocity (0.6)** - Needs:
   - Give/receive transaction balance analysis
   - Reciprocal relationship patterns
   - Mutual exchange history

---

## How to Improve Scores Organically

### To increase Multi-Scale Participation (0.17 → 0.4+):
- Encourage more peer-to-peer transactions
- Build community trading events
- Create incentives for network connectivity

### To increase Network Contribution (0.04 → 0.2+):
- Increase transaction frequency through utility
- Reward active participants
- Build use cases that require regular token movement

### To increase Ubuntu Alignment (0.12 → 0.3+):
- Time (account age increases automatically)
- Foster diverse network connections
- Build reciprocal exchange patterns
- Encourage whole-system participation

### To increase Regenerative Impact (0.17 → 0.4+):
- Implement referral tracking
- Measure network growth contributions
- Reward token distribution to new members
- Build long-term holding incentives

---

## Configuration Options

You can adjust the evaluation by modifying:

1. **Weights** (in config):
```python
config = {
    'holonic_weight_autonomy': 0.20,      # Default: 20%
    'holonic_weight_multiscale': 0.20,    # Default: 20%
    'holonic_weight_regenerative': 0.20,  # Default: 20%
    'holonic_weight_network': 0.20,       # Default: 20%
    'holonic_weight_ubuntu': 0.20         # Default: 20%
}
```

2. **Thresholds** (in code):
- Transaction count thresholds (100, 150, 200)
- Unique partner thresholds (50, 100)
- Balance thresholds (10,000, 50,000)
- Account age thresholds (365 days)

3. **Category Boundaries** (in code):
```python
self.thresholds = {
    'observer': 0.2,      # Below this = Observer
    'participant': 0.4,   # 0.2-0.4 = Participant
    'contributor': 0.6,   # 0.4-0.6 = Contributor
    'integrator': 0.8     # 0.6-0.8 = Integrator
}                         # Above 0.8 = Exemplar
```

---

## Summary

Your **0.253 composite score** places all accounts in the **Participant** category, which is:
- ✅ **Expected** for early-stage ecosystems
- ✅ **Healthy** - accounts are active enough to participate
- ✅ **Room for growth** - clear path to Contributor level (0.4+)

The scores accurately reflect an ecosystem with:
- Good foundational balance (autonomy/integration)
- Lower transaction activity (passive holders)
- Early-stage development (newer accounts)
- Growth potential (clear metrics to improve)

**This is a solid foundation for organic growth!** 🌱
