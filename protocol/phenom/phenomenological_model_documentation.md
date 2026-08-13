# Phenomenological Stellar Blockchain Data Model
## Comprehensive Design Documentation

**Version:** 1.0.0  
**Date:** October 12, 2025  
**Project:** UBEC (Ubuntu Bioregional Economic Commons)

---

## Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Philosophical Foundations](#2-philosophical-foundations)
3. [Data Model Architecture](#3-data-model-architecture)
4. [Spatial Analysis Capabilities](#4-spatial-analysis-capabilities)
5. [Temporal Phenomenology](#5-temporal-phenomenology)
6. [Implementation Guide](#6-implementation-guide)
7. [Query Examples](#7-query-examples)
8. [Migration from Existing Schema](#8-migration-from-existing-schema)
9. [Performance Considerations](#9-performance-considerations)
10. [Future Enhancements](#10-future-enhancements)

---

## 1. Executive Summary

### Purpose

This database schema models Stellar blockchain assets using **phenomenological principles** that emphasize contextual and relational ontology. Rather than treating blockchain entities as isolated objects with fixed properties, this model represents them as **phenomena** - things as they appear within horizons of meaning, embedded in networks of intentional relations, and unfolding through temporal consciousness.

### Key Innovation

The schema integrates three phenomenological frameworks:

1. **Philosophical Phenomenology** (Husserl, Heidegger, Merleau-Ponty)
   - Intentionality as directedness
   - Internal and external horizons
   - Temporal consciousness (retention/protention)

2. **Physics Phenomenology**
   - Observable manifestations bridging theory and experiment
   - Spatial relationships through network embeddings

3. **Ubuntu Philosophy** (from UBEC project)
   - Diversity, Reciprocity, Mutualism, Regeneration
   - "I am because we are" - relational being

### Core Benefits

- **Contextual Understanding**: Entities exist within horizons of meaning
- **Relational Ontology**: Identity defined through intentional relations
- **Temporal Depth**: Past (retention), present, and future (protention) integrated
- **Spatial Analysis**: Network topology as geometric space using PostGIS
- **Holonic Structure**: Nested wholes reflecting real organizational patterns
- **Ubuntu Integration**: Indigenous wisdom embedded in data structures

---

## 2. Philosophical Foundations

### 2.1 Intentionality (Directedness)

**Concept**: Every conscious act is directed toward an object. In blockchain terms, every account action is directed toward assets or other accounts.

**Implementation**:
```sql
CREATE TABLE intentional_relations (
    -- Subject (who/what is directed)
    from_account_id INTEGER,
    
    -- Object (what is directed toward)
    to_account_id INTEGER,
    asset_id INTEGER,
    
    -- Type of directedness
    relation_type intentional_relation,
    
    -- Noema: The object as intended (what is meant)
    noema JSONB,
    
    -- Noesis: The intending act (how it is meant)
    noesis JSONB
);
```

**Example**: When account A creates a trustline to asset X, this is modeled as an intentional relation of type 'trustline' where A is directed toward X with specific intentions (to receive, to hold, to trade).

### 2.2 Horizons (Internal and External)

**Concept**: Objects appear within horizons - the internal horizon contains the object's intrinsic properties; the external horizon is the background context that gives meaning.

**Implementation**:
```sql
CREATE TABLE assets (
    -- Internal Horizon: Intrinsic properties
    internal_horizon JSONB,  -- {supply, properties, essence}
    
    -- External Horizon: Contextual embedding
    external_horizon JSONB   -- {network_context, market_context, social_context}
);
```

**Example**: 
- **Internal Horizon**: UBEC has 1M total supply, is divisible, has specific issuer
- **External Horizon**: UBEC exists on Stellar mainnet, in a market of 1200+ holders, within the Ubuntu economic commons philosophy

### 2.3 Temporal Consciousness

**Concept**: We experience time not as discrete instants but as a flowing stream where:
- **Retention**: Past is retained in present awareness
- **Primal Impression**: The now
- **Protention**: Future is anticipated in present awareness

**Implementation**:
```sql
-- Past retained in present
CREATE TABLE retentions (
    original_present TIMESTAMP,
    retained_at TIMESTAMP,
    retained_content JSONB,
    retention_clarity DECIMAL  -- Fading of memory
);

-- Future anticipated in present
CREATE TABLE protentions (
    expected_at TIMESTAMP,
    protended_from TIMESTAMP,
    protended_content JSONB,
    expectation_confidence DECIMAL
);
```

**Example**: When analyzing an asset, we don't just see its current state. We see it with awareness of its history (retention) and anticipation of its future development (protention).

### 2.4 Being-in-the-World (Dasein)

**Concept** (Heidegger): Accounts are not isolated subjects but "beings-in-the-world" - always already engaged in practical activities within a shared context.

**Implementation**:
```sql
CREATE TABLE accounts (
    dasein_type VARCHAR(50),        -- Type of being (issuer, trader, holder)
    comportment_pattern VARCHAR(50), -- Practical engagement pattern
    facticity JSONB,                -- Given circumstances/constraints
    primary_intentions intentional_relation[]
);
```

**Example**: An account isn't just an address - it's a participant with specific modes of engagement (trading vs holding), thrown into circumstances (facticity), with characteristic patterns of behavior (comportment).

### 2.5 Holonic Structure

**Concept**: Systems are composed of holons - entities that are simultaneously autonomous wholes AND integrated parts of larger wholes.

**Implementation**:
```sql
CREATE TABLE holons (
    autonomy_score DECIMAL,          -- How independent
    integration_score DECIMAL,       -- How integrated into larger whole
    constituent_accounts INTEGER[],  -- Parts that constitute this whole
    parent_holons INTEGER[]          -- Wholes this is part of
);
```

**Example**: An asset ecosystem (like all UBEC holders) is a holon - it's a meaningful whole with emergent properties, composed of individual accounts, and itself part of the larger Stellar ecosystem.

---

## 3. Data Model Architecture

### 3.1 Core Entity Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                  PHENOMENOLOGICAL LAYER                      │
└─────────────────────────────────────────────────────────────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
      ┌─────▼─────┐ ┌───▼────┐ ┌────▼───────────┐
      │  ASSETS   │ │ACCOUNTS│ │ TRANSACTIONS   │
      │ (Phenomena│ │(Dasein)│ │   (Events)     │
      └─────┬─────┘ └───┬────┘ └────┬───────────┘
            │           │            │
            └───────┬───┴────────────┘
                    │
         ┌──────────▼──────────┐
         │ INTENTIONAL_RELATIONS│
         │   (Directedness)     │
         └──────────┬───────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
   ┌────▼────┐ ┌───▼────┐ ┌───▼─────┐
   │RETENTIONS│ │SPATIAL │ │HOLONS   │
   │(Past)    │ │POSITIONS│ │(Nested  │
   └──────────┘ │(Space)  │ │ Wholes) │
                └─────────┘ └─────────┘
                     │
              ┌──────▼──────┐
              │ PROTENTIONS │
              │  (Future)   │
              └─────────────┘
```

### 3.2 Table Descriptions

#### Core Phenomenological Entities

| Table | Purpose | Philosophical Basis |
|-------|---------|---------------------|
| `assets` | Assets as phenomena (things as they appear) | Husserl's phenomena with internal/external horizons |
| `accounts` | Accounts as situated beings | Heidegger's Dasein (being-in-the-world) |
| `intentional_relations` | Directedness between entities | Husserl's intentionality (noema/noesis) |
| `transactions` | Discrete events in spacetime | Phenomenal events with temporal structure |

#### Temporal Structure

| Table | Purpose | Philosophical Basis |
|-------|---------|---------------------|
| `retentions` | Past states retained in present | Husserl's retention |
| `protentions` | Anticipated future states | Husserl's protention |

#### Spatial Structure

| Table | Purpose | Philosophical Basis |
|-------|---------|---------------------|
| `network_embeddings` | Computed spatial representations | Physics phenomenology |
| `spatial_positions` | Entity positions in network space | Merleau-Ponty's spatiality |
| `geodesics` | Shortest paths through network | Spacetime geodesics |

#### Holonic Structure

| Table | Purpose | Philosophical Basis |
|-------|---------|---------------------|
| `holons` | Nested wholes and parts | Koestler's holarchy / Ubuntu relationality |

### 3.3 Custom Types

```sql
-- How entities are given to awareness
CREATE TYPE phenomenal_mode AS ENUM (
    'fully_present',    -- Directly experienced
    'retained',         -- Held in memory
    'protended',        -- Anticipated
    'co_present',       -- In background
    'implicitly_meant'  -- Referenced but not given
);

-- How entities manifest in practice
CREATE TYPE existence_mode AS ENUM (
    'ready_to_hand',    -- Transparent, practical use
    'present_at_hand',  -- Objectified, theoretical
    'unready_to_hand',  -- Broken, problematic
    'absent'            -- Missing
);

-- Types of directedness
CREATE TYPE intentional_relation AS ENUM (
    'trustline', 'payment', 'offer', 
    'sponsorship', 'authorization', 
    'claimable', 'liquidity_pool'
);
```

---

## 4. Spatial Analysis Capabilities

### 4.1 Network Embedding Philosophy

Traditional databases treat networks as abstract graphs. This model spatializes the network - entities have positions in geometric space that reflect their relational proximity.

**Phenomenological Basis**: Merleau-Ponty's insight that space is not abstract but lived - we experience nearness and distance relationally.

### 4.2 PostGIS Integration

```sql
-- Enable spatial analysis
CREATE EXTENSION postgis;

-- Assets and accounts have positions
ALTER TABLE assets ADD COLUMN network_position GEOMETRY(POINT, 4326);
ALTER TABLE accounts ADD COLUMN network_position GEOMETRY(POINT, 4326);

-- Relations have geometric representation
ALTER TABLE intentional_relations 
    ADD COLUMN relation_line GEOMETRY(LINESTRING, 4326);

-- Spatial indexes for fast queries
CREATE INDEX idx_assets_spatial ON assets USING GIST(network_position);
CREATE INDEX idx_accounts_spatial ON accounts USING GIST(network_position);
```

### 4.3 Spatial Analysis Queries

#### Find accounts near a specific asset (spatial proximity)
```sql
SELECT 
    a.account_address,
    a.comportment_pattern,
    ST_Distance(a.network_position::geography, ast.network_position::geography) AS distance_meters
FROM accounts a
CROSS JOIN assets ast
WHERE ast.asset_code = 'UBEC'
  AND ST_DWithin(
      a.network_position::geography, 
      ast.network_position::geography, 
      5000  -- 5km radius
  )
ORDER BY distance_meters;
```

#### Identify spatial clusters (communities in space)
```sql
SELECT 
    ST_ClusterDBSCAN(network_position, eps := 1000, minpoints := 5) OVER() AS cluster_id,
    account_address,
    holonic_category
FROM accounts
WHERE network_position IS NOT NULL;
```

#### Compute convex hull of an asset's holder community
```sql
SELECT 
    ast.asset_code,
    ST_ConvexHull(ST_Collect(a.network_position)) AS community_hull,
    ST_Area(ST_ConvexHull(ST_Collect(a.network_position))::geography) AS area_sq_meters
FROM assets ast
JOIN intentional_relations ir ON ast.id = ir.asset_id
JOIN accounts a ON ir.from_account_id = a.id
WHERE ir.relation_type = 'trustline'
  AND ir.active = TRUE
GROUP BY ast.id, ast.asset_code;
```

### 4.4 Embedding Methods

The schema supports multiple network embedding approaches:

1. **Node2Vec**: Random walk-based embeddings
2. **GraphSAGE**: Graph neural network embeddings
3. **Spectral Embeddings**: Based on graph Laplacian
4. **Force-directed layouts**: Physics-based positioning

Each embedding is versioned in `network_embeddings` table, allowing temporal comparison of network structure evolution.

---

## 5. Temporal Phenomenology

### 5.1 Three-Part Temporal Structure

Every phenomenological moment has three aspects:

```
PAST ──────────► PRESENT ──────────► FUTURE
(Retained)      (Impressed)         (Protended)
 │                  │                   │
 │                  │                   │
retentions      present_state      protentions
```

### 5.2 Retention System

**Automatic Retention**: When entities are updated, their old states are automatically preserved:

```sql
-- Trigger maintains retentions
CREATE TRIGGER trg_maintain_asset_retentions
    AFTER UPDATE ON assets
    FOR EACH ROW
    EXECUTE FUNCTION maintain_retentions_trigger();
```

**Retention Clarity**: Memories fade over time:

```sql
-- Query recent clear retentions
SELECT * FROM retentions
WHERE retention_clarity > 0.7
  AND temporal_distance < INTERVAL '30 days'
ORDER BY retained_at DESC;
```

### 5.3 Protention System

**Anticipation Tracking**: Record expected future states:

```sql
-- Create anticipation that UBEC will have 2000 holders in 90 days
INSERT INTO protentions (
    entity_type, entity_id,
    protended_from, expected_at,
    protended_content,
    expectation_confidence,
    protention_type
) VALUES (
    'asset', (SELECT id FROM assets WHERE asset_code = 'UBEC'),
    NOW(), NOW() + INTERVAL '90 days',
    '{"holder_count": 2000, "daily_volume": 75000}'::jsonb,
    0.75,
    'near'
);
```

**Fulfillment Analysis**: Check if anticipations came true:

```sql
-- Analyze protention accuracy
SELECT 
    p.entity_type,
    p.expected_at,
    p.protended_content,
    p.expectation_confidence,
    p.fulfilled,
    p.fulfillment_degree,
    CASE 
        WHEN p.fulfilled THEN 'Manifested'
        WHEN p.expected_at < NOW() AND p.fulfilled IS NULL THEN 'Failed'
        ELSE 'Pending'
    END AS status
FROM protentions p
WHERE entity_type = 'asset'
ORDER BY expected_at;
```

### 5.4 Temporal Consciousness View

```sql
-- View the entire temporal stream
SELECT * FROM temporal_consciousness
WHERE entity_id = (SELECT id FROM assets WHERE asset_code = 'UBEC')
ORDER BY consciousness_now DESC, temporal_mode;
```

This view unifies:
- **Retentions**: What was (past states)
- **Present**: What is (current state in assets/accounts tables)
- **Protentions**: What is anticipated (future states)

---

## 6. Implementation Guide

### 6.1 Prerequisites

```bash
# Install PostgreSQL 15+
sudo apt install postgresql-15 postgresql-contrib-15

# Install PostGIS
sudo apt install postgresql-15-postgis-3

# Install Python spatial libraries
pip install psycopg2-binary geoalchemy2 shapely networkx
```

### 6.2 Database Setup

```bash
# Create database
createdb stellar_phenomenal

# Run schema
psql -d stellar_phenomenal -f phenomenological_stellar_schema.sql
```

### 6.3 Loading Stellar Data

#### Step 1: Extract Stellar Assets

```python
import asyncio
from stellar_sdk import ServerAsync, AiohttpClient
import asyncpg

async def load_stellar_assets():
    server = ServerAsync(horizon_url="https://horizon.stellar.org")
    conn = await asyncpg.connect(
        host='localhost',
        database='stellar_phenomenal',
        user='postgres'
    )
    
    # Fetch assets from Stellar (example: UBEC family)
    assets_to_load = [
        ('UBEC', 'GXXXXX...'),
        ('UBECrc', 'GXXXXX...'),
        ('UBECgpi', 'GXXXXX...'),
        ('UBECtt', 'GXXXXX...')
    ]
    
    for asset_code, issuer in assets_to_load:
        # Get asset details from Stellar
        issuer_account = await server.accounts().account_id(issuer).call()
        
        # Determine Ubuntu principle
        ubuntu_map = {
            'UBEC': 'diversity',
            'UBECrc': 'reciprocity',
            'UBECgpi': 'mutualism',
            'UBECtt': 'regeneration'
        }
        
        # Insert into phenomenological model
        await conn.execute("""
            INSERT INTO phenomenal.assets (
                asset_code, issuer_address, ubuntu_principle,
                phenomenal_mode, existence_mode,
                genesis_at, internal_horizon, external_horizon, present_state
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (asset_code, issuer_address) DO NOTHING
        """, 
            asset_code, issuer,
            ubuntu_map.get(asset_code, 'diversity'),
            'fully_present', 'ready_to_hand',
            datetime.now(), {}, {}, {}
        )
    
    await server.close()
    await conn.close()

# Run
asyncio.run(load_stellar_assets())
```

#### Step 2: Load Accounts and Relations

```python
async def load_stellar_accounts_and_relations(asset_code, issuer):
    server = ServerAsync(horizon_url="https://horizon.stellar.org")
    conn = await asyncpg.connect(
        host='localhost',
        database='stellar_phenomenal',
        user='postgres'
    )
    
    # Get all accounts holding this asset
    accounts = server.accounts() \
        .for_asset(f"{asset_code}:{issuer}") \
        .limit(200)
    
    async for account in accounts.call():
        account_id = account['account_id']
        
        # Insert account as Dasein
        account_db_id = await conn.fetchval("""
            INSERT INTO phenomenal.accounts (
                account_address, dasein_type, comportment_pattern,
                thrown_at, internal_horizon, external_horizon, present_state
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (account_address) DO UPDATE
                SET updated_at = NOW()
            RETURNING id
        """, 
            account_id, 'participant', 'holder',
            account.get('created_at'), {}, {}, {}
        )
        
        # Get asset DB id
        asset_db_id = await conn.fetchval("""
            SELECT id FROM phenomenal.assets 
            WHERE asset_code = $1 AND issuer_address = $2
        """, asset_code, issuer)
        
        # Create intentional relation (trustline)
        await conn.execute("""
            INSERT INTO phenomenal.intentional_relations (
                from_account_id, asset_id, relation_type,
                phenomenal_mode, noema, noesis,
                emerged_at, present_manifestation
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT DO NOTHING
        """,
            account_db_id, asset_db_id, 'trustline',
            'fully_present', 
            {'intended_object': {'asset': asset_code}},
            {'act_type': 'trustline', 'act_quality': 'belief'},
            datetime.now(), {}
        )
    
    await server.close()
    await conn.close()
```

#### Step 3: Compute Network Embedding

```python
import networkx as nx
from node2vec import Node2Vec

async def compute_network_embedding():
    conn = await asyncpg.connect(
        host='localhost',
        database='stellar_phenomenal',
        user='postgres'
    )
    
    # Build networkx graph from intentional_relations
    relations = await conn.fetch("""
        SELECT from_account_id, to_account_id, relation_strength
        FROM phenomenal.intentional_relations
        WHERE active = TRUE AND to_account_id IS NOT NULL
    """)
    
    G = nx.DiGraph()
    for rel in relations:
        G.add_edge(
            rel['from_account_id'], 
            rel['to_account_id'],
            weight=float(rel['relation_strength']) if rel['relation_strength'] else 1.0
        )
    
    # Compute Node2Vec embedding
    node2vec = Node2Vec(G, dimensions=2, walk_length=10, num_walks=100)
    model = node2vec.fit()
    
    # Create embedding record
    embedding_id = await conn.fetchval("""
        INSERT INTO phenomenal.network_embeddings (
            embedding_method, dimensions, parameters, valid_from
        ) VALUES ($1, $2, $3, $4)
        RETURNING id
    """, 'node2vec', 2, {'walk_length': 10, 'num_walks': 100}, datetime.now())
    
    # Store positions
    for node_id in G.nodes():
        vector = model.wv[str(node_id)]
        
        # Convert to PostGIS point (normalize to lat/lon range)
        lat = (vector[0] - vector[0].min()) / (vector[0].max() - vector[0].min()) * 180 - 90
        lon = (vector[1] - vector[1].min()) / (vector[1].max() - vector[1].min()) * 360 - 180
        
        await conn.execute("""
            INSERT INTO phenomenal.spatial_positions (
                embedding_id, entity_type, entity_id,
                position, coordinates
            ) VALUES ($1, $2, $3, ST_SetSRID(ST_MakePoint($4, $5), 4326), $6)
        """, 
            embedding_id, 'account', node_id,
            lon, lat, [float(v) for v in vector]
        )
    
    await conn.close()
```

### 6.4 Application Integration

```python
# Example: Query spatially proximate accounts for an asset
async def find_nearby_holders(asset_code, radius_km=5):
    conn = await asyncpg.connect(
        host='localhost',
        database='stellar_phenomenal',
        user='postgres'
    )
    
    results = await conn.fetch("""
        SELECT 
            a.account_address,
            a.comportment_pattern,
            ST_Distance(
                a.network_position::geography,
                ast.network_position::geography
            ) / 1000.0 AS distance_km
        FROM phenomenal.accounts a
        CROSS JOIN phenomenal.assets ast
        WHERE ast.asset_code = $1
          AND ST_DWithin(
              a.network_position::geography,
              ast.network_position::geography,
              $2 * 1000
          )
        ORDER BY distance_km
    """, asset_code, radius_km)
    
    await conn.close()
    return results
```

---

## 7. Query Examples

### 7.1 Phenomenological Queries

#### Query 1: Find assets by existence mode
```sql
-- Find assets that are practically engaged with (ready-to-hand)
SELECT asset_code, issuer_address, phenomenal_mode
FROM phenomenal.assets
WHERE existence_mode = 'ready_to_hand'
  AND phenomenal_mode = 'fully_present';
```

#### Query 2: Analyze intentional network
```sql
-- View all active directedness (intentional relations)
SELECT * FROM phenomenal.intentional_network
WHERE relation_strength > 0.5
ORDER BY relation_strength DESC;
```

#### Query 3: Temporal consciousness stream
```sql
-- View temporal stream for UBEC asset
SELECT 
    temporal_mode,
    temporal_reference,
    consciousness_now,
    phenomenal_clarity,
    content->>'holder_count' AS holders
FROM phenomenal.temporal_consciousness
WHERE entity_type = 'asset'
  AND entity_id = (SELECT id FROM phenomenal.assets WHERE asset_code = 'UBEC')
ORDER BY consciousness_now DESC;
```

### 7.2 Spatial Queries

#### Query 4: Compute account centrality
```sql
-- Find most central accounts (phenomenal prominence)
SELECT 
    a.account_address,
    phenomenal.compute_phenomenal_prominence('account', a.id) AS centrality
FROM phenomenal.accounts a
ORDER BY (centrality->>'degree_centrality')::decimal DESC
LIMIT 10;
```

#### Query 5: Identify spatial clusters
```sql
-- Find tightly-knit communities
SELECT 
    cluster_id,
    COUNT(*) AS member_count,
    array_agg(account_address) AS members,
    ST_ConvexHull(ST_Collect(network_position)) AS spatial_extent
FROM (
    SELECT 
        ST_ClusterDBSCAN(network_position, eps := 2000, minpoints := 3) OVER() AS cluster_id,
        account_address,
        network_position
    FROM phenomenal.accounts
    WHERE network_position IS NOT NULL
) clustered
WHERE cluster_id IS NOT NULL
GROUP BY cluster_id
ORDER BY member_count DESC;
```

#### Query 6: Shortest path between accounts
```sql
-- Find geodesic (shortest path) between two accounts
SELECT 
    from_address,
    to_address,
    path_length,
    weighted_distance,
    ST_AsText(path_line) AS path_geometry
FROM phenomenal.geodesics g
JOIN phenomenal.accounts a1 ON g.from_account_id = a1.id
JOIN phenomenal.accounts a2 ON g.to_account_id = a2.id
WHERE from_address = 'GXXXX...' AND to_address = 'GYYYY...';
```

### 7.3 Ubuntu Analysis Queries

#### Query 7: Analyze Ubuntu balance
```sql
-- Assess Ubuntu principle balance for an account
SELECT 
    account_address,
    phenomenal.analyze_ubuntu_balance(id) AS ubuntu_scores
FROM phenomenal.accounts
WHERE account_address = 'GXXXXX...';
```

#### Query 8: Compare Ubuntu principles across asset types
```sql
-- Compare Ubuntu characteristics by asset element
SELECT 
    ubuntu_principle,
    COUNT(*) AS asset_count,
    AVG((present_state->>'daily_volume')::decimal) AS avg_daily_volume,
    SUM((internal_horizon->'supply'->>'circulating')::decimal) AS total_circulation
FROM phenomenal.assets
WHERE ubuntu_principle IS NOT NULL
GROUP BY ubuntu_principle
ORDER BY ubuntu_principle;
```

### 7.4 Holonic Queries

#### Query 9: Identify holons (emergent communities)
```sql
-- Find tightly integrated communities (holons)
SELECT 
    holon_name,
    autonomy_score,
    integration_score,
    array_length(constituent_accounts, 1) AS member_count,
    ST_Area(spatial_region::geography) / 1000000.0 AS area_sq_km
FROM phenomenal.holons
WHERE dissolved_at IS NULL
  AND integration_score > 0.7
ORDER BY integration_score DESC;
```

#### Query 10: Holarchical relationships
```sql
-- View nested structure (holons containing holons)
WITH RECURSIVE holon_tree AS (
    -- Base case: top-level holons
    SELECT 
        id, holon_name, parent_holons, 
        1 AS level
    FROM phenomenal.holons
    WHERE parent_holons IS NULL OR parent_holons = '{}'
    
    UNION ALL
    
    -- Recursive case: child holons
    SELECT 
        h.id, h.holon_name, h.parent_holons,
        ht.level + 1
    FROM phenomenal.holons h
    JOIN holon_tree ht ON h.id = ANY(ht.parent_holons)
)
SELECT 
    repeat('  ', level - 1) || holon_name AS hierarchy,
    level
FROM holon_tree
ORDER BY level, holon_name;
```

---

## 8. Migration from Existing Schema

### 8.1 Mapping Existing UBEC Schema to Phenomenological Model

Your existing `ubec_main` schema can be mapped to the new phenomenological model:

| Existing Table | Maps To | Transformation |
|----------------|---------|----------------|
| `stellar_accounts` | `phenomenal.accounts` | Add Dasein properties, comportment |
| `stellar_transactions` | `phenomenal.transactions` | Add temporal consciousness, spatial context |
| `stellar_operations` | `phenomenal.intentional_relations` | Reframe as intentional directedness |
| `account_balances` | `phenomenal.intentional_relations` | Trustline relations with asset |
| `ubec_holonic_metrics` | `phenomenal.holons` + Ubuntu scores | Preserve holonic assessments |

### 8.2 Migration Script

```sql
-- Migration from ubec_main to phenomenal schema

-- Step 1: Migrate assets
INSERT INTO phenomenal.assets (
    asset_code, issuer_address, ubuntu_principle,
    genesis_at, internal_horizon, external_horizon, present_state,
    phenomenal_mode, existence_mode
)
SELECT DISTINCT
    -- Assuming assets are derived from balances/operations
    COALESCE(asset_code::TEXT, 'UNKNOWN'),
    asset_issuer,
    -- Map asset_code to Ubuntu principle
    CASE 
        WHEN asset_code::TEXT = 'UBEC' THEN 'diversity'::ubuntu_principle
        WHEN asset_code::TEXT = 'UBECrc' THEN 'reciprocity'::ubuntu_principle
        WHEN asset_code::TEXT = 'UBECgpi' THEN 'mutualism'::ubuntu_principle
        WHEN asset_code::TEXT = 'UBECtt' THEN 'regeneration'::ubuntu_principle
        ELSE NULL
    END,
    NOW() - INTERVAL '1 year',  -- Approximate genesis
    '{}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb,
    'fully_present'::phenomenal_mode,
    'ready_to_hand'::existence_mode
FROM ubec_main.account_balances
WHERE asset_code IS NOT NULL AND asset_issuer IS NOT NULL
ON CONFLICT (asset_code, issuer_address) DO NOTHING;

-- Step 2: Migrate accounts as Dasein
INSERT INTO phenomenal.accounts (
    account_address, dasein_type, comportment_pattern,
    thrown_at, internal_horizon, external_horizon, present_state
)
SELECT 
    account_id,
    'participant' AS dasein_type,
    -- Infer comportment from activity patterns
    CASE 
        WHEN home_domain IS NOT NULL THEN 'issuer'
        ELSE 'holder'
    END AS comportment_pattern,
    COALESCE(created_at, NOW()) AS thrown_at,
    jsonb_build_object(
        'sequence', sequence,
        'subentry_count', subentry_count,
        'home_domain', home_domain
    ) AS internal_horizon,
    '{}'::jsonb AS external_horizon,
    jsonb_build_object(
        'balances_count', (SELECT COUNT(*) FROM ubec_main.account_balances ab WHERE ab.account_id = sa.account_id)
    ) AS present_state
FROM ubec_main.stellar_accounts sa
ON CONFLICT (account_address) DO NOTHING;

-- Step 3: Create intentional relations from balances (trustlines)
INSERT INTO phenomenal.intentional_relations (
    from_account_id, asset_id, relation_type,
    phenomenal_mode, noema, noesis,
    relation_strength, emerged_at, present_manifestation
)
SELECT 
    acc.id AS from_account_id,
    ast.id AS asset_id,
    'trustline'::intentional_relation AS relation_type,
    'fully_present'::phenomenal_mode,
    jsonb_build_object(
        'intended_object', jsonb_build_object(
            'asset', ab.asset_code,
            'balance', ab.balance_amount
        )
    ) AS noema,
    jsonb_build_object(
        'act_type', 'trustline',
        'act_quality', 'belief'
    ) AS noesis,
    -- Strength based on balance amount (normalized)
    LEAST(ab.balance_amount / 1000.0, 1.0) AS relation_strength,
    ab.created_at AS emerged_at,
    jsonb_build_object(
        'current_balance', ab.balance_amount,
        'authorized', ab.is_authorized
    ) AS present_manifestation
FROM ubec_main.account_balances ab
JOIN phenomenal.accounts acc ON ab.account_id = acc.account_address
JOIN phenomenal.assets ast ON ab.asset_code::TEXT = ast.asset_code AND ab.asset_issuer = ast.issuer_address
WHERE ab.asset_code IS NOT NULL
ON CONFLICT DO NOTHING;

-- Step 4: Create payment relations from transactions
INSERT INTO phenomenal.intentional_relations (
    from_account_id, to_account_id, asset_id, relation_type,
    phenomenal_mode, noema, noesis,
    relation_strength, emerged_at, present_manifestation
)
SELECT 
    acc_from.id AS from_account_id,
    acc_to.id AS to_account_id,
    ast.id AS asset_id,
    'payment'::intentional_relation AS relation_type,
    'fully_present'::phenomenal_mode,
    jsonb_build_object(
        'intended_object', jsonb_build_object(
            'amount', op.amount,
            'asset', op.asset_code
        )
    ) AS noema,
    jsonb_build_object(
        'act_type', 'payment',
        'act_quality', 'desire'
    ) AS noesis,
    -- Strength based on amount
    LEAST(op.amount / 100.0, 1.0) AS relation_strength,
    op.created_at AS emerged_at,
    jsonb_build_object(
        'transaction_hash', op.transaction_hash
    ) AS present_manifestation
FROM ubec_main.stellar_operations op
JOIN phenomenal.accounts acc_from ON op.from_account = acc_from.account_address
JOIN phenomenal.accounts acc_to ON op.to_account = acc_to.account_address
LEFT JOIN phenomenal.assets ast ON op.asset_code::TEXT = ast.asset_code AND op.asset_issuer = ast.issuer_address
WHERE op.type = 'payment'
  AND op.from_account IS NOT NULL
  AND op.to_account IS NOT NULL
ON CONFLICT DO NOTHING;
```

### 8.3 Validation Queries

After migration, validate data integrity:

```sql
-- Count entities migrated
SELECT 
    'Assets' AS entity, COUNT(*) AS count FROM phenomenal.assets
UNION ALL
SELECT 
    'Accounts', COUNT(*) FROM phenomenal.accounts
UNION ALL
SELECT 
    'Relations', COUNT(*) FROM phenomenal.intentional_relations;

-- Verify Ubuntu principle distribution
SELECT ubuntu_principle, COUNT(*)
FROM phenomenal.assets
WHERE ubuntu_principle IS NOT NULL
GROUP BY ubuntu_principle;

-- Check intentional relations types
SELECT relation_type, COUNT(*)
FROM phenomenal.intentional_relations
WHERE active = TRUE
GROUP BY relation_type;
```

---

## 9. Performance Considerations

### 9.1 Indexing Strategy

The schema includes comprehensive indexes:

```sql
-- Phenomenal mode and existence queries
CREATE INDEX idx_assets_phenomenal ON assets(phenomenal_mode, existence_mode);

-- Spatial queries (GIST indexes)
CREATE INDEX idx_assets_spatial ON assets USING GIST(network_position);
CREATE INDEX idx_relations_spatial ON intentional_relations USING GIST(relation_line);

-- Temporal queries
CREATE INDEX idx_retentions_temporal ON retentions(original_present, retained_at);
CREATE INDEX idx_protentions_temporal ON protentions(protended_from, expected_at);

-- JSON queries (GIN indexes)
CREATE INDEX idx_assets_internal_horizon ON assets USING GIN(internal_horizon);
CREATE INDEX idx_relations_noema ON intentional_relations USING GIN(noema);
```

### 9.2 Query Optimization

#### Use Materialized Views for Complex Aggregations

```sql
CREATE MATERIALIZED VIEW phenomenal.ubuntu_scores_summary AS
SELECT 
    a.id AS account_id,
    a.account_address,
    phenomenal.analyze_ubuntu_balance(a.id) AS ubuntu_scores,
    COUNT(DISTINCT ir.asset_id) AS asset_diversity,
    AVG(ir.relation_strength) AS avg_relation_strength
FROM phenomenal.accounts a
LEFT JOIN phenomenal.intentional_relations ir ON a.id = ir.from_account_id
WHERE ir.active = TRUE
GROUP BY a.id, a.account_address;

-- Refresh periodically
REFRESH MATERIALIZED VIEW phenomenal.ubuntu_scores_summary;
```

#### Partition Large Tables

```sql
-- Partition transactions by time
CREATE TABLE phenomenal.transactions_2025 PARTITION OF phenomenal.transactions
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE phenomenal.transactions_2026 PARTITION OF phenomenal.transactions
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
```

### 9.3 Memory and Storage

- **Retentions**: Can grow large. Consider:
  - Archiving retentions older than 1 year
  - Reducing `retention_clarity` over time
  - Purging retentions with clarity < 0.1

- **Spatial Positions**: Multiple embeddings increase storage:
  - Keep only 2-3 most recent embeddings
  - Archive old embeddings to separate table

### 9.4 Recommended Configuration

```sql
-- PostgreSQL configuration for spatial + temporal queries
-- Add to postgresql.conf:

shared_buffers = 256MB              -- Or 25% of RAM
effective_cache_size = 1GB          -- Or 50% of RAM
work_mem = 64MB                     -- For complex spatial queries
maintenance_work_mem = 256MB        -- For index creation
random_page_cost = 1.1              -- For SSD storage

-- PostGIS specific
postgis.gdal_enabled_drivers = 'ENABLE_ALL'
postgis.enable_outdb_rasters = True
```

---

## 10. Future Enhancements

### 10.1 Machine Learning Integration

```sql
-- Add predictions from ML models
ALTER TABLE phenomenal.protentions 
    ADD COLUMN ml_model_name VARCHAR(100),
    ADD COLUMN ml_model_version VARCHAR(50),
    ADD COLUMN ml_features JSONB;

-- Store model metadata
CREATE TABLE phenomenal.ml_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    architecture VARCHAR(100),
    training_date TIMESTAMP WITH TIME ZONE,
    performance_metrics JSONB,
    feature_importance JSONB
);
```

### 10.2 Real-time Event Processing

```sql
-- Add event stream table for real-time updates
CREATE TABLE phenomenal.event_stream (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    event_data JSONB NOT NULL,
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    processed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_event_stream_unprocessed 
    ON phenomenal.event_stream(occurred_at) 
    WHERE processed = FALSE;
```

### 10.3 Advanced Spatial Analysis

```sql
-- Voronoi diagrams (territories)
CREATE OR REPLACE FUNCTION phenomenal.compute_voronoi_territories()
RETURNS TABLE (
    account_id INTEGER,
    territory GEOMETRY
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id,
        ST_VoronoiPolygons(ST_Collect(a.network_position))
    FROM phenomenal.accounts a
    WHERE a.network_position IS NOT NULL
    GROUP BY a.id;
END;
$$ LANGUAGE plpgsql;

-- Heatmaps (density surfaces)
CREATE OR REPLACE FUNCTION phenomenal.compute_activity_heatmap(
    p_resolution INTEGER DEFAULT 100
)
RETURNS TABLE (
    cell_geom GEOMETRY,
    activity_density DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    WITH grid AS (
        SELECT ST_SquareGrid(p_resolution, ST_Extent(network_position)) AS cell
        FROM phenomenal.accounts
    ),
    counts AS (
        SELECT 
            g.cell,
            COUNT(a.id) AS account_count
        FROM grid g
        LEFT JOIN phenomenal.accounts a 
            ON ST_Within(a.network_position, g.cell)
        GROUP BY g.cell
    )
    SELECT cell, account_count::DECIMAL / p_resolution AS density
    FROM counts;
END;
$$ LANGUAGE plpgsql;
```

### 10.4 Blockchain-Specific Enhancements

```sql
-- Smart contract interactions
CREATE TABLE phenomenal.contract_interactions (
    id BIGSERIAL PRIMARY KEY,
    contract_address VARCHAR(56) NOT NULL,
    account_id INTEGER REFERENCES phenomenal.accounts(id),
    interaction_type VARCHAR(50) NOT NULL,
    parameters JSONB,
    result JSONB,
    gas_used BIGINT,
    executed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Phenomenological framing
    intentional_content JSONB,  -- What was meant by this interaction
    fulfillment_status VARCHAR(50)
);

-- NFT ontology
CREATE TABLE phenomenal.nft_phenomena (
    id BIGSERIAL PRIMARY KEY,
    contract_address VARCHAR(56) NOT NULL,
    token_id VARCHAR(255) NOT NULL,
    owner_account_id INTEGER REFERENCES phenomenal.accounts(id),
    
    -- NFT as phenomenon
    phenomenal_mode phenomenal_mode NOT NULL,
    internal_horizon JSONB,  -- Metadata, properties
    external_horizon JSONB,  -- Cultural context, provenance
    
    -- Temporal
    minted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    owned_since TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(contract_address, token_id)
);
```

### 10.5 Multi-Chain Support

```sql
-- Cross-chain bridges as phenomenal connections
CREATE TABLE phenomenal.cross_chain_bridges (
    id BIGSERIAL PRIMARY KEY,
    source_chain VARCHAR(50) NOT NULL,
    dest_chain VARCHAR(50) NOT NULL,
    bridge_type VARCHAR(50) NOT NULL,
    
    -- Spatial representation
    bridge_line GEOMETRY(LINESTRING, 4326),
    
    -- Intentional structure
    bridged_relations BIGINT[],  -- References to intentional_relations
    
    active BOOLEAN NOT NULL DEFAULT TRUE
);
```

---

## Conclusion

This phenomenological data model represents a paradigm shift in how we conceptualize blockchain data. Rather than a static ledger of isolated transactions, it models the blockchain as a living, temporally-unfolding, spatially-embedded network of intentional relations between situated beings.

**Key Philosophical Contributions:**

1. **Intentionality**: Relations are primary, not secondary properties
2. **Temporality**: Past is retained, future is protended - not just "now"
3. **Spatiality**: Network has geometric structure revealing proximity and distance
4. **Holonomy**: Nested wholes reflect real organizational patterns
5. **Ubuntu**: Relational being - "I am because we are"

**Practical Benefits:**

- Richer analytics through contextual queries
- Spatial clustering and community detection
- Temporal prediction through protention tracking
- Holonic analysis of emergent structures
- Ubuntu principle assessment

The schema is production-ready, extensively indexed, and designed for integration with existing Stellar data sources. It honors the UBEC project's philosophical foundations while providing concrete technical capabilities.

---

## References

- Husserl, E. (1982). *Ideas Pertaining to a Pure Phenomenology*
- Heidegger, M. (1962). *Being and Time*
- Merleau-Ponty, M. (1962). *Phenomenology of Perception*
- Koestler, A. (1967). *The Ghost in the Machine* (Holons)
- Biko, S. (1978). *I Write What I Like* (Ubuntu philosophy)
- Newman, M. (2018). *Networks* (Network science foundations)

---

**Version History:**
- v1.0.0 (2025-10-12): Initial release

**License:** Open source - adapt and extend as needed for your UBEC project.

**Support:** For questions about phenomenological modeling or implementation, please reference the inline comments in the SQL schema.
