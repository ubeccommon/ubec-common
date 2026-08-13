# Quick Reference: UBEC Protocol → Phenomenal Schema Mapping

**Attribution**: This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations.

---

## 🎯 One-Page Integration Map

### Protocol Mapping Table

| Your Component | Ubuntu Principle | Phenomenal Tables | Key Metrics | Integration Method |
|----------------|-----------------|-------------------|-------------|-------------------|
| **Air Protocol**<br/>(Gateway) | Diversity | `assets` (ubuntu_principle='diversity')<br/>`intentional_relations` (trustlines)<br/>`gravitational_mass` | - Gateway influence<br/>- Access count<br/>- Reach score | Write gateway events as relations<br/>Tag assets with diversity principle |
| **Water Protocol**<br/>(Reciprocity) | Reciprocity | `intentional_relations` (payments)<br/>`reciprocity_factor` field<br/>`analyze_ubuntu_balance()` | - Reciprocity score<br/>- Flow balance<br/>- Mutual exchanges | Record all flows<br/>Calculate reciprocity factors<br/>Use ubuntu analysis |
| **Earth Protocol**<br/>(Stability) | Mutualism | `holons` table<br/>`gravitational_mass.inertial_mass`<br/>`intentional_relations.stability_score` | - Inertial mass<br/>- Stability score<br/>- Community strength | Create holons for communities<br/>Track long-term relations<br/>Measure resistance to change |
| **Fire Protocol**<br/>(Transformation) | Regeneration | `transactions` table<br/>`quantum_states`<br/>`quantum_states.energy_level` | - Transformation count<br/>- Energy transitions<br/>- Regeneration score | Record transformations<br/>Model as quantum transitions<br/>Track energy levels |
| **Distribution Manager** | All 4 | `gravitational_mass`<br/>`gravitational_fields`<br/>`ubuntu_scores` | - Entity importance<br/>- Influence zones<br/>- Balance fairness | Use mass for weighting<br/>Apply ubuntu balance<br/>Prioritize by gravity |
| **Holonic Evaluator** | Mutualism | `holons` table<br/>`autonomy_score`<br/>`integration_score` | - Autonomy (independence)<br/>- Integration (unity)<br/>- Collective behavior | Direct 1:1 mapping<br/>Rich analytics<br/>Spatial extent tracking |
| **Data Synchronizer** | N/A | All tables<br/>Bidirectional sync | - Sync status<br/>- Data freshness<br/>- Consistency | Sync to both schemas<br/>Periodic enrichment<br/>Auto-calculations |

---

## 🔑 Key Integration Points

### 1. Account Tracking
```sql
-- Traditional: ubec_recipro.accounts
-- Phenomenal: phenomenal.accounts (Dasein - being-in-world)

-- Sync: Every account in traditional → phenomenal.accounts
-- Enrichment: + gravitational_mass, ubuntu_scores, spatial_position
```

### 2. Balance Tracking
```sql
-- Traditional: ubec_recipro.balances
-- Phenomenal: phenomenal.intentional_relations (trustlines)

-- Sync: Every balance → intentional_relation with type='trustline'
-- Enrichment: + reciprocity_factor, relation_strength, phenomenal_mode
```

### 3. Transfer Tracking
```sql
-- Traditional: ubec_recipro.transfers
-- Phenomenal: phenomenal.intentional_relations (payments)

-- Sync: Every transfer → intentional_relation with type='payment'
-- Enrichment: + reciprocity_factor, temporal_horizon, noema/noesis
```

### 4. Asset Tracking
```sql
-- Traditional: ubec_recipro.assets
-- Phenomenal: phenomenal.assets (as phenomena)

-- Sync: Every asset → phenomenal.assets
-- Enrichment: + ubuntu_principle, gravitational_mass, network_position
```

---

## 📊 Data Flow Patterns

### Pattern 1: Write to Both Schemas
```python
async def process_transaction(tx):
    # 1. Write to traditional schema (existing)
    await db.execute("INSERT INTO ubec_recipro.transfers ...")
    
    # 2. Write to phenomenal schema (new)
    await db.execute("INSERT INTO phenomenal.intentional_relations ...")
```

### Pattern 2: Query Phenomenal for Analytics
```python
async def get_account_analysis(account):
    # Use phenomenal for rich analytics
    ubuntu = await db.fetchval(
        "SELECT analyze_ubuntu_balance($1)", account_id
    )
    gravity = await db.fetchval(
        "SELECT gravitational_mass FROM gravitational_mass ..."
    )
    return combined_analysis(ubuntu, gravity)
```

### Pattern 3: Sync Periodically
```python
async def periodic_sync():
    # Sync traditional → phenomenal
    await sync_accounts()
    await sync_balances()
    await sync_transfers()
    
    # Enrich with calculations
    await calculate_all_masses()
    await detect_communities()
    await refresh_materialized_views()
```

---

## 🚀 Quick Start Integration

### Step 1: Choose a Protocol (Start Small)
```bash
# Start with one protocol, e.g., Water (easiest)
# It only requires adding intentional_relations
```

### Step 2: Add Phenomenal Writes
```python
# In your water protocol handler:
class WaterProtocol:
    async def record_payment(self, from_addr, to_addr, amount):
        # Existing logic
        await self.existing_payment_logic(...)
        
        # NEW: Add phenomenal tracking (5 lines)
        await self.phenomenal.create_relation(
            from_addr, to_addr,
            relation_type='payment',
            amount=amount
        )
```

### Step 3: Query for Insights
```python
# Now you can get rich analytics:
reciprocity_score = await phenomenal.analyze_ubuntu_balance(account_id)
network_influence = await phenomenal.get_gravitational_mass(account_id)
```

### Step 4: Repeat for Other Protocols
```bash
# Water ✓ → Air → Earth → Fire
# Each takes ~1 hour to integrate
```

---

## 🎨 Ubuntu Principle Assignment

### How to Tag Assets

| Asset Type | Ubuntu Principle | Reason |
|-----------|-----------------|---------|
| UBEC (Air) | diversity | Gateway, universal access |
| UBECrc (Water) | reciprocity | Reciprocal flows |
| UBECgpi (Earth) | mutualism | Stability, mutual support |
| UBECtt (Fire) | regeneration | Transformation |

### Automatic Tagging
```sql
-- Tag assets automatically based on code
UPDATE phenomenal.assets SET ubuntu_principle = 
    CASE 
        WHEN asset_code LIKE '%UBEC' AND asset_code NOT LIKE '%rc%' THEN 'diversity'
        WHEN asset_code LIKE '%rc%' THEN 'reciprocity'
        WHEN asset_code LIKE '%gpi%' THEN 'mutualism'
        WHEN asset_code LIKE '%tt%' THEN 'regeneration'
        ELSE NULL
    END;
```

---

## 📈 Metrics You Can Now Track

### Air Protocol
- Gateway influence: `SELECT gravitational_mass FROM gravitational_mass WHERE entity_type='asset' AND ubuntu_principle='diversity'`
- Access diversity: `SELECT COUNT(DISTINCT from_account_id) FROM intentional_relations WHERE asset.ubuntu_principle='diversity'`

### Water Protocol
- Reciprocity balance: `SELECT analyze_ubuntu_balance(account_id)->>'reciprocity'`
- Flow patterns: `SELECT * FROM intentional_network WHERE relation_type='payment'`

### Earth Protocol  
- Community stability: `SELECT integration_score FROM holons ORDER BY integration_score DESC`
- Inertial mass: `SELECT inertial_mass FROM gravitational_mass`

### Fire Protocol
- Transformation rate: `SELECT COUNT(*) FROM transactions WHERE event_type='transformation'`
- Energy levels: `SELECT energy_level FROM quantum_states`

### Distribution
- Fair allocation: Use `gravitational_mass` * `ubuntu_composite_score` for weights
- Influence zones: `SELECT * FROM gravitational_fields`

### Holonic
- Community health: `SELECT autonomy_score, integration_score FROM holons`
- Collective behavior: `SELECT emergent_properties FROM holons`

---

## 🔧 Code Snippets

### Create Phenomenal Account
```python
async def ensure_phenomenal_account(conn, address):
    return await conn.fetchval("""
        INSERT INTO phenomenal.accounts (
            account_address, dasein_type, thrown_at,
            internal_horizon, external_horizon, present_state
        ) VALUES (
            $1, 'participant', NOW(),
            '{}'::jsonb, '{}'::jsonb, 
            '{"active": true}'::jsonb
        )
        ON CONFLICT (account_address) DO UPDATE 
        SET updated_at = NOW()
        RETURNING id
    """, address)
```

### Record Flow with Reciprocity
```python
async def record_flow(conn, from_id, to_id, asset_id, amount):
    # Calculate reciprocity
    reciprocity = await conn.fetchval("""
        SELECT COALESCE(AVG(relation_strength), 0)
        FROM phenomenal.intentional_relations
        WHERE from_account_id = $1 AND to_account_id = $2
    """, to_id, from_id)
    
    # Create relation
    await conn.execute("""
        INSERT INTO phenomenal.intentional_relations (
            from_account_id, to_account_id, asset_id,
            relation_type, relation_strength, reciprocity_factor,
            emerged_at, present_manifestation, noema, noesis
        ) VALUES (
            $1, $2, $3, 'payment', $4 / 1000.0, $5,
            NOW(), '{"via": "water"}'::jsonb,
            '{"intended_object": "value_transfer"}'::jsonb,
            '{"act_type": "payment", "act_quality": "reciprocity"}'::jsonb
        )
    """, from_id, to_id, asset_id, amount, reciprocity)
```

### Get Account Insights
```python
async def get_account_insights(conn, account_id):
    return {
        'ubuntu': await conn.fetchval(
            "SELECT analyze_ubuntu_balance($1)", account_id
        ),
        'gravity': await conn.fetchrow("""
            SELECT gravitational_mass, inertial_mass
            FROM phenomenal.gravitational_mass
            WHERE entity_type='account' AND entity_id=$1
            ORDER BY calculated_at DESC LIMIT 1
        """, account_id),
        'prominence': await conn.fetchval(
            "SELECT compute_phenomenal_prominence('account', $1)", 
            account_id
        )
    }
```

---

## 🎯 Success Criteria

### Phase 1: Basic Integration ✓
- [ ] Data Synchronizer writes to phenomenal schema
- [ ] Accounts, assets, relations synced
- [ ] Gravitational masses auto-calculated

### Phase 2: Protocol Enhancement ✓
- [ ] Water protocol tracks reciprocity
- [ ] Air protocol measures influence
- [ ] Earth protocol uses holons
- [ ] Fire protocol tracks transformations

### Phase 3: Analytics ✓
- [ ] Distribution uses gravity for fairness
- [ ] Holonic evaluator uses rich metrics
- [ ] Dashboards show phenomenal insights

### Phase 4: Production ✓
- [ ] All protocols integrated
- [ ] Sync running smoothly
- [ ] Analytics providing value
- [ ] Team using new insights

---

## 💡 Pro Tips

### Tip 1: Start Small
Begin with Water protocol (simplest). Get comfortable with intentional_relations before adding complexity.

### Tip 2: Dual Write Pattern
Always write to traditional schema first (for stability), then phenomenal (for analytics). Never replace, only augment.

### Tip 3: Use Views
Query phenomenal views (like `network_gravity_map`) instead of raw tables for better performance and cleaner code.

### Tip 4: Batch Enrichment
Run gravitational calculations and other enrichments in background jobs, not in request path.

### Tip 5: Monitor Both
Keep monitoring both schemas. Phenomenal enriches but doesn't replace.

---

## 🆘 Common Questions

**Q: Do I need to migrate existing data?**
A: Yes, but incrementally. Start with active accounts, then historical data over time.

**Q: Will this slow down my app?**
A: No. Phenomenal writes are async and non-blocking. Calculations run in triggers/background.

**Q: Can I query both schemas together?**
A: Yes! `SELECT * FROM ubec_recipro.balances JOIN phenomenal.assets ...`

**Q: What if a protocol doesn't fit?**
A: Use the general `transactions` table or `intentional_relations` with custom noema/noesis.

**Q: How often to refresh materialized views?**
A: Every 1 hour in production, 15 min in dev. Adjust based on data freshness needs.

---

## 📞 Next Steps

1. **Read**: [INTEGRATION_ARCHITECTURE.md](computer:///mnt/user-data/outputs/INTEGRATION_ARCHITECTURE.md) for detailed examples
2. **Deploy**: [unified_phenomenological_quantum_schema.sql](computer:///mnt/user-data/outputs/unified_phenomenological_quantum_schema.sql)
3. **Verify**: Run [verify_schema_deployment.py](computer:///mnt/user-data/outputs/verify_schema_deployment.py)
4. **Integrate**: Start with Data Synchronizer, then protocols one by one
5. **Monitor**: Track sync status, data freshness, query performance

---

**Version**: 2.0.0  
**Date**: October 12, 2025  
**Integration Complexity**: Low (minimal code changes, high value)
