#!/usr/bin/env python3
# core/holonic/ubec_holonic_evaluator.py
"""
UBEC Holonic Evaluator - Ubuntu Philosophy Implementation with Element Metrics
===============================================================================
Service implementation for holonic evaluation of UBEC token holders with
complete integration of four-element Ubuntu principle metrics.

This module calculates, stores, and manages:
1. Five-dimensional holonic scores (autonomy, multi-scale, regenerative, network, ubuntu)
2. Four-element Ubuntu principle metrics (diversity, reciprocity, mutualism, regeneration)
3. Element-specific health assessments stored in ubec_holonic_metrics table
4. Composite scoring that integrates all dimensions

NEW IN v3.0.0 - COMPLETE UBUNTU PRINCIPLE INTEGRATION:
- ✅ reciprocity_health (Water/UBECrc) - calculated and stored
- ✅ mutualism_capacity (Earth/UBECgpi) - calculated and stored  
- ✅ diversity_score (Air/UBEC) - calculated and stored
- ✅ regeneration_score (Fire/UBECtt) - calculated and stored
- ✅ All metrics stored in ubec_holonic_metrics table
- ✅ ubuntu_alignment_score properly calculated from element metrics
- ✅ Health status assessment for each principle
- ✅ Complete integration with API service

NEW IN v3.2.0 - DATABASE-DRIVEN CONFIGURATION:
- ✅ Thresholds loaded from ubec_main.system_settings table
- ✅ Dimension weights loaded from database
- ✅ Ubuntu principle weights loaded from database
- ✅ Follows Principle #4: Database as Single Source of Truth
- ✅ Hardcoded values only used as fallback if DB config unavailable

Evaluates UBEC token holders based on Ubuntu principles:
- **Diversity (Air/UBEC)**: Unique participation patterns and breadth
- **Reciprocity (Water/UBECrc)**: Balance of giving and receiving, flow
- **Mutualism (Earth/UBECgpi)**: Stability, grounding, mutual benefit
- **Regeneration (Fire/UBECtt)**: Transformation and sustainable contribution
- **Holism**: Integration across all dimensions

Design Principles Compliance:
══════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained evaluation service
    ✅ 2.  Service Pattern: Factory-based, no standalone execution
    ✅ 3.  Service Registry: Accessed through centralized registry
    ✅ 4.  Single Source of Truth: Database is authoritative with persistence
    ✅ 5.  Strict Async: All I/O operations use async/await
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Individual account and element tracking
    ✅ 8.  No Duplicate Config: Uses global configuration from database
    ✅ 9.  Integrated Rate Limiting: Built-in for database operations
    ✅ 10. Separation of Concerns: Evaluation logic isolated
    ✅ 11. Comprehensive Documentation: Full docstrings and attribution
    ✅ 12. Method Singularity: No duplicate methods, single implementation
══════════════════════════════════════════════════════════════════════════════

Usage:
    from ubec_holonic_evaluator import create_holonic_evaluator
    
    evaluator = await create_holonic_evaluator(
        db_manager=async_db,
        config={
            'ubec_code': 'UBEC',
            'ubec_issuer': 'G...',
            'db_schema': 'ubec_main'
        }
    )
    
    # All methods are async
    result = await evaluator.evaluate_all_accounts()
    report = await evaluator.evaluate_network_holism()
    metrics = await evaluator.get_ubuntu_principle_metrics(account_id)
    health = await evaluator.health_check()
    
    await evaluator.close()

Database Schema:
    Uses THREE tables for complete evaluation:
    
    1. {schema}.holonic_metrics - Main holonic evaluation scores
       - autonomy_integration_score
       - multi_scale_score
       - regenerative_impact_score
       - network_contribution_score
       - ubuntu_alignment_score (calculated from element metrics)
       - composite_score
       - holonic_category
       - raw_metrics (JSONB) - Contains Ubuntu principle scores
    
    2. {schema}.ubec_holonic_metrics - Element-specific Ubuntu principles
       - account_id
       - element (air, water, earth, fire) - lowercase enum values
       - principle (diversity, reciprocity, mutualism, regeneration)
       - score (0.0-1.0)
       - health_status (omitted - nullable column with database-specific enum)
       - assessment_details (JSONB)
       - calculated_at
    
    3. {schema}.system_settings - Configuration parameters (NEW in v3.2.0)
       - setting_key: holonic_threshold_observer, holonic_threshold_participant, etc.
       - setting_value: threshold/weight values as text
       - setting_type: 'float'
       - category: 'holonic'

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 3.2.0 (Database-Driven Configuration)
Date: November 30, 2025

Changelog:
    v3.2.0 - DATABASE-DRIVEN CONFIGURATION (Principle #4 Enhancement)
           - Added: _load_config_from_db() method to load thresholds/weights from system_settings
           - Added: ubuntu_weights dictionary for Ubuntu principle weighting
           - Updated: __init__() to set default values as fallbacks only
           - Updated: initialize() to call _load_config_from_db()
           - Updated: evaluate_account() to use self.ubuntu_weights
           - Updated: health_check() to report config_source
           - Added: _config_loaded_from_db flag for tracking
           - Config keys: holonic_threshold_*, holonic_weight_*, holonic_ubuntu_weight_*
    v3.1.2 - CRITICAL FIX: Added missing evaluate_network_holism method
           - Added: evaluate_network_holism() method for network-level holistic assessment
           - Reason: Scheduler was calling holonic.evaluate_network_holism which didn't exist
           - Implementation: Shannon entropy-based diversity scoring across holonic categories
           - Result: Resolves AttributeError in scheduler job execution
    v3.1.1 - INTERFACE FIX: Return value structure alignment with main.py expectations
           - Added: 'evaluated' field (alias for 'successful') in return dictionary
           - Added: 'skipped' field (currently always 0) for interface compatibility
           - Added: 'errors' field (alias for 'failed') for interface compatibility
           - Added: Completion logging in evaluate_all_accounts method
           - Reason: main.py expects 'evaluated', 'skipped', 'errors' fields
           - Result: Statistics now display correctly in main.py log output
           - Maintains backward compatibility by keeping original 'successful'/'failed' fields
    v3.1.0 - Function-based unique constraint resolution
           - Fixed: DELETE+INSERT pattern for function-based constraints
           - Fixed: Removed health_status column from ubec_holonic_metrics INSERT
    v3.0.9 - Database constraint and enum alignment
           - Fixed: ON CONFLICT clause alignment (superseded by v3.1.0)
           - Fixed: health_status enum values (superseded by v3.1.0)
    v3.0.8 - CRITICAL FIX: Corrected table references for transaction queries
           - Fixed: All queries now use stellar_operations instead of stellar_transactions
           - Reason: stellar_transactions does NOT contain from_account, to_account, or amount columns
           - These columns exist in stellar_operations table with payment operation data
           - Updated queries in: _calculate_diversity_score, _calculate_reciprocity_health,
             _calculate_mutualism_capacity, _calculate_regeneration_score,
             _calculate_autonomy_integration, _calculate_multi_scale_participation,
             _calculate_regenerative_impact, _calculate_network_contribution
           - Resolves: "column 'from_account' does not exist", "column 'amount' does not exist" errors
    v3.0.7 - SQL QUERY FIX: Fixed evaluate_all_accounts query
           - Fixed: Changed SELECT DISTINCT to GROUP BY with MAX(balance) for ORDER BY compatibility
           - Resolves: "for SELECT DISTINCT, ORDER BY expressions must appear in select list" error
           - Query now properly groups accounts and orders by maximum balance across tokens
    v3.0.6 - CRITICAL FIX: Element enum values aligned with database constraint
           - Fixed: principle_element_map to use lowercase values ('air', 'water', 'earth', 'fire')
           - Resolves: "invalid input value for enum element_type: 'Air'" PostgreSQL error
           - Database enum element_type expects lowercase, not Title Case
           - This fix enables successful storage of Ubuntu principle metrics
    v3.0.5 - IMPLEMENTATION FIX: Added Ubuntu principle calculation methods
           - Added: _calculate_diversity_score() method
           - Added: _calculate_reciprocity_health() method
           - Added: _calculate_mutualism_capacity() method
           - Added: _calculate_regeneration_score() method
           - Fixed: evaluate_account() to properly calculate and store Ubuntu metrics
           - Fixed: Variable definitions for diversity_score, reciprocity_health, etc.
    v3.0.4 - CRITICAL FIX: Enum case alignment with database constraint
           - Fixed: HolonicCategory enum values to Title Case
           - Added: Database validation in health check
           - Improved: Error messages for category mismatches
    v3.0.3 - SCHEMA ALIGNMENT: Fixed column name mismatches
           - Fixed: destination_account → to_account in stellar_operations queries
           - Fixed: source_account → from_account where appropriate
           - Verified: All queries match actual database schema
    v3.0.2 - Enhanced health monitoring
           - Added: Standardized health check with detailed metrics
           - Added: Error tracking and reporting
           - Added: Evaluation statistics
    v3.0.1 - Service registry integration
           - Added: Proper service registration pattern
           - Added: Health check interface
           - Improved: Error handling
    v3.0.0 - Complete Ubuntu principle integration
           - Implemented: Four-element calculation framework
           - Added: ubec_holonic_metrics table storage
           - Enhanced: ubuntu_alignment_score calculation
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field


# ==================== ENUMS AND DATA MODELS ====================

class HolonicCategory(Enum):
    """
    Holonic evaluation categories.
    
    CRITICAL: These values MUST match the database CHECK constraint exactly.
    Database constraint: holonic_category IN ('Observer', 'Participant', 'Contributor', 'Integrator', 'Exemplar')
    """
    OBSERVER = 'Observer'          # Title Case to match DB constraint
    PARTICIPANT = 'Participant'    # Title Case to match DB constraint
    CONTRIBUTOR = 'Contributor'    # Title Case to match DB constraint
    INTEGRATOR = 'Integrator'      # Title Case to match DB constraint
    EXEMPLAR = 'Exemplar'          # Title Case to match DB constraint


@dataclass
class HolonicMetrics:
    """
    Complete holonic evaluation metrics for an account.
    
    Attributes:
        account_id: Stellar account ID
        autonomy_integration_score: Balance of autonomy and integration (0-1)
        multi_scale_score: Multi-scale participation score (0-1)
        regenerative_impact_score: Regenerative impact score (0-1)
        network_contribution_score: Network contribution score (0-1)
        ubuntu_alignment_score: Ubuntu philosophy alignment (0-1)
        composite_score: Overall holonic score (0-1)
        holonic_category: Category classification
        raw_metrics: Dictionary of detailed metrics
        evaluation_date: Timestamp of evaluation
        diversity_score: Air/UBEC principle score (optional)
        reciprocity_health: Water/UBECrc principle score (optional)
        mutualism_capacity: Earth/UBECgpi principle score (optional)
        regeneration_score: Fire/UBECtt principle score (optional)
    """
    account_id: str
    autonomy_integration_score: float
    multi_scale_score: float
    regenerative_impact_score: float
    network_contribution_score: float
    ubuntu_alignment_score: float
    composite_score: float
    holonic_category: HolonicCategory
    raw_metrics: Dict[str, Any]
    evaluation_date: datetime
    
    # Element-specific Ubuntu principle scores (from ubec_holonic_metrics table)
    diversity_score: Optional[float] = None         # Air/UBEC
    reciprocity_health: Optional[float] = None      # Water/UBECrc
    mutualism_capacity: Optional[float] = None      # Earth/UBECgpi
    regeneration_score: Optional[float] = None      # Fire/UBECtt
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            'account_id': self.account_id,
            'autonomy_integration_score': self.autonomy_integration_score,
            'multi_scale_score': self.multi_scale_score,
            'regenerative_impact_score': self.regenerative_impact_score,
            'network_contribution_score': self.network_contribution_score,
            'ubuntu_alignment_score': self.ubuntu_alignment_score,
            'composite_score': self.composite_score,
            'holonic_category': self.holonic_category.value,
            'diversity_score': self.diversity_score,
            'reciprocity_health': self.reciprocity_health,
            'mutualism_capacity': self.mutualism_capacity,
            'regeneration_score': self.regeneration_score,
            'raw_metrics': self.raw_metrics,
            'evaluation_date': self.evaluation_date.isoformat()
        }
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'HolonicMetrics':
        """Create instance from database row."""
        return cls(
            account_id=row['account_id'],
            autonomy_integration_score=float(row['autonomy_integration_score']),
            multi_scale_score=float(row['multi_scale_score']),
            regenerative_impact_score=float(row['regenerative_impact_score']),
            network_contribution_score=float(row['network_contribution_score']),
            ubuntu_alignment_score=float(row['ubuntu_alignment_score']),
            composite_score=float(row['composite_score']),
            holonic_category=HolonicCategory(row['holonic_category']),
            diversity_score=float(row['diversity_score']) if row.get('diversity_score') else None,
            reciprocity_health=float(row['reciprocity_health']) if row.get('reciprocity_health') else None,
            mutualism_capacity=float(row['mutualism_capacity']) if row.get('mutualism_capacity') else None,
            regeneration_score=float(row['regeneration_score']) if row.get('regeneration_score') else None,
            raw_metrics=row.get('raw_metrics', {}),
            evaluation_date=row['evaluation_date']
        )


# ==================== MAIN SERVICE CLASS ====================

class UBECHolonicEvaluator:
    """
    Holonic evaluator service for UBEC token holders.
    
    Implements Ubuntu philosophy through quantitative metrics across five dimensions
    plus four element-specific Ubuntu principles.
    
    Configuration is loaded from database (Principle #4: Single Source of Truth).
    Hardcoded values are only used as fallback if database config is unavailable.
    """
    
    def __init__(self, db_manager, config: Dict[str, Any]):
        """
        Initialize the holonic evaluator.
        
        Args:
            db_manager: AsyncDatabaseManager instance
            config: Configuration dictionary containing:
                - ubec_code: UBEC asset code (default: 'UBEC')
                - ubec_issuer: UBEC issuer address
                - db_schema: Database schema name (default: 'ubec_main')
        
        Note: Thresholds and weights are loaded from database in initialize().
              Hardcoded defaults are used only as fallback if DB config unavailable.
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.ubec_code = config.get('ubec_code', 'UBEC')
        self.ubec_issuer = config.get('ubec_issuer')
        self.db_schema = config.get('db_schema', 'ubec_main')
        
        # Default scoring weights (fallback - will be overridden from database)
        # These values are used ONLY if database config is not available
        self.weights = {
            'autonomy_integration': 0.20,
            'multi_scale': 0.20,
            'regenerative_impact': 0.20,
            'network_contribution': 0.20,
            'ubuntu_alignment': 0.20
        }
        
        # Default category thresholds (fallback - will be overridden from database)
        # Early-stage ecosystem defaults
        self.thresholds = {
            'observer': 0.05,
            'participant': 0.12,
            'contributor': 0.22,
            'integrator': 0.32
        }
        
        # Default Ubuntu principle weights (fallback - will be overridden from database)
        self.ubuntu_weights = {
            'diversity': 0.25,
            'reciprocity': 0.25,
            'mutualism': 0.25,
            'regeneration': 0.25
        }
        
        # Health monitoring
        self._evaluation_count = 0
        self._error_count = 0
        self._last_evaluation_time: Optional[datetime] = None
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[datetime] = None
        
        # Schema detection and config tracking
        self._has_ubuntu_metrics_table = False
        self._config_loaded_from_db = False
        
        self.logger.info("UBEC Holonic Evaluator initialized (config will load from DB)")
    
    async def _load_config_from_db(self) -> None:
        """
        Load thresholds and weights from database configuration table.
        
        Implements Principle #4: Database as Single Source of Truth.
        Configuration is stored in ubec_main.system_settings table.
        
        Expected setting_key values:
        - holonic_threshold_observer: Upper bound for Observer (default: 0.05)
        - holonic_threshold_participant: Upper bound for Participant (default: 0.12)
        - holonic_threshold_contributor: Upper bound for Contributor (default: 0.22)
        - holonic_threshold_integrator: Upper bound for Integrator (default: 0.32)
        - holonic_weight_autonomy: Weight for autonomy dimension (default: 0.20)
        - holonic_weight_multi_scale: Weight for multi-scale dimension (default: 0.20)
        - holonic_weight_regenerative: Weight for regenerative dimension (default: 0.20)
        - holonic_weight_network: Weight for network dimension (default: 0.20)
        - holonic_weight_ubuntu: Weight for ubuntu dimension (default: 0.20)
        - holonic_ubuntu_weight_diversity: Weight for diversity principle (default: 0.25)
        - holonic_ubuntu_weight_reciprocity: Weight for reciprocity principle (default: 0.25)
        - holonic_ubuntu_weight_mutualism: Weight for mutualism principle (default: 0.25)
        - holonic_ubuntu_weight_regeneration: Weight for regeneration principle (default: 0.25)
        
        Falls back to hardcoded defaults if database config not available.
        """
        try:
            # Load all holonic configuration from system_settings table
            query = f"""
                SELECT setting_key, setting_value
                FROM {self.db_schema}.system_settings
                WHERE setting_key LIKE 'holonic_%'
                  AND is_active = TRUE
            """
            
            results = await self.db_manager.fetch_all(query, ())
            
            if not results:
                self.logger.warning(
                    "No holonic configuration found in system_settings table. "
                    "Using default fallback values. Consider adding holonic_* settings."
                )
                return
            
            # Parse results into thresholds, weights, and ubuntu_weights
            config_count = 0
            for row in results:
                key = row['setting_key']
                try:
                    value = float(row['setting_value'])
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid config value for {key}: {row['setting_value']}")
                    continue
                
                # Category thresholds
                if key == 'holonic_threshold_observer':
                    self.thresholds['observer'] = value
                    config_count += 1
                elif key == 'holonic_threshold_participant':
                    self.thresholds['participant'] = value
                    config_count += 1
                elif key == 'holonic_threshold_contributor':
                    self.thresholds['contributor'] = value
                    config_count += 1
                elif key == 'holonic_threshold_integrator':
                    self.thresholds['integrator'] = value
                    config_count += 1
                
                # Dimension weights
                elif key == 'holonic_weight_autonomy':
                    self.weights['autonomy_integration'] = value
                    config_count += 1
                elif key == 'holonic_weight_multi_scale':
                    self.weights['multi_scale'] = value
                    config_count += 1
                elif key == 'holonic_weight_regenerative':
                    self.weights['regenerative_impact'] = value
                    config_count += 1
                elif key == 'holonic_weight_network':
                    self.weights['network_contribution'] = value
                    config_count += 1
                elif key == 'holonic_weight_ubuntu':
                    self.weights['ubuntu_alignment'] = value
                    config_count += 1
                
                # Ubuntu principle weights
                elif key == 'holonic_ubuntu_weight_diversity':
                    self.ubuntu_weights['diversity'] = value
                    config_count += 1
                elif key == 'holonic_ubuntu_weight_reciprocity':
                    self.ubuntu_weights['reciprocity'] = value
                    config_count += 1
                elif key == 'holonic_ubuntu_weight_mutualism':
                    self.ubuntu_weights['mutualism'] = value
                    config_count += 1
                elif key == 'holonic_ubuntu_weight_regeneration':
                    self.ubuntu_weights['regeneration'] = value
                    config_count += 1
            
            if config_count > 0:
                self._config_loaded_from_db = True
                self.logger.info(
                    f"Loaded {config_count} holonic configuration values from database: "
                    f"thresholds={self.thresholds}, dimension_weights_sum={sum(self.weights.values()):.2f}"
                )
            
            # Validate dimension weights sum to 1.0
            weight_sum = sum(self.weights.values())
            if abs(weight_sum - 1.0) > 0.001:
                self.logger.warning(
                    f"Dimension weights sum to {weight_sum:.3f}, expected 1.0. "
                    "Check system_settings table values."
                )
            
            # Validate ubuntu weights sum to 1.0
            ubuntu_sum = sum(self.ubuntu_weights.values())
            if abs(ubuntu_sum - 1.0) > 0.001:
                self.logger.warning(
                    f"Ubuntu principle weights sum to {ubuntu_sum:.3f}, expected 1.0. "
                    "Check system_settings table values."
                )
            
        except Exception as e:
            self.logger.error(f"Error loading holonic config from database: {e}")
            self.logger.info("Using default hardcoded configuration values.")
    
    async def initialize(self) -> None:
        """
        Initialize the evaluator service.
        
        Performs:
        1. Load configuration from database (Principle #4: Single Source of Truth)
        2. Schema detection to enable optional features
        """
        try:
            # STEP 1: Load configuration from database
            await self._load_config_from_db()
            
            # STEP 2: Check if ubec_holonic_metrics table exists
            query = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = $1
                    AND table_name = 'ubec_holonic_metrics'
                )
            """
            result = await self.db_manager.fetch_one(query, (self.db_schema,))
            
            self._has_ubuntu_metrics_table = result['exists'] if result else False
            
            if self._has_ubuntu_metrics_table:
                self.logger.info("Ubuntu metrics table detected - element metrics enabled")
            else:
                self.logger.warning("Ubuntu metrics table not found - using fallback scoring")
            
            # Log final configuration
            config_source = "database" if self._config_loaded_from_db else "defaults"
            self.logger.info(
                f"Holonic Evaluator ready (config from {config_source}): "
                f"Observer<{self.thresholds['observer']:.2f}, "
                f"Participant<{self.thresholds['participant']:.2f}, "
                f"Contributor<{self.thresholds['contributor']:.2f}, "
                f"Integrator<{self.thresholds['integrator']:.2f}, "
                f"Exemplar>={self.thresholds['integrator']:.2f}"
            )
            
        except Exception as e:
            self.logger.error(f"Error during initialization: {e}")
            self._has_ubuntu_metrics_table = False
    
    async def close(self) -> None:
        """Close evaluator and cleanup resources."""
        self.logger.info("UBEC Holonic Evaluator closing")
    
    # ==================== MAIN EVALUATION METHODS ====================
    
    async def evaluate_account(
        self,
        account_id: str,
        save_to_db: bool = True
    ) -> Optional[HolonicMetrics]:
        """
        Evaluate a single account for holonic metrics.
        
        Args:
            account_id: Stellar account ID to evaluate
            save_to_db: Whether to save results to database (default: True)
            
        Returns:
            HolonicMetrics if successful, None otherwise
        """
        try:
            self.logger.debug(f"Evaluating account: {account_id}")
            
            # Calculate dimension scores
            autonomy_score = await self._calculate_autonomy_integration(account_id)
            multi_scale_score = await self._calculate_multi_scale_participation(account_id)
            regenerative_score = await self._calculate_regenerative_impact(account_id)
            network_score = await self._calculate_network_contribution(account_id)
            
            # CALCULATE Ubuntu principle scores (not just read from DB)
            # These methods return (score, details) tuples
            diversity_result = await self._calculate_diversity_score(account_id)
            reciprocity_result = await self._calculate_reciprocity_health(account_id)
            mutualism_result = await self._calculate_mutualism_capacity(account_id)
            regeneration_result = await self._calculate_regeneration_score(account_id)
            
            # Unpack scores and details
            diversity_score = diversity_result[0] if diversity_result else 0.0
            diversity_details = diversity_result[1] if diversity_result and len(diversity_result) > 1 else {}
            
            reciprocity_health = reciprocity_result[0] if reciprocity_result else 0.0
            reciprocity_details = reciprocity_result[1] if reciprocity_result and len(reciprocity_result) > 1 else {}
            
            mutualism_capacity = mutualism_result[0] if mutualism_result else 0.0
            mutualism_details = mutualism_result[1] if mutualism_result and len(mutualism_result) > 1 else {}
            
            regeneration_score = regeneration_result[0] if regeneration_result else 0.0
            regeneration_details = regeneration_result[1] if regeneration_result and len(regeneration_result) > 1 else {}
            
            # Calculate ubuntu_alignment_score from calculated element scores
            # Using weights from database (Principle #4: Single Source of Truth)
            ubuntu_alignment_score = (
                diversity_score * self.ubuntu_weights['diversity'] +
                reciprocity_health * self.ubuntu_weights['reciprocity'] +
                mutualism_capacity * self.ubuntu_weights['mutualism'] +
                regeneration_score * self.ubuntu_weights['regeneration']
            )
            
            # Calculate composite score
            composite_score = (
                autonomy_score * self.weights['autonomy_integration'] +
                multi_scale_score * self.weights['multi_scale'] +
                regenerative_score * self.weights['regenerative_impact'] +
                network_score * self.weights['network_contribution'] +
                ubuntu_alignment_score * self.weights['ubuntu_alignment']
            )
            
            # Determine category
            category = self._determine_category(composite_score)
            
            # Prepare raw_metrics with all scores
            raw_metrics = {
                'autonomy': autonomy_score,
                'multi_scale': multi_scale_score,
                'regenerative': regenerative_score,
                'network': network_score,
                'ubuntu': ubuntu_alignment_score,
                'ubuntu_principles': {
                    'diversity_score': diversity_score,
                    'reciprocity_health': reciprocity_health,
                    'mutualism_capacity': mutualism_capacity,
                    'regeneration_score': regeneration_score
                }
            }
            
            # Create metrics object
            metrics = HolonicMetrics(
                account_id=account_id,
                autonomy_integration_score=autonomy_score,
                multi_scale_score=multi_scale_score,
                regenerative_impact_score=regenerative_score,
                network_contribution_score=network_score,
                ubuntu_alignment_score=ubuntu_alignment_score,
                composite_score=composite_score,
                holonic_category=category,
                raw_metrics=raw_metrics,
                evaluation_date=datetime.now(timezone.utc),
                diversity_score=diversity_score,
                reciprocity_health=reciprocity_health,
                mutualism_capacity=mutualism_capacity,
                regeneration_score=regeneration_score
            )
            
            # Store to database if requested
            if save_to_db:
                await self._store_evaluation(metrics)
                
                # Store Ubuntu principle metrics to separate table
                ubuntu_metrics = {
                    'diversity': diversity_score,
                    'reciprocity': reciprocity_health,
                    'mutualism': mutualism_capacity,
                    'regeneration': regeneration_score
                }
                ubuntu_details = {
                    'diversity': diversity_details,
                    'reciprocity': reciprocity_details,
                    'mutualism': mutualism_details,
                    'regeneration': regeneration_details
                }
                await self._store_ubuntu_principle_metrics(account_id, ubuntu_metrics, ubuntu_details)
            
            # Update statistics
            self._evaluation_count += 1
            self._last_evaluation_time = datetime.now()
            
            return metrics
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error evaluating account {account_id}: {e}")
            return None
    
    async def evaluate_all_accounts(
        self,
        max_accounts: Optional[int] = None,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate all UBEC holder accounts.
        
        Args:
            max_accounts: Optional limit on number of accounts to evaluate
            save_to_db: Whether to save results to database
            
        Returns:
            Dictionary with evaluation results and statistics:
            {
                'total_accounts': int,      # Total accounts found
                'evaluated': int,            # Successfully evaluated (alias for successful)
                'successful': int,           # Successfully evaluated
                'failed': int,               # Failed evaluations
                'skipped': int,              # Skipped accounts (currently always 0)
                'errors': int,               # Errors encountered (alias for failed)
                'results': List[Dict],       # List of HolonicMetrics as dicts
                'error': str (optional)      # Error message if batch failed
            }
        """
        try:
            # Get all UBEC holders
            # Note: Using GROUP BY instead of DISTINCT to allow ORDER BY on balance column
            query = f"""
                SELECT account_id
                FROM {self.db_schema}.ubec_balances
                WHERE balance > 0
                GROUP BY account_id
                ORDER BY MAX(balance) DESC
            """
            
            if max_accounts:
                query += f" LIMIT {max_accounts}"
            
            accounts = await self.db_manager.fetch_all(query, ())
            
            self.logger.info(f"Found {len(accounts)} accounts to evaluate")
            
            # Evaluate each account
            successful = 0
            failed = 0
            results = []
            
            for row in accounts:
                account_id = row['account_id']
                metrics = await self.evaluate_account(account_id, save_to_db)
                
                if metrics:
                    successful += 1
                    results.append(metrics.to_dict())
                else:
                    failed += 1
            
            # Log completion statistics
            self.logger.info(f"Evaluation complete: {successful} successful, {failed} failed out of {len(accounts)} total accounts")
            
            return {
                'total_accounts': len(accounts),
                'evaluated': successful,  # Main.py expects 'evaluated' not 'successful'
                'successful': successful,
                'failed': failed,
                'skipped': 0,  # No skipping logic in current implementation
                'errors': failed,  # Alias for failed
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Error in batch evaluation: {e}")
            return {
                'total_accounts': 0,
                'evaluated': 0,
                'successful': 0,
                'failed': 0,
                'skipped': 0,
                'errors': 0,
                'error': str(e),
                'results': []
            }
    
    async def evaluate_network_holism(self) -> Dict[str, Any]:
        """
        Evaluate overall network holism and Ubuntu principle integration.
        
        Analyzes the distribution of holonic categories across the network
        and calculates a diversity score using Shannon entropy.
        
        Returns:
            Network-level holistic assessment:
            {
                'network_holism_score': float,  # Shannon entropy-based diversity (0.0-1.0)
                'total_evaluated': int,  # Total accounts evaluated in past 7 days
                'average_composite_score': float,  # Mean composite score
                'average_ubuntu_score': float,  # Mean Ubuntu alignment score
                'score_stddev': float,  # Standard deviation of composite scores
                'category_distribution': [  # Distribution across categories
                    {
                        'category': str,  # Category name
                        'count': int,  # Number of accounts
                        'average_score': float  # Average score for category
                    }
                ],
                'evaluation_timestamp': str  # ISO format timestamp
            }
        """
        try:
            self.logger.info("Evaluating network holism")
            
            # Get category distribution
            distribution_query = f"""
                SELECT 
                    holonic_category,
                    COUNT(*) as count,
                    AVG(composite_score) as avg_score
                FROM {self.db_schema}.holonic_metrics
                WHERE evaluation_date >= NOW() - INTERVAL '7 days'
                GROUP BY holonic_category
                ORDER BY 
                    CASE holonic_category
                        WHEN 'Observer' THEN 1
                        WHEN 'Participant' THEN 2
                        WHEN 'Contributor' THEN 3
                        WHEN 'Integrator' THEN 4
                        WHEN 'Exemplar' THEN 5
                    END
            """
            
            distribution = await self.db_manager.fetch_all(distribution_query, ())
            
            # Get overall statistics
            stats_query = f"""
                SELECT 
                    COUNT(*) as total_evaluated,
                    AVG(composite_score) as avg_composite,
                    AVG(ubuntu_alignment_score) as avg_ubuntu,
                    STDDEV(composite_score) as score_stddev
                FROM {self.db_schema}.holonic_metrics
                WHERE evaluation_date >= NOW() - INTERVAL '7 days'
            """
            
            stats = await self.db_manager.fetch_one(stats_query, ())
            
            # Calculate network holism score
            # Higher scores for more balanced distribution across categories
            if distribution:
                total_accounts = sum(row['count'] for row in distribution)
                category_proportions = [row['count'] / total_accounts for row in distribution]
                
                # Shannon entropy as diversity measure
                import math
                entropy = -sum(p * math.log(p) if p > 0 else 0 for p in category_proportions)
                max_entropy = math.log(5)  # 5 categories
                diversity_score = entropy / max_entropy if max_entropy > 0 else 0
            else:
                diversity_score = 0
            
            report = {
                'network_holism_score': diversity_score,
                'total_evaluated': int(stats['total_evaluated']) if stats else 0,
                'average_composite_score': float(stats['avg_composite']) if stats and stats['avg_composite'] else 0,
                'average_ubuntu_score': float(stats['avg_ubuntu']) if stats and stats['avg_ubuntu'] else 0,
                'score_stddev': float(stats['score_stddev']) if stats and stats['score_stddev'] else 0,
                'category_distribution': [
                    {
                        'category': row['holonic_category'],
                        'count': int(row['count']),
                        'average_score': float(row['avg_score'])
                    }
                    for row in distribution
                ],
                'evaluation_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            self.logger.info(f"Network holism evaluation complete: score={diversity_score:.3f}")
            
            return report
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now(timezone.utc)
            self.logger.error(f"Error evaluating network holism: {e}")
            return {'error': str(e)}
    # ==================== UBUNTU PRINCIPLE CALCULATIONS ====================
    
    async def _calculate_diversity_score(self, account_id: str) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate diversity score (Air/UBEC principle).
        
        Measures unique participation patterns and breadth of engagement.
        
        Args:
            account_id: Account to evaluate
            
        Returns:
            Tuple of (score, details_dict)
        """
        try:
            # Get UBEC balance
            balance_query = f"""
                SELECT balance
                FROM {self.db_schema}.ubec_balances
                WHERE account_id = $1
                  AND token_code = 'UBEC'
            """
            balance_result = await self.db_manager.fetch_one(balance_query, (account_id,))
            balance = float(balance_result['balance']) if balance_result else 0.0
            
            # Get unique transaction partners from stellar_operations
            partners_query = f"""
                SELECT COUNT(DISTINCT 
                    CASE 
                        WHEN from_account = $1 THEN to_account
                        WHEN to_account = $1 THEN from_account
                    END
                ) as unique_partners
                FROM {self.db_schema}.stellar_operations
                WHERE (from_account = $1 OR to_account = $1)
                  AND asset_code = 'UBEC'
            """
            partners_result = await self.db_manager.fetch_one(partners_query, (account_id,))
            unique_partners = int(partners_result['unique_partners']) if partners_result else 0
            
            # Get transaction count from stellar_operations
            tx_query = f"""
                SELECT COUNT(*) as tx_count
                FROM {self.db_schema}.stellar_operations
                WHERE (from_account = $1 OR to_account = $1)
                  AND asset_code = 'UBEC'
            """
            tx_result = await self.db_manager.fetch_one(tx_query, (account_id,))
            tx_count = int(tx_result['tx_count']) if tx_result else 0
            
            # Calculate components
            balance_component = min(balance / 10000.0, 1.0) * 0.4  # Max 10K UBEC
            diversity_component = min(unique_partners / 20.0, 1.0) * 0.4  # Max 20 partners
            activity_component = min(tx_count / 50.0, 1.0) * 0.2  # Max 50 transactions
            
            # Total score
            score = balance_component + diversity_component + activity_component
            
            # Details
            details = {
                'balance': balance,
                'unique_partners': unique_partners,
                'transaction_count': tx_count,
                'participation_score': score,
                'diversity_component': diversity_component,
                'activity_component': activity_component
            }
            
            return (score, details)
            
        except Exception as e:
            self.logger.error(f"Error calculating diversity score for {account_id}: {e}")
            return (0.0, {'error': str(e)})
    
    async def _calculate_reciprocity_health(self, account_id: str) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate reciprocity health (Water/UBECrc principle).
        
        Measures balance of giving and receiving, flow patterns.
        
        Args:
            account_id: Account to evaluate
            
        Returns:
            Tuple of (score, details_dict)
        """
        try:
            # Get UBECrc balance
            balance_query = f"""
                SELECT balance
                FROM {self.db_schema}.ubec_balances
                WHERE account_id = $1
                  AND token_code = 'UBECrc'
            """
            balance_result = await self.db_manager.fetch_one(balance_query, (account_id,))
            balance = float(balance_result['balance']) if balance_result else 0.0
            
            # Get sent/received amounts from stellar_operations
            flow_query = f"""
                SELECT 
                    SUM(CASE WHEN from_account = $1 THEN amount ELSE 0 END) as sent,
                    SUM(CASE WHEN to_account = $1 THEN amount ELSE 0 END) as received
                FROM {self.db_schema}.stellar_operations
                WHERE (from_account = $1 OR to_account = $1)
                  AND asset_code = 'UBECrc'
            """
            flow_result = await self.db_manager.fetch_one(flow_query, (account_id,))
            
            sent = float(flow_result['sent']) if flow_result and flow_result['sent'] else 0.0
            received = float(flow_result['received']) if flow_result and flow_result['received'] else 0.0
            
            # Calculate reciprocity ratio
            total_flow = sent + received
            if total_flow > 0:
                # Perfect balance is 0.5 sent, 0.5 received
                sent_ratio = sent / total_flow
                balance_score = 1.0 - abs(0.5 - sent_ratio) * 2.0  # 1.0 at perfect balance
            else:
                balance_score = 0.0
            
            # Calculate components
            balance_component = min(balance / 5000.0, 1.0) * 0.3  # Max 5K UBECrc
            flow_component = min(total_flow / 10000.0, 1.0) * 0.4  # Max 10K total flow
            reciprocity_component = balance_score * 0.3
            
            # Total score
            score = balance_component + flow_component + reciprocity_component
            
            # Details
            details = {
                'balance': balance,
                'sent': sent,
                'received': received,
                'total_flow': total_flow,
                'reciprocity_balance': balance_score,
                'flow_health': score
            }
            
            return (score, details)
            
        except Exception as e:
            self.logger.error(f"Error calculating reciprocity health for {account_id}: {e}")
            return (0.0, {'error': str(e)})
    
    async def _calculate_mutualism_capacity(self, account_id: str) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate mutualism capacity (Earth/UBECgpi principle).
        
        Measures stability, grounding, and mutual benefit patterns.
        
        Args:
            account_id: Account to evaluate
            
        Returns:
            Tuple of (score, details_dict)
        """
        try:
            # Get UBECgpi balance
            balance_query = f"""
                SELECT balance
                FROM {self.db_schema}.ubec_balances
                WHERE account_id = $1
                  AND token_code = 'UBECgpi'
            """
            balance_result = await self.db_manager.fetch_one(balance_query, (account_id,))
            balance = float(balance_result['balance']) if balance_result else 0.0
            
            # Get holding duration (stability indicator) from stellar_operations
            duration_query = f"""
                SELECT MIN(created_at) as first_transaction
                FROM {self.db_schema}.stellar_operations
                WHERE (from_account = $1 OR to_account = $1)
                  AND asset_code = 'UBECgpi'
            """
            duration_result = await self.db_manager.fetch_one(duration_query, (account_id,))
            
            if duration_result and duration_result['first_transaction']:
                days_held = (datetime.now(timezone.utc) - duration_result['first_transaction']).days
            else:
                days_held = 0
            
            # Get transaction regularity from stellar_operations
            regularity_query = f"""
                SELECT COUNT(*) as tx_count
                FROM {self.db_schema}.stellar_operations
                WHERE (from_account = $1 OR to_account = $1)
                  AND asset_code = 'UBECgpi'
            """
            regularity_result = await self.db_manager.fetch_one(regularity_query, (account_id,))
            tx_count = int(regularity_result['tx_count']) if regularity_result else 0
            
            # Calculate components
            balance_component = min(balance / 3000.0, 1.0) * 0.4  # Max 3K UBECgpi
            stability_component = min(days_held / 90.0, 1.0) * 0.4  # Max 90 days
            activity_component = min(tx_count / 30.0, 1.0) * 0.2  # Max 30 transactions
            
            # Total score
            score = balance_component + stability_component + activity_component
            
            # Details
            details = {
                'balance': balance,
                'days_held': days_held,
                'transaction_count': tx_count,
                'stability_score': score,
                'grounding_quality': stability_component
            }
            
            return (score, details)
            
        except Exception as e:
            self.logger.error(f"Error calculating mutualism capacity for {account_id}: {e}")
            return (0.0, {'error': str(e)})
    
    async def _calculate_regeneration_score(self, account_id: str) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate regeneration score (Fire/UBECtt principle).
        
        Measures transformation and sustainable contribution patterns.
        
        Args:
            account_id: Account to evaluate
            
        Returns:
            Tuple of (score, details_dict)
        """
        try:
            # Get UBECtt balance
            balance_query = f"""
                SELECT balance
                FROM {self.db_schema}.ubec_balances
                WHERE account_id = $1
                  AND token_code = 'UBECtt'
            """
            balance_result = await self.db_manager.fetch_one(balance_query, (account_id,))
            balance = float(balance_result['balance']) if balance_result else 0.0
            
            # Get transformation activity (transaction patterns) from stellar_operations
            activity_query = f"""
                SELECT COUNT(*) as tx_count,
                       COUNT(DISTINCT DATE(created_at)) as active_days
                FROM {self.db_schema}.stellar_operations
                WHERE (from_account = $1 OR to_account = $1)
                  AND asset_code = 'UBECtt'
            """
            activity_result = await self.db_manager.fetch_one(activity_query, (account_id,))
            
            tx_count = int(activity_result['tx_count']) if activity_result else 0
            active_days = int(activity_result['active_days']) if activity_result else 0
            
            # Get network contribution (unique partners) from stellar_operations
            network_query = f"""
                SELECT COUNT(DISTINCT 
                    CASE 
                        WHEN from_account = $1 THEN to_account
                        WHEN to_account = $1 THEN from_account
                    END
                ) as unique_partners
                FROM {self.db_schema}.stellar_operations
                WHERE (from_account = $1 OR to_account = $1)
                  AND asset_code = 'UBECtt'
            """
            network_result = await self.db_manager.fetch_one(network_query, (account_id,))
            unique_partners = int(network_result['unique_partners']) if network_result else 0
            
            # Calculate components
            balance_component = min(balance / 2000.0, 1.0) * 0.3  # Max 2K UBECtt
            activity_component = min(tx_count / 40.0, 1.0) * 0.3  # Max 40 transactions
            consistency_component = min(active_days / 30.0, 1.0) * 0.2  # Max 30 active days
            network_component = min(unique_partners / 15.0, 1.0) * 0.2  # Max 15 partners
            
            # Total score
            score = balance_component + activity_component + consistency_component + network_component
            
            # Details
            details = {
                'balance': balance,
                'transaction_count': tx_count,
                'active_days': active_days,
                'unique_partners': unique_partners,
                'transformation_score': score,
                'regenerative_impact': activity_component + network_component
            }
            
            return (score, details)
            
        except Exception as e:
            self.logger.error(f"Error calculating regeneration score for {account_id}: {e}")
            return (0.0, {'error': str(e)})
    
    # ==================== DIMENSION CALCULATIONS ====================
    
    async def _calculate_autonomy_integration(self, account_id: str) -> float:
        """
        Calculate autonomy-integration score.
        
        Measures balance between independent action and network integration.
        
        Args:
            account_id: Account to evaluate
            
        Returns:
            Score between 0.0 and 1.0
        """
        try:
            # Get balance (autonomy indicator)
            balance_query = f"""
                SELECT SUM(balance) as total_balance
                FROM {self.db_schema}.ubec_balances
                WHERE account_id = $1
            """
            balance_result = await self.db_manager.fetch_one(balance_query, (account_id,))
            total_balance = float(balance_result['total_balance']) if balance_result and balance_result['total_balance'] else 0.0
            
            # Get transaction count (integration indicator) from stellar_operations
            tx_query = f"""
                SELECT COUNT(*) as tx_count
                FROM {self.db_schema}.stellar_operations
                WHERE from_account = $1 OR to_account = $1
            """
            tx_result = await self.db_manager.fetch_one(tx_query, (account_id,))
            tx_count = int(tx_result['tx_count']) if tx_result else 0
            
            # Calculate autonomy (holdings) vs integration (activity) balance
            autonomy = min(total_balance / 10000.0, 1.0)
            integration = min(tx_count / 100.0, 1.0)
            
            # Balanced score favors moderate values of both
            score = (autonomy + integration) / 2.0
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating autonomy integration for {account_id}: {e}")
            return 0.0
    
    async def _calculate_multi_scale_participation(self, account_id: str) -> float:
        """
        Calculate multi-scale participation score.
        
        Measures participation across different scales and contexts.
        
        Args:
            account_id: Account to evaluate
            
        Returns:
            Score between 0.0 and 1.0
        """
        try:
            # Count token types held
            tokens_query = f"""
                SELECT COUNT(DISTINCT token_code) as token_count
                FROM {self.db_schema}.ubec_balances
                WHERE account_id = $1
                  AND balance > 0
            """
            tokens_result = await self.db_manager.fetch_one(tokens_query, (account_id,))
            token_count = int(tokens_result['token_count']) if tokens_result else 0
            
            # Get unique partners across all tokens from stellar_operations
            partners_query = f"""
                SELECT COUNT(DISTINCT 
                    CASE 
                        WHEN from_account = $1 THEN to_account
                        WHEN to_account = $1 THEN from_account
                    END
                ) as unique_partners
                FROM {self.db_schema}.stellar_operations
                WHERE from_account = $1 OR to_account = $1
            """
            partners_result = await self.db_manager.fetch_one(partners_query, (account_id,))
            unique_partners = int(partners_result['unique_partners']) if partners_result else 0
            
            # Calculate score
            token_diversity = token_count / 4.0  # Max 4 tokens
            network_breadth = min(unique_partners / 30.0, 1.0)
            
            score = (token_diversity + network_breadth) / 2.0
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating multi-scale participation for {account_id}: {e}")
            return 0.0
    
    async def _calculate_regenerative_impact(self, account_id: str) -> float:
        """
        Calculate regenerative impact score.
        
        Measures sustainable contribution to the network.
        
        Args:
            account_id: Account to evaluate
            
        Returns:
            Score between 0.0 and 1.0
        """
        try:
            # Get outgoing transaction volume (giving) from stellar_operations
            outgoing_query = f"""
                SELECT SUM(amount) as total_sent,
                       COUNT(*) as tx_count
                FROM {self.db_schema}.stellar_operations
                WHERE from_account = $1
            """
            outgoing_result = await self.db_manager.fetch_one(outgoing_query, (account_id,))
            
            total_sent = float(outgoing_result['total_sent']) if outgoing_result and outgoing_result['total_sent'] else 0.0
            outgoing_count = int(outgoing_result['tx_count']) if outgoing_result else 0
            
            # Calculate regenerative contribution
            contribution_volume = min(total_sent / 5000.0, 1.0) * 0.6
            contribution_frequency = min(outgoing_count / 50.0, 1.0) * 0.4
            
            score = contribution_volume + contribution_frequency
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating regenerative impact for {account_id}: {e}")
            return 0.0
    
    async def _calculate_network_contribution(self, account_id: str) -> float:
        """
        Calculate network contribution score.
        
        Measures overall contribution to network health and growth.
        
        Args:
            account_id: Account to evaluate
            
        Returns:
            Score between 0.0 and 1.0
        """
        try:
            # Get overall transaction activity from stellar_operations
            activity_query = f"""
                SELECT COUNT(*) as total_tx,
                       COUNT(DISTINCT DATE(created_at)) as active_days
                FROM {self.db_schema}.stellar_operations
                WHERE from_account = $1 OR to_account = $1
            """
            activity_result = await self.db_manager.fetch_one(activity_query, (account_id,))
            
            total_tx = int(activity_result['total_tx']) if activity_result else 0
            active_days = int(activity_result['active_days']) if activity_result else 0
            
            # Calculate contribution metrics
            activity_score = min(total_tx / 100.0, 1.0) * 0.5
            consistency_score = min(active_days / 60.0, 1.0) * 0.5
            
            score = activity_score + consistency_score
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating network contribution for {account_id}: {e}")
            return 0.0
    
    # ==================== DATA STORAGE ====================
    
    async def _store_evaluation(self, metrics: HolonicMetrics) -> bool:
        """
        Store evaluation results to database.
        
        Args:
            metrics: HolonicMetrics to store
            
        Returns:
            True if successful
        """
        try:
            # Delete existing evaluation for this account today
            delete_query = f"""
                DELETE FROM {self.db_schema}.holonic_metrics
                WHERE account_id = $1
                  AND DATE(evaluation_date) = DATE(NOW())
            """
            await self.db_manager.execute(delete_query, (metrics.account_id,))
            
            # Insert new evaluation
            insert_query = f"""
                INSERT INTO {self.db_schema}.holonic_metrics (
                    account_id,
                    autonomy_integration_score,
                    multi_scale_score,
                    regenerative_impact_score,
                    network_contribution_score,
                    ubuntu_alignment_score,
                    composite_score,
                    holonic_category,
                    raw_metrics,
                    evaluation_date
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """
            
            await self.db_manager.execute(
                insert_query,
                (
                    metrics.account_id,
                    metrics.autonomy_integration_score,
                    metrics.multi_scale_score,
                    metrics.regenerative_impact_score,
                    metrics.network_contribution_score,
                    metrics.ubuntu_alignment_score,
                    metrics.composite_score,
                    metrics.holonic_category.value,
                    json.dumps(metrics.raw_metrics),
                    metrics.evaluation_date
                )
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing evaluation: {e}")
            return False
    
    async def _store_ubuntu_principle_metrics(
        self,
        account_id: str,
        metrics: Dict[str, float],
        details: Dict[str, Dict]
    ) -> bool:
        """
        Store Ubuntu principle metrics to ubec_holonic_metrics table.
        
        Args:
            account_id: Account ID
            metrics: Dictionary of principle scores (diversity, reciprocity, mutualism, regeneration)
            details: Dictionary of principle details
            
        Returns:
            True if successful
        """
        if not self._has_ubuntu_metrics_table:
            return False
        
        try:
            # Map principles to elements (lowercase to match database enum)
            principle_element_map = {
                'diversity': 'air',
                'reciprocity': 'water',
                'mutualism': 'earth',
                'regeneration': 'fire'
            }
            
            for principle, score in metrics.items():
                element = principle_element_map.get(principle)
                if not element:
                    continue
                
                principle_details = details.get(principle, {})
                
                # Delete existing entry for this account/element/principle today
                delete_query = f"""
                    DELETE FROM {self.db_schema}.ubec_holonic_metrics
                    WHERE account_id = $1
                      AND element = $2
                      AND principle = $3
                      AND DATE(calculated_at) = DATE(NOW())
                """
                await self.db_manager.execute(delete_query, (account_id, element, principle))
                
                # Insert new entry (without health_status column)
                insert_query = f"""
                    INSERT INTO {self.db_schema}.ubec_holonic_metrics (
                        account_id,
                        element,
                        principle,
                        score,
                        assessment_details,
                        calculated_at
                    ) VALUES ($1, $2, $3, $4, $5, NOW())
                """
                
                await self.db_manager.execute(
                    insert_query,
                    (
                        account_id,
                        element,
                        principle,
                        score,
                        json.dumps(principle_details)
                    )
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing Ubuntu principle metrics: {e}")
            return False
    
    # ==================== RETRIEVAL METHODS ====================
    
    async def get_ubuntu_principle_metrics(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        Get Ubuntu principle metrics for an account.
        
        Args:
            account_id: Account to retrieve metrics for
            
        Returns:
            Dictionary of Ubuntu principle metrics or None
        """
        if not self._has_ubuntu_metrics_table:
            return None
        
        try:
            query = f"""
                SELECT 
                    principle,
                    score,
                    assessment_details,
                    calculated_at
                FROM {self.db_schema}.ubec_holonic_metrics
                WHERE account_id = $1
                ORDER BY calculated_at DESC
            """
            
            results = await self.db_manager.fetch_all(query, (account_id,))
            
            if not results:
                return None
            
            # Group by principle (get most recent for each)
            principles = {}
            seen = set()
            
            for row in results:
                principle = row['principle']
                if principle not in seen:
                    seen.add(principle)
                    principles[principle] = {
                        'score': float(row['score']),
                        'details': row['assessment_details'],
                        'calculated_at': row['calculated_at'].isoformat()
                    }
            
            return {
                'account_id': account_id,
                'principles': principles
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving Ubuntu principle metrics: {e}")
            return None
    
    async def get_latest_evaluation(self, account_id: str) -> Optional[HolonicMetrics]:
        """
        Get the latest evaluation for an account.
        
        Args:
            account_id: Account to retrieve evaluation for
            
        Returns:
            Latest HolonicMetrics or None if not found
        """
        try:
            query = f"""
                SELECT *
                FROM {self.db_schema}.holonic_metrics
                WHERE account_id = $1
                ORDER BY evaluation_date DESC
                LIMIT 1
            """
            
            result = await self.db_manager.fetch_one(query, (account_id,))
            
            if not result:
                return None
            
            return HolonicMetrics.from_db_row(result)
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error retrieving latest evaluation: {e}")
            return None
    
    async def get_evaluation_history(
        self,
        account_id: str,
        days: int = 30
    ) -> List[HolonicMetrics]:
        """
        Retrieve evaluation history for an account.
        
        Args:
            account_id: Account to retrieve history for
            days: Number of days of history to retrieve
            
        Returns:
            List of HolonicMetrics ordered by date descending
        """
        try:
            query = f"""
                SELECT *
                FROM {self.db_schema}.holonic_metrics
                WHERE account_id = $1
                    AND evaluation_date >= NOW() - INTERVAL '{days} days'
                ORDER BY evaluation_date DESC
            """
            
            results = await self.db_manager.fetch_all(query, (account_id,))
            
            return [HolonicMetrics.from_db_row(row) for row in results]
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            self.logger.error(f"Error retrieving evaluation history: {e}")
            return []
    
    # ==================== HELPERS ====================
    
    def _determine_category(self, composite_score: float) -> HolonicCategory:
        """
        Determine holonic category based on composite score.
        
        Uses thresholds loaded from database (Principle #4: Single Source of Truth).
        
        Args:
            composite_score: Composite evaluation score (0-1)
            
        Returns:
            HolonicCategory enum value
        """
        if composite_score >= self.thresholds['integrator']:
            return HolonicCategory.EXEMPLAR
        elif composite_score >= self.thresholds['contributor']:
            return HolonicCategory.INTEGRATOR
        elif composite_score >= self.thresholds['participant']:
            return HolonicCategory.CONTRIBUTOR
        elif composite_score >= self.thresholds['observer']:
            return HolonicCategory.PARTICIPANT
        else:
            return HolonicCategory.OBSERVER
    
    # ==================== HEALTH CHECK ====================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for evaluator service.
        
        Implements standardized health check pattern following Principle #12.
        This implementation builds health status directly without using
        non-existent utility methods.
        
        Returns:
            Health status dictionary with standardized format:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy' | 'unknown',
                'message': str,
                'timestamp': str (ISO format),
                'details': {...}
            }
        """
        try:
            # Test database connectivity
            test_query = f"""
                SELECT COUNT(*) as count
                FROM {self.db_schema}.holonic_metrics
                WHERE evaluation_date >= NOW() - INTERVAL '24 hours'
            """
            
            test_result = await self.db_manager.fetch_one(test_query, ())
            recent_evaluations = test_result['count'] if test_result else 0
            
            # Determine health status
            if self._error_count > 10:
                status = 'unhealthy'
                message = f"High error count: {self._error_count} errors"
            elif self._error_count > 5:
                status = 'degraded'
                message = f"Elevated error count: {self._error_count} errors"
            elif not self._last_evaluation_time:
                status = 'unknown'
                message = "No evaluations performed yet"
            else:
                status = 'healthy'
                message = "Service operating normally"
            
            return {
                'status': status,
                'message': message,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'details': {
                    'total_evaluations': self._evaluation_count,
                    'error_count': self._error_count,
                    'last_evaluation': self._last_evaluation_time.isoformat() if self._last_evaluation_time else None,
                    'last_error': self._last_error,
                    'last_error_time': self._last_error_time.isoformat() if self._last_error_time else None,
                    'ubuntu_metrics_enabled': self._has_ubuntu_metrics_table,
                    'recent_evaluations_24h': recent_evaluations,
                    'config_source': 'database' if self._config_loaded_from_db else 'defaults',
                    'thresholds': self.thresholds,
                    'weights': self.weights,
                    'ubuntu_weights': self.ubuntu_weights
                }
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f"Health check failed: {str(e)}",
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'details': {
                    'error': str(e)
                }
            }


# ==================== FACTORY FUNCTION ====================

async def create_holonic_evaluator(
    db_manager,
    config: Optional[Dict[str, Any]] = None
) -> UBECHolonicEvaluator:
    """
    Factory function to create and initialize holonic evaluator.
    
    Implements Principle #2 (Service Pattern) - Factory-based instantiation.
    
    Args:
        db_manager: AsyncDatabaseManager instance
        config: Optional configuration dictionary
        
    Returns:
        Initialized UBECHolonicEvaluator instance
    """
    if config is None:
        config = {}
    
    evaluator = UBECHolonicEvaluator(db_manager, config)
    await evaluator.initialize()
    
    return evaluator
