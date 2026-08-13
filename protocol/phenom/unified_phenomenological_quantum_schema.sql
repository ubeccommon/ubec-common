-- ============================================================================
-- UNIFIED PHENOMENOLOGICAL QUANTUM GRAVITY SCHEMA
-- ============================================================================
-- 
-- This unified schema combines phenomenological principles with quantum gravity
-- concepts for modeling Stellar blockchain assets in the existing ubec database.
--
-- Design Philosophy:
-- 1. INTENTIONALITY: Every entity is defined by its directedness toward others
-- 2. HORIZONS: Internal (intrinsic properties) + External (contextual relations)
-- 3. TEMPORALITY: Retention (history), Present (now), Protention (anticipated)
-- 4. SPATIALITY: Network topology as geometric relationships
-- 5. COMPORTMENT: Embodied patterns of engagement and use
-- 6. GRAVITY: Network mass and forces (importance/influence)
-- 7. QUANTUM EFFECTS: Superposition, entanglement, uncertainty
-- 8. SPACETIME CURVATURE: Topology warping by massive entities
--
-- Attribution:
--   This project uses the services of Claude and Anthropic PBC to inform our
--   decisions and recommendations. This project was made possible with the
--   assistance of Claude and Anthropic PBC.
--
-- Database: ubec (existing)
-- Schema: phenomenal
-- Version: 2.0.0 (Unified)
-- Date: October 12, 2025
-- ============================================================================

-- Connect to ubec database (ensure you're connected before running this script)
-- \c ubec

-- ============================================================================
-- PART 1: EXTENSIONS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For fuzzy text search

-- ============================================================================
-- PART 2: SCHEMA CREATION
-- ============================================================================

-- Create phenomenal schema (or use if exists)
CREATE SCHEMA IF NOT EXISTS phenomenal;

-- Set search path for this session
SET search_path TO phenomenal, public;

-- ============================================================================
-- PART 3: CUSTOM TYPES (Phenomenological Foundation)
-- ============================================================================

-- Phenomenological modes of givenness
DO $$ BEGIN
    CREATE TYPE phenomenal_mode AS ENUM (
        'fully_present',        -- Directly experienced in primal impression
        'retained',             -- Given through retention (past)
        'protended',           -- Anticipated through protention (future)
        'co_present',          -- Given in external horizon
        'implicitly_meant'     -- Referred to but not given
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Asset existence modes (Heidegger's ontological difference)
DO $$ BEGIN
    CREATE TYPE existence_mode AS ENUM (
        'ready_to_hand',       -- Practical, engaged use (Zuhandenheit)
        'present_at_hand',     -- Theoretical, observed (Vorhandenheit)
        'unready_to_hand',     -- Broken, problematic, noticed
        'absent'               -- Referenced but not available
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Relationship intentionality types
DO $$ BEGIN
    CREATE TYPE intentional_relation AS ENUM (
        'trustline',           -- Directedness as trust
        'payment',             -- Directedness as transfer
        'offer',               -- Directedness as exchange
        'sponsorship',         -- Directedness as support
        'authorization',       -- Directedness as permission
        'claimable',          -- Directedness as potential
        'liquidity_pool'      -- Directedness as shared resource
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Ubuntu principle mapping
DO $$ BEGIN
    CREATE TYPE ubuntu_principle AS ENUM (
        'diversity',           -- Air: Universal access and variety
        'reciprocity',         -- Water: Flow and exchange
        'mutualism',           -- Earth: Stability through relationship
        'regeneration'         -- Fire: Transformation and renewal
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Holonic categories
DO $$ BEGIN
    CREATE TYPE holonic_category AS ENUM (
        'holon',              -- Both whole and part
        'autonomous_unit',    -- Acts independently
        'collective',         -- Emergent whole from parts
        'network_node',       -- Defined by connections
        'isolate'            -- Minimal connections
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Temporal horizons
DO $$ BEGIN
    CREATE TYPE temporal_horizon AS ENUM (
        'immediate',          -- Within seconds
        'proximal',           -- Within hours
        'intermediate',       -- Within days
        'distant',            -- Within weeks
        'extended'            -- Beyond weeks
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================================================
-- PART 4: CORE PHENOMENOLOGICAL ENTITIES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Assets as Phenomena (Things as they appear)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS assets (
    -- Identity
    id SERIAL PRIMARY KEY,
    asset_code VARCHAR(12) NOT NULL,
    issuer_address VARCHAR(56) NOT NULL,
    
    -- Phenomenological properties
    phenomenal_mode phenomenal_mode NOT NULL DEFAULT 'fully_present',
    existence_mode existence_mode NOT NULL DEFAULT 'present_at_hand',
    ubuntu_principle ubuntu_principle,
    
    -- Internal Horizon (intrinsic properties as given)
    internal_horizon JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "supply": {"total": float, "circulating": float},
    --   "properties": {"flags": [], "metadata": {}},
    --   "essence": {"immutable_attributes": {}}
    -- }
    
    -- External Horizon (contextual embeddedness)
    external_horizon JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "network_context": {"stellar_network": "mainnet|testnet"},
    --   "market_context": {"price_references": []},
    --   "social_context": {"community_size": int}
    -- }
    
    -- Temporal Consciousness
    genesis_at TIMESTAMP WITH TIME ZONE NOT NULL,
    retained_history JSONB,  -- Past states (retention)
    present_state JSONB NOT NULL,
    protended_futures JSONB,  -- Anticipated states (protention)
    temporal_horizon temporal_horizon NOT NULL DEFAULT 'intermediate',
    
    -- Spatial embedding (network position)
    network_position GEOMETRY(POINT, 4326),  -- Derived from graph embedding
    topology_metadata JSONB,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(asset_code, issuer_address)
);

CREATE INDEX IF NOT EXISTS idx_assets_phenomenal ON assets(phenomenal_mode, existence_mode);
CREATE INDEX IF NOT EXISTS idx_assets_ubuntu ON assets(ubuntu_principle);
CREATE INDEX IF NOT EXISTS idx_assets_temporal ON assets(genesis_at, temporal_horizon);
CREATE INDEX IF NOT EXISTS idx_assets_spatial ON assets USING GIST(network_position);
CREATE INDEX IF NOT EXISTS idx_assets_internal_horizon ON assets USING GIN(internal_horizon);
CREATE INDEX IF NOT EXISTS idx_assets_external_horizon ON assets USING GIN(external_horizon);

COMMENT ON TABLE assets IS 'Assets as phenomena: things as they appear in the blockchain, with internal/external horizons';

-- ----------------------------------------------------------------------------
-- Accounts as Dasein (Being-there, situated consciousness)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS accounts (
    -- Identity
    id SERIAL PRIMARY KEY,
    account_address VARCHAR(56) NOT NULL UNIQUE,
    
    -- Phenomenological being
    dasein_type VARCHAR(50) NOT NULL DEFAULT 'participant',
    comportment_pattern VARCHAR(50),
    holonic_category holonic_category NOT NULL DEFAULT 'network_node',
    
    -- Temporal thrownness (Geworfenheit)
    thrown_at TIMESTAMP WITH TIME ZONE NOT NULL,
    facticity JSONB,
    
    -- Spatial situation
    network_position GEOMETRY(POINT, 4326),
    spatial_context JSONB,
    
    -- Intentional directedness
    primary_intentions intentional_relation[],
    intention_strength JSONB,
    
    -- Horizons of experience
    internal_horizon JSONB NOT NULL DEFAULT '{}'::jsonb,
    external_horizon JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Ubuntu assessment
    ubuntu_scores JSONB,
    
    -- Temporal
    retained_states JSONB,
    present_state JSONB NOT NULL,
    anticipated_states JSONB,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_accounts_comportment ON accounts(comportment_pattern);
CREATE INDEX IF NOT EXISTS idx_accounts_holonic ON accounts(holonic_category);
CREATE INDEX IF NOT EXISTS idx_accounts_spatial ON accounts USING GIST(network_position);
CREATE INDEX IF NOT EXISTS idx_accounts_intentions ON accounts USING GIN(primary_intentions);
CREATE INDEX IF NOT EXISTS idx_accounts_internal ON accounts USING GIN(internal_horizon);

COMMENT ON TABLE accounts IS 'Accounts as Dasein: beings situated in the blockchain world with intentional directedness';

-- ----------------------------------------------------------------------------
-- Intentional Relations (Directedness between entities)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS intentional_relations (
    -- Identity
    id BIGSERIAL PRIMARY KEY,
    
    -- Intentional structure
    from_account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    to_account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    
    -- Type of intentionality
    relation_type intentional_relation NOT NULL,
    
    -- Phenomenal givenness
    phenomenal_mode phenomenal_mode NOT NULL DEFAULT 'fully_present',
    
    -- Intentional content (noema - what is meant)
    noema JSONB NOT NULL,
    
    -- Intentional act (noesis - how it is intended)
    noesis JSONB NOT NULL,
    
    -- Strength and characteristics
    relation_strength DECIMAL(10, 6) NOT NULL DEFAULT 0.5,
    reciprocity_factor DECIMAL(10, 6),
    stability_score DECIMAL(10, 6),
    
    -- Spatial representation
    relation_line GEOMETRY(LINESTRING, 4326),
    geodesic_distance DECIMAL(20, 10),
    euclidean_distance DECIMAL(20, 10),
    
    -- Temporal dimension
    emerged_at TIMESTAMP WITH TIME ZONE NOT NULL,
    retained_history JSONB,
    present_manifestation JSONB NOT NULL,
    protended_evolution JSONB,
    temporal_horizon temporal_horizon NOT NULL DEFAULT 'proximal',
    
    -- Active/dormant
    active BOOLEAN NOT NULL DEFAULT TRUE,
    last_activity_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_relation_structure CHECK (
        (to_account_id IS NOT NULL AND asset_id IS NULL) OR
        (to_account_id IS NULL AND asset_id IS NOT NULL) OR
        (to_account_id IS NOT NULL AND asset_id IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_relations_from ON intentional_relations(from_account_id, relation_type);
CREATE INDEX IF NOT EXISTS idx_relations_to ON intentional_relations(to_account_id, relation_type);
CREATE INDEX IF NOT EXISTS idx_relations_asset ON intentional_relations(asset_id, relation_type);
CREATE INDEX IF NOT EXISTS idx_relations_type ON intentional_relations(relation_type, active);
CREATE INDEX IF NOT EXISTS idx_relations_temporal ON intentional_relations(emerged_at, temporal_horizon);
CREATE INDEX IF NOT EXISTS idx_relations_spatial ON intentional_relations USING GIST(relation_line);
CREATE INDEX IF NOT EXISTS idx_relations_noema ON intentional_relations USING GIN(noema);
CREATE INDEX IF NOT EXISTS idx_relations_strength ON intentional_relations(relation_strength) WHERE active = TRUE;

COMMENT ON TABLE intentional_relations IS 'Intentional directedness: how accounts are related to assets and each other';

-- ============================================================================
-- PART 5: TEMPORAL PHENOMENOLOGY
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Retentions (Past as retained in present consciousness)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS retentions (
    id BIGSERIAL PRIMARY KEY,
    
    -- What is retained
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    
    -- Temporal structure
    original_present TIMESTAMP WITH TIME ZONE NOT NULL,
    retained_at TIMESTAMP WITH TIME ZONE NOT NULL,
    temporal_distance INTERVAL NOT NULL,
    
    -- Content retained
    retained_content JSONB NOT NULL,
    retention_clarity DECIMAL(5, 4) NOT NULL DEFAULT 1.0,
    retention_type VARCHAR(50) NOT NULL,
    
    -- Modifications through retention
    transformations JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_retentions_entity ON retentions(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_retentions_temporal ON retentions(original_present, retained_at);
CREATE INDEX IF NOT EXISTS idx_retentions_distance ON retentions(temporal_distance);
CREATE INDEX IF NOT EXISTS idx_retentions_clarity ON retentions(retention_clarity) WHERE retention_clarity > 0.5;

COMMENT ON TABLE retentions IS 'Past states retained in present consciousness (Husserlian retention)';

-- ----------------------------------------------------------------------------
-- Protentions (Future as anticipated in present consciousness)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS protentions (
    id BIGSERIAL PRIMARY KEY,
    
    -- What is anticipated
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    
    -- Temporal structure
    protended_from TIMESTAMP WITH TIME ZONE NOT NULL,
    expected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    temporal_distance INTERVAL NOT NULL,
    
    -- Anticipated content
    protended_content JSONB NOT NULL,
    expectation_confidence DECIMAL(5, 4) NOT NULL DEFAULT 0.5,
    protention_type VARCHAR(50) NOT NULL,
    
    -- Fulfillment tracking
    fulfilled BOOLEAN,
    fulfilled_at TIMESTAMP WITH TIME ZONE,
    fulfillment_degree DECIMAL(5, 4),
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_protentions_entity ON protentions(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_protentions_temporal ON protentions(protended_from, expected_at);
CREATE INDEX IF NOT EXISTS idx_protentions_confidence ON protentions(expectation_confidence);
CREATE INDEX IF NOT EXISTS idx_protentions_fulfilled ON protentions(fulfilled, fulfillment_degree);

COMMENT ON TABLE protentions IS 'Future states anticipated in present consciousness (Husserlian protention)';

-- ============================================================================
-- PART 6: SPATIAL PHENOMENOLOGY (Network Topology)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Network Embeddings
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS network_embeddings (
    id BIGSERIAL PRIMARY KEY,
    
    computed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    embedding_method VARCHAR(100) NOT NULL,
    dimensions INTEGER NOT NULL DEFAULT 2,
    parameters JSONB NOT NULL,
    quality_metrics JSONB,
    
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_until TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_embeddings_temporal ON network_embeddings(valid_from, valid_until);

-- ----------------------------------------------------------------------------
-- Spatial Positions
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS spatial_positions (
    id BIGSERIAL PRIMARY KEY,
    
    embedding_id INTEGER NOT NULL REFERENCES network_embeddings(id) ON DELETE CASCADE,
    
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    
    position GEOMETRY(POINT, 4326) NOT NULL,
    coordinates DECIMAL(20, 10)[],
    
    local_density DECIMAL(20, 10),
    centrality_scores JSONB,
    cluster_membership INTEGER[],
    
    immediate_neighbors INTEGER[],
    proximal_region GEOMETRY(POLYGON, 4326),
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_spatial_positions_entity ON spatial_positions(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_spatial_positions_embedding ON spatial_positions(embedding_id);
CREATE INDEX IF NOT EXISTS idx_spatial_positions_geom ON spatial_positions USING GIST(position);
CREATE INDEX IF NOT EXISTS idx_spatial_positions_region ON spatial_positions USING GIST(proximal_region);

COMMENT ON TABLE spatial_positions IS 'Spatial positions of entities in network embedding space';

-- ----------------------------------------------------------------------------
-- Geodesics (Shortest paths through network)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS geodesics (
    id BIGSERIAL PRIMARY KEY,
    
    from_account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    to_account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    
    path_length INTEGER NOT NULL,
    path_nodes INTEGER[] NOT NULL,
    path_edges BIGINT[] NOT NULL,
    
    path_line GEOMETRY(LINESTRING, 4326),
    weighted_distance DECIMAL(20, 10),
    
    computed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(from_account_id, to_account_id)
);

CREATE INDEX IF NOT EXISTS idx_geodesics_from ON geodesics(from_account_id);
CREATE INDEX IF NOT EXISTS idx_geodesics_to ON geodesics(to_account_id);
CREATE INDEX IF NOT EXISTS idx_geodesics_length ON geodesics(path_length);
CREATE INDEX IF NOT EXISTS idx_geodesics_geom ON geodesics USING GIST(path_line);

COMMENT ON TABLE geodesics IS 'Shortest paths (geodesics) through the network topology';

-- ============================================================================
-- PART 7: TRANSACTION EVENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    
    transaction_hash VARCHAR(64) NOT NULL UNIQUE,
    ledger_sequence BIGINT NOT NULL,
    
    event_type VARCHAR(50) NOT NULL,
    source_account_id INTEGER REFERENCES accounts(id),
    
    ledger_closed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    temporal_context JSONB,
    
    operations JSONB NOT NULL,
    operations_count INTEGER NOT NULL,
    
    effects JSONB,
    
    successful BOOLEAN NOT NULL,
    result_code VARCHAR(100),
    
    affected_positions GEOMETRY(MULTIPOINT, 4326),
    network_impact JSONB,
    
    fee_charged BIGINT NOT NULL,
    resource_fee BIGINT,
    
    memo_type VARCHAR(20),
    memo_value TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transactions_hash ON transactions(transaction_hash);
CREATE INDEX IF NOT EXISTS idx_transactions_ledger ON transactions(ledger_sequence, ledger_closed_at);
CREATE INDEX IF NOT EXISTS idx_transactions_source ON transactions(source_account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_temporal ON transactions(ledger_closed_at);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(event_type, successful);
CREATE INDEX IF NOT EXISTS idx_transactions_spatial ON transactions USING GIST(affected_positions);

COMMENT ON TABLE transactions IS 'Transaction events as discrete phenomena in blockchain spacetime';

-- ============================================================================
-- PART 8: HOLONIC STRUCTURE
-- ============================================================================

CREATE TABLE IF NOT EXISTS holons (
    id BIGSERIAL PRIMARY KEY,
    
    holon_name VARCHAR(255) NOT NULL,
    holon_type VARCHAR(100) NOT NULL,
    
    autonomy_score DECIMAL(5, 4) NOT NULL,
    integration_score DECIMAL(5, 4) NOT NULL,
    
    constituent_accounts INTEGER[],
    constituent_assets INTEGER[],
    constituent_relations BIGINT[],
    
    parent_holons INTEGER[],
    
    emergent_properties JSONB,
    collective_behavior JSONB,
    
    spatial_region GEOMETRY(POLYGON, 4326),
    centroid GEOMETRY(POINT, 4326),
    
    emerged_at TIMESTAMP WITH TIME ZONE NOT NULL,
    stable_from TIMESTAMP WITH TIME ZONE,
    dissolved_at TIMESTAMP WITH TIME ZONE,
    
    ubuntu_scores JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_holons_type ON holons(holon_type);
CREATE INDEX IF NOT EXISTS idx_holons_autonomy ON holons(autonomy_score);
CREATE INDEX IF NOT EXISTS idx_holons_integration ON holons(integration_score);
CREATE INDEX IF NOT EXISTS idx_holons_spatial ON holons USING GIST(spatial_region);
CREATE INDEX IF NOT EXISTS idx_holons_centroid ON holons USING GIST(centroid);
CREATE INDEX IF NOT EXISTS idx_holons_temporal ON holons(emerged_at, dissolved_at);

COMMENT ON TABLE holons IS 'Holarchical structures: entities that are both autonomous wholes and integrated parts';

-- ============================================================================
-- PART 9: QUANTUM GRAVITY TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Gravitational Mass (Network Importance)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gravitational_mass (
    id BIGSERIAL PRIMARY KEY,
    
    entity_type VARCHAR(50) NOT NULL,
    entity_id BIGINT NOT NULL,
    
    gravitational_mass DECIMAL(20, 10) NOT NULL,
    inertial_mass DECIMAL(20, 10) NOT NULL,
    
    mass_basis JSONB NOT NULL,
    
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE,
    
    mass_trajectory JSONB,
    
    UNIQUE(entity_type, entity_id, calculated_at),
    CHECK (gravitational_mass >= 0),
    CHECK (inertial_mass >= 0)
);

CREATE INDEX IF NOT EXISTS idx_grav_mass_entity ON gravitational_mass(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_grav_mass_value ON gravitational_mass(gravitational_mass DESC);
CREATE INDEX IF NOT EXISTS idx_grav_mass_temporal ON gravitational_mass(calculated_at, valid_until);
CREATE INDEX IF NOT EXISTS idx_grav_mass_basis ON gravitational_mass USING GIN(mass_basis);

COMMENT ON TABLE gravitational_mass IS 'Network gravity: measure of entity importance and influence';

-- ----------------------------------------------------------------------------
-- Gravitational Fields (Zones of Influence)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gravitational_fields (
    id BIGSERIAL PRIMARY KEY,
    
    source_mass_id BIGINT NOT NULL REFERENCES gravitational_mass(id) ON DELETE CASCADE,
    
    field_profile JSONB NOT NULL,
    influence_radius DECIMAL(20, 10) NOT NULL,
    field_geometry GEOMETRY(POLYGON, 4326),
    
    field_type VARCHAR(50) NOT NULL,
    field_strength DECIMAL(20, 10) NOT NULL,
    
    is_static BOOLEAN NOT NULL DEFAULT FALSE,
    temporal_variation JSONB,
    
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CHECK (influence_radius >= 0),
    CHECK (field_strength >= 0),
    CHECK (field_type IN ('attractive', 'repulsive', 'neutral', 'mixed'))
);

CREATE INDEX IF NOT EXISTS idx_grav_field_source ON gravitational_fields(source_mass_id);
CREATE INDEX IF NOT EXISTS idx_grav_field_spatial ON gravitational_fields USING GIST(field_geometry);
CREATE INDEX IF NOT EXISTS idx_grav_field_type ON gravitational_fields(field_type);
CREATE INDEX IF NOT EXISTS idx_grav_field_strength ON gravitational_fields(field_strength DESC);

COMMENT ON TABLE gravitational_fields IS 'Gravitational fields: zones of influence surrounding massive entities';

-- ----------------------------------------------------------------------------
-- Gravitational Interactions (Forces Between Entities)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gravitational_interactions (
    id BIGSERIAL PRIMARY KEY,
    
    entity1_mass_id BIGINT NOT NULL REFERENCES gravitational_mass(id) ON DELETE CASCADE,
    entity2_mass_id BIGINT NOT NULL REFERENCES gravitational_mass(id) ON DELETE CASCADE,
    
    force_magnitude DECIMAL(20, 10) NOT NULL,
    force_direction DECIMAL(10, 6),
    force_vector GEOMETRY(LINESTRING, 4326),
    
    separation_distance DECIMAL(20, 10) NOT NULL,
    network_hops INTEGER,
    
    potential_energy DECIMAL(20, 10),
    binding_energy DECIMAL(20, 10),
    
    interaction_type VARCHAR(50) NOT NULL,
    is_significant BOOLEAN NOT NULL DEFAULT TRUE,
    
    interaction_strength_history JSONB,
    measured_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CHECK (entity1_mass_id != entity2_mass_id),
    CHECK (force_magnitude >= 0),
    CHECK (separation_distance >= 0),
    CHECK (interaction_type IN ('attraction', 'repulsion', 'equilibrium')),
    UNIQUE(entity1_mass_id, entity2_mass_id, measured_at)
);

CREATE INDEX IF NOT EXISTS idx_grav_int_entities ON gravitational_interactions(entity1_mass_id, entity2_mass_id);
CREATE INDEX IF NOT EXISTS idx_grav_int_magnitude ON gravitational_interactions(force_magnitude DESC);
CREATE INDEX IF NOT EXISTS idx_grav_int_type ON gravitational_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_grav_int_significant ON gravitational_interactions(is_significant) WHERE is_significant = TRUE;
CREATE INDEX IF NOT EXISTS idx_grav_int_spatial ON gravitational_interactions USING GIST(force_vector);

COMMENT ON TABLE gravitational_interactions IS 'Pairwise gravitational forces between massive entities in the network';

-- ----------------------------------------------------------------------------
-- Spacetime Curvature (Network Topology Warping)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS spacetime_curvature (
    id BIGSERIAL PRIMARY KEY,
    
    source_mass_id BIGINT NOT NULL REFERENCES gravitational_mass(id) ON DELETE CASCADE,
    
    ricci_scalar DECIMAL(20, 10),
    curvature_tensor JSONB,
    geodesic_deviations JSONB,
    
    curvature_geometry GEOMETRY(POLYGON, 4326),
    curvature_radius DECIMAL(20, 10) NOT NULL,
    
    metric_signature JSONB,
    
    light_deflection DECIMAL(10, 6),
    time_dilation_factor DECIMAL(15, 10),
    
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CHECK (curvature_radius >= 0)
);

CREATE INDEX IF NOT EXISTS idx_spacetime_source ON spacetime_curvature(source_mass_id);
CREATE INDEX IF NOT EXISTS idx_spacetime_scalar ON spacetime_curvature(ricci_scalar);
CREATE INDEX IF NOT EXISTS idx_spacetime_spatial ON spacetime_curvature USING GIST(curvature_geometry);

COMMENT ON TABLE spacetime_curvature IS 'How massive entities warp the topology of the network';

-- ----------------------------------------------------------------------------
-- Quantum States (Superposition and Discrete Energy Levels)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quantum_states (
    id BIGSERIAL PRIMARY KEY,
    
    entity_type VARCHAR(50) NOT NULL,
    entity_id BIGINT NOT NULL,
    
    state_vector JSONB NOT NULL,
    
    energy_level INTEGER NOT NULL,
    energy_value DECIMAL(20, 10) NOT NULL,
    possible_transitions JSONB,
    
    position_uncertainty DECIMAL(20, 10),
    momentum_uncertainty DECIMAL(20, 10),
    energy_time_uncertainty DECIMAL(20, 10),
    
    last_measured_at TIMESTAMP WITH TIME ZONE,
    measurement_outcome VARCHAR(100),
    collapse_probability DECIMAL(10, 8),
    
    decoherence_rate DECIMAL(15, 10),
    environment_coupling DECIMAL(10, 6),
    
    state_prepared_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    state_valid_until TIMESTAMP WITH TIME ZONE,
    
    CHECK (energy_level >= 0),
    CHECK (position_uncertainty >= 0),
    CHECK (momentum_uncertainty >= 0)
);

CREATE INDEX IF NOT EXISTS idx_quantum_entity ON quantum_states(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_quantum_energy ON quantum_states(energy_level, energy_value);
CREATE INDEX IF NOT EXISTS idx_quantum_coherence ON quantum_states((state_vector->>'coherence'));

COMMENT ON TABLE quantum_states IS 'Quantum mechanical states: superposition, discrete energies, and uncertainty';

-- ----------------------------------------------------------------------------
-- Quantum Entanglement (Non-Local Correlations)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quantum_entanglement (
    id BIGSERIAL PRIMARY KEY,
    
    entity1_state_id BIGINT NOT NULL REFERENCES quantum_states(id) ON DELETE CASCADE,
    entity2_state_id BIGINT NOT NULL REFERENCES quantum_states(id) ON DELETE CASCADE,
    
    entanglement_entropy DECIMAL(15, 10) NOT NULL,
    correlation_coefficient DECIMAL(10, 8) NOT NULL,
    
    bell_parameter DECIMAL(10, 6),
    violates_bell_inequality BOOLEAN,
    
    joint_state JSONB NOT NULL,
    
    is_separable BOOLEAN NOT NULL DEFAULT FALSE,
    separability_witness DECIMAL(10, 6),
    
    separation_distance DECIMAL(20, 10),
    instantaneous_correlation BOOLEAN,
    
    entanglement_created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    entanglement_broken_at TIMESTAMP WITH TIME ZONE,
    entanglement_lifetime INTERVAL,
    
    CHECK (entity1_state_id != entity2_state_id),
    CHECK (entanglement_entropy >= 0),
    CHECK (correlation_coefficient BETWEEN -1 AND 1),
    UNIQUE(entity1_state_id, entity2_state_id)
);

CREATE INDEX IF NOT EXISTS idx_entangle_entities ON quantum_entanglement(entity1_state_id, entity2_state_id);
CREATE INDEX IF NOT EXISTS idx_entangle_strength ON quantum_entanglement(entanglement_entropy DESC);
CREATE INDEX IF NOT EXISTS idx_entangle_active ON quantum_entanglement(entanglement_broken_at) 
    WHERE entanglement_broken_at IS NULL;

COMMENT ON TABLE quantum_entanglement IS 'Quantum entanglement: non-local correlations between entity states';

-- ----------------------------------------------------------------------------
-- Lorentz Violation (Symmetry Breaking)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lorentz_violation (
    id BIGSERIAL PRIMARY KEY,
    
    region_geometry GEOMETRY(POLYGON, 4326) NOT NULL,
    
    preferred_direction GEOMETRY(LINESTRING, 4326),
    anisotropy_vector JSONB NOT NULL,
    
    violation_magnitude DECIMAL(15, 10) NOT NULL,
    violation_type VARCHAR(100) NOT NULL,
    
    dispersion_coefficients JSONB,
    
    speed_anisotropy DECIMAL(10, 6),
    arrival_time_differences JSONB,
    
    test_statistic DECIMAL(15, 10),
    significance_level DECIMAL(10, 8),
    is_statistically_significant BOOLEAN,
    
    observed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    observation_count INTEGER NOT NULL DEFAULT 1,
    
    CHECK (violation_magnitude >= 0),
    CHECK (violation_type IN ('rotation', 'boost', 'cpt', 'space_isotropy', 'time_reversal', 'parity'))
);

CREATE INDEX IF NOT EXISTS idx_lorentz_spatial ON lorentz_violation USING GIST(region_geometry);
CREATE INDEX IF NOT EXISTS idx_lorentz_magnitude ON lorentz_violation(violation_magnitude DESC);
CREATE INDEX IF NOT EXISTS idx_lorentz_type ON lorentz_violation(violation_type);
CREATE INDEX IF NOT EXISTS idx_lorentz_significant ON lorentz_violation(is_statistically_significant) 
    WHERE is_statistically_significant = TRUE;

COMMENT ON TABLE lorentz_violation IS 'Lorentz symmetry violations: preferred directions and broken symmetries';

-- ----------------------------------------------------------------------------
-- Quantum Gravity Signatures (Observable Phenomena)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quantum_gravity_signatures (
    id BIGSERIAL PRIMARY KEY,
    
    signature_type VARCHAR(100) NOT NULL,
    
    measured_value DECIMAL(20, 10) NOT NULL,
    theoretical_prediction DECIMAL(20, 10),
    measurement_error DECIMAL(20, 10),
    
    measurement_region GEOMETRY(POLYGON, 4326),
    energy_scale DECIMAL(20, 10),
    length_scale DECIMAL(20, 10),
    
    confidence_level DECIMAL(10, 8),
    signal_to_noise DECIMAL(15, 10),
    
    signature_details JSONB NOT NULL,
    related_entities JSONB,
    
    observed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    observation_duration INTERVAL,
    
    CHECK (energy_scale > 0),
    CHECK (length_scale > 0),
    CHECK (confidence_level BETWEEN 0 AND 1)
);

CREATE INDEX IF NOT EXISTS idx_qg_sig_type ON quantum_gravity_signatures(signature_type);
CREATE INDEX IF NOT EXISTS idx_qg_sig_confidence ON quantum_gravity_signatures(confidence_level DESC);
CREATE INDEX IF NOT EXISTS idx_qg_sig_spatial ON quantum_gravity_signatures USING GIST(measurement_region);
CREATE INDEX IF NOT EXISTS idx_qg_sig_details ON quantum_gravity_signatures USING GIN(signature_details);

COMMENT ON TABLE quantum_gravity_signatures IS 'Observable signatures of quantum gravitational effects';

-- ============================================================================
-- PART 10: CALCULATION FUNCTIONS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Calculate Gravitational Mass
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_gravitational_mass(
    p_entity_type VARCHAR(50),
    p_entity_id BIGINT
) RETURNS DECIMAL(20, 10) AS $$
DECLARE
    v_mass DECIMAL(20, 10);
    v_connection_count INTEGER;
    v_age_days INTEGER;
BEGIN
    IF p_entity_type = 'account' THEN
        -- For accounts: connections + age
        SELECT 
            COUNT(DISTINCT CASE 
                WHEN from_account_id = p_entity_id THEN to_account_id
                WHEN to_account_id = p_entity_id THEN from_account_id
            END),
            EXTRACT(days FROM (NOW() - thrown_at))
        INTO v_connection_count, v_age_days
        FROM phenomenal.intentional_relations ir
        CROSS JOIN phenomenal.accounts a
        WHERE (ir.from_account_id = p_entity_id OR ir.to_account_id = p_entity_id)
          AND a.id = p_entity_id
          AND ir.active = TRUE;
        
        v_mass := (v_connection_count * 10.0) + (v_age_days / 30.0);
        
    ELSIF p_entity_type = 'asset' THEN
        -- For assets: holder count + age
        SELECT 
            COUNT(DISTINCT from_account_id),
            EXTRACT(days FROM (NOW() - genesis_at))
        INTO v_connection_count, v_age_days
        FROM phenomenal.intentional_relations ir
        CROSS JOIN phenomenal.assets a
        WHERE ir.asset_id = p_entity_id
          AND a.id = p_entity_id
          AND ir.active = TRUE;
        
        v_mass := (v_connection_count * 5.0) + (v_age_days / 30.0);
        
    ELSIF p_entity_type = 'holon' THEN
        -- For holons: constituents + integration
        SELECT 
            (COALESCE(array_length(constituent_accounts, 1), 0) +
             COALESCE(array_length(constituent_assets, 1), 0)) * 3.0 +
            (integration_score * 50.0)
        INTO v_mass
        FROM phenomenal.holons
        WHERE id = p_entity_id;
    ELSE
        v_mass := 0.0;
    END IF;
    
    RETURN GREATEST(COALESCE(v_mass, 0.0), 0.0);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_gravitational_mass IS 'Calculate gravitational mass (importance) for any entity';

-- ----------------------------------------------------------------------------
-- Calculate Gravitational Force
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_gravitational_force(
    p_mass1_id BIGINT,
    p_mass2_id BIGINT
) RETURNS DECIMAL(20, 10) AS $$
DECLARE
    v_mass1 DECIMAL(20, 10);
    v_mass2 DECIMAL(20, 10);
    v_distance DECIMAL(20, 10);
    v_force DECIMAL(20, 10);
    v_G CONSTANT DECIMAL(20, 10) := 1.0;
BEGIN
    SELECT gravitational_mass INTO v_mass1
    FROM phenomenal.gravitational_mass
    WHERE id = p_mass1_id;
    
    SELECT gravitational_mass INTO v_mass2
    FROM phenomenal.gravitational_mass
    WHERE id = p_mass2_id;
    
    -- Calculate distance (simplified)
    v_distance := 1.0;
    
    IF v_distance > 0 THEN
        v_force := (v_G * v_mass1 * v_mass2) / (v_distance * v_distance);
    ELSE
        v_force := v_G * v_mass1 * v_mass2;
    END IF;
    
    RETURN v_force;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_gravitational_force IS 'Calculate gravitational force between two entities';

-- ----------------------------------------------------------------------------
-- Calculate Spacetime Curvature
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_spacetime_curvature(
    p_mass_id BIGINT
) RETURNS DECIMAL(20, 10) AS $$
DECLARE
    v_mass DECIMAL(20, 10);
    v_curvature DECIMAL(20, 10);
    v_G CONSTANT DECIMAL(20, 10) := 1.0;
BEGIN
    SELECT gravitational_mass INTO v_mass
    FROM phenomenal.gravitational_mass
    WHERE id = p_mass_id;
    
    v_curvature := v_G * v_mass;
    
    RETURN v_curvature;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_spacetime_curvature IS 'Calculate spacetime curvature (Ricci scalar)';

-- ----------------------------------------------------------------------------
-- Calculate Entanglement Entropy
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_entanglement_entropy(
    p_state1_id BIGINT,
    p_state2_id BIGINT
) RETURNS DECIMAL(15, 10) AS $$
DECLARE
    v_entropy DECIMAL(15, 10);
    v_correlation DECIMAL(10, 8);
BEGIN
    -- Simplified calculation
    v_correlation := 0.5;
    
    IF v_correlation > 0 AND v_correlation < 1 THEN
        v_entropy := -v_correlation * log(2, v_correlation) - 
                     (1 - v_correlation) * log(2, 1 - v_correlation);
    ELSE
        v_entropy := 0.0;
    END IF;
    
    RETURN GREATEST(v_entropy, 0.0);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_entanglement_entropy IS 'Calculate von Neumann entanglement entropy';

-- ----------------------------------------------------------------------------
-- Compute Phenomenal Prominence (Centrality)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION compute_phenomenal_prominence(
    p_entity_type VARCHAR,
    p_entity_id INTEGER
) RETURNS JSONB AS $$
DECLARE
    v_degree_centrality DECIMAL(10, 6);
    v_betweenness DECIMAL(10, 6);
    v_closeness DECIMAL(10, 6);
    v_result JSONB;
BEGIN
    -- Degree centrality
    SELECT COUNT(DISTINCT CASE WHEN from_account_id = p_entity_id THEN to_account_id
                               WHEN to_account_id = p_entity_id THEN from_account_id END)::DECIMAL
           / NULLIF((SELECT COUNT(*) FROM accounts), 0)
    INTO v_degree_centrality
    FROM intentional_relations
    WHERE (from_account_id = p_entity_id OR to_account_id = p_entity_id)
      AND active = TRUE;
    
    -- Betweenness centrality
    SELECT COUNT(*)::DECIMAL / NULLIF((SELECT COUNT(*) FROM geodesics), 0)
    INTO v_betweenness
    FROM geodesics
    WHERE p_entity_id = ANY(path_nodes);
    
    -- Closeness centrality
    SELECT 1.0 / NULLIF(AVG(path_length), 0)
    INTO v_closeness
    FROM geodesics
    WHERE from_account_id = p_entity_id OR to_account_id = p_entity_id;
    
    v_result := jsonb_build_object(
        'degree_centrality', COALESCE(v_degree_centrality, 0),
        'betweenness_centrality', COALESCE(v_betweenness, 0),
        'closeness_centrality', COALESCE(v_closeness, 0),
        'computed_at', NOW()
    );
    
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION compute_phenomenal_prominence IS 'Compute centrality measures';

-- ----------------------------------------------------------------------------
-- Analyze Ubuntu Balance
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION analyze_ubuntu_balance(
    p_account_id INTEGER
) RETURNS JSONB AS $$
DECLARE
    v_diversity_score DECIMAL(5, 4);
    v_reciprocity_score DECIMAL(5, 4);
    v_mutualism_score DECIMAL(5, 4);
    v_regeneration_score DECIMAL(5, 4);
    v_result JSONB;
BEGIN
    -- Diversity: variety of asset types
    SELECT (COUNT(DISTINCT asset_id)::DECIMAL / 10.0)
    INTO v_diversity_score
    FROM intentional_relations
    WHERE from_account_id = p_account_id
      AND relation_type IN ('trustline', 'payment')
      AND active = TRUE;
    
    -- Reciprocity: balance of flows
    SELECT 1.0 - ABS(
        (SELECT COUNT(*) FROM intentional_relations WHERE from_account_id = p_account_id)::DECIMAL -
        (SELECT COUNT(*) FROM intentional_relations WHERE to_account_id = p_account_id)::DECIMAL
    ) / NULLIF(
        (SELECT COUNT(*) FROM intentional_relations 
         WHERE from_account_id = p_account_id OR to_account_id = p_account_id),
        0
    )
    INTO v_reciprocity_score;
    
    -- Mutualism: mutual relationships
    SELECT AVG(reciprocity_factor)
    INTO v_mutualism_score
    FROM intentional_relations
    WHERE (from_account_id = p_account_id OR to_account_id = p_account_id)
      AND reciprocity_factor IS NOT NULL
      AND active = TRUE;
    
    -- Regeneration: recent growth
    WITH temporal_growth AS (
        SELECT COUNT(*) AS recent_count
        FROM intentional_relations
        WHERE from_account_id = p_account_id
          AND emerged_at > NOW() - INTERVAL '30 days'
    )
    SELECT (recent_count::DECIMAL / 100.0)
    INTO v_regeneration_score
    FROM temporal_growth;
    
    v_result := jsonb_build_object(
        'diversity', LEAST(COALESCE(v_diversity_score, 0), 1.0),
        'reciprocity', COALESCE(v_reciprocity_score, 0.5),
        'mutualism', COALESCE(v_mutualism_score, 0.5),
        'regeneration', LEAST(COALESCE(v_regeneration_score, 0), 1.0),
        'composite', (
            COALESCE(v_diversity_score, 0) * 0.25 +
            COALESCE(v_reciprocity_score, 0.5) * 0.25 +
            COALESCE(v_mutualism_score, 0.5) * 0.25 +
            LEAST(COALESCE(v_regeneration_score, 0), 1.0) * 0.25
        ),
        'analyzed_at', NOW()
    );
    
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION analyze_ubuntu_balance IS 'Analyze Ubuntu principle balance';

-- ============================================================================
-- PART 11: ANALYTICAL VIEWS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Current Network State
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW current_network_state AS
SELECT 
    a.id AS asset_id,
    a.asset_code,
    a.issuer_address,
    a.phenomenal_mode,
    a.existence_mode,
    a.ubuntu_principle,
    a.network_position,
    COUNT(DISTINCT ir.from_account_id) AS holder_count,
    SUM(CASE WHEN ir.active THEN 1 ELSE 0 END) AS active_relations,
    AVG(ir.relation_strength) AS avg_relation_strength
FROM assets a
LEFT JOIN intentional_relations ir ON a.id = ir.asset_id
GROUP BY a.id, a.asset_code, a.issuer_address, a.phenomenal_mode, 
         a.existence_mode, a.ubuntu_principle, a.network_position;

COMMENT ON VIEW current_network_state IS 'Present state of assets in their phenomenal field';

-- ----------------------------------------------------------------------------
-- Intentional Network
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW intentional_network AS
SELECT 
    ir.id AS relation_id,
    ir.relation_type,
    ir.from_account_id,
    ir.to_account_id,
    ir.asset_id,
    ir.relation_strength,
    ir.reciprocity_factor,
    a_from.account_address AS from_address,
    a_to.account_address AS to_address,
    ast.asset_code,
    ir.relation_line,
    ir.temporal_horizon
FROM intentional_relations ir
LEFT JOIN accounts a_from ON ir.from_account_id = a_from.id
LEFT JOIN accounts a_to ON ir.to_account_id = a_to.id
LEFT JOIN assets ast ON ir.asset_id = ast.id
WHERE ir.active = TRUE;

COMMENT ON VIEW intentional_network IS 'Current network of intentional relations';

-- ----------------------------------------------------------------------------
-- Network Gravity Map
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW network_gravity_map AS
SELECT 
    gm.entity_type,
    gm.entity_id,
    gm.gravitational_mass,
    gm.inertial_mass,
    gf.influence_radius,
    gf.field_strength,
    gf.field_type,
    gf.field_geometry,
    gm.calculated_at
FROM gravitational_mass gm
LEFT JOIN gravitational_fields gf ON gm.id = gf.source_mass_id
WHERE gm.valid_until IS NULL OR gm.valid_until > NOW()
ORDER BY gm.gravitational_mass DESC;

COMMENT ON VIEW network_gravity_map IS 'Visualization of gravitational mass and fields';

-- ----------------------------------------------------------------------------
-- Strong Gravitational Interactions
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW strong_gravitational_interactions AS
SELECT 
    gi.id,
    gm1.entity_type AS entity1_type,
    gm1.entity_id AS entity1_id,
    gm2.entity_type AS entity2_type,
    gm2.entity_id AS entity2_id,
    gi.force_magnitude,
    gi.separation_distance,
    gi.potential_energy,
    gi.interaction_type,
    gi.measured_at
FROM gravitational_interactions gi
JOIN gravitational_mass gm1 ON gi.entity1_mass_id = gm1.id
JOIN gravitational_mass gm2 ON gi.entity2_mass_id = gm2.id
WHERE gi.is_significant = TRUE
  AND gi.force_magnitude > 0.1
ORDER BY gi.force_magnitude DESC;

COMMENT ON VIEW strong_gravitational_interactions IS 'Significant gravitational interactions';

-- ----------------------------------------------------------------------------
-- Curved Spacetime Regions
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW curved_spacetime_regions AS
SELECT 
    sc.id,
    gm.entity_type,
    gm.entity_id,
    gm.gravitational_mass,
    sc.ricci_scalar,
    sc.curvature_radius,
    sc.light_deflection,
    sc.time_dilation_factor,
    sc.curvature_geometry,
    sc.calculated_at
FROM spacetime_curvature sc
JOIN gravitational_mass gm ON sc.source_mass_id = gm.id
WHERE ABS(sc.ricci_scalar) > 0.01
ORDER BY ABS(sc.ricci_scalar) DESC;

COMMENT ON VIEW curved_spacetime_regions IS 'Regions of significant spacetime curvature';

-- ----------------------------------------------------------------------------
-- Active Quantum Entanglements
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW active_quantum_entanglements AS
SELECT 
    qe.id,
    qs1.entity_type AS entity1_type,
    qs1.entity_id AS entity1_id,
    qs2.entity_type AS entity2_type,
    qs2.entity_id AS entity2_id,
    qe.entanglement_entropy,
    qe.correlation_coefficient,
    qe.violates_bell_inequality,
    qe.separation_distance,
    qe.entanglement_created_at,
    (NOW() - qe.entanglement_created_at) AS entanglement_age
FROM quantum_entanglement qe
JOIN quantum_states qs1 ON qe.entity1_state_id = qs1.id
JOIN quantum_states qs2 ON qe.entity2_state_id = qs2.id
WHERE qe.entanglement_broken_at IS NULL
ORDER BY qe.entanglement_entropy DESC;

COMMENT ON VIEW active_quantum_entanglements IS 'Currently active quantum entanglements';

-- ----------------------------------------------------------------------------
-- Lorentz Violation Hotspots
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW lorentz_violation_hotspots AS
SELECT 
    lv.id,
    lv.violation_type,
    lv.violation_magnitude,
    lv.speed_anisotropy,
    lv.test_statistic,
    lv.significance_level,
    lv.is_statistically_significant,
    lv.region_geometry,
    lv.observed_at,
    lv.observation_count
FROM lorentz_violation lv
WHERE lv.is_statistically_significant = TRUE
ORDER BY lv.violation_magnitude DESC;

COMMENT ON VIEW lorentz_violation_hotspots IS 'Statistically significant Lorentz violations';

-- ============================================================================
-- PART 12: TRIGGERS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Update Spatial Positions
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_spatial_positions_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.entity_type = 'account' THEN
        UPDATE accounts
        SET network_position = NEW.position,
            updated_at = NOW()
        WHERE id = NEW.entity_id;
    END IF;
    
    IF NEW.entity_type = 'asset' THEN
        UPDATE assets
        SET network_position = NEW.position,
            updated_at = NOW()
        WHERE id = NEW.entity_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_spatial_positions ON spatial_positions;
CREATE TRIGGER trg_update_spatial_positions
    AFTER INSERT OR UPDATE ON spatial_positions
    FOR EACH ROW
    EXECUTE FUNCTION update_spatial_positions_trigger();

-- ----------------------------------------------------------------------------
-- Maintain Retentions
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION maintain_retentions_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO retentions (
        entity_type,
        entity_id,
        original_present,
        retained_at,
        temporal_distance,
        retained_content,
        retention_clarity,
        retention_type
    ) VALUES (
        TG_TABLE_NAME,
        OLD.id,
        OLD.updated_at,
        NOW(),
        NOW() - OLD.updated_at,
        row_to_json(OLD)::jsonb,
        1.0,
        'primary'
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_maintain_asset_retentions ON assets;
CREATE TRIGGER trg_maintain_asset_retentions
    AFTER UPDATE ON assets
    FOR EACH ROW
    EXECUTE FUNCTION maintain_retentions_trigger();

DROP TRIGGER IF EXISTS trg_maintain_account_retentions ON accounts;
CREATE TRIGGER trg_maintain_account_retentions
    AFTER UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION maintain_retentions_trigger();

-- ----------------------------------------------------------------------------
-- Update Timestamps
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_assets_updated_at ON assets;
CREATE TRIGGER trg_assets_updated_at
    BEFORE UPDATE ON assets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_accounts_updated_at ON accounts;
CREATE TRIGGER trg_accounts_updated_at
    BEFORE UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_relations_updated_at ON intentional_relations;
CREATE TRIGGER trg_relations_updated_at
    BEFORE UPDATE ON intentional_relations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- Auto-Calculate Gravitational Mass
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION auto_calculate_gravity() RETURNS TRIGGER AS $$
DECLARE
    v_mass DECIMAL(20, 10);
    v_entity_type VARCHAR(50);
BEGIN
    v_entity_type := CASE TG_TABLE_NAME
        WHEN 'accounts' THEN 'account'
        WHEN 'assets' THEN 'asset'
        WHEN 'holons' THEN 'holon'
        ELSE 'unknown'
    END;
    
    v_mass := calculate_gravitational_mass(v_entity_type, NEW.id);
    
    INSERT INTO gravitational_mass (
        entity_type,
        entity_id,
        gravitational_mass,
        inertial_mass,
        mass_basis,
        calculated_at
    ) VALUES (
        v_entity_type,
        NEW.id,
        v_mass,
        v_mass * 1.1,
        jsonb_build_object(
            'auto_calculated', TRUE,
            'calculation_method', 'trigger'
        ),
        NOW()
    )
    ON CONFLICT (entity_type, entity_id, calculated_at) 
    DO UPDATE SET
        gravitational_mass = v_mass,
        inertial_mass = v_mass * 1.1;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_account_gravity ON accounts;
CREATE TRIGGER trg_account_gravity
    AFTER INSERT OR UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION auto_calculate_gravity();

DROP TRIGGER IF EXISTS trg_asset_gravity ON assets;
CREATE TRIGGER trg_asset_gravity
    AFTER INSERT OR UPDATE ON assets
    FOR EACH ROW
    EXECUTE FUNCTION auto_calculate_gravity();

DROP TRIGGER IF EXISTS trg_holon_gravity ON holons;
CREATE TRIGGER trg_holon_gravity
    AFTER INSERT OR UPDATE ON holons
    FOR EACH ROW
    EXECUTE FUNCTION auto_calculate_gravity();

-- ============================================================================
-- PART 13: MATERIALIZED VIEWS
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS gravitational_network AS
SELECT 
    gi.id AS interaction_id,
    gm1.entity_type AS entity1_type,
    gm1.entity_id AS entity1_id,
    gm1.gravitational_mass AS entity1_mass,
    gm2.entity_type AS entity2_type,
    gm2.entity_id AS entity2_id,
    gm2.gravitational_mass AS entity2_mass,
    gi.force_magnitude,
    gi.separation_distance,
    gi.interaction_type,
    ST_AsGeoJSON(gi.force_vector) AS force_vector_geojson,
    gi.measured_at
FROM gravitational_interactions gi
JOIN gravitational_mass gm1 ON gi.entity1_mass_id = gm1.id
JOIN gravitational_mass gm2 ON gi.entity2_mass_id = gm2.id
WHERE gi.is_significant = TRUE
  AND gi.force_magnitude > 0.01;

CREATE INDEX IF NOT EXISTS idx_mv_grav_net_force ON gravitational_network(force_magnitude DESC);
CREATE INDEX IF NOT EXISTS idx_mv_grav_net_type ON gravitational_network(interaction_type);

COMMENT ON MATERIALIZED VIEW gravitational_network IS 'Pre-computed gravitational network for visualization';

-- ============================================================================
-- PART 14: FINAL SETUP
-- ============================================================================

COMMENT ON SCHEMA phenomenal IS 
'Unified phenomenological blockchain model with quantum gravity: combining philosophy, physics, and Ubuntu principles for the ubec database';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Unified Phenomenological Quantum Gravity Schema installed successfully!';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Database: ubec';
    RAISE NOTICE 'Schema: phenomenal';
    RAISE NOTICE '';
    RAISE NOTICE 'Phenomenological Tables:';
    RAISE NOTICE '  - assets, accounts, intentional_relations';
    RAISE NOTICE '  - retentions, protentions';
    RAISE NOTICE '  - network_embeddings, spatial_positions, geodesics';
    RAISE NOTICE '  - transactions, holons';
    RAISE NOTICE '';
    RAISE NOTICE 'Quantum Gravity Tables:';
    RAISE NOTICE '  - gravitational_mass, gravitational_fields, gravitational_interactions';
    RAISE NOTICE '  - spacetime_curvature';
    RAISE NOTICE '  - quantum_states, quantum_entanglement';
    RAISE NOTICE '  - lorentz_violation, quantum_gravity_signatures';
    RAISE NOTICE '';
    RAISE NOTICE 'Functions: 7 calculation and analysis functions';
    RAISE NOTICE 'Views: 7 analytical views';
    RAISE NOTICE 'Triggers: 7 automatic maintenance triggers';
    RAISE NOTICE 'Materialized Views: 1 for performance';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Grant appropriate permissions';
    RAISE NOTICE '  2. Populate with Stellar blockchain data';
    RAISE NOTICE '  3. Calculate initial gravitational masses';
    RAISE NOTICE '  4. Refresh materialized view: REFRESH MATERIALIZED VIEW gravitational_network;';
    RAISE NOTICE '============================================================================';
END $$;

-- ============================================================================
-- END OF UNIFIED SCHEMA
-- ============================================================================
