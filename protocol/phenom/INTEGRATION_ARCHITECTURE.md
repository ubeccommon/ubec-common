# Integration Architecture: UBEC Protocols → Phenomenal Schema

**Attribution**: This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## Overview

This document shows how the new **phenomenal schema** integrates with and enhances your **existing UBEC protocol architecture**. Rather than replacing your current system, the phenomenal schema provides a **rich analytical layer** that augments each protocol.

---

## 🎯 Integration Philosophy

### Current Architecture (Existing)
```
┌─────────────────────────────────────────────────────────┐
│              UBEC Protocol Layer                         │
├─────────────────────────────────────────────────────────┤
│  Air     │  Water   │  Earth   │  Fire                  │
│ Gateway  │ Recipro  │  GPI     │  TT                    │
├──────────┴──────────┴──────────┴────────────────────────┤
│  Distribution Manager │ Holonic Evaluator               │
├───────────────────────┴─────────────────────────────────┤
│              Data Synchronizer                           │
├─────────────────────────────────────────────────────────┤
│         Existing ubec_recipro Schema                     │
└─────────────────────────────────────────────────────────┘
```

### Enhanced Architecture (With Phenomenal Schema)
```
┌─────────────────────────────────────────────────────────┐
│         UBEC Protocol Layer (Existing)                   │
│  Operational, Real-time, Transaction Processing          │
├─────────────────────────────────────────────────────────┤
│                         ↕                                │
│              Integration Layer (NEW)                     │
│         Bidirectional Sync & Enrichment                  │
│                         ↕                                │
├─────────────────────────────────────────────────────────┤
│         Phenomenal Schema (NEW)                          │
│  Analytical, Gravitational, Quantum, Ubuntu              │
├─────────────────────────────────────────────────────────┤
│         PostgreSQL (ubec database)                       │
│  Schema: ubec_recipro (existing) + phenomenal (new)      │
└─────────────────────────────────────────────────────────┘
```

**Key Principle**: The phenomenal schema **enriches** your protocols with:
- Network gravity (influence/importance)
- Temporal consciousness (patterns over time)
- Spatial topology (network structure)
- Quantum effects (uncertainty, entanglement)
- Ubuntu metrics (balance across principles)

---

## 📊 Protocol-to-Schema Mapping

### 1. Air Protocol (Gateway / Universal Access) → Phenomenal Diversity

**Current Air Protocol Purpose:**
- Universal access to UBEC ecosystem
- Gateway for onboarding
- Asset discovery and distribution

**Phenomenal Schema Enhancement:**

| Air Protocol Concern | Phenomenal Schema Component | Integration Point |
|---------------------|----------------------------|------------------|
| Universal Access | `assets.ubuntu_principle = 'diversity'` | Tag air assets with diversity |
| Gateway Metrics | `assets.external_horizon->>'gateway_metrics'` | Store access patterns |
| Distribution Reach | `gravitational_mass` for air assets | Measure gateway influence |
| Access Patterns | `intentional_relations` with `relation_type = 'trustline'` | Track who accesses via air |

**Integration Code:**

```python
# core/protocols/air_protocol.py

class AirProtocolEnhanced:
    """Air Protocol with Phenomenal Analytics"""
    
    def __init__(self, db_pool, phenomenal_service):
        self.db_pool = db_pool
        self.phenomenal = phenomenal_service
    
    async def track_gateway_access(self, account_address: str, asset_code: str):
        """Track access through air gateway with phenomenal enrichment"""
        
        # 1. Existing air protocol logic (unchanged)
        await self.process_gateway_transaction(account_address, asset_code)
        
        # 2. NEW: Enrich with phenomenal data
        async with self.db_pool.acquire() as conn:
            # Get or create phenomenal account
            account_id = await self._ensure_phenomenal_account(conn, account_address)
            asset_id = await self._ensure_phenomenal_asset(conn, asset_code)
            
            # Create intentional relation (gateway access)
            await conn.execute("""
                INSERT INTO phenomenal.intentional_relations (
                    from_account_id, asset_id, relation_type,
                    phenomenal_mode, noema, noesis,
                    relation_strength, emerged_at, present_manifestation
                ) VALUES (
                    $1, $2, 'trustline',
                    'fully_present',
                    jsonb_build_object(
                        'intended_object', 'gateway_access',
                        'mode_of_presentation', 'air_protocol',
                        'meaning', jsonb_build_object('access_type', 'universal')
                    ),
                    jsonb_build_object(
                        'act_type', 'trustline',
                        'act_quality', 'desire',
                        'fulfillment_status', 'fulfilled'
                    ),
                    1.0, NOW(),
                    jsonb_build_object('via_protocol', 'air', 'gateway_session', gen_random_uuid())
                )
                ON CONFLICT DO NOTHING
            """, account_id, asset_id)
            
            # Mark asset as air/diversity
            await conn.execute("""
                UPDATE phenomenal.assets
                SET ubuntu_principle = 'diversity',
                    external_horizon = external_horizon || 
                        jsonb_build_object(
                            'air_protocol', jsonb_build_object(
                                'is_gateway', true,
                                'access_count', COALESCE((external_horizon->'air_protocol'->>'access_count')::int, 0) + 1,
                                'last_access', NOW()
                            )
                        )
                WHERE id = $1
            """, asset_id)
    
    async def get_gateway_influence(self, asset_code: str) -> dict:
        """Get gravitational influence of gateway asset"""
        
        async with self.db_pool.acquire() as conn:
            # Query phenomenal schema for gravity metrics
            result = await conn.fetchrow("""
                SELECT 
                    gm.gravitational_mass,
                    gm.inertial_mass,
                    gm.mass_basis,
                    COUNT(DISTINCT ir.from_account_id) as access_count,
                    a.external_horizon->'air_protocol' as air_metrics
                FROM phenomenal.assets a
                LEFT JOIN phenomenal.gravitational_mass gm ON gm.entity_id = a.id 
                    AND gm.entity_type = 'asset'
                LEFT JOIN phenomenal.intentional_relations ir ON ir.asset_id = a.id
                WHERE a.asset_code = $1
                  AND a.ubuntu_principle = 'diversity'
                GROUP BY gm.id, a.id
                ORDER BY gm.calculated_at DESC
                LIMIT 1
            """, asset_code)
            
            return {
                'gravitational_mass': float(result['gravitational_mass'] or 0),
                'gateway_reach': result['access_count'],
                'air_metrics': dict(result['air_metrics'] or {}),
                'influence_level': 'high' if result['gravitational_mass'] > 100 else 'medium' if result['gravitational_mass'] > 10 else 'low'
            }
```

---

### 2. Water Protocol (Reciprocity / Flow) → Phenomenal Reciprocity

**Current Water Protocol Purpose:**
- Track reciprocal exchanges
- Measure flow balance
- Reward mutual support

**Phenomenal Schema Enhancement:**

| Water Protocol Concern | Phenomenal Schema Component | Integration Point |
|------------------------|----------------------------|------------------|
| Reciprocity Score | `intentional_relations.reciprocity_factor` | Direct mapping |
| Flow Patterns | `intentional_relations` with `relation_type = 'payment'` | Track all flows |
| Balance Metrics | `analyze_ubuntu_balance()` function | Calculate reciprocity |
| Flow Velocity | `temporal_horizon` on relations | Track flow speed |
| Flow Networks | `intentional_network` view | Visualize flows |

**Integration Code:**

```python
# core/protocols/water_protocol.py

class WaterProtocolEnhanced:
    """Water Protocol with Phenomenal Flow Analytics"""
    
    async def record_flow(self, from_account: str, to_account: str, 
                          amount: float, asset_code: str):
        """Record flow with phenomenal reciprocity tracking"""
        
        # 1. Existing water protocol logic (unchanged)
        await self.process_reciprocal_transfer(from_account, to_account, amount)
        
        # 2. NEW: Create phenomenal intentional relation
        async with self.db_pool.acquire() as conn:
            from_id = await self._ensure_phenomenal_account(conn, from_account)
            to_id = await self._ensure_phenomenal_account(conn, to_account)
            asset_id = await self._ensure_phenomenal_asset(conn, asset_code)
            
            # Calculate reciprocity factor (has to_account sent to from_account before?)
            reciprocity = await conn.fetchval("""
                SELECT COALESCE(AVG(relation_strength), 0)
                FROM phenomenal.intentional_relations
                WHERE from_account_id = $1 AND to_account_id = $2
                  AND relation_type = 'payment'
            """, to_id, from_id)
            
            # Create flow relation
            await conn.execute("""
                INSERT INTO phenomenal.intentional_relations (
                    from_account_id, to_account_id, asset_id,
                    relation_type, phenomenal_mode,
                    noema, noesis,
                    relation_strength, reciprocity_factor,
                    emerged_at, present_manifestation,
                    temporal_horizon
                ) VALUES (
                    $1, $2, $3,
                    'payment', 'fully_present',
                    jsonb_build_object(
                        'intended_object', 'value_transfer',
                        'amount', $4,
                        'meaning', 'reciprocal_flow'
                    ),
                    jsonb_build_object(
                        'act_type', 'payment',
                        'act_quality', 'reciprocity',
                        'fulfillment_status', 'fulfilled'
                    ),
                    $4 / 1000.0,  -- Normalize strength
                    $5,            -- reciprocity_factor
                    NOW(),
                    jsonb_build_object(
                        'via_protocol', 'water',
                        'amount_usd', $4
                    ),
                    'proximal'  -- Recent flow
                )
            """, from_id, to_id, asset_id, amount, reciprocity)
            
            # Mark asset with water/reciprocity principle
            await conn.execute("""
                UPDATE phenomenal.assets
                SET ubuntu_principle = 'reciprocity'
                WHERE id = $1 AND ubuntu_principle IS NULL
            """, asset_id)
    
    async def analyze_account_reciprocity(self, account_address: str) -> dict:
        """Analyze reciprocity using phenomenal ubuntu balance"""
        
        async with self.db_pool.acquire() as conn:
            account_id = await self._get_phenomenal_account_id(conn, account_address)
            
            # Use phenomenal function for ubuntu analysis
            ubuntu_scores = await conn.fetchval("""
                SELECT phenomenal.analyze_ubuntu_balance($1)
            """, account_id)
            
            # Get detailed flow metrics
            flow_metrics = await conn.fetchrow("""
                SELECT 
                    COUNT(*) FILTER (WHERE from_account_id = $1) as outflows,
                    COUNT(*) FILTER (WHERE to_account_id = $1) as inflows,
                    AVG(reciprocity_factor) as avg_reciprocity,
                    SUM((present_manifestation->>'amount_usd')::float) 
                        FILTER (WHERE from_account_id = $1) as total_sent,
                    SUM((present_manifestation->>'amount_usd')::float) 
                        FILTER (WHERE to_account_id = $1) as total_received
                FROM phenomenal.intentional_relations
                WHERE (from_account_id = $1 OR to_account_id = $1)
                  AND relation_type = 'payment'
                  AND active = TRUE
            """, account_id)
            
            return {
                'ubuntu_reciprocity': ubuntu_scores['reciprocity'],
                'ubuntu_composite': ubuntu_scores['composite'],
                'outflows': flow_metrics['outflows'],
                'inflows': flow_metrics['inflows'],
                'avg_reciprocity': float(flow_metrics['avg_reciprocity'] or 0),
                'balance_ratio': (flow_metrics['total_received'] or 0) / max(flow_metrics['total_sent'] or 1, 1),
                'water_health': 'excellent' if ubuntu_scores['reciprocity'] > 0.8 else 'good' if ubuntu_scores['reciprocity'] > 0.5 else 'needs_improvement'
            }
```

---

### 3. Earth Protocol (Ground / Stability) → Phenomenal Mutualism

**Current Earth Protocol Purpose:**
- Ground/stabilize network
- Measure stability metrics
- Reward long-term participation

**Phenomenal Schema Enhancement:**

| Earth Protocol Concern | Phenomenal Schema Component | Integration Point |
|------------------------|----------------------------|------------------|
| Stability Metrics | `intentional_relations.stability_score` | Direct stability measure |
| Long-term Bonds | `holons` table | Stable communities |
| Mutual Support | `assets.ubuntu_principle = 'mutualism'` | Tag earth assets |
| Inertial Mass | `gravitational_mass.inertial_mass` | Resistance to change |
| Geodesics | `geodesics` table | Stable paths |

**Integration Code:**

```python
# core/protocols/earth_protocol.py

class EarthProtocolEnhanced:
    """Earth Protocol with Phenomenal Stability Analytics"""
    
    async def calculate_stability_score(self, account_address: str) -> dict:
        """Calculate account stability using phenomenal metrics"""
        
        async with self.db_pool.acquire() as conn:
            account_id = await self._get_phenomenal_account_id(conn, account_address)
            
            # Get gravitational inertial mass (resistance to change)
            inertial_mass = await conn.fetchval("""
                SELECT inertial_mass
                FROM phenomenal.gravitational_mass
                WHERE entity_type = 'account' AND entity_id = $1
                ORDER BY calculated_at DESC
                LIMIT 1
            """, account_id)
            
            # Get relation stability scores
            stability_metrics = await conn.fetchrow("""
                SELECT 
                    AVG(stability_score) as avg_stability,
                    COUNT(*) as stable_relations,
                    AVG(EXTRACT(days FROM (NOW() - emerged_at))) as avg_relation_age_days,
                    COUNT(*) FILTER (
                        WHERE EXTRACT(days FROM (NOW() - emerged_at)) > 90
                    ) as long_term_relations
                FROM phenomenal.intentional_relations
                WHERE (from_account_id = $1 OR to_account_id = $1)
                  AND active = TRUE
                  AND stability_score IS NOT NULL
            """, account_id)
            
            # Check if part of stable holon
            holon_membership = await conn.fetchval("""
                SELECT COUNT(*)
                FROM phenomenal.holons
                WHERE $1 = ANY(constituent_accounts)
                  AND integration_score > 0.7
                  AND dissolved_at IS NULL
            """, account_id)
            
            # Calculate composite earth score
            earth_score = (
                (inertial_mass or 0) / 100.0 * 0.3 +
                (stability_metrics['avg_stability'] or 0) * 0.3 +
                min((stability_metrics['avg_relation_age_days'] or 0) / 365.0, 1.0) * 0.2 +
                min((stability_metrics['long_term_relations'] or 0) / 10.0, 1.0) * 0.1 +
                min(holon_membership / 3.0, 1.0) * 0.1
            )
            
            return {
                'earth_score': earth_score,
                'inertial_mass': float(inertial_mass or 0),
                'avg_stability': float(stability_metrics['avg_stability'] or 0),
                'stable_relations': stability_metrics['stable_relations'],
                'avg_relation_age_days': float(stability_metrics['avg_relation_age_days'] or 0),
                'long_term_relations': stability_metrics['long_term_relations'],
                'holon_memberships': holon_membership,
                'stability_level': 'bedrock' if earth_score > 0.8 else 'stable' if earth_score > 0.5 else 'forming'
            }
    
    async def identify_stable_communities(self) -> List[dict]:
        """Identify stable communities using holons"""
        
        async with self.db_pool.acquire() as conn:
            # Query stable holons (earth protocol communities)
            holons = await conn.fetch("""
                SELECT 
                    h.id,
                    h.holon_name,
                    h.autonomy_score,
                    h.integration_score,
                    h.constituent_accounts,
                    h.constituent_assets,
                    h.ubuntu_scores,
                    EXTRACT(days FROM (NOW() - h.emerged_at)) as age_days,
                    ST_Area(h.spatial_region::geography) / 1000000.0 as area_km2
                FROM phenomenal.holons h
                WHERE h.integration_score > 0.7  -- High integration = stable
                  AND h.dissolved_at IS NULL
                  AND EXTRACT(days FROM (NOW() - h.emerged_at)) > 30  -- At least 30 days old
                ORDER BY h.integration_score DESC, h.autonomy_score DESC
                LIMIT 20
            """)
            
            return [
                {
                    'holon_id': h['id'],
                    'name': h['holon_name'],
                    'stability': float(h['integration_score']),
                    'autonomy': float(h['autonomy_score']),
                    'member_count': len(h['constituent_accounts'] or []),
                    'asset_count': len(h['constituent_assets'] or []),
                    'age_days': float(h['age_days']),
                    'ubuntu_balance': dict(h['ubuntu_scores'] or {}),
                    'community_strength': 'strong' if h['integration_score'] > 0.85 else 'moderate'
                }
                for h in holons
            ]
```

---

### 4. Fire Protocol (Transformation) → Phenomenal Regeneration

**Current Fire Protocol Purpose:**
- Track transformative transactions
- Measure network growth
- Incentivize regenerative behavior

**Phenomenal Schema Enhancement:**

| Fire Protocol Concern | Phenomenal Schema Component | Integration Point |
|------------------------|----------------------------|------------------|
| Transformation Events | `transactions` table | Track all transformations |
| State Transitions | `quantum_states` with `possible_transitions` | Model state changes |
| Regeneration Score | `assets.ubuntu_principle = 'regeneration'` | Tag fire assets |
| Energy Levels | `quantum_states.energy_level` | Discrete transformation states |
| Growth Metrics | `analyze_ubuntu_balance()` regeneration score | Measure growth |

**Integration Code:**

```python
# core/protocols/fire_protocol.py

class FireProtocolEnhanced:
    """Fire Protocol with Phenomenal Transformation Analytics"""
    
    async def record_transformation(self, transaction_hash: str, 
                                   account_address: str,
                                   transformation_type: str,
                                   impact_score: float):
        """Record transformative event with phenomenal quantum state"""
        
        async with self.db_pool.acquire() as conn:
            account_id = await self._ensure_phenomenal_account(conn, account_address)
            
            # 1. Record transaction in phenomenal schema
            await conn.execute("""
                INSERT INTO phenomenal.transactions (
                    transaction_hash, ledger_sequence, event_type,
                    source_account_id, ledger_closed_at,
                    temporal_context, operations, operations_count,
                    effects, successful, result_code,
                    network_impact, fee_charged
                ) VALUES (
                    $1, 0, $2,
                    $3, NOW(),
                    jsonb_build_object('transformation_type', $2, 'via_protocol', 'fire'),
                    jsonb_build_array(jsonb_build_object('type', $2, 'impact', $4)),
                    1,
                    jsonb_build_object('transformation_complete', true),
                    TRUE, 'success',
                    jsonb_build_object('regeneration_impact', $4),
                    0
                )
                ON CONFLICT (transaction_hash) DO NOTHING
            """, transaction_hash, transformation_type, account_id, impact_score)
            
            # 2. Update quantum state (transformation = state transition)
            current_state = await conn.fetchrow("""
                SELECT id, energy_level, state_vector
                FROM phenomenal.quantum_states
                WHERE entity_type = 'account' AND entity_id = $1
                ORDER BY state_prepared_at DESC
                LIMIT 1
            """, account_id)
            
            if current_state:
                # Transition to higher energy state (transformation)
                new_energy_level = current_state['energy_level'] + 1
                
                await conn.execute("""
                    INSERT INTO phenomenal.quantum_states (
                        entity_type, entity_id,
                        state_vector, energy_level, energy_value,
                        possible_transitions,
                        state_prepared_at
                    ) VALUES (
                        'account', $1,
                        jsonb_build_object(
                            'basis_states', jsonb_build_array(
                                jsonb_build_object('state', 'transforming', 'amplitude', 1.0, 'probability', 1.0)
                            ),
                            'phase', 0,
                            'coherence', 0.9
                        ),
                        $2,
                        $2 * 10.0,  -- Energy = level * 10
                        jsonb_build_array(
                            jsonb_build_object(
                                'from_level', $2,
                                'to_level', $2 + 1,
                                'transition_probability', $3,
                                'energy_diff', 10.0
                            )
                        ),
                        NOW()
                    )
                """, account_id, new_energy_level, impact_score)
            
            # 3. Update ubuntu regeneration score
            await conn.execute("""
                UPDATE phenomenal.accounts
                SET ubuntu_scores = COALESCE(ubuntu_scores, '{}'::jsonb) ||
                    jsonb_build_object(
                        'regeneration', LEAST(
                            COALESCE((ubuntu_scores->>'regeneration')::float, 0) + $2 / 10.0,
                            1.0
                        ),
                        'last_transformation', NOW()
                    )
                WHERE id = $1
            """, account_id, impact_score)
    
    async def analyze_regeneration_capacity(self, account_address: str) -> dict:
        """Analyze regeneration capacity using quantum states"""
        
        async with self.db_pool.acquire() as conn:
            account_id = await self._get_phenomenal_account_id(conn, account_address)
            
            # Get current quantum state (energy level = transformation capacity)
            quantum_state = await conn.fetchrow("""
                SELECT 
                    energy_level,
                    energy_value,
                    possible_transitions,
                    state_vector->>'coherence' as coherence
                FROM phenomenal.quantum_states
                WHERE entity_type = 'account' AND entity_id = $1
                ORDER BY state_prepared_at DESC
                LIMIT 1
            """, account_id)
            
            # Get transformation history
            transformations = await conn.fetchval("""
                SELECT COUNT(*)
                FROM phenomenal.transactions
                WHERE source_account_id = $1
                  AND event_type LIKE '%transformation%'
                  AND ledger_closed_at > NOW() - INTERVAL '90 days'
            """, account_id)
            
            # Get ubuntu regeneration score
            ubuntu_scores = await conn.fetchval("""
                SELECT analyze_ubuntu_balance($1)
            """, account_id)
            
            # Calculate fire protocol score
            energy_level = quantum_state['energy_level'] if quantum_state else 0
            coherence = float(quantum_state['coherence'] or 0) if quantum_state else 0
            regeneration = ubuntu_scores.get('regeneration', 0)
            
            fire_score = (
                min(energy_level / 10.0, 1.0) * 0.4 +
                coherence * 0.3 +
                regeneration * 0.3
            )
            
            return {
                'fire_score': fire_score,
                'energy_level': energy_level,
                'coherence': coherence,
                'transformations_90d': transformations,
                'regeneration_score': regeneration,
                'transformation_capacity': 'high' if fire_score > 0.7 else 'medium' if fire_score > 0.4 else 'developing',
                'next_transition_probability': float(quantum_state['possible_transitions'][0]['transition_probability']) if quantum_state and quantum_state['possible_transitions'] else 0
            }
```

---

### 5. Distribution Manager → Gravitational Mass & Fields

**Current Distribution Manager Purpose:**
- Track token balances
- Calculate distributions
- Manage allocations

**Phenomenal Schema Enhancement:**

| Distribution Manager Concern | Phenomenal Schema Component | Integration Point |
|------------------------------|----------------------------|------------------|
| Balance Tracking | `gravitational_mass` | Mass = importance for distribution |
| Distribution Priority | `gravitational_fields` | High-mass entities get priority |
| Allocation Fairness | `ubuntu_scores` | Balance across principles |
| Network Position | `spatial_positions` | Geographic/network fairness |
| Influence Zones | `gravitational_fields.field_geometry` | Distribution zones |

**Integration Code:**

```python
# core/distribution/distribution_manager.py

class DistributionManagerEnhanced:
    """Distribution Manager with Gravitational Prioritization"""
    
    async def calculate_distribution_weights(self, asset_code: str) -> List[dict]:
        """Calculate distribution weights using gravitational mass"""
        
        async with self.db_pool.acquire() as conn:
            # Get all eligible accounts with their gravitational mass
            accounts = await conn.fetch("""
                SELECT 
                    a.id,
                    a.account_address,
                    gm.gravitational_mass,
                    gm.inertial_mass,
                    a.ubuntu_scores,
                    sp.position,
                    COUNT(DISTINCT ir.to_account_id) as connections
                FROM phenomenal.accounts a
                LEFT JOIN phenomenal.gravitational_mass gm ON gm.entity_id = a.id 
                    AND gm.entity_type = 'account'
                LEFT JOIN phenomenal.spatial_positions sp ON sp.entity_id = a.id 
                    AND sp.entity_type = 'account'
                LEFT JOIN phenomenal.intentional_relations ir ON ir.from_account_id = a.id
                WHERE a.present_state->>'eligible_for_distribution' = 'true'
                GROUP BY a.id, gm.id, sp.id
                ORDER BY gm.gravitational_mass DESC NULLS LAST
            """)
            
            # Calculate weights
            total_mass = sum(float(a['gravitational_mass'] or 0) for a in accounts)
            
            distribution_list = []
            for account in accounts:
                mass = float(account['gravitational_mass'] or 0)
                ubuntu = dict(account['ubuntu_scores'] or {})
                
                # Weight factors:
                # 1. Gravitational mass (40%) - importance/contribution
                # 2. Ubuntu balance (30%) - fairness across principles
                # 3. Network connectivity (20%) - engagement
                # 4. Spatial diversity (10%) - geographic distribution
                
                mass_weight = (mass / total_mass) if total_mass > 0 else 0
                ubuntu_weight = ubuntu.get('composite', 0.5)
                connectivity_weight = min(account['connections'] / 20.0, 1.0)
                
                composite_weight = (
                    mass_weight * 0.4 +
                    ubuntu_weight * 0.3 +
                    connectivity_weight * 0.2 +
                    0.1  # Base spatial diversity weight
                )
                
                distribution_list.append({
                    'account_address': account['account_address'],
                    'weight': composite_weight,
                    'gravitational_mass': mass,
                    'ubuntu_balance': ubuntu_weight,
                    'connections': account['connections'],
                    'allocation_priority': 'high' if composite_weight > 0.05 else 'medium' if composite_weight > 0.01 else 'low'
                })
            
            # Normalize weights to sum to 1.0
            total_weight = sum(d['weight'] for d in distribution_list)
            if total_weight > 0:
                for d in distribution_list:
                    d['weight'] = d['weight'] / total_weight
            
            return sorted(distribution_list, key=lambda x: x['weight'], reverse=True)
    
    async def get_balance_with_gravity(self, account_address: str) -> dict:
        """Get balance enriched with gravitational context"""
        
        async with self.db_pool.acquire() as conn:
            # Traditional balance (existing logic)
            traditional_balance = await self._get_traditional_balance(account_address)
            
            # Gravitational context (phenomenal)
            account_id = await self._get_phenomenal_account_id(conn, account_address)
            
            gravity_context = await conn.fetchrow("""
                SELECT 
                    gm.gravitational_mass,
                    gm.inertial_mass,
                    gf.field_strength,
                    gf.influence_radius,
                    COUNT(DISTINCT gi.entity2_mass_id) as gravitational_connections
                FROM phenomenal.gravitational_mass gm
                LEFT JOIN phenomenal.gravitational_fields gf ON gf.source_mass_id = gm.id
                LEFT JOIN phenomenal.gravitational_interactions gi ON gi.entity1_mass_id = gm.id
                WHERE gm.entity_type = 'account' AND gm.entity_id = $1
                GROUP BY gm.id, gf.id
                ORDER BY gm.calculated_at DESC
                LIMIT 1
            """, account_id)
            
            return {
                **traditional_balance,  # Existing balance data
                'gravity': {
                    'mass': float(gravity_context['gravitational_mass'] or 0),
                    'influence': float(gravity_context['field_strength'] or 0),
                    'influence_radius': float(gravity_context['influence_radius'] or 0),
                    'connections': gravity_context['gravitational_connections'],
                    'importance_percentile': await self._calculate_percentile(
                        conn, account_id, gravity_context['gravitational_mass']
                    )
                }
            }
```

---

### 6. Holonic Evaluator → Holons Table

**Current Holonic Evaluator Purpose:**
- Evaluate nested structures
- Assess autonomy and integration
- Track collective behavior

**Phenomenal Schema Enhancement:**

| Holonic Evaluator Concern | Phenomenal Schema Component | Integration Point |
|----------------------------|----------------------------|------------------|
| Holon Structure | `holons` table | Direct mapping |
| Autonomy Score | `holons.autonomy_score` | Measure independence |
| Integration Score | `holons.integration_score` | Measure collective strength |
| Constituent Members | `holons.constituent_accounts/assets` | Track membership |
| Emergent Properties | `holons.emergent_properties` | Collective behavior |
| Spatial Extent | `holons.spatial_region` | Geographic footprint |

**Integration Code:**

```python
# core/evaluation/holonic_evaluator.py

class HolonicEvaluatorEnhanced:
    """Holonic Evaluator with Phenomenal Holon Analytics"""
    
    async def create_holon(self, name: str, member_accounts: List[str],
                          holon_type: str = 'collective') -> int:
        """Create holon in phenomenal schema"""
        
        async with self.db_pool.acquire() as conn:
            # Convert addresses to phenomenal account IDs
            account_ids = []
            for address in member_accounts:
                account_id = await self._ensure_phenomenal_account(conn, address)
                account_ids.append(account_id)
            
            # Get assets held by members
            asset_ids = await conn.fetch("""
                SELECT DISTINCT asset_id
                FROM phenomenal.intentional_relations
                WHERE from_account_id = ANY($1)
                  AND asset_id IS NOT NULL
                  AND active = TRUE
            """, account_ids)
            asset_ids = [r['asset_id'] for r in asset_ids]
            
            # Get relations between members
            relation_ids = await conn.fetch("""
                SELECT id
                FROM phenomenal.intentional_relations
                WHERE from_account_id = ANY($1)
                  AND to_account_id = ANY($1)
                  AND active = TRUE
            """, account_ids)
            relation_ids = [r['id'] for r in relation_ids]
            
            # Calculate autonomy (how independent is this group?)
            external_connections = await conn.fetchval("""
                SELECT COUNT(*)
                FROM phenomenal.intentional_relations
                WHERE (from_account_id = ANY($1) AND to_account_id != ALL($1))
                   OR (to_account_id = ANY($1) AND from_account_id != ALL($1))
            """, account_ids)
            
            internal_connections = len(relation_ids)
            autonomy_score = internal_connections / max(internal_connections + external_connections, 1)
            
            # Calculate integration (how unified is this group?)
            integration_score = internal_connections / max(len(account_ids) * (len(account_ids) - 1) / 2, 1)
            integration_score = min(integration_score, 1.0)
            
            # Calculate spatial extent
            spatial_region = await conn.fetchval("""
                SELECT ST_ConvexHull(ST_Collect(network_position))
                FROM phenomenal.accounts
                WHERE id = ANY($1)
                  AND network_position IS NOT NULL
            """, account_ids)
            
            centroid = await conn.fetchval("""
                SELECT ST_Centroid(ST_Collect(network_position))
                FROM phenomenal.accounts
                WHERE id = ANY($1)
                  AND network_position IS NOT NULL
            """, account_ids)
            
            # Calculate Ubuntu scores for holon
            ubuntu_scores_list = await conn.fetch("""
                SELECT analyze_ubuntu_balance(id) as scores
                FROM phenomenal.accounts
                WHERE id = ANY($1)
            """, account_ids)
            
            # Average Ubuntu scores
            avg_ubuntu = {
                'diversity': sum(s['scores']['diversity'] for s in ubuntu_scores_list) / len(ubuntu_scores_list),
                'reciprocity': sum(s['scores']['reciprocity'] for s in ubuntu_scores_list) / len(ubuntu_scores_list),
                'mutualism': sum(s['scores']['mutualism'] for s in ubuntu_scores_list) / len(ubuntu_scores_list),
                'regeneration': sum(s['scores']['regeneration'] for s in ubuntu_scores_list) / len(ubuntu_scores_list)
            }
            
            # Create holon
            holon_id = await conn.fetchval("""
                INSERT INTO phenomenal.holons (
                    holon_name, holon_type,
                    autonomy_score, integration_score,
                    constituent_accounts, constituent_assets, constituent_relations,
                    emergent_properties, collective_behavior,
                    spatial_region, centroid,
                    emerged_at, ubuntu_scores
                ) VALUES (
                    $1, $2,
                    $3, $4,
                    $5, $6, $7,
                    jsonb_build_object(
                        'member_count', $8,
                        'internal_connections', $9,
                        'external_connections', $10
                    ),
                    jsonb_build_object(
                        'cooperation_level', CASE 
                            WHEN $4 > 0.8 THEN 'high'
                            WHEN $4 > 0.5 THEN 'medium'
                            ELSE 'low'
                        END
                    ),
                    $11, $12,
                    NOW(), $13
                ) RETURNING id
            """, name, holon_type,
                autonomy_score, integration_score,
                account_ids, asset_ids, relation_ids,
                len(account_ids), internal_connections, external_connections,
                spatial_region, centroid, avg_ubuntu
            )
            
            return holon_id
    
    async def evaluate_all_holons(self) -> List[dict]:
        """Evaluate all holons with rich phenomenal metrics"""
        
        async with self.db_pool.acquire() as conn:
            holons = await conn.fetch("""
                SELECT 
                    h.id,
                    h.holon_name,
                    h.holon_type,
                    h.autonomy_score,
                    h.integration_score,
                    h.constituent_accounts,
                    h.constituent_assets,
                    h.emergent_properties,
                    h.ubuntu_scores,
                    h.emerged_at,
                    h.dissolved_at,
                    ST_Area(h.spatial_region::geography) / 1000000.0 as area_km2,
                    -- Gravitational mass of holon
                    gm.gravitational_mass,
                    -- Member health
                    AVG(member_gm.gravitational_mass) as avg_member_mass
                FROM phenomenal.holons h
                LEFT JOIN phenomenal.gravitational_mass gm ON gm.entity_id = h.id 
                    AND gm.entity_type = 'holon'
                LEFT JOIN phenomenal.gravitational_mass member_gm 
                    ON member_gm.entity_id = ANY(h.constituent_accounts)
                    AND member_gm.entity_type = 'account'
                WHERE h.dissolved_at IS NULL
                GROUP BY h.id, gm.id
                ORDER BY h.integration_score DESC, h.autonomy_score DESC
            """)
            
            return [
                {
                    'holon_id': h['id'],
                    'name': h['holon_name'],
                    'type': h['holon_type'],
                    'scores': {
                        'autonomy': float(h['autonomy_score']),
                        'integration': float(h['integration_score']),
                        'health': (float(h['autonomy_score']) + float(h['integration_score'])) / 2
                    },
                    'ubuntu': dict(h['ubuntu_scores'] or {}),
                    'members': {
                        'count': len(h['constituent_accounts'] or []),
                        'avg_mass': float(h['avg_member_mass'] or 0)
                    },
                    'gravity': {
                        'collective_mass': float(h['gravitational_mass'] or 0)
                    },
                    'spatial': {
                        'area_km2': float(h['area_km2'] or 0)
                    },
                    'age_days': (datetime.now() - h['emerged_at']).days,
                    'status': 'thriving' if h['integration_score'] > 0.8 else 'stable' if h['integration_score'] > 0.5 else 'forming'
                }
                for h in holons
            ]
```

---

### 7. Data Synchronizer → Bidirectional Sync Service

**Current Data Synchronizer Purpose:**
- Sync Stellar blockchain data
- Update local database
- Maintain consistency

**Phenomenal Schema Enhancement:**

**Integration Code:**

```python
# core/db/UBECDataSynchronizer.py

class UBECDataSynchronizerEnhanced:
    """Enhanced Data Synchronizer with Phenomenal Schema Integration"""
    
    def __init__(self, stellar_client, db_pool, phenomenal_service):
        self.stellar = stellar_client
        self.db_pool = db_pool
        self.phenomenal = phenomenal_service
    
    async def sync_account(self, account_address: str):
        """Sync account to both traditional and phenomenal schemas"""
        
        # 1. Sync to traditional schema (existing logic)
        await self._sync_traditional_account(account_address)
        
        # 2. Sync to phenomenal schema (new)
        stellar_account = await self.stellar.accounts().account_id(account_address).call()
        
        async with self.db_pool.acquire() as conn:
            # Create or update phenomenal account
            account_id = await conn.fetchval("""
                INSERT INTO phenomenal.accounts (
                    account_address,
                    dasein_type,
                    comportment_pattern,
                    holonic_category,
                    thrown_at,
                    facticity,
                    internal_horizon,
                    external_horizon,
                    present_state,
                    network_position
                ) VALUES (
                    $1,
                    'participant',
                    $2,
                    'network_node',
                    $3,
                    jsonb_build_object(
                        'sequence', $4,
                        'subentry_count', $5
                    ),
                    jsonb_build_object(
                        'balances', $6
                    ),
                    jsonb_build_object(
                        'stellar_network', 'mainnet',
                        'home_domain', $7
                    ),
                    jsonb_build_object(
                        'active', true,
                        'last_synced', NOW()
                    ),
                    ST_SetSRID(ST_MakePoint(0, 0), 4326)  -- Will be updated by network embedding
                )
                ON CONFLICT (account_address) DO UPDATE SET
                    present_state = jsonb_build_object('active', true, 'last_synced', NOW()),
                    updated_at = NOW()
                RETURNING id
            """,
                account_address,
                self._infer_comportment(stellar_account),
                stellar_account.get('date_created'),
                stellar_account.get('sequence'),
                stellar_account.get('subentry_count'),
                stellar_account.get('balances', []),
                stellar_account.get('home_domain')
            )
            
            # Sync balances as intentional relations
            for balance in stellar_account.get('balances', []):
                if balance['asset_type'] != 'native':
                    await self._sync_balance_as_relation(
                        conn, account_id, balance
                    )
            
            # Trigger gravitational mass calculation (automatic via trigger)
            # But we can also explicitly recalculate
            await conn.execute("""
                SELECT phenomenal.calculate_gravitational_mass('account', $1)
            """, account_id)
    
    async def sync_transaction(self, tx_hash: str):
        """Sync transaction to both schemas"""
        
        # 1. Sync to traditional schema
        await self._sync_traditional_transaction(tx_hash)
        
        # 2. Sync to phenomenal schema
        stellar_tx = await self.stellar.transactions().transaction(tx_hash).call()
        
        async with self.db_pool.acquire() as conn:
            source_account_id = await self._get_phenomenal_account_id(
                conn, stellar_tx['source_account']
            )
            
            # Determine transformation type for fire protocol
            transformation_type = self._classify_transaction(stellar_tx)
            
            await conn.execute("""
                INSERT INTO phenomenal.transactions (
                    transaction_hash,
                    ledger_sequence,
                    event_type,
                    source_account_id,
                    ledger_closed_at,
                    temporal_context,
                    operations,
                    operations_count,
                    effects,
                    successful,
                    result_code,
                    network_impact,
                    fee_charged,
                    memo_type,
                    memo_value
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
                )
                ON CONFLICT (transaction_hash) DO NOTHING
            """,
                tx_hash,
                stellar_tx['ledger'],
                transformation_type,
                source_account_id,
                stellar_tx['created_at'],
                {
                    'paging_token': stellar_tx.get('paging_token'),
                    'source': stellar_tx.get('source_account')
                },
                stellar_tx.get('operations', []),
                stellar_tx.get('operation_count', 0),
                {},  # Effects would be populated separately
                stellar_tx.get('successful', True),
                stellar_tx.get('result_code'),
                {
                    'protocol': self._detect_protocol(stellar_tx),
                    'transformation_score': self._calculate_transformation_score(stellar_tx)
                },
                int(stellar_tx.get('fee_charged', 0)),
                stellar_tx.get('memo_type'),
                stellar_tx.get('memo')
            )
    
    async def periodic_enrichment(self):
        """Periodically enrich phenomenal schema with calculated metrics"""
        
        async with self.db_pool.acquire() as conn:
            # 1. Recalculate gravitational masses
            await conn.execute("""
                INSERT INTO phenomenal.gravitational_mass (
                    entity_type, entity_id,
                    gravitational_mass, inertial_mass,
                    mass_basis, calculated_at
                )
                SELECT 
                    'account', id,
                    phenomenal.calculate_gravitational_mass('account', id),
                    phenomenal.calculate_gravitational_mass('account', id) * 1.1,
                    jsonb_build_object('method', 'periodic_enrichment'),
                    NOW()
                FROM phenomenal.accounts
                ON CONFLICT (entity_type, entity_id, calculated_at) DO NOTHING
            """)
            
            # 2. Update gravitational interactions
            await self._update_gravitational_interactions(conn)
            
            # 3. Detect and record quantum entanglements
            await self._detect_entanglements(conn)
            
            # 4. Update holons
            await self._update_holons(conn)
            
            # 5. Refresh materialized view
            await conn.execute("""
                REFRESH MATERIALIZED VIEW CONCURRENTLY phenomenal.gravitational_network
            """)
    
    def _detect_protocol(self, tx: dict) -> str:
        """Detect which UBEC protocol this transaction belongs to"""
        
        memo = tx.get('memo', '')
        operations = tx.get('operations', [])
        
        # Protocol detection logic
        if 'gateway' in memo.lower() or any(op.get('type') == 'create_account' for op in operations):
            return 'air'
        elif 'recipro' in memo.lower() or any(op.get('type') == 'payment' for op in operations):
            return 'water'
        elif 'stability' in memo.lower() or any(op.get('type') == 'create_passive_offer' for op in operations):
            return 'earth'
        elif 'transform' in memo.lower() or any(op.get('type') == 'manage_buy_offer' for op in operations):
            return 'fire'
        else:
            return 'unknown'
```

---

## 🔄 Bidirectional Sync Flow

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│          Stellar Blockchain                         │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
        ┌────────────────┐
        │ Data Sync      │
        │ Service        │
        └───┬────────┬───┘
            │        │
            ↓        ↓
┌───────────────┐ ┌──────────────────┐
│ Traditional   │ │ Phenomenal       │
│ Schema        │ │ Schema           │
│ (ubec_recipro)│ │ (phenomenal)     │
│               │ │                  │
│ - Balances    │ │ - Assets         │
│ - Transfers   │ │ - Accounts       │
│ - Offers      │ │ - Relations      │
│               │ │ - Gravity        │
│               │ │ - Quantum States │
└───────────────┘ └──────────────────┘
            │        │
            ↓        ↓
┌─────────────────────────────────────┐
│      Protocol Services               │
│  Air, Water, Earth, Fire             │
│  Distribution, Holonic, Evaluator    │
└─────────────────────────────────────┘
```

---

## 📋 Migration Checklist

### Phase 1: Setup (Day 1)
- [ ] Deploy phenomenal schema to ubec database
- [ ] Verify all tables, views, functions created
- [ ] Grant permissions to application user
- [ ] Run verification script

### Phase 2: Initial Population (Day 2-3)
- [ ] Migrate existing accounts to phenomenal.accounts
- [ ] Migrate existing assets to phenomenal.assets
- [ ] Create initial intentional_relations from balances/transfers
- [ ] Calculate initial gravitational masses

### Phase 3: Protocol Integration (Week 1)
- [ ] Update Air Protocol to write to phenomenal schema
- [ ] Update Water Protocol to track reciprocity
- [ ] Update Earth Protocol to use holons
- [ ] Update Fire Protocol to use quantum states

### Phase 4: Manager Integration (Week 2)
- [ ] Integrate Distribution Manager with gravity
- [ ] Integrate Holonic Evaluator with holons table
- [ ] Update Data Synchronizer for bidirectional sync

### Phase 5: Analytics & Monitoring (Week 3)
- [ ] Set up materialized view refresh schedule
- [ ] Create dashboards using phenomenal views
- [ ] Monitor gravitational network evolution
- [ ] Track Ubuntu balance across protocols

### Phase 6: Optimization (Week 4)
- [ ] Performance tune queries
- [ ] Add protocol-specific indexes
- [ ] Optimize sync frequency
- [ ] Document integration patterns

---

## 🎯 Summary

### What You Get

The phenomenal schema **doesn't replace** your existing UBEC protocols—it **enriches** them with:

1. **Air Protocol** → Diversity tracking + gateway influence measurement
2. **Water Protocol** → Reciprocity scoring + flow visualization
3. **Earth Protocol** → Stability metrics + community detection
4. **Fire Protocol** → Transformation tracking + quantum state modeling
5. **Distribution Manager** → Gravity-based prioritization + fair allocation
6. **Holonic Evaluator** → Rich holon analytics + collective behavior
7. **Data Synchronizer** → Bidirectional sync + automatic enrichment

### Integration Pattern

Every protocol can:
1. **Continue operating** with existing schema (no breaking changes)
2. **Write to phenomenal** schema for rich analytics
3. **Query phenomenal** views for enhanced insights
4. **Use phenomenal** functions for advanced calculations

### Code Changes Required

Minimal! Each protocol adds ~50-100 lines to write phenomenal data alongside existing logic. Data Synchronizer adds bidirectional sync.

---

**Ready to integrate?** Start with the Data Synchronizer enhancement, then add protocols one at a time.

