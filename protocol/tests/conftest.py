"""
UBEC Protocol Test Suite - Pytest Configuration
================================================
Central configuration for all pytest tests.

This conftest.py provides:
- Async test support
- Database fixtures
- Service fixtures
- Mock configurations
- Test utilities

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 1.0.0
Date: October 17, 2025
"""

import os
import sys
import asyncio
from pathlib import Path
import pytest
from typing import Dict, Any, Generator
from unittest.mock import Mock, AsyncMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test environment
os.environ['TESTING'] = 'true'
os.environ['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
os.environ['DB_PORT'] = os.getenv('DB_PORT', '5432')
os.environ['DB_NAME'] = os.getenv('DB_NAME', 'ubec_test')
os.environ['DB_USER'] = os.getenv('DB_USER', 'ubec_app')
os.environ['DB_PASSWORD'] = os.getenv('DB_PASSWORD', '')
os.environ['DB_SCHEMA'] = os.getenv('DB_SCHEMA', 'ubec_main')


# ==================== PYTEST CONFIGURATION ====================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", 
        "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", 
        "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", 
        "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers",
        "requires_db: mark test as requiring database connection"
    )


# ==================== ASYNC TEST SUPPORT ====================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==================== MOCK DATABASE ====================

class MockAsyncDatabaseManager:
    """Mock database manager for testing without real database."""
    
    def __init__(self):
        self.schema = 'ubec_main'
        self.primary_schema = 'ubec_main'
        self._initialized = True
        self._connected = True
        self._fetch_one_responses = {}
        self._fetch_all_responses = {}
    
    async def initialize(self):
        """Mock initialization."""
        self._initialized = True
    
    async def close(self):
        """Mock close."""
        self._connected = False
    
    async def fetch_one(self, query: str, params: tuple = ()) -> Dict[str, Any]:
        """Mock fetch_one with configurable responses."""
        # Check if we have a response configured for this query
        for key, response in self._fetch_one_responses.items():
            if key in query:
                return response
        
        # Default responses
        if 'SELECT 1' in query:
            return {'test': 1}
        
        return None
    
    async def fetch_all(self, query: str, params: tuple = ()) -> list:
        """Mock fetch_all with configurable responses."""
        # Check if we have a response configured for this query
        for key, response in self._fetch_all_responses.items():
            if key in query:
                return response
        
        # Default empty response
        return []
    
    async def execute(self, query: str, params: tuple = ()) -> None:
        """Mock execute."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Mock health check."""
        return {
            'status': 'healthy',
            'message': 'Mock database operational',
            'details': {
                'connected': self._connected,
                'initialized': self._initialized
            }
        }
    
    def set_fetch_one_response(self, query_key: str, response: Dict[str, Any]):
        """Configure response for fetch_one queries containing query_key."""
        self._fetch_one_responses[query_key] = response
    
    def set_fetch_all_response(self, query_key: str, response: list):
        """Configure response for fetch_all queries containing query_key."""
        self._fetch_all_responses[query_key] = response


@pytest.fixture
def mock_db():
    """Provide mock database manager."""
    return MockAsyncDatabaseManager()


# ==================== MOCK STELLAR CLIENT ====================

class MockStellarClient:
    """Mock Stellar Horizon client."""
    
    def __init__(self):
        self._initialized = True
        self.base_url = 'https://horizon-testnet.stellar.org'
    
    async def accounts(self):
        """Mock accounts endpoint."""
        return AsyncMock()
    
    async def transactions(self):
        """Mock transactions endpoint."""
        return AsyncMock()
    
    async def operations(self):
        """Mock operations endpoint."""
        return AsyncMock()
    
    async def close(self):
        """Mock close."""
        pass


@pytest.fixture
def mock_stellar():
    """Provide mock Stellar client."""
    return MockStellarClient()


# ==================== MOCK CONFIGURATION ====================

class MockConfig:
    """Mock system configuration."""
    
    def __init__(self):
        self.HORIZON_URL = 'https://horizon-testnet.stellar.org'
        self.UBEC_CODE = 'UBEC'
        self.UBEC_ISSUER = 'GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        self.UBECRC_CODE = 'UBECrc'
        self.UBECRC_ISSUER = 'GYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'
        self.UBECGPI_CODE = 'UBECgpi'
        self.UBECGPI_ISSUER = 'GZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ'
        self.UBECTT_CODE = 'UBECtt'
        self.UBECTT_ISSUER = 'GWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW'
        
        self.ACCOUNTS = {
            'administration': 'GADMINXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            'stewardship': [
                'GSTEWARD1XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                'GSTEWARD2XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                'GSTEWARD3XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
            ],
            'general': 'GGENERALXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        }
        
        self.TARGET_DISTRIBUTION = {
            'general': 0.75,
            'administration': 0.05,
            'stewardship': 0.20
        }
        
        self.REBALANCE_THRESHOLD = 0.02
        self.NETWORK = 'TESTNET'
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        return getattr(self, key, default)
    
    def __getitem__(self, key: str):
        """Dictionary-style access."""
        return getattr(self, key)
    
    def __contains__(self, key: str):
        """Check if key exists."""
        return hasattr(self, key)
    
    async def health_check(self) -> Dict[str, Any]:
        """Mock health check."""
        return {
            'status': 'healthy',
            'message': 'Mock configuration operational'
        }


@pytest.fixture
def mock_config():
    """Provide mock configuration."""
    return MockConfig()


# ==================== SERVICE MOCKS ====================

@pytest.fixture
def mock_protocol_service(mock_db, mock_stellar, mock_config):
    """Create mock protocol service with standardized health check."""
    
    class MockProtocolService:
        def __init__(self):
            self.db_manager = mock_db
            self.stellar_client = mock_stellar
            self.config = mock_config
            self._initialized = True
            self.asset_code = 'UBEC'
            self.issuer = mock_config.UBEC_ISSUER
        
        async def initialize(self):
            """Mock initialization."""
            self._initialized = True
        
        async def health_check(self) -> Dict[str, Any]:
            """Mock health check using api_dependent_health pattern."""
            return {
                'status': 'healthy',
                'message': 'mock_protocol operational',
                'timestamp': '2025-10-17T12:00:00',
                'details': {
                    'initialized': self._initialized,
                    'database_connected': True,
                    'api_accessible': True,
                    'asset_code': self.asset_code
                }
            }
        
        async def close(self):
            """Mock close."""
            pass
    
    return MockProtocolService()


@pytest.fixture
def mock_distribution_service(mock_db, mock_config):
    """Create mock distribution service."""
    
    class MockDistributionService:
        def __init__(self):
            self.db_manager = mock_db
            self.config = mock_config
            self._initialized = True
            self.target_distribution = mock_config.TARGET_DISTRIBUTION
            self.rebalance_threshold = mock_config.REBALANCE_THRESHOLD
            self.db_schema = 'ubec_main'
            self.asset_code = 'UBEC'
        
        async def health_check(self) -> Dict[str, Any]:
            """Mock health check."""
            return {
                'status': 'healthy',
                'message': 'mock_distribution operational'
            }
        
        async def get_current_distribution(self) -> Dict[str, Any]:
            """Mock distribution data."""
            return {
                'total_supply': 190000000.0,
                'distribution_of_supply': {
                    'general': 0.75,
                    'administration': 0.05,
                    'stewardship': 0.20
                },
                'target_distribution': self.target_distribution
            }
        
        async def check_compliance(self) -> Dict[str, Any]:
            """Mock compliance check."""
            return {
                'overall_compliant': True,
                'compliance': {
                    'general': True,
                    'administration': True,
                    'stewardship': True
                },
                'deviations': {}
            }
    
    return MockDistributionService()


@pytest.fixture
def mock_audit_service(mock_db):
    """Create mock audit service."""
    
    class MockAuditService:
        def __init__(self):
            self.db_manager = mock_db
            self._initialized = True
        
        async def health_check(self) -> Dict[str, Any]:
            """Mock health check."""
            return {
                'status': 'healthy',
                'message': 'mock_audit operational'
            }
    
    return MockAuditService()


# ==================== TEST UTILITIES ====================

@pytest.fixture
def assert_healthy():
    """Utility to assert service health."""
    def _assert_healthy(health_response: Dict[str, Any], service_name: str = 'service'):
        """Assert that health response indicates healthy status."""
        assert 'status' in health_response, f"{service_name}: Missing 'status' in health response"
        assert health_response['status'] in ['healthy', 'degraded'], \
            f"{service_name}: Expected 'healthy' or 'degraded', got '{health_response['status']}'"
        assert 'details' in health_response, f"{service_name}: Missing 'details' in health response"
        
        if 'initialized' in health_response['details']:
            assert health_response['details']['initialized'] is True, \
                f"{service_name}: Service not initialized"
    
    return _assert_healthy


@pytest.fixture
def sample_account_data():
    """Provide sample account data for testing."""
    return {
        'account_id': 'GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
        'balance': 50000.0,
        'account_type': 'general',
        'is_active': True
    }


@pytest.fixture
def sample_transaction_data():
    """Provide sample transaction data for testing."""
    return {
        'transaction_hash': 'abc123def456',
        'source_account': 'GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
        'destination_account': 'GYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY',
        'amount': 1000.0,
        'asset_code': 'UBEC',
        'timestamp': '2025-10-17T12:00:00'
    }


# ==================== CLEANUP ====================

@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test."""
    yield
    # Add any cleanup logic here
    pass


# ==================== MODULE INFO ====================

__all__ = [
    'mock_db',
    'mock_stellar',
    'mock_config',
    'mock_protocol_service',
    'mock_distribution_service',
    'mock_audit_service',
    'assert_healthy',
    'sample_account_data',
    'sample_transaction_data'
]
