#!/usr/bin/env python3
"""
UBEC Protocol Suite - Production Monitoring Service
====================================================
Comprehensive monitoring, alerting, and health tracking for production deployment.

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Self-contained monitoring service
    ✅ #2  Service Pattern: Factory-based instantiation, no standalone execution
    ✅ #3  Service Registry: Accessed through centralized registry
    ✅ #4  Single Source of Truth: Database for historical metrics
    ✅ #5  Strict Async Operations: ALL I/O operations use async/await
    ✅ #6  No Sync Fallbacks: Pure async implementation
    ✅ #7  Per-Asset Monitoring: Individual service and component tracking
    ✅ #8  No Duplicate Configuration: Database-backed configuration
    ✅ #9  Integrated Rate Limiting: Built-in for monitoring operations
    ✅ #10 Separation of Concerns: Monitoring logic isolated
    ✅ #11 Comprehensive Documentation: Full docstrings and attribution
    ✅ #12 Method Singularity: Each method implemented once
════════════════════════════════════════════════════════════════════════════

Key Features:
- Real-time health monitoring
- Alert generation and notification
- Metrics collection and storage
- Performance tracking
- Incident detection
- Dashboard data aggregation
- Historical trend analysis

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team with Claude AI assistance
Version: 1.0.0 (Production Monitoring)
Date: October 19, 2025
"""

import asyncio
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum
import statistics


# ═════════════════════════════════════════════════════════════════════════════
# Alert Severity and Types
# ═════════════════════════════════════════════════════════════════════════════

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of alerts"""
    SERVICE_DOWN = "service_down"
    SERVICE_DEGRADED = "service_degraded"
    HIGH_ERROR_RATE = "high_error_rate"
    SLOW_RESPONSE = "slow_response"
    DATABASE_ISSUE = "database_issue"
    SYNC_FAILURE = "sync_failure"
    DISTRIBUTION_VIOLATION = "distribution_violation"
    LOW_BALANCE = "low_balance"
    CUSTOM = "custom"


@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    severity: AlertSeverity
    alert_type: AlertType
    service_name: str
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None


@dataclass
class MetricPoint:
    """Single metric measurement"""
    service_name: str
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str]


# ═════════════════════════════════════════════════════════════════════════════
# Monitoring Service Class
# ═════════════════════════════════════════════════════════════════════════════

class UBECMonitoringService:
    """
    Production monitoring service for UBEC Protocol Suite.
    
    Provides:
    - Continuous health monitoring
    - Alert generation and management
    - Metrics collection and aggregation
    - Performance tracking
    - Incident detection and logging
    
    Design Pattern:
        Service class instantiated via factory function only.
        Integrates with service registry for access to all services.
        Follows async-first architecture.
    
    Attributes:
        service_registry: Reference to service registry for health checks
        db_manager: Async database manager
        config: Configuration dictionary
        logger: Logging instance
        alert_handlers: List of alert notification handlers
        metrics_buffer: In-memory metrics buffer before DB write
        active_alerts: Currently active alerts
        alert_history: Recent alert history
    """
    
    def __init__(
        self,
        service_registry: Any,
        db_manager: Any,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize monitoring service.
        
        Args:
            service_registry: Service registry for accessing all services
            db_manager: Async database manager instance
            config: Configuration dictionary
            logger: Optional logger instance
        """
        self.service_registry = service_registry
        self.db_manager = db_manager
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Configuration
        self.db_schema = config.get('db_schema', 'public')
        self.health_check_interval = config.get('health_check_interval', 60)  # seconds
        self.metrics_retention_days = config.get('metrics_retention_days', 90)
        self.alert_cooldown = config.get('alert_cooldown', 300)  # seconds
        
        # Alert thresholds
        self.thresholds = {
            'error_rate': config.get('error_rate_threshold', 0.05),  # 5%
            'response_time': config.get('response_time_threshold', 5000),  # 5s in ms
            'db_pool_usage': config.get('db_pool_threshold', 0.9),  # 90%
        }
        
        # Alert handlers (email, Slack, PagerDuty, etc.)
        self.alert_handlers = []
        
        # Metrics buffer (store in memory before batch write)
        self.metrics_buffer: deque = deque(maxlen=1000)
        self.metrics_write_interval = config.get('metrics_write_interval', 300)  # 5 min
        
        # Active alerts (keyed by service_name + alert_type)
        self.active_alerts: Dict[str, Alert] = {}
        
        # Alert history (last 100 alerts)
        self.alert_history: deque = deque(maxlen=100)
        
        # Last alert time per service (for cooldown)
        self.last_alert_time: Dict[str, datetime] = {}
        
        # Service health tracking
        self.service_health_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Performance metrics
        self._checks_performed = 0
        self._alerts_generated = 0
        self._metrics_collected = 0
        
        # Lifecycle
        self._initialized = False
        self._monitoring_task = None
        self._metrics_flush_task = None
        
        self.logger.info(
            f"UBECMonitoringService initialized | "
            f"interval={self.health_check_interval}s | "
            f"retention={self.metrics_retention_days}d"
        )
    
    async def initialize(self) -> bool:
        """
        Initialize the monitoring service.
        
        Sets up database tables and starts background monitoring tasks.
        
        Returns:
            True if initialization successful
        """
        try:
            # Create monitoring tables if they don't exist
            await self._create_monitoring_tables()
            
            # Load active alerts from database
            await self._load_active_alerts()
            
            # Start background monitoring
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            self._metrics_flush_task = asyncio.create_task(self._metrics_flush_loop())
            
            self._initialized = True
            
            self.logger.info("UBECMonitoringService initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing monitoring service: {e}", exc_info=True)
            self._initialized = False
            return False
    
    async def _create_monitoring_tables(self):
        """Create monitoring tables in database if they don't exist."""
        queries = [
            # Metrics table
            f"""
            CREATE TABLE IF NOT EXISTS {self.db_schema}.monitoring_metrics (
                id SERIAL PRIMARY KEY,
                service_name VARCHAR(100) NOT NULL,
                metric_name VARCHAR(100) NOT NULL,
                value NUMERIC NOT NULL,
                unit VARCHAR(50),
                tags JSONB,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Index for metrics queries
            f"""
            CREATE INDEX IF NOT EXISTS idx_monitoring_metrics_service_time 
            ON {self.db_schema}.monitoring_metrics (service_name, timestamp DESC)
            """,
            
            # Alerts table
            f"""
            CREATE TABLE IF NOT EXISTS {self.db_schema}.monitoring_alerts (
                alert_id VARCHAR(100) PRIMARY KEY,
                severity VARCHAR(20) NOT NULL,
                alert_type VARCHAR(50) NOT NULL,
                service_name VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                details JSONB,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                resolved_at TIMESTAMP WITH TIME ZONE,
                acknowledged BOOLEAN DEFAULT FALSE,
                acknowledged_by VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Index for active alerts
            f"""
            CREATE INDEX IF NOT EXISTS idx_monitoring_alerts_active 
            ON {self.db_schema}.monitoring_alerts (service_name, resolved, timestamp DESC)
            """,
            
            # Health checks table
            f"""
            CREATE TABLE IF NOT EXISTS {self.db_schema}.monitoring_health_checks (
                id SERIAL PRIMARY KEY,
                service_name VARCHAR(100) NOT NULL,
                status VARCHAR(20) NOT NULL,
                response_time_ms NUMERIC,
                details JSONB,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Index for health history
            f"""
            CREATE INDEX IF NOT EXISTS idx_monitoring_health_service_time 
            ON {self.db_schema}.monitoring_health_checks (service_name, timestamp DESC)
            """
        ]
        
        for query in queries:
            try:
                await self.db_manager.execute(query, ())
            except Exception as e:
                self.logger.error(f"Error creating monitoring table: {e}")
                raise
        
        self.logger.info("Monitoring tables created/verified")
    
    async def _load_active_alerts(self):
        """Load active (unresolved) alerts from database."""
        try:
            query = f"""
                SELECT alert_id, severity, alert_type, service_name, message, 
                       details, timestamp, resolved, resolved_at, 
                       acknowledged, acknowledged_by
                FROM {self.db_schema}.monitoring_alerts
                WHERE resolved = FALSE
                ORDER BY timestamp DESC
            """
            
            rows = await self.db_manager.fetch_all(query, ())
            
            for row in rows:
                alert = Alert(
                    alert_id=row['alert_id'],
                    severity=AlertSeverity(row['severity']),
                    alert_type=AlertType(row['alert_type']),
                    service_name=row['service_name'],
                    message=row['message'],
                    details=row['details'] or {},
                    timestamp=row['timestamp'],
                    resolved=row['resolved'],
                    resolved_at=row['resolved_at'],
                    acknowledged=row['acknowledged'],
                    acknowledged_by=row['acknowledged_by']
                )
                
                alert_key = f"{alert.service_name}:{alert.alert_type.value}"
                self.active_alerts[alert_key] = alert
            
            self.logger.info(f"Loaded {len(self.active_alerts)} active alerts")
            
        except Exception as e:
            self.logger.error(f"Error loading active alerts: {e}", exc_info=True)
    
    # ═════════════════════════════════════════════════════════════════════════
    # Health Monitoring
    # ═════════════════════════════════════════════════════════════════════════
    
    async def _monitoring_loop(self):
        """
        Background monitoring loop.
        
        Continuously checks all service health and generates alerts.
        """
        self.logger.info(f"Starting monitoring loop (interval={self.health_check_interval}s)")
        
        while True:
            try:
                await self.check_all_services()
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                self.logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(self.health_check_interval)
    
    async def check_all_services(self) -> Dict[str, Any]:
        """
        Check health of all registered services.
        
        Returns:
            Dictionary with health status of all services
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get health from service registry
            registry_health = await self.service_registry.health_check(detailed=True)
            
            self._checks_performed += 1
            
            # Process each service
            for service_name, service_health in registry_health['services'].items():
                # Record metric
                await self.record_metric(
                    service_name=service_name,
                    metric_name='health_status',
                    value=1.0 if service_health['status'] == 'healthy' else 0.0,
                    unit='boolean',
                    tags={'status': service_health['status']}
                )
                
                # Track health history
                self.service_health_history[service_name].append({
                    'timestamp': start_time,
                    'status': service_health['status'],
                    'details': service_health.get('details', {})
                })
                
                # Store in database
                await self._store_health_check(service_name, service_health, start_time)
                
                # Check for alerts
                await self._check_service_alerts(service_name, service_health)
            
            # Calculate and record overall system health
            healthy_count = registry_health['summary']['healthy']
            total_count = registry_health['summary']['total']
            system_health_pct = (healthy_count / total_count) * 100 if total_count > 0 else 0
            
            await self.record_metric(
                service_name='system',
                metric_name='health_percentage',
                value=system_health_pct,
                unit='percent',
                tags={'healthy': str(healthy_count), 'total': str(total_count)}
            )
            
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            self.logger.debug(
                f"Health check completed | "
                f"services={total_count} | "
                f"healthy={healthy_count} | "
                f"duration={duration_ms:.2f}ms"
            )
            
            return registry_health
            
        except Exception as e:
            self.logger.error(f"Error checking all services: {e}", exc_info=True)
            return {}
    
    async def _store_health_check(
        self,
        service_name: str,
        health_data: Dict[str, Any],
        timestamp: datetime
    ):
        """Store health check result in database."""
        try:
            # Extract response time if available
            response_time = health_data.get('details', {}).get('response_time_ms')
            
            query = f"""
                INSERT INTO {self.db_schema}.monitoring_health_checks
                (service_name, status, response_time_ms, details, timestamp)
                VALUES ($1, $2, $3, $4, $5)
            """
            
            await self.db_manager.execute(
                query,
                (
                    service_name,
                    health_data['status'],
                    response_time,
                    json.dumps(health_data.get('details', {})),
                    timestamp
                )
            )
            
        except Exception as e:
            self.logger.error(f"Error storing health check: {e}", exc_info=True)
    
    async def _check_service_alerts(
        self,
        service_name: str,
        health_data: Dict[str, Any]
    ):
        """
        Check if service health requires alerting.
        
        Args:
            service_name: Name of the service
            health_data: Health check data from service
        """
        status = health_data.get('status', 'unknown')
        details = health_data.get('details', {})
        
        # Check for service down
        if status == 'unhealthy':
            await self.generate_alert(
                severity=AlertSeverity.CRITICAL,
                alert_type=AlertType.SERVICE_DOWN,
                service_name=service_name,
                message=f"Service {service_name} is unhealthy",
                details=details
            )
        
        # Check for service degraded
        elif status == 'degraded':
            await self.generate_alert(
                severity=AlertSeverity.WARNING,
                alert_type=AlertType.SERVICE_DEGRADED,
                service_name=service_name,
                message=f"Service {service_name} is degraded",
                details=details
            )
        
        # Resolve alerts if service is now healthy
        elif status == 'healthy':
            await self._resolve_service_alerts(service_name)
        
        # Check response time
        response_time = details.get('response_time_ms', 0)
        if response_time > self.thresholds['response_time']:
            await self.generate_alert(
                severity=AlertSeverity.WARNING,
                alert_type=AlertType.SLOW_RESPONSE,
                service_name=service_name,
                message=f"Service {service_name} response time: {response_time:.2f}ms",
                details={'response_time_ms': response_time, 'threshold': self.thresholds['response_time']}
            )
        
        # Check error rate if available
        error_count = details.get('errors', 0)
        total_operations = details.get('operations', 0)
        
        if total_operations > 0:
            error_rate = error_count / total_operations
            if error_rate > self.thresholds['error_rate']:
                await self.generate_alert(
                    severity=AlertSeverity.ERROR,
                    alert_type=AlertType.HIGH_ERROR_RATE,
                    service_name=service_name,
                    message=f"High error rate in {service_name}: {error_rate*100:.1f}%",
                    details={'error_rate': error_rate, 'errors': error_count, 'operations': total_operations}
                )
    
    async def _resolve_service_alerts(self, service_name: str):
        """Resolve all active alerts for a service."""
        resolved_count = 0
        
        for alert_key in list(self.active_alerts.keys()):
            if alert_key.startswith(f"{service_name}:"):
                alert = self.active_alerts[alert_key]
                if not alert.resolved:
                    await self.resolve_alert(alert.alert_id)
                    resolved_count += 1
        
        if resolved_count > 0:
            self.logger.info(f"Resolved {resolved_count} alerts for {service_name}")
    
    # ═════════════════════════════════════════════════════════════════════════
    # Alert Management
    # ═════════════════════════════════════════════════════════════════════════
    
    async def generate_alert(
        self,
        severity: AlertSeverity,
        alert_type: AlertType,
        service_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[Alert]:
        """
        Generate a new alert.
        
        Args:
            severity: Alert severity level
            alert_type: Type of alert
            service_name: Service that triggered the alert
            message: Human-readable alert message
            details: Additional alert details
            
        Returns:
            Generated Alert object or None if cooldown active
        """
        alert_key = f"{service_name}:{alert_type.value}"
        
        # Check if alert already exists
        if alert_key in self.active_alerts:
            existing_alert = self.active_alerts[alert_key]
            if not existing_alert.resolved:
                self.logger.debug(f"Alert already active: {alert_key}")
                return None
        
        # Check cooldown
        if service_name in self.last_alert_time:
            time_since_last = (datetime.now(timezone.utc) - self.last_alert_time[service_name]).total_seconds()
            if time_since_last < self.alert_cooldown:
                self.logger.debug(f"Alert cooldown active for {service_name} ({time_since_last:.0f}s)")
                return None
        
        # Create alert
        timestamp = datetime.now(timezone.utc)
        alert_id = f"{service_name}_{alert_type.value}_{int(timestamp.timestamp())}"
        
        alert = Alert(
            alert_id=alert_id,
            severity=severity,
            alert_type=alert_type,
            service_name=service_name,
            message=message,
            details=details or {},
            timestamp=timestamp
        )
        
        # Store alert
        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)
        self.last_alert_time[service_name] = timestamp
        self._alerts_generated += 1
        
        # Persist to database
        await self._store_alert(alert)
        
        # Trigger alert handlers
        await self._trigger_alert_handlers(alert)
        
        self.logger.warning(
            f"ALERT GENERATED | {severity.value.upper()} | "
            f"{service_name} | {alert_type.value} | {message}"
        )
        
        return alert
    
    async def _store_alert(self, alert: Alert):
        """Store alert in database."""
        try:
            query = f"""
                INSERT INTO {self.db_schema}.monitoring_alerts
                (alert_id, severity, alert_type, service_name, message, details, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (alert_id) DO UPDATE SET
                    severity = EXCLUDED.severity,
                    message = EXCLUDED.message,
                    details = EXCLUDED.details
            """
            
            await self.db_manager.execute(
                query,
                (
                    alert.alert_id,
                    alert.severity.value,
                    alert.alert_type.value,
                    alert.service_name,
                    alert.message,
                    json.dumps(alert.details),
                    alert.timestamp
                )
            )
            
        except Exception as e:
            self.logger.error(f"Error storing alert: {e}", exc_info=True)
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """
        Resolve an active alert.
        
        Args:
            alert_id: ID of alert to resolve
            
        Returns:
            True if alert was resolved
        """
        try:
            # Find and update alert
            alert_key = None
            for key, alert in self.active_alerts.items():
                if alert.alert_id == alert_id:
                    alert_key = key
                    alert.resolved = True
                    alert.resolved_at = datetime.now(timezone.utc)
                    break
            
            if not alert_key:
                self.logger.warning(f"Alert not found: {alert_id}")
                return False
            
            # Update database
            query = f"""
                UPDATE {self.db_schema}.monitoring_alerts
                SET resolved = TRUE, resolved_at = $1
                WHERE alert_id = $2
            """
            
            await self.db_manager.execute(query, (datetime.now(timezone.utc), alert_id))
            
            # Remove from active alerts
            del self.active_alerts[alert_key]
            
            self.logger.info(f"Alert resolved: {alert_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error resolving alert: {e}", exc_info=True)
            return False
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: ID of alert to acknowledge
            acknowledged_by: User/system that acknowledged the alert
            
        Returns:
            True if alert was acknowledged
        """
        try:
            # Find and update alert
            for alert in self.active_alerts.values():
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    alert.acknowledged_by = acknowledged_by
                    break
            
            # Update database
            query = f"""
                UPDATE {self.db_schema}.monitoring_alerts
                SET acknowledged = TRUE, acknowledged_by = $1
                WHERE alert_id = $2
            """
            
            await self.db_manager.execute(query, (acknowledged_by, alert_id))
            
            self.logger.info(f"Alert acknowledged by {acknowledged_by}: {alert_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {e}", exc_info=True)
            return False
    
    async def _trigger_alert_handlers(self, alert: Alert):
        """Trigger all registered alert handlers."""
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {e}", exc_info=True)
    
    def register_alert_handler(self, handler: Any):
        """
        Register an alert notification handler.
        
        Handler should be an async callable that accepts an Alert object.
        
        Example:
            async def email_handler(alert: Alert):
                await send_email(alert)
            
            monitoring.register_alert_handler(email_handler)
        """
        self.alert_handlers.append(handler)
        self.logger.info(f"Registered alert handler: {handler.__name__}")
    
    # ═════════════════════════════════════════════════════════════════════════
    # Metrics Collection
    # ═════════════════════════════════════════════════════════════════════════
    
    async def record_metric(
        self,
        service_name: str,
        metric_name: str,
        value: float,
        unit: str = '',
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Record a metric point.
        
        Metrics are buffered in memory and flushed to database periodically.
        
        Args:
            service_name: Service the metric belongs to
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement (optional)
            tags: Additional tags (optional)
        """
        metric = MetricPoint(
            service_name=service_name,
            metric_name=metric_name,
            value=value,
            unit=unit,
            timestamp=datetime.now(timezone.utc),
            tags=tags or {}
        )
        
        self.metrics_buffer.append(metric)
        self._metrics_collected += 1
    
    async def _metrics_flush_loop(self):
        """Background loop to flush metrics to database."""
        self.logger.info(f"Starting metrics flush loop (interval={self.metrics_write_interval}s)")
        
        while True:
            try:
                await asyncio.sleep(self.metrics_write_interval)
                await self.flush_metrics()
                
            except asyncio.CancelledError:
                self.logger.info("Metrics flush loop cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in metrics flush loop: {e}", exc_info=True)
    
    async def flush_metrics(self):
        """Flush buffered metrics to database."""
        if not self.metrics_buffer:
            return
        
        try:
            # Get all metrics from buffer
            metrics_to_write = list(self.metrics_buffer)
            self.metrics_buffer.clear()
            
            # Batch insert
            query = f"""
                INSERT INTO {self.db_schema}.monitoring_metrics
                (service_name, metric_name, value, unit, tags, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6)
            """
            
            params_batch = [
                (
                    m.service_name,
                    m.metric_name,
                    m.value,
                    m.unit,
                    json.dumps(m.tags),
                    m.timestamp
                )
                for m in metrics_to_write
            ]
            
            await self.db_manager.execute_many(query, params_batch)
            
            self.logger.debug(f"Flushed {len(metrics_to_write)} metrics to database")
            
        except Exception as e:
            self.logger.error(f"Error flushing metrics: {e}", exc_info=True)
    
    async def get_metrics(
        self,
        service_name: Optional[str] = None,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Retrieve metrics from database.
        
        Args:
            service_name: Filter by service (optional)
            metric_name: Filter by metric name (optional)
            start_time: Start of time range (optional)
            end_time: End of time range (optional)
            limit: Maximum number of metrics to return
            
        Returns:
            List of metric dictionaries
        """
        try:
            conditions = []
            params = []
            param_counter = 1
            
            if service_name:
                conditions.append(f"service_name = ${param_counter}")
                params.append(service_name)
                param_counter += 1
            
            if metric_name:
                conditions.append(f"metric_name = ${param_counter}")
                params.append(metric_name)
                param_counter += 1
            
            if start_time:
                conditions.append(f"timestamp >= ${param_counter}")
                params.append(start_time)
                param_counter += 1
            
            if end_time:
                conditions.append(f"timestamp <= ${param_counter}")
                params.append(end_time)
                param_counter += 1
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            query = f"""
                SELECT service_name, metric_name, value, unit, tags, timestamp
                FROM {self.db_schema}.monitoring_metrics
                {where_clause}
                ORDER BY timestamp DESC
                LIMIT {limit}
            """
            
            rows = await self.db_manager.fetch_all(query, tuple(params))
            
            return rows
            
        except Exception as e:
            self.logger.error(f"Error retrieving metrics: {e}", exc_info=True)
            return []
    
    # ═════════════════════════════════════════════════════════════════════════
    # Dashboard and Reporting
    # ═════════════════════════════════════════════════════════════════════════
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data.
        
        Returns:
            Dashboard data including current status, active alerts, recent metrics
        """
        try:
            # Get current system health
            registry_health = await self.service_registry.health_check(detailed=True)
            
            # Get active alerts
            active_alerts_list = [
                {
                    'alert_id': alert.alert_id,
                    'severity': alert.severity.value,
                    'alert_type': alert.alert_type.value,
                    'service_name': alert.service_name,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'acknowledged': alert.acknowledged
                }
                for alert in self.active_alerts.values()
            ]
            
            # Get recent alerts
            recent_alerts_list = [
                {
                    'alert_id': alert.alert_id,
                    'severity': alert.severity.value,
                    'alert_type': alert.alert_type.value,
                    'service_name': alert.service_name,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'resolved': alert.resolved
                }
                for alert in list(self.alert_history)[-10:]
            ]
            
            # Get service uptime metrics
            uptime_stats = await self._calculate_uptime_stats()
            
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'system_health': {
                    'overall_status': registry_health['overall_status'],
                    'healthy_services': registry_health['summary']['healthy'],
                    'total_services': registry_health['summary']['total'],
                    'health_percentage': (registry_health['summary']['healthy'] / registry_health['summary']['total'] * 100) 
                                       if registry_health['summary']['total'] > 0 else 0
                },
                'active_alerts': {
                    'total': len(active_alerts_list),
                    'critical': sum(1 for a in active_alerts_list if a['severity'] == 'critical'),
                    'error': sum(1 for a in active_alerts_list if a['severity'] == 'error'),
                    'warning': sum(1 for a in active_alerts_list if a['severity'] == 'warning'),
                    'alerts': active_alerts_list
                },
                'recent_alerts': recent_alerts_list,
                'monitoring_stats': {
                    'checks_performed': self._checks_performed,
                    'alerts_generated': self._alerts_generated,
                    'metrics_collected': self._metrics_collected
                },
                'uptime_stats': uptime_stats
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}", exc_info=True)
            return {}
    
    async def _calculate_uptime_stats(self) -> Dict[str, Any]:
        """Calculate uptime statistics for all services."""
        try:
            # Get health check data from last 24 hours
            start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            
            query = f"""
                SELECT service_name, status, COUNT(*) as check_count
                FROM {self.db_schema}.monitoring_health_checks
                WHERE timestamp >= $1
                GROUP BY service_name, status
                ORDER BY service_name, status
            """
            
            rows = await self.db_manager.fetch_all(query, (start_time,))
            
            # Calculate uptime per service
            service_stats = defaultdict(lambda: {'healthy': 0, 'degraded': 0, 'unhealthy': 0, 'total': 0})
            
            for row in rows:
                service = row['service_name']
                status = row['status']
                count = row['check_count']
                
                service_stats[service][status] = count
                service_stats[service]['total'] += count
            
            # Calculate uptime percentage
            uptime_results = {}
            for service, stats in service_stats.items():
                total = stats['total']
                healthy = stats['healthy']
                uptime_pct = (healthy / total * 100) if total > 0 else 0
                
                uptime_results[service] = {
                    'uptime_percentage': round(uptime_pct, 2),
                    'checks': stats
                }
            
            return uptime_results
            
        except Exception as e:
            self.logger.error(f"Error calculating uptime stats: {e}", exc_info=True)
            return {}
    
    # ═════════════════════════════════════════════════════════════════════════
    # Service Lifecycle
    # ═════════════════════════════════════════════════════════════════════════
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Health check for the monitoring service itself.
        
        Returns:
            Health status dictionary
        """
        return {
            'status': 'healthy' if self._initialized else 'unhealthy',
            'message': 'Monitoring service operational' if self._initialized else 'Not initialized',
            'details': {
                'initialized': self._initialized,
                'checks_performed': self._checks_performed,
                'alerts_generated': self._alerts_generated,
                'metrics_collected': self._metrics_collected,
                'active_alerts': len(self.active_alerts),
                'metrics_buffer_size': len(self.metrics_buffer),
                'monitoring_running': self._monitoring_task is not None and not self._monitoring_task.done(),
                'metrics_flush_running': self._metrics_flush_task is not None and not self._metrics_flush_task.done()
            }
        }
    
    async def close(self):
        """Clean up monitoring service."""
        try:
            # Cancel background tasks
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass
            
            if self._metrics_flush_task:
                self._metrics_flush_task.cancel()
                try:
                    await self._metrics_flush_task
                except asyncio.CancelledError:
                    pass
            
            # Flush remaining metrics
            await self.flush_metrics()
            
            self.logger.info("UBECMonitoringService closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing monitoring service: {e}", exc_info=True)


# ═════════════════════════════════════════════════════════════════════════════
# Factory Function (Service Registry Integration)
# ═════════════════════════════════════════════════════════════════════════════

async def create_monitoring_service(
    service_registry: Any,
    db_manager: Any,
    config: Dict[str, Any],
    logger: Optional[logging.Logger] = None
) -> UBECMonitoringService:
    """
    Factory function to create and initialize monitoring service.
    
    Args:
        service_registry: Service registry instance
        db_manager: Async database manager instance
        config: Configuration dictionary
        logger: Optional logger instance
        
    Returns:
        Initialized UBECMonitoringService instance
        
    Raises:
        RuntimeError: If initialization fails
    """
    monitoring = UBECMonitoringService(
        service_registry=service_registry,
        db_manager=db_manager,
        config=config,
        logger=logger
    )
    
    success = await monitoring.initialize()
    
    if not success:
        raise RuntimeError("Failed to initialize UBECMonitoringService")
    
    return monitoring


# ═════════════════════════════════════════════════════════════════════════════
# Module Documentation
# ═════════════════════════════════════════════════════════════════════════════

__all__ = [
    'UBECMonitoringService',
    'create_monitoring_service',
    'Alert',
    'AlertSeverity',
    'AlertType',
    'MetricPoint'
]

"""
UBEC Monitoring Service - Usage Examples
═════════════════════════════════════════════════════════════════════════════

Basic Usage (via Service Registry):
───────────────────────────────────────────────────────────────────────────────
    # Initialize monitoring service
    monitoring = await create_monitoring_service(
        service_registry=registry,
        db_manager=db,
        config={'health_check_interval': 60}
    )
    
    # Get dashboard data
    dashboard = await monitoring.get_dashboard_data()
    print(f"System health: {dashboard['system_health']['health_percentage']:.1f}%")
    print(f"Active alerts: {dashboard['active_alerts']['total']}")

Manual Health Check:
───────────────────────────────────────────────────────────────────────────────
    # Check all services manually
    health = await monitoring.check_all_services()

Alert Management:
───────────────────────────────────────────────────────────────────────────────
    # Generate custom alert
    await monitoring.generate_alert(
        severity=AlertSeverity.WARNING,
        alert_type=AlertType.CUSTOM,
        service_name='distribution',
        message='Distribution approaching non-compliance',
        details={'admin_pct': 6.2, 'threshold': 5.0}
    )
    
    # Acknowledge alert
    await monitoring.acknowledge_alert(alert_id='alert_123', acknowledged_by='admin')
    
    # Resolve alert
    await monitoring.resolve_alert(alert_id='alert_123')

Metrics Recording:
───────────────────────────────────────────────────────────────────────────────
    # Record metrics
    await monitoring.record_metric(
        service_name='synchronizer',
        metric_name='accounts_synced',
        value=150,
        unit='count',
        tags={'element': 'air'}
    )
    
    # Query metrics
    metrics = await monitoring.get_metrics(
        service_name='synchronizer',
        metric_name='accounts_synced',
        start_time=datetime.now() - timedelta(hours=24)
    )

Alert Handlers:
───────────────────────────────────────────────────────────────────────────────
    # Register email alert handler
    async def email_alert_handler(alert: Alert):
        if alert.severity == AlertSeverity.CRITICAL:
            await send_email(
                to='ops@example.com',
                subject=f'CRITICAL: {alert.message}',
                body=f"Service: {alert.service_name}\nDetails: {alert.details}"
            )
    
    monitoring.register_alert_handler(email_alert_handler)
    
    # Register Slack handler
    async def slack_alert_handler(alert: Alert):
        await post_to_slack(
            channel='#alerts',
            message=f"🚨 {alert.severity.value.upper()}: {alert.message}"
        )
    
    monitoring.register_alert_handler(slack_alert_handler)

Dashboard Integration:
───────────────────────────────────────────────────────────────────────────────
    # Get comprehensive dashboard data
    dashboard = await monitoring.get_dashboard_data()
    
    # Access system health
    print(f"Overall Status: {dashboard['system_health']['overall_status']}")
    print(f"Healthy Services: {dashboard['system_health']['healthy_services']}")
    
    # Access active alerts
    for alert in dashboard['active_alerts']['alerts']:
        print(f"  [{alert['severity']}] {alert['service_name']}: {alert['message']}")
    
    # Access uptime stats
    for service, stats in dashboard['uptime_stats'].items():
        print(f"{service}: {stats['uptime_percentage']}% uptime")

Attribution:
───────────────────────────────────────────────────────────────────────────────
This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
═════════════════════════════════════════════════════════════════════════════
"""
