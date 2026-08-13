# Health Monitoring Quick Reference Guide

## Overview

This guide provides quick reference for implementing and using health checks in the UBEC protocol system, following Principle #12 (Method Singularity) with the ServiceHealthCheck utility.

---

## Health Check Status Levels

| Status | Meaning | Color | Symbol |
|--------|---------|-------|---------|
| `healthy` | Service fully operational | Green | ✓ |
| `degraded` | Service operational but with limitations | Yellow | ⚠ |
| `unhealthy` | Service not operational | Red | ✗ |
| `unknown` | Health status cannot be determined | Gray | ? |

---

## Running Health Checks

### System-Wide Health Check
```bash
python main.py --mode health
```

**Output:**
- Overall system status
- Per-service health status
- Category-level aggregation
- Detailed health metrics

### Protocol-Specific Health Check
```bash
python main.py --mode protocol-health
```

**Output:**
- Health status for all 4 element protocols
- Element metadata (name, principle, symbol)
- Protocol-specific metrics

### Status Summary
```bash
python main.py --mode status
```

**Output:**
- Database connection status
- Synchronizer status
- Protocol summaries
- Service summaries

---

## ServiceHealthCheck Utility Usage

### For Element Protocols

```python
from core.utils.service_health import ServiceHealthCheck

class MyProtocolService:
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check using standardized ServiceHealthCheck utility.
        
        Implements Principle #12 (Method Singularity).
        """
        return await ServiceHealthCheck.element_protocol_health(
            element_name=self.element,  # Instance variable
            token_code=self.token_code,  # Instance variable
            db_manager=self.db,
            is_initialized=self._initialized,
            last_sync=self._last_sync_time,
            cached_accounts=len(self._account_cache),
            ubuntu_principle=self.ubuntu_principle,  # Instance variable
            element_description=self.element_description,  # Instance variable
            symbol=self.symbol,  # Instance variable
            issuer=self.issuer,
            sync_count=self._sync_count,
            query_count=self._query_count,
            error_count=self._error_count,
            last_error=self._last_error,
            last_error_time=self._last_error_time
        )
```

### For Database-Dependent Services

```python
from core.utils.service_health import ServiceHealthCheck

class MyDatabaseService:
    async def health_check(self) -> Dict[str, Any]:
        """Health check for database-dependent service."""
        return await ServiceHealthCheck.database_dependent_health(
            service_name='my_service',
            db_manager=self.db,
            is_initialized=self._initialized,
            # Optional parameters
            cache_size=len(self._cache),
            last_operation=self._last_operation_time,
            operation_count=self._operation_count,
            error_count=self._error_count,
            custom_checks={'custom_metric': self._custom_value}
        )
```

### For API-Dependent Services

```python
from core.utils.service_health import ServiceHealthCheck

class MyAPIService:
    async def health_check(self) -> Dict[str, Any]:
        """Health check for API-dependent service."""
        return await ServiceHealthCheck.api_dependent_health(
            service_name='my_api_service',
            is_initialized=self._initialized,
            rate_limiter=self.rate_limiter,  # Optional
            cache_info={
                'size': len(self._cache),
                'ttl': self._cache_ttl,
                'last_fetch': self._last_fetch_time
            },
            api_connected=await self._test_api_connection(),
            # Optional parameters
            request_count=self._request_count,
            error_count=self._error_count,
            last_error=self._last_error
        )
```

### For Basic Services

```python
from core.utils.service_health import ServiceHealthCheck

class MyBasicService:
    async def health_check(self) -> Dict[str, Any]:
        """Basic health check."""
        return await ServiceHealthCheck.basic_health_check(
            service_name='my_basic_service',
            is_initialized=self._initialized,
            # Optional parameters
            operation_count=self._operation_count,
            error_count=self._error_count,
            custom_status={'metric': 'value'}
        )
```

---

## Implementing Degraded State

### In Service Initialization

```python
class MyService:
    def __init__(self, config: Dict[str, Any]):
        self._initialized = False
        self._degraded = False
        self._degraded_reason = None
        
    async def initialize(self):
        """Initialize with graceful degradation."""
        try:
            # Attempt full initialization
            await self._full_initialization()
            self._initialized = True
            
        except MissingConfigError as e:
            # Gracefully degrade
            logger.warning(f"Service degraded: {e}")
            self._initialized = True
            self._degraded = True
            self._degraded_reason = str(e)
            
            # Initialize only core features
            await self._minimal_initialization()
```

### In Health Checks

```python
async def health_check(self) -> Dict[str, Any]:
    """Health check with degraded state reporting."""
    health = await ServiceHealthCheck.database_dependent_health(
        service_name='my_service',
        db_manager=self.db,
        is_initialized=self._initialized
    )
    
    # Override status if degraded
    if self._degraded:
        health['status'] = 'degraded'
        health['message'] = f"Service operational but degraded: {self._degraded_reason}"
        health['details']['degraded'] = True
        health['details']['degraded_reason'] = self._degraded_reason
    
    return health
```

---

## Health Check Response Format

### Standard Response Structure

```json
{
  "status": "healthy|degraded|unhealthy|unknown",
  "message": "Human-readable status message",
  "timestamp": "2025-10-20T03:28:17.459000",
  "details": {
    "initialized": true,
    "service_specific_metric": "value",
    "operation_count": 42,
    "error_count": 0,
    "last_error": null,
    "last_error_time": null
  }
}
```

### Element Protocol Response

```json
{
  "status": "healthy",
  "message": "Air protocol (UBEC) operational",
  "timestamp": "2025-10-20T03:28:17.459000",
  "details": {
    "initialized": true,
    "element": "Air",
    "ubuntu_principle": "Diversity",
    "symbol": "🜁",
    "token_code": "UBEC",
    "issuer": "GC7PK...XYZ",
    "last_sync": "2025-10-20T02:15:00.000000",
    "cached_accounts": 150,
    "sync_count": 25,
    "query_count": 1250,
    "error_count": 0,
    "last_error": null,
    "last_error_time": null,
    "database_connected": true
  }
}
```

### Degraded Service Response

```json
{
  "status": "degraded",
  "message": "Service operational but degraded: administration_account not configured",
  "timestamp": "2025-10-20T03:28:17.466000",
  "details": {
    "initialized": true,
    "degraded": true,
    "degraded_reason": "administration_account not configured",
    "available_features": ["monitoring", "reporting"],
    "unavailable_features": ["compliance_checking", "rebalancing"],
    "database_connected": true
  }
}
```

---

## Health Check Best Practices

### 1. **Always Use Instance Variables**
❌ **DON'T:**
```python
return await ServiceHealthCheck.element_protocol_health(
    element_name="Air",  # Hardcoded!
    ubuntu_principle="Diversity"  # Hardcoded!
)
```

✅ **DO:**
```python
return await ServiceHealthCheck.element_protocol_health(
    element_name=self.element,  # Instance variable
    ubuntu_principle=self.ubuntu_principle  # Instance variable
)
```

### 2. **Track Operations and Errors**
```python
class MyService:
    def __init__(self):
        self._operation_count = 0
        self._error_count = 0
        self._last_error = None
        self._last_error_time = None
    
    async def perform_operation(self):
        try:
            self._operation_count += 1
            # ... operation logic ...
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self._last_error_time = datetime.now()
            raise
```

### 3. **Implement Graceful Degradation**
```python
async def initialize(self):
    """Initialize with feature detection."""
    self._initialized = False
    self._available_features = []
    
    # Try to enable each feature
    for feature in ['feature_a', 'feature_b', 'feature_c']:
        try:
            await self._enable_feature(feature)
            self._available_features.append(feature)
        except FeatureError as e:
            logger.warning(f"Feature {feature} unavailable: {e}")
    
    self._initialized = True
    
    # Report degraded if critical features missing
    if 'feature_a' not in self._available_features:
        self._degraded = True
        self._degraded_reason = "Critical feature unavailable"
```

### 4. **Include Meaningful Context**
```python
async def health_check(self) -> Dict[str, Any]:
    """Health check with rich context."""
    health = await ServiceHealthCheck.database_dependent_health(
        service_name='my_service',
        db_manager=self.db,
        is_initialized=self._initialized,
        custom_checks={
            'feature_a_enabled': 'feature_a' in self._available_features,
            'feature_b_enabled': 'feature_b' in self._available_features,
            'last_successful_operation': self._last_success_time,
            'pending_operations': len(self._operation_queue)
        }
    )
    return health
```

---

## Troubleshooting Health Issues

### Service Shows as DEGRADED

1. **Check the health check output:**
   ```bash
   python main.py --mode health | grep -A 20 "service_name"
   ```

2. **Review degraded reason:**
   ```python
   health = await service.health_check()
   print(health['details'].get('degraded_reason'))
   ```

3. **Resolve configuration issues:**
   - Add missing configuration to database
   - Set required environment variables
   - Ensure all dependencies are available

### Service Shows as UNHEALTHY

1. **Check initialization:**
   ```python
   if not service._initialized:
       await service.initialize()
   ```

2. **Test database connection:**
   ```python
   await service.db.execute("SELECT 1")
   ```

3. **Review error logs:**
   ```bash
   python main.py --mode health --log-level DEBUG
   ```

### High Error Count

1. **Check last error:**
   ```python
   health = await service.health_check()
   print(f"Last error: {health['details']['last_error']}")
   print(f"Error time: {health['details']['last_error_time']}")
   ```

2. **Reset error tracking after fixes:**
   ```python
   service._error_count = 0
   service._last_error = None
   service._last_error_time = None
   ```

---

## Integration with Monitoring Systems

### Prometheus Metrics Format

```python
def to_prometheus(health: Dict[str, Any]) -> str:
    """Convert health check to Prometheus format."""
    metrics = []
    
    # Status metric (1=healthy, 0.5=degraded, 0=unhealthy)
    status_value = {
        'healthy': 1.0,
        'degraded': 0.5,
        'unhealthy': 0.0,
        'unknown': -1.0
    }.get(health['status'], -1.0)
    
    metrics.append(f"ubec_service_health{{service=\"{health['service']}\"}} {status_value}")
    
    # Operation metrics
    if 'operation_count' in health['details']:
        metrics.append(f"ubec_service_operations_total{{service=\"{health['service']}\"}} {health['details']['operation_count']}")
    
    if 'error_count' in health['details']:
        metrics.append(f"ubec_service_errors_total{{service=\"{health['service']}\"}} {health['details']['error_count']}")
    
    return '\n'.join(metrics)
```

### Alerting Rules

```yaml
# Alert on unhealthy services
- alert: ServiceUnhealthy
  expr: ubec_service_health < 0.5
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Service {{ $labels.service }} is unhealthy"

# Alert on degraded services
- alert: ServiceDegraded
  expr: ubec_service_health == 0.5
  for: 15m
  labels:
    severity: warning
  annotations:
    summary: "Service {{ $labels.service }} is degraded"

# Alert on high error rate
- alert: HighErrorRate
  expr: rate(ubec_service_errors_total[5m]) > 0.1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Service {{ $labels.service }} has high error rate"
```

---

## Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## See Also

- [Health Check Standard Specification](docs/HEALTH_CHECK_STANDARD_SPECIFICATION.md)
- [Service Registry Documentation](docs/SERVICE_REGISTRY_V3_SUMMARY.md)
- [Design Principles](docs/PROJECT_DESIGN_PRINCIPLES.md)
