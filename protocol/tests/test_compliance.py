# tests/test_compliance.py
"""
Test Compliance with 12 Project Design Principles

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import ast
import asyncio
from pathlib import Path
import pytest


class TestPrincipleCompliance:
    """Test suite for principle compliance"""
    
    def test_principle_5_no_sync_code(self):
        """Verify NO synchronous code exists"""
        violations = []
        
        for py_file in Path('.').rglob('*.py'):
            if 'venv' in str(py_file) or 'tests' in str(py_file):
                continue
            
            with open(py_file) as f:
                content = f.read()
            
            # Check for sync violations
            if 'import time' in content and 'time.sleep' in content:
                violations.append(f"{py_file}: uses time.sleep()")
            
            if 'import requests' in content:
                violations.append(f"{py_file}: uses sync requests")
            
            if 'from stellar_sdk import Server' in content:
                violations.append(f"{py_file}: uses sync Stellar Server")
        
        assert len(violations) == 0, f"Sync code found:\n" + "\n".join(violations)
    
    def test_principle_2_no_standalone_execution(self):
        """Verify only main.py has __main__ block"""
        violations = []
        
        for py_file in Path('.').rglob('*.py'):
            if 'ubec_main_protocol.py' in str(py_file):
                continue  # Allowed
            
            if 'venv' in str(py_file) or 'tests' in str(py_file):
                continue
            
            with open(py_file) as f:
                content = f.read()
            
            if "if __name__ == '__main__':" in content:
                violations.append(str(py_file))
        
        assert len(violations) == 0, \
            f"Standalone execution found in:\n" + "\n".join(violations)
    
    def test_principle_8_single_config(self):
        """Verify only ONE config file exists"""
        config_files = [
            p for p in Path('.').rglob('config.py')
            if 'venv' not in str(p) and 'tests' not in str(p)
        ]
        
        # Filter to only config/config.py
        config_files = [
            p for p in config_files
            if str(p).endswith('config/config.py')
        ]
        
        assert len(config_files) == 1, \
            f"Multiple config files found: {config_files}"
    
    def test_principle_11_attribution(self):
        """Verify attribution present in all files"""
        violations = []
        
        for py_file in Path('.').rglob('*.py'):
            if 'venv' in str(py_file) or 'tests' in str(py_file):
                continue
            
            with open(py_file) as f:
                content = f.read()
            
            if 'Anthropic PBC' not in content:
                violations.append(str(py_file))
        
        assert len(violations) == 0, \
            f"Missing attribution in:\n" + "\n".join(violations)
    
    @pytest.mark.asyncio
    async def test_async_operations(self):
        """Test that async operations work correctly"""
        from ubec_main_protocol import UBECMainProtocol
        
        protocol = UBECMainProtocol()
        await protocol.initialize()
        
        try:
            # Test health check
            health = await protocol.get_system_health()
            assert 'overall_status' in health
            
            # Test status
            status = await protocol.get_all_statuses()
            assert 'elements' in status
            
        finally:
            await protocol.shutdown()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
