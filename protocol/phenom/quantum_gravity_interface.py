"""
Quantum Gravity Interface for Phenomenological Blockchain Model

This module provides a Python interface for working with gravity and quantum
gravity concepts in the phenomenological blockchain database.

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Design Principles:
    - Strict async operations (Principle #5)
    - Service pattern with registry (Principles #2, #3)
    - Single source of truth - database (Principle #4)
    - No duplicate code (Principle #12)
    - Explicit schema names in all queries (Principle #8)

Version: 1.0.1
Date: November 3, 2025
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple
import json

import asyncpg
from shapely.geometry import Point, LineString, Polygon
from shapely import wkt, wkb
import numpy as np


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class GravitationalMass:
    """Represents gravitational mass of an entity"""
    id: Optional[int]
    entity_type: str
    entity_id: int
    gravitational_mass: Decimal
    inertial_mass: Decimal
    mass_basis: Dict[str, Any]
    calculated_at: datetime
    valid_until: Optional[datetime] = None
    mass_trajectory: Optional[Dict[str, Any]] = None


@dataclass
class GravitationalField:
    """Represents gravitational field around massive entity"""
    id: Optional[int]
    source_mass_id: int
    field_profile: Dict[str, Any]
    influence_radius: Decimal
    field_geometry: Optional[Polygon]
    field_type: str
    field_strength: Decimal
    is_static: bool = False
    temporal_variation: Optional[Dict[str, Any]] = None
    calculated_at: Optional[datetime] = None


@dataclass
class GravitationalInteraction:
    """Represents force between two massive entities"""
    id: Optional[int]
    entity1_mass_id: int
    entity2_mass_id: int
    force_magnitude: Decimal
    force_direction: Optional[Decimal]
    force_vector: Optional[LineString]
    separation_distance: Decimal
    network_hops: Optional[int]
    potential_energy: Optional[Decimal]
    binding_energy: Optional[Decimal]
    interaction_type: str
    is_significant: bool = True
    measured_at: Optional[datetime] = None


@dataclass
class SpacetimeCurvature:
    """Represents how mass curves spacetime"""
    id: Optional[int]
    source_mass_id: int
    ricci_scalar: Optional[Decimal]
    curvature_tensor: Dict[str, Any]
    geodesic_deviations: Dict[str, Any]
    curvature_geometry: Optional[Polygon]
    curvature_radius: Decimal
    metric_signature: Dict[str, Any]
    light_deflection: Optional[Decimal]
    time_dilation_factor: Optional[Decimal]
    calculated_at: Optional[datetime] = None


@dataclass
class QuantumState:
    """Represents quantum mechanical state of entity"""
    id: Optional[int]
    entity_type: str
    entity_id: int
    state_vector: Dict[str, Any]
    energy_level: int
    energy_value: Decimal
    possible_transitions: Dict[str, Any]
    position_uncertainty: Optional[Decimal] = None
    momentum_uncertainty: Optional[Decimal] = None
    energy_time_uncertainty: Optional[Decimal] = None
    decoherence_rate: Optional[Decimal] = None
    state_prepared_at: Optional[datetime] = None


@dataclass
class QuantumEntanglement:
    """Represents entanglement between two quantum states"""
    id: Optional[int]
    entity1_state_id: int
    entity2_state_id: int
    entanglement_entropy: Decimal
    correlation_coefficient: Decimal
    joint_state: Dict[str, Any]
    bell_parameter: Optional[Decimal] = None
    violates_bell_inequality: Optional[bool] = None
    is_separable: bool = False
    separation_distance: Optional[Decimal] = None
    instantaneous_correlation: Optional[bool] = None
    entanglement_created_at: Optional[datetime] = None


@dataclass
class LorentzViolation:
    """Represents Lorentz symmetry violation"""
    id: Optional[int]
    region_geometry: Polygon
    anisotropy_vector: Dict[str, Any]
    violation_magnitude: Decimal
    violation_type: str
    preferred_direction: Optional[LineString] = None
    dispersion_coefficients: Optional[Dict[str, Any]] = None
    speed_anisotropy: Optional[Decimal] = None
    test_statistic: Optional[Decimal] = None
    significance_level: Optional[Decimal] = None
    is_statistically_significant: Optional[bool] = None
    observed_at: Optional[datetime] = None


# ============================================================================
# QUANTUM GRAVITY SERVICE
# ============================================================================

class QuantumGravityService:
    """
    Service for quantum gravity operations on blockchain network.
    
    This service provides methods to:
    - Calculate gravitational masses
    - Compute gravitational interactions
    - Analyze spacetime curvature
    - Track quantum states and entanglement
    - Detect Lorentz violations
    
    All operations are strictly async (Principle #5).
    All queries use explicit schema names (Principle #8).
    """
    
    def __init__(self, pool: asyncpg.Pool):
        """
        Initialize quantum gravity service.
        
        Args:
            pool: AsyncPG connection pool
        """
        self.pool = pool
    
    # ========================================================================
    # GRAVITATIONAL MASS OPERATIONS
    # ========================================================================
    
    async def calculate_mass(
        self,
        entity_type: str,
        entity_id: int
    ) -> Decimal:
        """
        Calculate gravitational mass for an entity.
        
        Args:
            entity_type: Type of entity ('account', 'asset', 'holon')
            entity_id: ID of the entity
            
        Returns:
            Calculated gravitational mass
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT phenomenal.calculate_gravitational_mass($1, $2)",
                entity_type,
                entity_id
            )
            return Decimal(str(result))
    
    async def get_mass(
        self,
        entity_type: str,
        entity_id: int,
        at_time: Optional[datetime] = None
    ) -> Optional[GravitationalMass]:
        """
        Get current gravitational mass for an entity.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            at_time: Optional time for historical lookup
            
        Returns:
            GravitationalMass object or None if not found
        """
        async with self.pool.acquire() as conn:
            if at_time is None:
                query = """
                    SELECT * FROM phenomenal.gravitational_mass
                    WHERE entity_type = $1 AND entity_id = $2
                    AND (valid_until IS NULL OR valid_until > NOW())
                    ORDER BY calculated_at DESC
                    LIMIT 1
                """
                row = await conn.fetchrow(query, entity_type, entity_id)
            else:
                query = """
                    SELECT * FROM phenomenal.gravitational_mass
                    WHERE entity_type = $1 AND entity_id = $2
                    AND calculated_at <= $3
                    AND (valid_until IS NULL OR valid_until > $3)
                    ORDER BY calculated_at DESC
                    LIMIT 1
                """
                row = await conn.fetchrow(query, entity_type, entity_id, at_time)
            
            if not row:
                return None
            
            return GravitationalMass(
                id=row['id'],
                entity_type=row['entity_type'],
                entity_id=row['entity_id'],
                gravitational_mass=row['gravitational_mass'],
                inertial_mass=row['inertial_mass'],
                mass_basis=row['mass_basis'],
                calculated_at=row['calculated_at'],
                valid_until=row['valid_until'],
                mass_trajectory=row.get('mass_trajectory')
            )
    
    async def get_top_masses(
        self,
        entity_type: Optional[str] = None,
        limit: int = 10
    ) -> List[GravitationalMass]:
        """
        Get entities with highest gravitational mass.
        
        Args:
            entity_type: Optional filter by entity type
            limit: Number of results
            
        Returns:
            List of GravitationalMass objects
        """
        async with self.pool.acquire() as conn:
            if entity_type:
                query = """
                    SELECT * FROM phenomenal.gravitational_mass
                    WHERE entity_type = $1
                    AND (valid_until IS NULL OR valid_until > NOW())
                    ORDER BY gravitational_mass DESC
                    LIMIT $2
                """
                rows = await conn.fetch(query, entity_type, limit)
            else:
                query = """
                    SELECT * FROM phenomenal.gravitational_mass
                    WHERE valid_until IS NULL OR valid_until > NOW()
                    ORDER BY gravitational_mass DESC
                    LIMIT $1
                """
                rows = await conn.fetch(query, limit)
            
            return [
                GravitationalMass(
                    id=row['id'],
                    entity_type=row['entity_type'],
                    entity_id=row['entity_id'],
                    gravitational_mass=row['gravitational_mass'],
                    inertial_mass=row['inertial_mass'],
                    mass_basis=row['mass_basis'],
                    calculated_at=row['calculated_at'],
                    valid_until=row['valid_until'],
                    mass_trajectory=row.get('mass_trajectory')
                )
                for row in rows
            ]
    
    # ========================================================================
    # GRAVITATIONAL INTERACTION OPERATIONS
    # ========================================================================
    
    async def calculate_gravitational_force(
        self,
        mass1_id: int,
        mass2_id: int
    ) -> Decimal:
        """
        Calculate gravitational force between two masses.
        
        Args:
            mass1_id: ID of first mass
            mass2_id: ID of second mass
            
        Returns:
            Force magnitude
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT phenomenal.calculate_gravitational_force($1, $2)",
                mass1_id,
                mass2_id
            )
            return Decimal(str(result))
    
    async def get_strong_interactions(
        self,
        min_force: Decimal = Decimal('0.1'),
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get strong gravitational interactions.
        
        Args:
            min_force: Minimum force threshold
            limit: Maximum results
            
        Returns:
            List of interaction dictionaries
        """
        async with self.pool.acquire() as conn:
            query = """
                SELECT * FROM phenomenal.strong_gravitational_interactions
                WHERE force_magnitude >= $1
                ORDER BY force_magnitude DESC
                LIMIT $2
            """
            rows = await conn.fetch(query, min_force, limit)
            return [dict(row) for row in rows]
    
    # ========================================================================
    # SPACETIME CURVATURE OPERATIONS
    # ========================================================================
    
    async def calculate_curvature(
        self,
        mass_id: int
    ) -> Decimal:
        """
        Calculate spacetime curvature (Ricci scalar) around a mass.
        
        Args:
            mass_id: ID of gravitational mass
            
        Returns:
            Ricci scalar (curvature measure)
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT phenomenal.calculate_spacetime_curvature($1)",
                mass_id
            )
            return Decimal(str(result))
    
    async def get_curved_regions(
        self,
        min_curvature: Decimal = Decimal('0.01'),
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get regions with significant spacetime curvature.
        
        Args:
            min_curvature: Minimum absolute Ricci scalar
            limit: Maximum number of results
            
        Returns:
            List of curved region dictionaries
        """
        async with self.pool.acquire() as conn:
            query = """
                SELECT * FROM phenomenal.curved_spacetime_regions
                WHERE ABS(ricci_scalar) >= $1
                ORDER BY ABS(ricci_scalar) DESC
                LIMIT $2
            """
            rows = await conn.fetch(query, min_curvature, limit)
            return [dict(row) for row in rows]
    
    # ========================================================================
    # QUANTUM STATE OPERATIONS
    # ========================================================================
    
    async def create_quantum_state(
        self,
        state: QuantumState
    ) -> int:
        """
        Create a quantum state for an entity.
        
        Args:
            state: QuantumState to create
            
        Returns:
            ID of created state
        """
        async with self.pool.acquire() as conn:
            query = """
                INSERT INTO phenomenal.quantum_states (
                    entity_type, entity_id, state_vector, energy_level,
                    energy_value, possible_transitions, position_uncertainty,
                    momentum_uncertainty, energy_time_uncertainty, decoherence_rate,
                    state_prepared_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING id
            """
            state_id = await conn.fetchval(
                query,
                state.entity_type,
                state.entity_id,
                json.dumps(state.state_vector),
                state.energy_level,
                state.energy_value,
                json.dumps(state.possible_transitions),
                state.position_uncertainty,
                state.momentum_uncertainty,
                state.energy_time_uncertainty,
                state.decoherence_rate,
                state.state_prepared_at or datetime.now()
            )
            return state_id
    
    async def get_quantum_state(
        self,
        entity_type: str,
        entity_id: int
    ) -> Optional[QuantumState]:
        """
        Get current quantum state for an entity.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            
        Returns:
            QuantumState object or None if not found
        """
        async with self.pool.acquire() as conn:
            query = """
                SELECT * FROM phenomenal.quantum_states
                WHERE entity_type = $1 AND entity_id = $2
                ORDER BY state_prepared_at DESC
                LIMIT 1
            """
            row = await conn.fetchrow(query, entity_type, entity_id)
            
            if not row:
                return None
            
            return QuantumState(
                id=row['id'],
                entity_type=row['entity_type'],
                entity_id=row['entity_id'],
                state_vector=row['state_vector'],
                energy_level=row['energy_level'],
                energy_value=row['energy_value'],
                possible_transitions=row['possible_transitions'],
                position_uncertainty=row['position_uncertainty'],
                momentum_uncertainty=row['momentum_uncertainty'],
                energy_time_uncertainty=row['energy_time_uncertainty'],
                decoherence_rate=row['decoherence_rate'],
                state_prepared_at=row['state_prepared_at']
            )
    
    # ========================================================================
    # QUANTUM ENTANGLEMENT OPERATIONS
    # ========================================================================
    
    async def calculate_entanglement_entropy(
        self,
        state1_id: int,
        state2_id: int
    ) -> Decimal:
        """
        Calculate entanglement entropy between two quantum states.
        
        Args:
            state1_id: ID of first quantum state
            state2_id: ID of second quantum state
            
        Returns:
            Entanglement entropy (0 = separable, 1 = maximally entangled)
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT phenomenal.calculate_entanglement_entropy($1, $2)",
                state1_id,
                state2_id
            )
            return Decimal(str(result))
    
    async def find_entangled_states(
        self,
        min_entropy: Decimal = Decimal('0.5'),
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Find strongly entangled quantum states.
        
        Args:
            min_entropy: Minimum entanglement entropy
            limit: Maximum results
            
        Returns:
            List of entanglement dictionaries
        """
        async with self.pool.acquire() as conn:
            query = """
                SELECT * FROM phenomenal.active_quantum_entanglements
                WHERE entanglement_entropy >= $1
                ORDER BY entanglement_entropy DESC
                LIMIT $2
            """
            rows = await conn.fetch(query, min_entropy, limit)
            return [dict(row) for row in rows]
    
    # ========================================================================
    # LORENTZ VIOLATION OPERATIONS
    # ========================================================================
    
    async def detect_lorentz_violation(
        self,
        region: Polygon,
        violation_type: str,
        test_statistic: Decimal,
        significance_level: Decimal = Decimal('0.05')
    ) -> Optional[int]:
        """
        Detect and record Lorentz symmetry violation.
        
        Args:
            region: Geographic region being tested
            violation_type: Type of violation detected
            test_statistic: Statistical test result
            significance_level: P-value threshold
            
        Returns:
            ID of violation record or None if not significant
        """
        is_significant = test_statistic > (1 / significance_level)
        
        if not is_significant:
            return None
        
        async with self.pool.acquire() as conn:
            region_wkb = wkb.dumps(region)
            
            query = """
                INSERT INTO phenomenal.lorentz_violation (
                    region_geometry, violation_type, violation_magnitude,
                    test_statistic, significance_level, is_statistically_significant,
                    anisotropy_vector, observed_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """
            violation_id = await conn.fetchval(
                query,
                region_wkb,
                violation_type,
                test_statistic / 10,  # Normalize to magnitude
                test_statistic,
                significance_level,
                is_significant,
                json.dumps({"temporal": 0, "spatial": {"x": 0, "y": 0}}),
                datetime.now()
            )
            return violation_id
    
    async def get_lorentz_hotspots(
        self,
        min_magnitude: Decimal = Decimal('0.1'),
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get regions with significant Lorentz violations.
        
        Args:
            min_magnitude: Minimum violation magnitude
            limit: Maximum number of results
            
        Returns:
            List of violation hotspot dictionaries
        """
        async with self.pool.acquire() as conn:
            query = """
                SELECT * FROM phenomenal.lorentz_violation_hotspots
                WHERE violation_magnitude >= $1
                ORDER BY violation_magnitude DESC
                LIMIT $2
            """
            rows = await conn.fetch(query, min_magnitude, limit)
            return [dict(row) for row in rows]
    
    # ========================================================================
    # ANALYSIS AND VISUALIZATION
    # ========================================================================
    
    async def get_gravity_network(
        self,
        min_force: Decimal = Decimal('0.01')
    ) -> Dict[str, Any]:
        """
        Get complete gravitational network for visualization.
        
        Args:
            min_force: Minimum force threshold
            
        Returns:
            Dictionary with nodes (masses) and edges (interactions)
        """
        async with self.pool.acquire() as conn:
            # Get nodes (massive entities)
            nodes_query = """
                SELECT entity_type, entity_id, gravitational_mass,
                       ST_AsText(field_geometry) as geometry
                FROM phenomenal.network_gravity_map
                ORDER BY gravitational_mass DESC
            """
            nodes = await conn.fetch(nodes_query)
            
            # Get edges (interactions)
            edges_query = """
                SELECT entity1_type, entity1_id, entity2_type, entity2_id,
                       force_magnitude, interaction_type,
                       ST_AsText(force_vector) as vector
                FROM phenomenal.strong_gravitational_interactions
                WHERE force_magnitude >= $1
            """
            edges = await conn.fetch(edges_query, min_force)
            
            return {
                "nodes": [dict(node) for node in nodes],
                "edges": [dict(edge) for edge in edges],
                "metadata": {
                    "node_count": len(nodes),
                    "edge_count": len(edges),
                    "min_force_threshold": float(min_force)
                }
            }
    
    async def get_quantum_network(
        self,
        min_entanglement: Decimal = Decimal('0.3')
    ) -> Dict[str, Any]:
        """
        Get quantum entanglement network for visualization.
        
        Args:
            min_entanglement: Minimum entanglement entropy
            
        Returns:
            Dictionary with quantum nodes and entanglement edges
        """
        async with self.pool.acquire() as conn:
            query = """
                SELECT * FROM phenomenal.active_quantum_entanglements
                WHERE entanglement_entropy >= $1
                ORDER BY entanglement_entropy DESC
            """
            entanglements = await conn.fetch(query, min_entanglement)
            
            return {
                "entanglements": [dict(ent) for ent in entanglements],
                "metadata": {
                    "entanglement_count": len(entanglements),
                    "min_entropy_threshold": float(min_entanglement)
                }
            }
    
    async def analyze_network_gravity(self) -> Dict[str, Any]:
        """
        Perform comprehensive gravity analysis of network.
        
        Returns:
            Dictionary with gravity statistics and insights
        """
        async with self.pool.acquire() as conn:
            # Total mass in network
            total_mass = await conn.fetchval("""
                SELECT SUM(gravitational_mass)
                FROM phenomenal.gravitational_mass
                WHERE valid_until IS NULL OR valid_until > NOW()
            """)
            
            # Number of massive entities
            entity_count = await conn.fetchval("""
                SELECT COUNT(*)
                FROM phenomenal.gravitational_mass
                WHERE valid_until IS NULL OR valid_until > NOW()
            """)
            
            # Average mass
            avg_mass = await conn.fetchval("""
                SELECT AVG(gravitational_mass)
                FROM phenomenal.gravitational_mass
                WHERE valid_until IS NULL OR valid_until > NOW()
            """)
            
            # Number of significant interactions
            interaction_count = await conn.fetchval("""
                SELECT COUNT(*)
                FROM phenomenal.gravitational_interactions
                WHERE is_significant = TRUE
            """)
            
            # Regions with high curvature
            curved_regions = await conn.fetchval("""
                SELECT COUNT(*)
                FROM phenomenal.spacetime_curvature
                WHERE ABS(ricci_scalar) > 0.1
            """)
            
            return {
                "total_mass": float(total_mass) if total_mass else 0,
                "entity_count": entity_count,
                "average_mass": float(avg_mass) if avg_mass else 0,
                "interaction_count": interaction_count,
                "curved_region_count": curved_regions,
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    async def close(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def create_quantum_gravity_service(
    database_url: str
) -> QuantumGravityService:
    """
    Create and initialize QuantumGravityService.
    
    Args:
        database_url: PostgreSQL connection string
        
    Returns:
        Initialized QuantumGravityService
    """
    pool = await asyncpg.create_pool(database_url)
    return QuantumGravityService(pool)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_usage():
    """Example usage of QuantumGravityService"""
    
    # Create service
    service = await create_quantum_gravity_service(
        "postgresql://user:pass@localhost/dbname"
    )
    
    # Calculate mass for an account
    mass = await service.calculate_mass('account', 12345)
    print(f"Gravitational mass: {mass}")
    
    # Get top 10 most massive entities
    top_masses = await service.get_top_masses(limit=10)
    for gm in top_masses:
        print(f"{gm.entity_type} {gm.entity_id}: mass = {gm.gravitational_mass}")
    
    # Get strong gravitational interactions
    interactions = await service.get_strong_interactions(min_force=Decimal('0.5'))
    print(f"Found {len(interactions)} strong interactions")
    
    # Analyze overall network gravity
    analysis = await service.analyze_network_gravity()
    print(f"Network analysis: {analysis}")
    
    # Get gravity network for visualization
    gravity_net = await service.get_gravity_network()
    print(f"Gravity network: {gravity_net['metadata']}")
    
    # Close connection pool
    await service.close()


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
