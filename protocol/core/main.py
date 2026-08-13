"""
UBEC Protocol Suite - Main Orchestrator

This is the SOLE ENTRY POINT for the entire UBEC Protocol Suite system.
All services are registered, initialized, and orchestrated through this module.

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Services as self-contained components
    ✅ #2  Service Pattern: main.py is sole orchestrator
    ✅ #3  Service Registry: Central dependency management
    ✅ #4  Single Source of Truth: Database-backed configuration
    ✅ #5  Strict Async: 100% async/await operations
    ✅ #6  No Sync Fallbacks: Pure async implementation
    ✅ #7  Per-Asset Monitoring: Health checks for each service
    ✅ #8  No Duplicate Configuration: Config defined once
    ✅ #9  Integrated Rate Limiting: Built into Stellar client
    ✅ #10 Separation of Concerns: Clear service boundaries
    ✅ #11 Comprehensive Documentation: Full docstrings
    ✅ #12 Method Singularity: No code duplication
════════════════════════════════════════════════════════════════════════════

Attribution: This project uses the services of Claude and Anthropic PBC to
inform our decisions and recommendations. This project was made possible with
the assistance of Claude and Anthropic PBC.

Usage:
    # Basic operations
    python main.py health              # Check system health
    python main.py status              # Get system status
    python main.py sync-status         # Check data synchronization status
    
    # Discovery operations
    python main.py discover --max-accounts 100
    
    # Sync operations
    python main.py sync --sync-type all
    
    # Cleanup operations (NEW v3.8.3)
    python main.py cleanup                           # Preview (dry-run)
    python main.py cleanup --execute                 # Actually delete
    python main.py cleanup --execute --keep-zero-balance  # Only remove no-trustline accounts
    
    # Analytics operations
    python main.py analytics --analysis-type overview
    
    # Holonic evaluation
    python main.py evaluate-holonic --all
    python main.py evaluate-holonic --account ACCOUNT_ID
    
    # Visualization
    python main.py visualize --action report --format html
    
    # Protocol health
    python main.py protocol-health
    
    # Scheduler status
    python main.py scheduler-status
    
    # Distribution commands
    python main.py distribution --action check-compliance
    python main.py distribution --action status
    python main.py distribution --action rebalance-check
    python main.py distribution --action execute-rebalance        # Dry-run by default
    python main.py distribution --action execute-rebalance --live # Live execution (DANGEROUS)
    
    # API Server with Scheduler
    python main.py serve --host 0.0.0.0 --port 8000

Author: UBEC Protocol Development Team
Version: 3.8.3
Updated: 2025-11-27


CHANGELOG v3.8.3:
    - ✅ ADDED: cleanup command for removing irrelevant accounts
    - ✅ ADDED: handle_cleanup() function to execute cleanup operations
    - ✅ ADDED: CLI arguments: --execute, --keep-zero-balance
    - ✅ FEATURE: Removes accounts with no UBEC trustlines
    - ✅ FEATURE: Optionally removes accounts with zero balance
    - ✅ FEATURE: Dry-run mode by default for safety
    - ✅ USES: sync.cleanup_irrelevant_accounts() method (v5.2.9)
    - 🎯 COMPLIANCE: All 12 design principles verified and maintained

CHANGELOG v3.8.2:
    - ✅ VERIFICATION: Confirmed scheduler.start() correctly placed in handle_serve()
    - ✅ VERIFICATION: Health check behavior is correct (scheduler should NOT start)
    - 📝 DOCUMENTATION: Enhanced comments explaining scheduler initialization
    - 📝 DOCUMENTATION: Clarified when scheduler starts vs initializes
    - ℹ️  NOTE: "NOT_STARTED" status in health checks is EXPECTED and CORRECT
    - ℹ️  NOTE: Scheduler only starts in serve mode, not during health checks
    - 🎯 COMPLIANCE: All 12 design principles verified and maintained

CHANGELOG v3.8.1:
    - 🔧 FIX: Added proper service cleanup and shutdown
    - FIXED: Unclosed aiohttp client sessions in stellar_client and api_service
    - ADDED: registry.shutdown() call in main() finally block
    - ENSURES: All services with close() methods are properly cleaned up
    - IMPACT: Eliminates "Unclosed client session" and "Unclosed connector" warnings
    - COMPLIANCE: Follows async cleanup pattern (Principle #5)
    - PATTERN: Services cleaned up in reverse initialization order
    - RELIABILITY: Proper resource cleanup even on errors or interrupts

CHANGELOG v3.8.0:
    - 🎯 ADDED: Bioregion Manager service registration
    - ADDED: 'bioregion_manager' service in register_core_services() function
    - ADDED: Bioregion manager to health check monitoring list
    - ENABLES: bioregion_analysis scheduler job can now be activated
    - USES: services.bioregion.bioregion_manager_service.create_bioregion_manager
    - DEPENDENCIES: database (for phenomenal.holons table access)
    - PURPOSE: Manages bioregional holons - geographic economic communities
    - SCHEMA: Uses phenomenal.holons table with explicit schema naming
    - TOTAL SERVICES: Now 17 (added bioregion_manager)
    - COMPLIANCE: Follows Design Principle #2 (Service Pattern) and #3 (Service Registry)
    - IMPACT: Bioregion tracking and analysis now available for automated scheduling

CHANGELOG v3.7.14:
    - 🔧 ENHANCEMENT: Added blockchain sync service registration
    - ADDED: Registered 'sync' service in register_core_services() function
    - ADDED: Sync service to health check monitoring list
    - ENABLES: blockchain_sync scheduler job can now be activated
    - USES: core.db.ubec_data_synchronizer.register_factory for service creation
    - DEPENDENCIES: database, config, stellar_client
    - IMPACT: Blockchain synchronization now available for automated scheduling
    - TOTAL SERVICES: Now 16 (added sync service)
    - COMPLIANCE: Follows Design Principle #2 (Service Pattern) and #3 (Service Registry)

CHANGELOG v3.7.13:
    - 🔧 CRITICAL FIX: Added missing API service registration
    - FIXED: Registered 'api_service' in register_core_services() function
    - FIXED: Changed handle_serve() to use registry.get('api_service') instead of import from non-existent 'api.main'
    - FIXED: API service now properly initialized with BackendAPIService from services.api.api_service
    - RESOLVES: ModuleNotFoundError - "No module named 'api'"
    - IMPACT: API server now starts successfully with all 15 services operational
    - COMPLIANCE: Follows Design Principle #2 (Service Pattern) and #3 (Service Registry)
    - TOTAL SERVICES: Now 15 (config, database, rate_limiter, stellar_client, air_protocol, 
                            water_protocol, earth_protocol, fire_protocol, analytics, audit, 
                            distribution, holonic_evaluator, visualizer, api_service, scheduler)

CHANGELOG v3.7.12:
    - 🔧 FIX: Fixed transaction detail display for nested transaction data
    - FIXED: Access tx.get('transaction', tx) to handle nested structure
    - IMPACT: Transaction amounts and destinations now display correctly
    - NOTE: Distribution service wraps transaction data in result object

CHANGELOG v3.7.11:
    - 🔧 FIX: Fixed string formatting error in execute-rebalance results display
    - FIXED: Use tx.get('amount') instead of tx['amount'] for safe access
    - IMPACT: execute-rebalance results now display without AttributeError

CHANGELOG v3.7.10:
    - 🔧 FIX: Improved rebalance execution safety checks
    - FIXED: Added validation for required transaction fields
    - ENHANCED: Better error messages for malformed transactions
    - IMPACT: Prevent errors when rebalance generates invalid transactions

CHANGELOG v3.7.9:
    - 🔧 FIX: Fixed handle_distribution results display for check-compliance
    - FIXED: Access distribution_state via result['distribution_state']
    - IMPACT: Compliance checks now display current distribution properly

CHANGELOG v3.7.8:
    - 🔧 FIX: Fixed dry-run display logic in execute-rebalance
    - FIXED: Show DRY RUN banner only when dry_run=True
    - ENHANCED: Clear distinction between dry-run and live execution
    - IMPACT: execute-rebalance now correctly indicates execution mode

CHANGELOG v3.7.7:
    - 🔧 FIX: Restored full command set in argument parser
    - FIXED: Added back all commands that were accidentally removed
    - IMPACT: All operations (sync, analytics, evaluate-holonic, etc.) restored

CHANGELOG v3.7.6:
    - 🔧 FIX: Added missing 'audit' dependency to distribution service
    - FIXED: Registered audit service BEFORE distribution service
    - FIXED: Pass audit_service to create_distribution_service factory
    - RESOLVES: KeyError when distribution service initializes
    - IMPACT: Distribution service now initializes correctly with audit logging

CHANGELOG v3.7.5:
    - 🔧 FIX: Corrected distribution service factory parameters
    - FIXED: Changed 'database=' to 'db_manager=' (matches factory signature)
    - ADDED: 'audit_service' parameter to distribution service initialization
    - IMPACT: Distribution service now initializes without parameter errors

CHANGELOG v3.7.4:
    - 🔧 FIX: Added holonic_evaluator dependency to health check services list
    - IMPACT: Holonic evaluator now monitored in health checks

CHANGELOG v3.7.3:
    - 🔧 FIX: Removed scheduler from auto-start in handle_health
    - WHY: Scheduler should only start in serve mode, not during health checks
    - IMPACT: Health checks no longer inadvertently start scheduler background loop

CHANGELOG v3.7.2:
    - 🔧 FIX: Fixed scheduler service initialization
    - ISSUE: Scheduler was being instantiated directly instead of via factory
    - ROOT CAUSE: register() stores factory function directly without calling it
    - SOLUTION: register_factory() stores in _factories and calls on first access

CHANGELOG v3.5.1:
    - 🔥 CRITICAL FIX: Corrected distribution service factory parameters
    - FIXED: Changed 'database=' to 'db_manager=' (matches factory signature)
    - ADDED: 'audit_service' parameter to distribution service initialization
    - FIXED: Moved audit service registration BEFORE distribution (dependency order)

CHANGELOG v3.5.0:
    - 🔧 FIX: Corrected dry-run argument parsing logic for execute-rebalance
    - FIXED: Removed redundant --dry-run flag
    - SIMPLIFIED: Now uses single --live flag to override default dry-run behavior
"""

import asyncio
import argparse
import logging
import sys
import os
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import uvicorn
from dotenv import load_dotenv

# ========================================================================
# LOAD ENVIRONMENT VARIABLES
# Principle #8: No Duplicate Configuration - Single source from .env
# ========================================================================

# Load environment variables from .env file FIRST
load_dotenv()

# ========================================================================
# IMPORT CORE COMPONENTS
# Principle #3: Service Registry - Central orchestration
# ========================================================================

from core.service_registry import ServiceRegistry
from core.db.database_manager import AsyncDatabaseManager
from config.logging import setup_logging

# ========================================================================
# LOGGING SETUP
# Principle #11: Comprehensive Documentation
# ========================================================================

# Setup logging after loading env vars
setup_logging()
logger = logging.getLogger(__name__)

# CRITICAL: Force logging to INFO level for console output
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Ensure we have a console handler with INFO level
console_handler = None
for handler in root_logger.handlers:
    handler.setLevel(logging.INFO)
    if isinstance(handler, logging.StreamHandler):
        console_handler = handler

if not console_handler:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


# ========================================================================
# SERVICE REGISTRY FACTORY
# Principle #3: Service Registry - Central dependency management
# ========================================================================

def register_core_services() -> ServiceRegistry:
    """
    Register all core services with the service registry.
    
    This function registers services in dependency order:
    1. Configuration services (no dependencies)
    2. Infrastructure services (database, Stellar client)
    3. Protocol services (depends on infrastructure)
    4. Analytics services (depends on protocol services)
    5. Evaluation services (depends on analytics)
    6. Community services (bioregion management)
    7. Utility services (audit, scheduler)
    
    Returns:
        ServiceRegistry with all services registered
        
    Design Principles:
        ✅ #3: Service Registry for dependency management
        ✅ #10: Clear separation of concerns
        ✅ #12: Method singularity - services registered once
    """
    registry = ServiceRegistry()
    
    logger.info("=" * 70)
    logger.info("REGISTERING CORE SERVICES")
    logger.info("=" * 70)
    
    # ========================================================================
    # CONFIGURATION SERVICES (No dependencies)
    # ========================================================================
    
    async def create_config(registry):
        """Create system configuration from database."""
        from config.settings import get_system_config
        logger.info("✅ Registering: System Configuration")
        
        # Create bootstrap database connection to load configuration
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', '5432'))
        db_name = os.getenv('DB_NAME', 'ubec_protocol')
        db_user = os.getenv('DB_USER', 'ubec_user')
        db_password = os.getenv('DB_PASSWORD', '')
        
        logger.info(f"📊 Connecting to database: {db_user}@{db_host}:{db_port}/{db_name}")
        
        bootstrap_db = AsyncDatabaseManager(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            schema='ubec_main'
        )
        
        await bootstrap_db.initialize()
        logger.info("✅ Bootstrap database connection established")
        
        # Load configuration from database using factory function
        config = await get_system_config(bootstrap_db)
        logger.info("✅ Configuration loaded from database")
        
        # Close bootstrap connection
        await bootstrap_db.close()
        logger.info("✅ Bootstrap database connection closed")
        
        return config
    
    registry.register_factory('config', create_config, dependencies=[])
    
    # ========================================================================
    # INFRASTRUCTURE SERVICES (Depends on config)
    # ========================================================================
    
    async def create_database(registry):
        """Create database manager with configuration."""
        logger.info("✅ Registering: Database Manager")
        
        # Get config from registry
        config = await registry.get('config')
        
        # Get database configuration from environment
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'ubec_protocol'),
            'user': os.getenv('DB_USER', 'ubec_user'),
            'password': os.getenv('DB_PASSWORD', ''),
            'schema': 'ubec_main'
        }
        
        logger.info(f"📊 Creating production database pool: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        db = AsyncDatabaseManager(**db_config)
        await db.initialize()
        
        logger.info("✅ Database manager initialized")
        return db
    
    registry.register_factory('database', create_database, dependencies=['config'])
    
    async def create_rate_limiter(registry):
        """
        Create rate limiter service.
        
        Dependencies: database (for loading rate limit configurations)
        """
        from services.stellar.rate_limiter_service import create_rate_limiter_service
        logger.info("✅ Registering: Rate Limiter Service")
        
        # Get dependencies from registry
        db_manager = await registry.get('database')
        
        # Create and initialize rate limiter service
        rate_limiter = create_rate_limiter_service(db_manager)
        await rate_limiter.initialize()
        
        logger.info("✅ Rate limiter service initialized")
        return rate_limiter
    
    registry.register_factory('rate_limiter', create_rate_limiter, 
                             dependencies=['database'])
    
    async def create_stellar_client(registry):
        """
        Create Stellar client with rate limiting.
        
        Uses the correct import path: services.stellar.stellar_client_service
        Dependencies: config (for database settings), rate_limiter (for API rate limiting)
        """
        from services.stellar.stellar_client_service import StellarClientService
        logger.info("✅ Registering: Stellar Client")
        
        # Get dependencies from registry
        config = await registry.get('config')
        rate_limiter = await registry.get('rate_limiter')
        
        # Create service with dependencies
        client = StellarClientService(config=config, rate_limiter=rate_limiter)
        
        # Initialize service (loads config from database)
        await client.initialize()
        logger.info("✅ Stellar client initialized")
        return client
    
    registry.register_factory('stellar_client', create_stellar_client, 
                             dependencies=['config', 'rate_limiter'])
    
    # ========================================================================
    # PROTOCOL SERVICES (Depends on infrastructure)
    # ========================================================================
    
    async def create_air_protocol(registry):
        """Create Air/UBEC Protocol service."""
        from core.protocols.UBEC_protocol import create_ubec_service
        logger.info("✅ Registering: Air Protocol (UBEC)")
        
        # Get dependencies from registry
        database = await registry.get('database')
        stellar_client = await registry.get('stellar_client')
        config = await registry.get('config')
        
        service = await create_ubec_service(
            db_manager=database,
            config={'asset_code': 'UBEC', 'issuer': config.get('ubec_issuer')},
            stellar_client=stellar_client
        )
        
        logger.info("✅ Air Protocol service initialized")
        return service
    
    registry.register_factory('air_protocol', create_air_protocol,
                             dependencies=['database', 'stellar_client', 'config'])
    
    async def create_water_protocol(registry):
        """Create Water/UBECrc Protocol service."""
        from core.protocols.UBECrc_protocol import create_ubecrc_service
        logger.info("✅ Registering: Water Protocol (UBECrc)")
        
        # Get dependencies from registry
        database = await registry.get('database')
        stellar_client = await registry.get('stellar_client')
        config = await registry.get('config')
        
        service = await create_ubecrc_service(
            db_manager=database,
            config={'asset_code': 'UBECrc', 'issuer': config.get('ubecrc_issuer')},
            stellar_client=stellar_client
        )
        
        logger.info("✅ Water Protocol service initialized")
        return service
    
    registry.register_factory('water_protocol', create_water_protocol,
                             dependencies=['database', 'stellar_client', 'config'])
    
    async def create_earth_protocol(registry):
        """Create Earth/UBECgpi Protocol service."""
        from core.protocols.UBECgpi_protocol import create_ubecgpi_service
        logger.info("✅ Registering: Earth Protocol (UBECgpi)")
        
        # Get dependencies from registry
        database = await registry.get('database')
        stellar_client = await registry.get('stellar_client')
        config = await registry.get('config')
        
        service = await create_ubecgpi_service(
            db_manager=database,
            config={'asset_code': 'UBECgpi', 'issuer': config.get('ubecgpi_issuer')},
            stellar_client=stellar_client
        )
        
        logger.info("✅ Earth Protocol service initialized")
        return service
    
    registry.register_factory('earth_protocol', create_earth_protocol,
                             dependencies=['database', 'stellar_client', 'config'])
    
    async def create_fire_protocol(registry):
        """Create Fire/UBECtt Protocol service."""
        from core.protocols.UBECtt_protocol import create_ubectt_service
        logger.info("✅ Registering: Fire Protocol (UBECtt)")
        
        # Get dependencies from registry
        database = await registry.get('database')
        stellar_client = await registry.get('stellar_client')
        config = await registry.get('config')
        
        service = await create_ubectt_service(
            db_manager=database,
            config={'asset_code': 'UBECtt', 'issuer': config.get('ubectt_issuer')},
            stellar_client=stellar_client
        )
        
        logger.info("✅ Fire Protocol service initialized")
        return service
    
    registry.register_factory('fire_protocol', create_fire_protocol,
                             dependencies=['database', 'stellar_client', 'config'])
    
    # ========================================================================
    # SYNC SERVICE (Depends on database and stellar_client)
    # ========================================================================
    
    async def create_sync(registry):
        """
        Create blockchain synchronization service.
        
        The sync service synchronizes UBEC token family data from the Stellar
        blockchain to the PostgreSQL database. Handles all four UBEC tokens:
        UBEC (Air), UBECrc (Water), UBECgpi (Earth), UBECtt (Fire).
        
        v5.2.9: Now includes cleanup_irrelevant_accounts() method for
        removing accounts with no UBEC trustlines or zero balance.
        
        Dependencies:
            - database: For storing synchronized blockchain data
            - stellar_client: For accessing Stellar Horizon API
            - config: For system configuration
        """
        from core.db.ubec_data_synchronizer import register_factory as create_synchronizer
        logger.info("✅ Registering: Blockchain Sync Service")
        
        # Get dependencies from registry
        database = await registry.get('database')
        config = await registry.get('config')
        stellar_client = await registry.get('stellar_client')
        
        # Create and initialize synchronizer service
        service = await create_synchronizer(
            database=database,
            config=config,
            stellar_client=stellar_client
        )
        
        logger.info("✅ Blockchain sync service initialized")
        return service
    
    registry.register_factory('sync', create_sync,
                             dependencies=['database', 'config', 'stellar_client'])
    
    # ========================================================================
    # ANALYTICS SERVICES (Depends on protocol services)
    # ========================================================================
    
    async def create_analytics(registry):
        """Create analytics service."""
        from services.analytics.ubec_analytics_service import UBECAnalyticsService
        logger.info("✅ Registering: Analytics Service")
        
        # Get dependencies from registry
        database = await registry.get('database')
        config = await registry.get('config')
        
        service = UBECAnalyticsService(database=database, config=config)
        await service.initialize()
        
        logger.info("✅ Analytics service initialized")
        return service
    
    registry.register_factory('analytics', create_analytics,
                             dependencies=['database', 'config'])
    
    # ========================================================================
    # AUDIT SERVICE (Depends on database)
    # ========================================================================
    
    async def create_audit(registry):
        """Create audit service."""
        from services.audit.ubec_audit_service import create_audit_service
        logger.info("✅ Registering: Audit Service")
        
        # Get dependencies from registry
        database = await registry.get('database')
        config = await registry.get('config')
        
        service = await create_audit_service(db_manager=database, config=config)
        
        logger.info("✅ Audit service initialized")
        return service
    
    registry.register_factory('audit', create_audit,
                             dependencies=['database', 'config'])
    
    # ========================================================================
    # DISTRIBUTION SERVICE (Depends on database, stellar client, and audit)
    # ========================================================================
    
    async def create_distribution(registry):
        """Create distribution service."""
        from services.distribution.ubec_distribution_service import create_distribution_service
        logger.info("✅ Registering: Distribution Service")
        
        # Get dependencies from registry
        database = await registry.get('database')
        stellar_client = await registry.get('stellar_client')
        config = await registry.get('config')
        audit = await registry.get('audit')
        
        service = await create_distribution_service(
            db_manager=database,
            stellar_client=stellar_client,
            config=config,
            audit_service=audit
        )
        
        # Initialize service (loads configuration from database)
        await service.initialize()
        
        logger.info("✅ Distribution service initialized")
        return service
    
    registry.register_factory('distribution', create_distribution,
                             dependencies=['database', 'stellar_client', 'config', 'audit'])
    
    # ========================================================================
    # HOLONIC EVALUATION SERVICE (Depends on analytics)
    # ========================================================================
    
    async def create_holonic_evaluator(registry):
        """Create holonic evaluation service."""
        from core.holonic.ubec_holonic_evaluator import create_holonic_evaluator
        logger.info("✅ Registering: Holonic Evaluator")
        
        # Get dependencies from registry
        database = await registry.get('database')
        config = await registry.get('config')
        
        service = await create_holonic_evaluator(db_manager=database, config=config)
        
        logger.info("✅ Holonic evaluator initialized")
        return service
    
    registry.register_factory('holonic_evaluator', create_holonic_evaluator,
                             dependencies=['database', 'config'])
    
    # ========================================================================
    # HOLONIC VISUALIZER (Depends on holonic evaluator)
    # ========================================================================
    
    async def create_visualizer(registry):
        """Create holonic visualizer service."""
        from core.holonic.ubec_holonic_visualizer import create_holonic_visualizer
        logger.info("✅ Registering: Holonic Visualizer")
        
        # Get dependencies from registry
        database = await registry.get('database')
        config = await registry.get('config')
        
        service = await create_holonic_visualizer(db_manager=database, config=config)
        
        logger.info("✅ Holonic visualizer initialized")
        return service
    
    registry.register_factory('visualizer', create_visualizer,
                             dependencies=['database', 'config'])
    
    # ========================================================================
    # BIOREGION MANAGER SERVICE (Depends on database)
    # ========================================================================
    
    async def create_bioregion_manager(registry):
        """
        Create bioregion manager service.
        
        Manages bioregional holons - geographic economic communities defined by
        natural boundaries (watersheds, ecosystems) and cultural characteristics.
        
        Uses phenomenal.holons table for data storage with explicit schema naming.
        Supports automated updates via scheduler integration.
        
        Dependencies:
            - database: For accessing phenomenal.holons table
        """
        from services.bioregion.bioregion_manager_service import create_bioregion_manager
        logger.info("✅ Registering: Bioregion Manager")
        
        # Get dependencies from registry
        database = await registry.get('database')
        
        # Create and initialize bioregion manager service
        service = await create_bioregion_manager(registry)
        
        logger.info("✅ Bioregion manager initialized")
        return service
    
    registry.register_factory('bioregion_manager', create_bioregion_manager,
                             dependencies=['database'])
    
    # ========================================================================
    # API SERVICE (Depends on infrastructure and analytics services)
    # ========================================================================
    
    async def create_api_service(registry):
        """
        Create Backend API Service for REST endpoints.
        
        The API service provides read-only REST endpoints for the public website,
        with comprehensive rate limiting and proper error handling.
        
        Dependencies:
            - database: For direct database queries
            - config: For system configuration
            - analytics: For ecosystem metrics
            - distribution: For tokenomics compliance
            - holonic_evaluator: For Ubuntu alignment scores
        """
        from services.api.api_service import create_backend_api_service
        logger.info("✅ Registering: Backend API Service")
        
        # Create API service with registry for dependency injection
        api_service = await create_backend_api_service(registry)
        
        logger.info("✅ Backend API service initialized")
        return api_service
    
    registry.register_factory('api_service', create_api_service,
                             dependencies=['database', 'config', 'analytics', 'distribution', 'holonic_evaluator'])
    
    # ========================================================================
    # SCHEDULER SERVICE (Depends on all services)
    # ========================================================================
    
    async def create_scheduler(registry):
        """
        Create scheduler service for automated task execution.
        
        IMPORTANT: The scheduler is registered and initialized here, but NOT started.
        Starting the scheduler means beginning the background job execution loop.
        
        Scheduler Lifecycle:
        1. Registration (here) - Service factory registered with registry
        2. Initialization (on first access) - Service created, jobs loaded from DB
        3. Starting (explicit call) - Background loop begins executing jobs
        
        The scheduler ONLY starts in serve mode via handle_serve() function.
        This ensures:
        - Health checks don't inadvertently start background jobs
        - Scheduler only runs when API server is active
        - Clean separation between initialization and execution
        
        When you see "NOT_STARTED" in health checks, this is CORRECT behavior.
        The scheduler should only show "RUNNING" when serve mode is active.
        
        Uses factory function from ubec_scheduler_service module.
        """
        from services.scheduler.ubec_scheduler_service import create_scheduler_service
        logger.info("✅ Registering: Scheduler Service")
        
        # Use the factory function which handles initialization
        scheduler = await create_scheduler_service(registry)
        
        logger.info("✅ Scheduler service initialized (not started - call start() to begin)")
        return scheduler
    
    registry.register_factory('scheduler', create_scheduler,
                             dependencies=['database', 'config'])
    
    logger.info("=" * 70)
    logger.info("SERVICE REGISTRATION COMPLETE")
    logger.info(f"Total services registered: {len(registry.list_services())}")
    logger.info("=" * 70)
    
    return registry


# ========================================================================
# COMMAND HANDLERS
# Principle #10: Separation of Concerns - Each handler does one thing
# ========================================================================

async def handle_health(registry: ServiceRegistry, detailed: bool = False):
    """
    Perform system health check.
    
    NOTE: The scheduler will show "NOT_STARTED" status here, which is CORRECT.
    The scheduler only starts in serve mode, not during health checks.
    This prevents background jobs from running during diagnostic operations.
    
    Args:
        registry: Service registry with initialized services
        detailed: Whether to show detailed health information
    """
    logger.info("=" * 70)
    logger.info("SYSTEM HEALTH CHECK")
    logger.info("=" * 70)
    
    # Get all services
    services = [
        ('database', 'Database'),
        ('stellar_client', 'Stellar Client'),
        ('air_protocol', 'Air Protocol (UBEC)'),
        ('water_protocol', 'Water Protocol (UBECrc)'),
        ('earth_protocol', 'Earth Protocol (UBECgpi)'),
        ('fire_protocol', 'Fire Protocol (UBECtt)'),
        ('sync', 'Blockchain Sync Service'),
        ('analytics', 'Analytics Service'),
        ('distribution', 'Distribution Service'),
        ('holonic_evaluator', 'Holonic Evaluator'),
        ('visualizer', 'Holonic Visualizer'),
        ('audit', 'Audit Service'),
        ('bioregion_manager', 'Bioregion Manager'),
        ('api_service', 'API Service'),
        ('scheduler', 'Scheduler Service'),
    ]
    
    healthy_count = 0
    total_count = len(services)
    
    for service_key, service_name in services:
        try:
            service = await registry.get(service_key)
            
            # Check if service has health_check method
            if hasattr(service, 'health_check'):
                health = await service.health_check()
                status = health.get('status', 'unknown')
                
                # Special handling for scheduler NOT_STARTED status
                if service_key == 'scheduler' and status == 'not_started':
                    logger.info(f"✅ {service_name}: NOT_STARTED (expected in health check mode)")
                    healthy_count += 1
                    if detailed:
                        logger.info("   ℹ️  Scheduler only starts in serve mode")
                        logger.info("   ℹ️  This status is correct and expected")
                elif status == 'healthy':
                    logger.info(f"✅ {service_name}: HEALTHY")
                    healthy_count += 1
                    
                    if detailed and 'details' in health:
                        for key, value in health['details'].items():
                            logger.info(f"   {key}: {value}")
                else:
                    logger.warning(f"⚠️  {service_name}: {status.upper()}")
                    
                    if 'error' in health:
                        logger.warning(f"   Error: {health['error']}")
                    if 'message' in health:
                        logger.warning(f"   Message: {health['message']}")
            else:
                logger.info(f"✅ {service_name}: OK (no health check)")
                healthy_count += 1
                
        except Exception as e:
            logger.error(f"❌ {service_name}: ERROR - {e}")
    
    # Overall health summary
    logger.info("\n" + "=" * 70)
    logger.info(f"HEALTH SUMMARY: {healthy_count}/{total_count} services healthy")
    logger.info("=" * 70)
    
    return {'healthy': healthy_count, 'total': total_count}


async def handle_status(registry: ServiceRegistry):
    """Get detailed system status."""
    logger.info("=" * 70)
    logger.info("SYSTEM STATUS")
    logger.info("=" * 70)
    
    # Get all services for status check
    services_to_check = [
        'database', 'stellar_client', 'air_protocol', 'water_protocol',
        'earth_protocol', 'fire_protocol', 'sync', 'analytics', 'distribution',
        'holonic_evaluator', 'visualizer', 'audit', 'bioregion_manager',
        'api_service', 'scheduler'
    ]
    
    for service_key in services_to_check:
        try:
            service = await registry.get(service_key)
            
            if hasattr(service, 'health_check'):
                health = await service.health_check()
                logger.info(f"\n{service_key}:")
                logger.info(f"  Status: {health.get('status', 'unknown')}")
                
                if 'details' in health:
                    for key, value in health['details'].items():
                        logger.info(f"  {key}: {value}")
        except Exception as e:
            logger.error(f"Error checking {service_key}: {e}")


async def handle_sync_status(registry: ServiceRegistry):
    """Check data synchronization status."""
    logger.info("=" * 70)
    logger.info("SYNCHRONIZATION STATUS")
    logger.info("=" * 70)
    
    try:
        # Check each protocol's sync status
        protocols = [
            ('air_protocol', 'UBEC (Air)'),
            ('water_protocol', 'UBECrc (Water)'),
            ('earth_protocol', 'UBECgpi (Earth)'),
            ('fire_protocol', 'UBECtt (Fire)')
        ]
        
        for protocol_key, protocol_name in protocols:
            protocol = await registry.get(protocol_key)
            
            if hasattr(protocol, 'get_sync_status'):
                status = await protocol.get_sync_status()
                logger.info(f"\n{protocol_name}:")
                logger.info(f"  Last Sync: {status.get('last_sync', 'Never')}")
                logger.info(f"  Accounts: {status.get('account_count', 0)}")
                logger.info(f"  Status: {status.get('status', 'Unknown')}")
                
    except Exception as e:
        logger.error(f"Error checking sync status: {e}")


async def handle_discover(registry: ServiceRegistry, max_accounts: int = 100):
    """Discover token holders for all UBEC tokens."""
    logger.info("=" * 70)
    logger.info(f"DISCOVERING TOKEN HOLDERS (max: {max_accounts} per token)")
    logger.info("=" * 70)
    
    try:
        sync_service = await registry.get('sync')
        
        # Discover holders for each token
        tokens = ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']
        
        for token in tokens:
            logger.info(f"\nDiscovering {token} holders...")
            
            if hasattr(sync_service, 'discover_token_holders'):
                result = await sync_service.discover_token_holders(
                    asset_code=token,
                    max_accounts=max_accounts
                )
                
                logger.info(f"✓ Found {result.get('discovered', 0)} holders for {token}")
            else:
                logger.warning(f"Sync service doesn't support discovery")
                
    except Exception as e:
        logger.error(f"Discovery failed: {e}", exc_info=True)


async def handle_sync(
    registry: ServiceRegistry,
    sync_type: str = 'all',
    max_accounts: Optional[int] = None,
    force: bool = False
):
    """
    Synchronize blockchain data.
    
    Args:
        registry: Service registry
        sync_type: Type of sync (all, UBEC, UBECrc, UBECgpi, UBECtt)
        max_accounts: Maximum accounts to sync per token
        force: Force resync even if recently synced
    """
    logger.info("=" * 70)
    logger.info(f"BLOCKCHAIN SYNCHRONIZATION (type: {sync_type})")
    logger.info("=" * 70)
    
    try:
        sync_service = await registry.get('sync')
        
        tokens_to_sync = ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt'] if sync_type == 'all' else [sync_type]
        
        for token in tokens_to_sync:
            logger.info(f"\n{'='*70}")
            logger.info(f"Syncing {token}...")
            logger.info(f"{'='*70}")
            
            if hasattr(sync_service, 'sync_token_data'):
                result = await sync_service.sync_token_data(
                    asset_code=token,
                    max_accounts=max_accounts,
                    force=force
                )
                
                logger.info(f"\n✓ Sync complete for {token}:")
                logger.info(f"  Accounts synced: {result.get('accounts_synced', 0)}")
                logger.info(f"  Operations synced: {result.get('operations_synced', 0)}")
                logger.info(f"  Duration: {result.get('duration', 0):.2f}s")
            else:
                logger.warning(f"Sync service doesn't support token sync")
                
    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)


async def handle_cleanup(
    registry: ServiceRegistry,
    dry_run: bool = True,
    include_zero_balance: bool = True
):
    """
    Clean up irrelevant accounts from the database.
    
    NEW in v3.8.3: Removes accounts that have no relevance to UBEC tokens:
    1. Accounts with no UBEC trustlines (no entry in ubec_balances)
    2. Optionally: Accounts with zero balance across all tokens
    
    These accounts typically result from:
    - One-time interactions that never materialized into holdings
    - Accounts that removed their trustlines
    - Historical sync artifacts
    
    The cleanup respects foreign key constraints by deleting in order:
    1. stellar_operations (references transactions and accounts)
    2. stellar_transactions (references accounts)
    3. ubec_balances (references accounts)
    4. stellar_accounts (parent table)
    
    Args:
        registry: Service registry
        dry_run: If True, preview only. If False, perform deletion. Default: True
        include_zero_balance: If True, also remove zero-balance accounts. Default: True
    
    Design Principles:
        ✅ #4: Database as single source of truth (explicit schema names)
        ✅ #5: Strict async operations
        ✅ #10: Separation of concerns (uses sync service method)
        ✅ #11: Comprehensive documentation
    """
    logger.info("=" * 70)
    logger.info(f"ACCOUNT CLEANUP {'(DRY RUN - PREVIEW ONLY)' if dry_run else '(LIVE - DELETING)'}")
    logger.info("=" * 70)
    
    try:
        # Get sync service (cleanup method is on sync service)
        sync_service = await registry.get('sync')
        
        # Check if sync service has cleanup method
        if not hasattr(sync_service, 'cleanup_irrelevant_accounts'):
            logger.error("Sync service does not have cleanup_irrelevant_accounts method")
            logger.error("Please update ubec_data_synchronizer.py to v5.2.9 or later")
            return
        
        # Perform cleanup
        result = await sync_service.cleanup_irrelevant_accounts(
            dry_run=dry_run,
            include_zero_balance=include_zero_balance
        )
        
        # Display results
        logger.info("\n" + "=" * 70)
        logger.info(f"{'PREVIEW' if dry_run else 'CLEANUP'} RESULTS")
        logger.info("=" * 70)
        logger.info(f"Accounts with no trustlines: {result['no_trustline_count']}")
        logger.info(f"Accounts with zero balance:  {result['zero_balance_count']}")
        logger.info(f"Total identified:            {result['total_accounts']}")
        
        if dry_run:
            # Show preview information
            if result.get('affected_transactions'):
                logger.info(f"Would affect transactions:   ~{result['affected_transactions']}")
            if result.get('affected_operations'):
                logger.info(f"Would affect operations:     ~{result['affected_operations']}")
            
            if result.get('sample_accounts'):
                logger.info(f"\nSample accounts to remove (first 20):")
                for acc in result['sample_accounts'][:20]:
                    logger.info(f"  - {acc}")
            
            logger.info(f"\n⚠️  This was a DRY RUN - no data was modified")
            logger.info(f"   Run with --execute to perform actual deletion")
        else:
            # Show deletion results
            logger.info(f"\nDELETED:")
            logger.info(f"  Accounts:        {result['deleted']['accounts']}")
            logger.info(f"  Transactions:    {result['deleted']['transactions']}")
            logger.info(f"  Operations:      {result['deleted']['operations']}")
            logger.info(f"  Balances:        {result['deleted']['balances']}")
            logger.info(f"  Holonic metrics: {result['deleted'].get('holonic_metrics', 0)}")
            logger.info(f"\n✓ Cleanup completed successfully")
        
        logger.info(f"\nDuration: {result.get('duration_seconds', 0):.2f} seconds")
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}", exc_info=True)
        raise


async def handle_analytics(registry: ServiceRegistry, analysis_type: str = 'overview'):
    """Run analytics on ecosystem data."""
    logger.info("=" * 70)
    logger.info(f"ANALYTICS: {analysis_type.upper()}")
    logger.info("=" * 70)
    
    try:
        analytics = await registry.get('analytics')
        
        if analysis_type == 'overview':
            if hasattr(analytics, 'get_ecosystem_overview'):
                result = await analytics.get_ecosystem_overview()
                
                logger.info("\n✓ Ecosystem Overview:")
                logger.info(f"  Total Supply: {result.get('total_supply', 0):,.2f}")
                logger.info(f"  Circulating: {result.get('circulating', 0):,.2f}")
                logger.info(f"  Holders: {result.get('total_holders', 0)}")
                
        elif analysis_type == 'detailed':
            logger.info("Detailed analytics not yet implemented")
            
    except Exception as e:
        logger.error(f"Analytics failed: {e}", exc_info=True)


async def handle_holonic_evaluation(
    registry: ServiceRegistry,
    evaluate_all: bool = False,
    account_id: Optional[str] = None,
    max_accounts: Optional[int] = None,
    save_to_db: bool = True
):
    """
    Evaluate Ubuntu principles for accounts.
    
    Args:
        registry: Service registry
        evaluate_all: Evaluate all accounts
        account_id: Specific account to evaluate
        max_accounts: Maximum accounts to evaluate
        save_to_db: Whether to save results to database
    """
    logger.info("=" * 70)
    logger.info("HOLONIC EVALUATION")
    logger.info("=" * 70)
    
    try:
        evaluator = await registry.get('holonic_evaluator')
        
        if account_id:
            logger.info(f"\nEvaluating account: {account_id}")
            
            if hasattr(evaluator, 'evaluate_account'):
                result = await evaluator.evaluate_account(
                    account_id=account_id,
                    save_to_db=save_to_db
                )
                
                logger.info(f"\n✓ Evaluation complete:")
                logger.info(f"  Ubuntu Score: {result.ubuntu_alignment_score:.3f}")
                logger.info(f"  Category: {result.category.value}")
                
        elif evaluate_all:
            logger.info("\nEvaluating all accounts...")
            
            if hasattr(evaluator, 'evaluate_all_accounts'):
                result = await evaluator.evaluate_all_accounts(
                    max_accounts=max_accounts,
                    save_to_db=save_to_db
                )
                
                logger.info(f"\n✓ Batch evaluation complete:")
                logger.info(f"  Accounts evaluated: {result.get('evaluated', 0)}")
                logger.info(f"  Average Ubuntu score: {result.get('avg_score', 0):.3f}")
                
    except Exception as e:
        logger.error(f"Holonic evaluation failed: {e}", exc_info=True)


async def handle_visualize(
    registry: ServiceRegistry,
    action: str = 'report',
    format: str = 'html',
    include_advanced: bool = False
):
    """
    Generate visualizations.
    
    Args:
        registry: Service registry
        action: Action to perform (report)
        format: Output format (html, json)
        include_advanced: Include advanced metrics
    """
    logger.info("=" * 70)
    logger.info(f"VISUALIZATION: {action.upper()}")
    logger.info("=" * 70)
    
    try:
        visualizer = await registry.get('visualizer')
        
        if action == 'report':
            if hasattr(visualizer, 'generate_report'):
                result = await visualizer.generate_report(
                    format=format,
                    include_advanced=include_advanced
                )
                
                logger.info(f"\n✓ Report generated: {result.get('file_path')}")
                
    except Exception as e:
        logger.error(f"Visualization failed: {e}", exc_info=True)


async def handle_protocol_health(registry: ServiceRegistry):
    """Check health of all four element protocols."""
    logger.info("=" * 70)
    logger.info("PROTOCOL HEALTH CHECK")
    logger.info("=" * 70)
    
    protocols = [
        ('air_protocol', 'Air/UBEC'),
        ('water_protocol', 'Water/UBECrc'),
        ('earth_protocol', 'Earth/UBECgpi'),
        ('fire_protocol', 'Fire/UBECtt')
    ]
    
    for protocol_key, protocol_name in protocols:
        try:
            protocol = await registry.get(protocol_key)
            
            if hasattr(protocol, 'health_check'):
                health = await protocol.health_check()
                status = health.get('status', 'unknown')
                
                logger.info(f"\n{protocol_name}:")
                logger.info(f"  Status: {status}")
                
                if 'details' in health:
                    details = health['details']
                    logger.info(f"  Last Sync: {details.get('last_sync', 'N/A')}")
                    logger.info(f"  Cached Accounts: {details.get('cached_accounts', 0)}")
                    
        except Exception as e:
            logger.error(f"Error checking {protocol_name}: {e}")


async def handle_scheduler_status(registry: ServiceRegistry):
    """Check scheduler service status and job information."""
    logger.info("=" * 70)
    logger.info("SCHEDULER STATUS")
    logger.info("=" * 70)
    
    try:
        scheduler = await registry.get('scheduler')
        
        if hasattr(scheduler, 'health_check'):
            health = await scheduler.health_check()
            
            logger.info(f"\nStatus: {health.get('status', 'unknown').upper()}")
            logger.info(f"Running: {health.get('running', False)}")
            
            if 'jobs' in health:
                logger.info(f"\nJobs ({len(health['jobs'])}):")
                for job in health['jobs']:
                    logger.info(f"\n  {job.get('name', 'unknown')}:")
                    logger.info(f"    Enabled: {job.get('enabled', False)}")
                    logger.info(f"    Next run: {job.get('next_run', 'N/A')}")
                    logger.info(f"    Success rate: {job.get('success_rate', 0):.1%}")
        else:
            logger.info("Scheduler does not provide health information")
            
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")


async def handle_distribution(
    registry: ServiceRegistry,
    action: str = 'status',
    dry_run: bool = True
):
    """
    Handle distribution operations.
    
    Args:
        registry: Service registry
        action: Action to perform
        dry_run: Whether to run in dry-run mode (default: True)
    """
    logger.info("=" * 70)
    logger.info(f"DISTRIBUTION: {action.upper()}")
    logger.info("=" * 70)
    
    try:
        distribution = await registry.get('distribution')
        
        if action == 'status':
            logger.info("Getting distribution status...")
            status = await distribution.get_current_state()
            
            logger.info(f"\n✓ Distribution Status:")
            logger.info(f"  Total Supply: {status.get('total_supply', 0):,.2f} UBEC")
            logger.info(f"  Circulating: {status.get('circulating', 0):,.2f} UBEC")
            
        elif action == 'check-compliance':
            logger.info("Checking tokenomics compliance...")
            result = await distribution.check_compliance()
            
            dist_state = result.get('distribution_state', {})
            logger.info(f"\n✓ Compliance Check:")
            logger.info(f"  Status: {result.get('status', 'unknown')}")
            logger.info(f"  General Distribution: {dist_state.get('general_pct', 0):.2f}%")
            logger.info(f"  Stewardship: {dist_state.get('steward_pct', 0):.2f}%")
            logger.info(f"  Administration: {dist_state.get('admin_pct', 0):.2f}%")
            
        elif action == 'rebalance-check':
            logger.info("Checking if rebalance is needed...")
            result = await distribution.check_rebalance_needed()
            
            logger.info(f"\n✓ Rebalance Check:")
            logger.info(f"  Rebalance needed: {result.get('rebalance_needed', False)}")
            
        elif action == 'execute-rebalance':
            if dry_run:
                logger.info("\n" + "=" * 70)
                logger.info("DRY RUN MODE - No actual transactions will be executed")
                logger.info("=" * 70 + "\n")
            
            logger.info("Executing rebalance...")
            result = await distribution.execute_rebalance(dry_run=dry_run)
            
            logger.info(f"\n✓ Rebalance {'Simulation' if dry_run else 'Execution'}:")
            logger.info(f"  Status: {result.get('status', 'unknown')}")
            logger.info(f"  Transactions: {result.get('transaction_count', 0)}")
            
            if result.get('transactions'):
                logger.info("\n  Transaction Details:")
                for tx in result['transactions']:
                    # Handle nested transaction structure
                    tx_data = tx.get('transaction', tx)
                    amount = tx_data.get('amount', 'N/A')
                    dest = tx_data.get('destination', 'N/A')
                    logger.info(f"    {amount} UBEC → {dest[:8]}...")
            
        else:
            logger.warning(f"Unknown action: {action}")
            
    except Exception as e:
        logger.error(f"Distribution operation failed: {e}", exc_info=True)


async def handle_serve(
    registry: ServiceRegistry,
    host: str = '0.0.0.0',
    port: int = 8000,
    reload: bool = False
):
    """
    Start API server with scheduler.
    
    CRITICAL: This is the ONLY place where scheduler.start() is called.
    The scheduler background loop begins here and runs until the server stops.
    
    Scheduler Lifecycle in serve mode:
    1. Get scheduler from registry (already initialized)
    2. Call scheduler.start() to begin background job execution
    3. Start API server
    4. On shutdown, call scheduler.stop() to gracefully terminate jobs
    
    This ensures:
    - Automated background jobs only run when API server is active
    - Clean startup and shutdown of scheduler
    - No scheduler running during health checks or other commands
    
    Args:
        registry: Service registry
        host: Server host
        port: Server port
        reload: Enable auto-reload (development only)
    """
    logger.info("=" * 70)
    logger.info(f"STARTING API SERVER (host: {host}, port: {port})")
    logger.info("=" * 70)
    
    scheduler = None
    
    try:
        # Get API service from registry
        api_service = await registry.get('api_service')
        
        # ═══════════════════════════════════════════════════════════════════
        # CRITICAL: Start the scheduler service here
        # This is the ONLY place where the scheduler background loop starts
        # ═══════════════════════════════════════════════════════════════════
        logger.info("\n" + "=" * 70)
        logger.info("STARTING SCHEDULER SERVICE")
        logger.info("=" * 70)
        
        scheduler = await registry.get('scheduler')
        await scheduler.start()
        
        logger.info("✅ Scheduler started - background jobs active")
        logger.info("=" * 70 + "\n")
        
        # Get the FastAPI app from the service
        app = api_service.app
        
        logger.info(f"🚀 Starting server at http://{host}:{port}")
        logger.info(f"📊 Swagger docs: http://{host}:{port}/docs")
        logger.info("=" * 70)
        
        # Configure uvicorn
        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        # Run server
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Server shutdown requested")
        
    finally:
        # ═══════════════════════════════════════════════════════════════════
        # CRITICAL: Stop scheduler gracefully on shutdown
        # ═══════════════════════════════════════════════════════════════════
        if scheduler:
            try:
                logger.info("\nStopping scheduler...")
                await scheduler.stop()
                logger.info("✅ Scheduler stopped")
            except Exception as e:
                logger.warning(f"⚠️  Error stopping scheduler: {e}")


# ========================================================================
# ARGUMENT PARSER
# ========================================================================

def create_argument_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description='UBEC Protocol Suite - Main Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Check system health')
    health_parser.add_argument('--detailed', action='store_true',
                              help='Show detailed health information')
    
    # Status command
    subparsers.add_parser('status', help='Get system status')
    
    # Sync status command
    subparsers.add_parser('sync-status', help='Check synchronization status')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover token holders')
    discover_parser.add_argument('--max-accounts', type=int, default=100,
                                help='Maximum accounts to discover per token')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Synchronize blockchain data')
    sync_parser.add_argument('--sync-type', type=str, default='all',
                            help='Type of sync: all, UBEC, UBECrc, UBECgpi, UBECtt')
    sync_parser.add_argument('--max-accounts', type=int, default=None,
                            help='Maximum accounts to sync per token')
    sync_parser.add_argument('--force', action='store_true',
                            help='Force resync even if recently synced')
    
    # ════════════════════════════════════════════════════════════════════
    # NEW v3.8.3: Cleanup command
    # ════════════════════════════════════════════════════════════════════
    cleanup_parser = subparsers.add_parser('cleanup', 
                                           help='Remove irrelevant accounts (no UBEC trustlines or zero balance)')
    cleanup_parser.add_argument('--execute', action='store_true',
                               help='Actually perform deletion (default is dry-run/preview)')
    cleanup_parser.add_argument('--keep-zero-balance', action='store_true',
                               help='Keep accounts with zero balance (only remove accounts with no trustlines)')
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Run analytics')
    analytics_parser.add_argument('--analysis-type', type=str, default='overview',
                                  help='Type of analysis: overview, detailed')
    
    # Holonic evaluation command
    holonic_parser = subparsers.add_parser('evaluate-holonic',
                                          help='Evaluate Ubuntu principles')
    holonic_parser.add_argument('--all', action='store_true',
                               help='Evaluate all accounts')
    holonic_parser.add_argument('--account', type=str,
                               help='Specific account to evaluate')
    holonic_parser.add_argument('--max-accounts', type=int,
                               help='Maximum accounts to evaluate')
    holonic_parser.add_argument('--no-save', action='store_true',
                               help='Do not save results to database')
    
    # Visualization command
    viz_parser = subparsers.add_parser('visualize', help='Generate visualizations')
    viz_parser.add_argument('--action', type=str, default='report',
                           help='Action: report')
    viz_parser.add_argument('--format', type=str, default='html',
                           help='Output format: html, json')
    viz_parser.add_argument('--include-advanced', action='store_true',
                           help='Include advanced metrics')
    
    # Protocol health command
    subparsers.add_parser('protocol-health', help='Check protocol health')
    
    # Scheduler status command
    subparsers.add_parser('scheduler-status', help='Check scheduler status')
    
    # Distribution command
    dist_parser = subparsers.add_parser('distribution',
                                       help='Distribution operations')
    dist_parser.add_argument('--action', type=str, default='status',
                            help='Action: status, check-compliance, rebalance-check, execute-rebalance')
    dist_parser.add_argument('--live', action='store_true',
                            help='Execute live (default is dry-run)')
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start API server')
    serve_parser.add_argument('--host', type=str, default='0.0.0.0',
                             help='Server host')
    serve_parser.add_argument('--port', type=int, default=8000,
                             help='Server port')
    serve_parser.add_argument('--reload', action='store_true',
                             help='Enable auto-reload (development)')
    
    return parser


# ========================================================================
# MAIN ENTRY POINT
# ========================================================================

async def main():
    """
    Main entry point for UBEC Protocol Suite.
    
    Orchestrates all system operations through the service registry.
    """
    parser = create_argument_parser()
    args = parser.parse_args()
    
    registry = None
    
    try:
        # Register all core services
        registry = register_core_services()
        
        # Initialize services (happens on first access via registry)
        await registry.initialize_all()
        
        # Execute command
        if not args.command:
            parser.print_help()
            logger.info("\nNo command specified. Use --help for options.")
            
        else:
            if args.command == 'health':
                await handle_health(registry, detailed=args.detailed)
                
            elif args.command == 'status':
                await handle_status(registry)
                
            elif args.command == 'sync-status':
                await handle_sync_status(registry)
                
            elif args.command == 'discover':
                await handle_discover(registry, max_accounts=args.max_accounts)
                
            elif args.command == 'sync':
                await handle_sync(
                    registry,
                    sync_type=args.sync_type,
                    max_accounts=args.max_accounts,
                    force=args.force
                )
            
            # ════════════════════════════════════════════════════════════════
            # NEW v3.8.3: Cleanup command handler
            # ════════════════════════════════════════════════════════════════
            elif args.command == 'cleanup':
                dry_run = not args.execute
                include_zero_balance = not args.keep_zero_balance
                await handle_cleanup(
                    registry,
                    dry_run=dry_run,
                    include_zero_balance=include_zero_balance
                )
                
            elif args.command == 'analytics':
                await handle_analytics(registry, analysis_type=args.analysis_type)
            
            elif args.command == 'evaluate-holonic':
                await handle_holonic_evaluation(
                    registry,
                    evaluate_all=args.all,
                    account_id=args.account,
                    max_accounts=args.max_accounts,
                    save_to_db=not args.no_save
                )
                
            elif args.command == 'visualize':
                await handle_visualize(
                    registry,
                    action=args.action,
                    format=args.format,
                    include_advanced=args.include_advanced
                )
                
            elif args.command == 'protocol-health':
                await handle_protocol_health(registry)
                
            elif args.command == 'scheduler-status':
                await handle_scheduler_status(registry)
            
            elif args.command == 'distribution':
                dry_run = not args.live
                await handle_distribution(registry, action=args.action, dry_run=dry_run)
                
            elif args.command == 'serve':
                await handle_serve(
                    registry,
                    host=args.host,
                    port=args.port,
                    reload=args.reload
                )
                
            else:
                parser.print_help()
                logger.info("\nNo command specified. Use --help for options.")
        
        logger.info("\n✅ Operation completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Operation cancelled by user")
        return 130
        
    except Exception as e:
        logger.error(f"\n❌ Operation failed: {e}", exc_info=True)
        return 1
        
    finally:
        # ═══════════════════════════════════════════════════════════════════
        # CRITICAL: Cleanup all services to prevent resource leaks
        # ═══════════════════════════════════════════════════════════════════
        if registry is not None:
            try:
                logger.info("\n🔄 Cleaning up services...")
                await registry.shutdown()
                logger.info("✅ All services cleaned up successfully")
            except Exception as e:
                logger.warning(f"⚠️  Error during cleanup: {e}")


# ========================================================================
# STANDALONE EXECUTION
# ========================================================================

if __name__ == "__main__":
    """
    Entry point for the entire UBEC Protocol Suite.
    
    This is the ONLY place where the system should be executed.
    """
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
