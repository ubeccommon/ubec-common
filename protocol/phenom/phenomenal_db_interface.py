"""
Phenomenological Stellar Database Interface

This module provides async Python interfaces for interacting with the
phenomenological Stellar blockchain data model.

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 1.0.0
Date: October 12, 2025
"""

import asyncio
import asyncpg
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS (Match database custom types)
# ============================================================================

class PhenomenalMode(str, Enum):
    """How entities are given to consciousness/observers"""
    FULLY_PRESENT = 'fully_present'
    RETAINED = 'retained'
    PROTENDED = 'protended'
    CO_PRESENT = 'co_present'
    IMPLICITLY_MEANT = 'implicitly_meant'


class ExistenceMode(str, Enum):
    """Heideggerian modes of being"""
    READY_TO_HAND = 'ready_to_hand'  # Transparent practical use
    PRESENT_AT_HAND = 'present_at_hand'  # Objectified theoretical
    UNREADY_TO_HAND = 'unready_to_hand'  # Broken, problematic
    ABSENT = 'absent'


class IntentionalRelationType(str, Enum):
    """Types of directedness between entities"""
    TRUSTLINE = 'trustline'
    PAYMENT = 'payment'
    OFFER = 'offer'
    SPONSORSHIP = 'sponsorship'
    AUTHORIZATION = 'authorization'
    CLAIMABLE = 'claimable'
    LIQUIDITY_POOL = 'liquidity_pool'


class UbuntuPrinciple(str, Enum):
    """Four Ubuntu principles from UBEC project"""
    DIVERSITY = 'diversity'  # Air
    RECIPROCITY = 'reciprocity'  # Water
    MUTUALISM = 'mutualism'  # Earth
    REGENERATION = 'regeneration'  # Fire


class HolonicCategory(str, Enum):
    """Categories of holonic structure"""
    HOLON = 'holon'
    AUTONOMOUS_UNIT = 'autonomous_unit'
    COLLECTIVE = 'collective'
    NETWORK_NODE = 'network_node'
    ISOLATE = 'isolate'


class TemporalHorizon(str, Enum):
    """Temporal distance categories"""
    IMMEDIATE = 'immediate'  # Within seconds
    PROXIMAL = 'proximal'  # Within hours
    INTERMEDIATE = 'intermediate'  # Within days
    DISTANT = 'distant'  # Within weeks
    EXTENDED = 'extended'  # Beyond weeks


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Asset:
    """Represents an asset as phenomenon"""
    id: Optional[int] = None
    asset_code: str = ''
    issuer_address: str = ''
    phenomenal_mode: PhenomenalMode = PhenomenalMode.FULLY_PRESENT
    existence_mode: ExistenceMode = ExistenceMode.READY_TO_HAND
    ubuntu_principle: Optional[UbuntuPrinciple] = None
    internal_horizon: Dict[str, Any] = None
    external_horizon: Dict[str, Any] = None
    genesis_at: datetime = None
    retained_history: Optional[Dict[str, Any]] = None
    present_state: Dict[str, Any] = None
    protended_futures: Optional[Dict[str, Any]] = None
    temporal_horizon: TemporalHorizon = TemporalHorizon.INTERMEDIATE
    network_position: Optional[Tuple[float, float]] = None  # (lon, lat)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.internal_horizon is None:
            self.internal_horizon = {}
        if self.external_horizon is None:
            self.external_horizon = {}
        if self.present_state is None:
            self.present_state = {}


@dataclass
class Account:
    """Represents an account as Dasein (being-in-the-world)"""
    id: Optional[int] = None
    account_address: str = ''
    dasein_type: str = 'participant'
    comportment_pattern: Optional[str] = None
    holonic_category: HolonicCategory = HolonicCategory.NETWORK_NODE
    thrown_at: datetime = None
    facticity: Optional[Dict[str, Any]] = None
    network_position: Optional[Tuple[float, float]] = None
    primary_intentions: List[IntentionalRelationType] = None
    internal_horizon: Dict[str, Any] = None
    external_horizon: Dict[str, Any] = None
    ubuntu_scores: Optional[Dict[str, float]] = None
    present_state: Dict[str, Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.primary_intentions is None:
            self.primary_intentions = []
        if self.internal_horizon is None:
            self.internal_horizon = {}
        if self.external_horizon is None:
            self.external_horizon = {}
        if self.present_state is None:
            self.present_state = {}


@dataclass
class IntentionalRelation:
    """Represents intentional directedness between entities"""
    id: Optional[int] = None
    from_account_id: int = None
    to_account_id: Optional[int] = None
    asset_id: Optional[int] = None
    relation_type: IntentionalRelationType = IntentionalRelationType.TRUSTLINE
    phenomenal_mode: PhenomenalMode = PhenomenalMode.FULLY_PRESENT
    noema: Dict[str, Any] = None  # The intended object
    noesis: Dict[str, Any] = None  # The intending act
    relation_strength: Decimal = Decimal('0.5')
    reciprocity_factor: Optional[Decimal] = None
    emerged_at: datetime = None
    present_manifestation: Dict[str, Any] = None
    active: bool = True
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.noema is None:
            self.noema = {}
        if self.noesis is None:
            self.noesis = {}
        if self.present_manifestation is None:
            self.present_manifestation = {}


# ============================================================================
# DATABASE CONNECTION POOL
# ============================================================================

class PhenomenalDB:
    """
    Async database interface for phenomenological Stellar model
    
    Implements the service pattern: no standalone execution.
    All methods are async and use connection pooling.
    """

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 5432,
        database: str = 'stellar_phenomenal',
        user: str = 'postgres',
        password: str = None,
        min_pool_size: int = 10,
        max_pool_size: int = 20
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        """Initialize connection pool"""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=self.min_pool_size,
                max_size=self.max_pool_size,
                command_timeout=60
            )
            logger.info(f"Connected to phenomenal database: {self.database}")

    async def disconnect(self) -> None:
        """Close connection pool"""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            logger.info("Disconnected from phenomenal database")

    async def execute(self, query: str, *args) -> str:
        """Execute a query without returning results"""
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """Fetch multiple rows"""
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Fetch single row"""
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args) -> Any:
        """Fetch single value"""
        async with self._pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    # ========================================================================
    # ASSET OPERATIONS
    # ========================================================================

    async def create_asset(self, asset: Asset) -> int:
        """
        Create a new asset in the phenomenological model
        
        Returns:
            Asset ID
        """
        query = """
            INSERT INTO phenomenal.assets (
                asset_code, issuer_address, phenomenal_mode, existence_mode,
                ubuntu_principle, internal_horizon, external_horizon,
                genesis_at, present_state, temporal_horizon, network_position
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 
                      CASE WHEN $11 IS NOT NULL THEN ST_SetSRID(ST_MakePoint($11, $12), 4326) ELSE NULL END)
            RETURNING id
        """
        
        lon, lat = asset.network_position if asset.network_position else (None, None)
        
        asset_id = await self.fetchval(
            query,
            asset.asset_code,
            asset.issuer_address,
            asset.phenomenal_mode.value,
            asset.existence_mode.value,
            asset.ubuntu_principle.value if asset.ubuntu_principle else None,
            json.dumps(asset.internal_horizon),
            json.dumps(asset.external_horizon),
            asset.genesis_at or datetime.now(),
            json.dumps(asset.present_state),
            asset.temporal_horizon.value,
            lon, lat
        )
        
        logger.info(f"Created asset: {asset.asset_code} (ID: {asset_id})")
        return asset_id

    async def get_asset(self, asset_code: str, issuer_address: str) -> Optional[Asset]:
        """Get asset by code and issuer"""
        query = """
            SELECT 
                id, asset_code, issuer_address, phenomenal_mode, existence_mode,
                ubuntu_principle, internal_horizon, external_horizon,
                genesis_at, retained_history, present_state, protended_futures,
                temporal_horizon, 
                ST_X(network_position) AS lon, ST_Y(network_position) AS lat,
                created_at, updated_at
            FROM phenomenal.assets
            WHERE asset_code = $1 AND issuer_address = $2
        """
        
        row = await self.fetchrow(query, asset_code, issuer_address)
        if not row:
            return None
        
        return Asset(
            id=row['id'],
            asset_code=row['asset_code'],
            issuer_address=row['issuer_address'],
            phenomenal_mode=PhenomenalMode(row['phenomenal_mode']),
            existence_mode=ExistenceMode(row['existence_mode']),
            ubuntu_principle=UbuntuPrinciple(row['ubuntu_principle']) if row['ubuntu_principle'] else None,
            internal_horizon=row['internal_horizon'],
            external_horizon=row['external_horizon'],
            genesis_at=row['genesis_at'],
            retained_history=row['retained_history'],
            present_state=row['present_state'],
            protended_futures=row['protended_futures'],
            temporal_horizon=TemporalHorizon(row['temporal_horizon']),
            network_position=(row['lon'], row['lat']) if row['lon'] else None,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    async def update_asset_state(
        self,
        asset_id: int,
        present_state: Dict[str, Any]
    ) -> None:
        """
        Update asset present state (automatically creates retention of old state)
        """
        query = """
            UPDATE phenomenal.assets
            SET present_state = $2, updated_at = NOW()
            WHERE id = $1
        """
        await self.execute(query, asset_id, json.dumps(present_state))
        logger.info(f"Updated asset {asset_id} state")

    # ========================================================================
    # ACCOUNT OPERATIONS
    # ========================================================================

    async def create_account(self, account: Account) -> int:
        """
        Create a new account as Dasein
        
        Returns:
            Account ID
        """
        query = """
            INSERT INTO phenomenal.accounts (
                account_address, dasein_type, comportment_pattern, holonic_category,
                thrown_at, facticity, internal_horizon, external_horizon, present_state,
                network_position, primary_intentions
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9,
                      CASE WHEN $10 IS NOT NULL THEN ST_SetSRID(ST_MakePoint($10, $11), 4326) ELSE NULL END,
                      $12)
            RETURNING id
        """
        
        lon, lat = account.network_position if account.network_position else (None, None)
        intentions_array = [i.value for i in account.primary_intentions]
        
        account_id = await self.fetchval(
            query,
            account.account_address,
            account.dasein_type,
            account.comportment_pattern,
            account.holonic_category.value,
            account.thrown_at or datetime.now(),
            json.dumps(account.facticity) if account.facticity else None,
            json.dumps(account.internal_horizon),
            json.dumps(account.external_horizon),
            json.dumps(account.present_state),
            lon, lat,
            intentions_array
        )
        
        logger.info(f"Created account: {account.account_address} (ID: {account_id})")
        return account_id

    async def get_account(self, account_address: str) -> Optional[Account]:
        """Get account by address"""
        query = """
            SELECT 
                id, account_address, dasein_type, comportment_pattern, holonic_category,
                thrown_at, facticity, internal_horizon, external_horizon,
                ubuntu_scores, present_state,
                ST_X(network_position) AS lon, ST_Y(network_position) AS lat,
                primary_intentions, created_at, updated_at
            FROM phenomenal.accounts
            WHERE account_address = $1
        """
        
        row = await self.fetchrow(query, account_address)
        if not row:
            return None
        
        return Account(
            id=row['id'],
            account_address=row['account_address'],
            dasein_type=row['dasein_type'],
            comportment_pattern=row['comportment_pattern'],
            holonic_category=HolonicCategory(row['holonic_category']),
            thrown_at=row['thrown_at'],
            facticity=row['facticity'],
            internal_horizon=row['internal_horizon'],
            external_horizon=row['external_horizon'],
            ubuntu_scores=row['ubuntu_scores'],
            present_state=row['present_state'],
            network_position=(row['lon'], row['lat']) if row['lon'] else None,
            primary_intentions=[IntentionalRelationType(i) for i in (row['primary_intentions'] or [])],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    async def analyze_ubuntu_balance(self, account_id: int) -> Dict[str, float]:
        """
        Analyze Ubuntu principle balance for an account
        
        Returns:
            Dict with scores for diversity, reciprocity, mutualism, regeneration
        """
        query = "SELECT phenomenal.analyze_ubuntu_balance($1) AS scores"
        result = await self.fetchval(query, account_id)
        return result

    # ========================================================================
    # INTENTIONAL RELATIONS
    # ========================================================================

    async def create_relation(self, relation: IntentionalRelation) -> int:
        """
        Create an intentional relation (directedness)
        
        Returns:
            Relation ID
        """
        query = """
            INSERT INTO phenomenal.intentional_relations (
                from_account_id, to_account_id, asset_id, relation_type,
                phenomenal_mode, noema, noesis, relation_strength,
                reciprocity_factor, emerged_at, present_manifestation, active
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id
        """
        
        relation_id = await self.fetchval(
            query,
            relation.from_account_id,
            relation.to_account_id,
            relation.asset_id,
            relation.relation_type.value,
            relation.phenomenal_mode.value,
            json.dumps(relation.noema),
            json.dumps(relation.noesis),
            relation.relation_strength,
            relation.reciprocity_factor,
            relation.emerged_at or datetime.now(),
            json.dumps(relation.present_manifestation),
            relation.active
        )
        
        logger.info(f"Created intentional relation: {relation.relation_type.value} (ID: {relation_id})")
        return relation_id

    async def get_account_relations(
        self,
        account_id: int,
        relation_type: Optional[IntentionalRelationType] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all relations for an account
        
        Returns:
            List of relation dictionaries
        """
        query = """
            SELECT 
                ir.id, ir.relation_type, ir.relation_strength,
                ir.from_account_id, ir.to_account_id, ir.asset_id,
                ir.noema, ir.noesis, ir.active,
                a_from.account_address AS from_address,
                a_to.account_address AS to_address,
                ast.asset_code
            FROM phenomenal.intentional_relations ir
            LEFT JOIN phenomenal.accounts a_from ON ir.from_account_id = a_from.id
            LEFT JOIN phenomenal.accounts a_to ON ir.to_account_id = a_to.id
            LEFT JOIN phenomenal.assets ast ON ir.asset_id = ast.id
            WHERE (ir.from_account_id = $1 OR ir.to_account_id = $1)
        """
        
        params = [account_id]
        
        if relation_type:
            query += " AND ir.relation_type = $2"
            params.append(relation_type.value)
        
        if active_only:
            query += " AND ir.active = TRUE"
        
        rows = await self.fetch(query, *params)
        return [dict(row) for row in rows]

    # ========================================================================
    # TEMPORAL OPERATIONS
    # ========================================================================

    async def create_protention(
        self,
        entity_type: str,
        entity_id: int,
        expected_at: datetime,
        protended_content: Dict[str, Any],
        confidence: float = 0.5
    ) -> int:
        """
        Create an anticipation (protention) of future state
        
        Returns:
            Protention ID
        """
        query = """
            INSERT INTO phenomenal.protentions (
                entity_type, entity_id, protended_from, expected_at,
                temporal_distance, protended_content, expectation_confidence,
                protention_type
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """
        
        now = datetime.now()
        distance = expected_at - now
        
        # Determine protention type
        if distance < timedelta(hours=1):
            p_type = 'immediate'
        elif distance < timedelta(days=1):
            p_type = 'near'
        else:
            p_type = 'distant'
        
        protention_id = await self.fetchval(
            query,
            entity_type, entity_id, now, expected_at, distance,
            json.dumps(protended_content), Decimal(str(confidence)), p_type
        )
        
        logger.info(f"Created protention for {entity_type} {entity_id}")
        return protention_id

    async def get_temporal_stream(
        self,
        entity_type: str,
        entity_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get temporal consciousness stream (retentions + protentions)
        
        Returns:
            List of temporal states ordered by time
        """
        query = """
            SELECT * FROM phenomenal.temporal_consciousness
            WHERE entity_type = $1 AND entity_id = $2
            ORDER BY consciousness_now DESC, temporal_mode
            LIMIT $3
        """
        
        rows = await self.fetch(query, entity_type, entity_id, limit)
        return [dict(row) for row in rows]

    # ========================================================================
    # SPATIAL OPERATIONS
    # ========================================================================

    async def compute_spatial_proximity(
        self,
        entity1_type: str,
        entity1_id: int,
        entity2_type: str,
        entity2_id: int
    ) -> Dict[str, Any]:
        """
        Compute spatial proximity between two entities
        
        Returns:
            Dict with distance and proximity info
        """
        query = "SELECT phenomenal.compute_spatial_proximity($1, $2, $3, $4) AS result"
        result = await self.fetchval(query, entity1_type, entity1_id, entity2_type, entity2_id)
        return result

    async def find_nearby_accounts(
        self,
        asset_code: str,
        issuer_address: str,
        radius_km: float = 5.0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Find accounts spatially near an asset
        
        Returns:
            List of accounts with distances
        """
        query = """
            SELECT 
                a.id, a.account_address, a.comportment_pattern,
                ST_Distance(
                    a.network_position::geography,
                    ast.network_position::geography
                ) / 1000.0 AS distance_km
            FROM phenomenal.accounts a
            CROSS JOIN phenomenal.assets ast
            WHERE ast.asset_code = $1 AND ast.issuer_address = $2
              AND a.network_position IS NOT NULL
              AND ast.network_position IS NOT NULL
              AND ST_DWithin(
                  a.network_position::geography,
                  ast.network_position::geography,
                  $3 * 1000
              )
            ORDER BY distance_km
            LIMIT $4
        """
        
        rows = await self.fetch(query, asset_code, issuer_address, radius_km, limit)
        return [dict(row) for row in rows]

    async def identify_spatial_clusters(
        self,
        eps_meters: float = 2000,
        min_points: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Identify spatial clusters using DBSCAN
        
        Returns:
            List of clusters with member counts and extents
        """
        query = """
            SELECT 
                cluster_id,
                COUNT(*) AS member_count,
                array_agg(account_address) AS members,
                ST_AsGeoJSON(ST_ConvexHull(ST_Collect(network_position))) AS spatial_extent
            FROM (
                SELECT 
                    ST_ClusterDBSCAN(network_position, eps := $1, minpoints := $2) OVER() AS cluster_id,
                    account_address,
                    network_position
                FROM phenomenal.accounts
                WHERE network_position IS NOT NULL
            ) clustered
            WHERE cluster_id IS NOT NULL
            GROUP BY cluster_id
            ORDER BY member_count DESC
        """
        
        rows = await self.fetch(query, eps_meters, min_points)
        return [dict(row) for row in rows]

    # ========================================================================
    # HOLONIC OPERATIONS
    # ========================================================================

    async def create_holon(
        self,
        holon_name: str,
        holon_type: str,
        constituent_accounts: List[int],
        autonomy_score: float,
        integration_score: float
    ) -> int:
        """
        Create a holon (entity that is both whole and part)
        
        Returns:
            Holon ID
        """
        query = """
            INSERT INTO phenomenal.holons (
                holon_name, holon_type, constituent_accounts,
                autonomy_score, integration_score, emerged_at
            ) VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        """
        
        holon_id = await self.fetchval(
            query,
            holon_name, holon_type, constituent_accounts,
            Decimal(str(autonomy_score)), Decimal(str(integration_score)),
            datetime.now()
        )
        
        logger.info(f"Created holon: {holon_name} (ID: {holon_id})")
        return holon_id

    async def get_active_holons(self, min_integration: float = 0.5) -> List[Dict[str, Any]]:
        """
        Get active holons with high integration
        
        Returns:
            List of holons
        """
        query = """
            SELECT 
                id, holon_name, holon_type,
                autonomy_score, integration_score,
                array_length(constituent_accounts, 1) AS member_count,
                emerged_at
            FROM phenomenal.holons
            WHERE dissolved_at IS NULL
              AND integration_score >= $1
            ORDER BY integration_score DESC
        """
        
        rows = await self.fetch(query, Decimal(str(min_integration)))
        return [dict(row) for row in rows]

    # ========================================================================
    # ANALYTICAL QUERIES
    # ========================================================================

    async def get_network_state(self) -> List[Dict[str, Any]]:
        """
        Get current network state (present phenomenal field)
        
        Returns:
            List of assets with holder counts and metrics
        """
        query = "SELECT * FROM phenomenal.current_network_state"
        rows = await self.fetch(query)
        return [dict(row) for row in rows]

    async def get_intentional_network(
        self,
        min_strength: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Get intentional network (graph of directedness)
        
        Returns:
            List of active relations
        """
        query = """
            SELECT * FROM phenomenal.intentional_network
            WHERE relation_strength >= $1
            ORDER BY relation_strength DESC
        """
        rows = await self.fetch(query, Decimal(str(min_strength)))
        return [dict(row) for row in rows]

    async def compute_phenomenal_prominence(
        self,
        entity_type: str,
        entity_id: int
    ) -> Dict[str, float]:
        """
        Compute centrality (phenomenal prominence) for entity
        
        Returns:
            Dict with centrality scores
        """
        query = "SELECT phenomenal.compute_phenomenal_prominence($1, $2) AS scores"
        result = await self.fetchval(query, entity_type, entity_id)
        return result


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def initialize_phenomenal_db(
    host: str = 'localhost',
    database: str = 'stellar_phenomenal',
    user: str = 'postgres',
    password: str = None
) -> PhenomenalDB:
    """
    Initialize and connect to phenomenological database
    
    Returns:
        Connected PhenomenalDB instance
    """
    db = PhenomenalDB(
        host=host,
        database=database,
        user=user,
        password=password
    )
    await db.connect()
    return db


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_usage():
    """Demonstrate usage of phenomenological database interface"""
    
    # Initialize
    db = await initialize_phenomenal_db()
    
    try:
        # Create an asset
        ubec_asset = Asset(
            asset_code='UBEC',
            issuer_address='GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            ubuntu_principle=UbuntuPrinciple.DIVERSITY,
            genesis_at=datetime.now() - timedelta(days=365),
            internal_horizon={
                'supply': {'total': 1000000, 'circulating': 750000},
                'properties': {'divisible': True}
            },
            external_horizon={
                'network_context': {'stellar_network': 'mainnet'},
                'market_context': {}
            },
            present_state={'active_holders': 1200, 'daily_volume': 50000}
        )
        
        asset_id = await db.create_asset(ubec_asset)
        print(f"Created asset with ID: {asset_id}")
        
        # Create an account
        account = Account(
            account_address='GYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY',
            dasein_type='participant',
            comportment_pattern='holder',
            holonic_category=HolonicCategory.NETWORK_NODE,
            thrown_at=datetime.now() - timedelta(days=180),
            internal_horizon={'joined_via': 'referral'},
            present_state={'active': True}
        )
        
        account_id = await db.create_account(account)
        print(f"Created account with ID: {account_id}")
        
        # Create intentional relation (trustline)
        relation = IntentionalRelation(
            from_account_id=account_id,
            asset_id=asset_id,
            relation_type=IntentionalRelationType.TRUSTLINE,
            noema={'intended_object': {'asset': 'UBEC', 'limit': 10000}},
            noesis={'act_type': 'trustline', 'act_quality': 'belief'},
            relation_strength=Decimal('0.8')
        )
        
        relation_id = await db.create_relation(relation)
        print(f"Created relation with ID: {relation_id}")
        
        # Analyze Ubuntu balance
        ubuntu_scores = await db.analyze_ubuntu_balance(account_id)
        print(f"Ubuntu scores: {ubuntu_scores}")
        
        # Get network state
        network_state = await db.get_network_state()
        print(f"Network has {len(network_state)} active assets")
        
    finally:
        await db.disconnect()


if __name__ == '__main__':
    # Run example
    asyncio.run(example_usage())
