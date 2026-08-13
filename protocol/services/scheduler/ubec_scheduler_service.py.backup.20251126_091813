#!/usr/bin/env python3
"""
UBEC Protocol Scheduler Service - Production Version 1.0.4
=========================================================
Automated task scheduling and execution for continuous protocol operation.

This service manages periodic execution of critical system tasks including
blockchain synchronization, analytics updates, holonic evaluation, and
report generation. All configuration is database-driven and fully async.

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Self-contained scheduler with clear boundaries
    ✅ #2  Service Pattern: No standalone execution, registry-managed
    ✅ #3  Service Registry: Full dependency injection via registry
    ✅ #4  Single Source of Truth: Job config in database scheduler_jobs table
    ✅ #5  Strict Async: 100% async/await operations throughout
    ✅ #6  No Sync Fallbacks: Pure async implementation
    ✅ #7  Per-Asset Monitoring: Per-job health tracking
    ✅ #8  No Duplicate Configuration: Jobs defined once in database
    ✅ #9  Integrated Rate Limiting: Respects service rate limits
    ✅ #10 Separation of Concerns: Orchestrates, doesn't execute logic
    ✅ #11 Comprehensive Documentation: Full docstrings and examples
    ✅ #12 Method Singularity: Reuses existing service methods
════════════════════════════════════════════════════════════════════════════

Attribution: This project uses the services of Claude and Anthropic PBC to 
inform our decisions and recommendations. This project was made possible with 
the assistance of Claude and Anthropic PBC.

Features:
    - Database-driven job configuration
    - Interval-based scheduling (no external dependencies)
    - Comprehensive error handling with circuit breaker
    - Health monitoring and metrics
    - Graceful shutdown
    - Dynamic job reloading
    - Enhanced status detection for NOT RUNNING state

Usage Example:
    ```python
    # Via service registry (proper pattern)
    from core.service_registry import ServiceRegistry
    
    registry = ServiceRegistry()
    await registry.initialize()
    
    scheduler = await registry.get('scheduler')
    await scheduler.start()  # Begins background task loop
    
    # Runs until interrupted
    await scheduler.wait_for_completion()
    ```

Author: UBEC Protocol Development Team
Version: 1.0.4 (Enhanced Health Monitoring & Wait Support)
Updated: 2025-11-08

CHANGELOG v1.0.4:
    - ENHANCEMENT: Health check now explicitly detects NOT RUNNING state
    - ENHANCEMENT: Added wait_for_completion() method for proper shutdown handling
    - ENHANCEMENT: Status determination considers scheduler._running state
    - ENHANCEMENT: Better diagnostic information when scheduler not started
    - FIX: Health check now returns 'not_started' status when initialized but not running
    
CHANGELOG v1.0.3:
    - CRITICAL FIX: Added _parse_job_parameters() for robust JSONB parsing
    - CRITICAL FIX: Safe parameter extraction with type checking in _execute_job()
    - CRITICAL FIX: Exclude 'timeout' from method execution parameters
    - Enhanced error handling in job loading with per-job try-catch
    - Improved debug logging for parameter types
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import traceback
import json

logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class JobStatus(str, Enum):
    """Job execution status"""
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    DISABLED = 'disabled'


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = 'closed'      # Normal operation
    OPEN = 'open'          # Too many failures, job disabled
    HALF_OPEN = 'half_open'  # Testing if service recovered


@dataclass
class JobMetrics:
    """Metrics for a scheduled job"""
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    total_duration_ms: float = 0
    avg_duration_ms: float = 0
    last_duration_ms: float = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    consecutive_failures: int = 0
    circuit_state: CircuitState = CircuitState.CLOSED


@dataclass
class ScheduledJob:
    """Represents a scheduled job"""
    id: int
    job_name: str
    schedule_interval: int  # seconds
    next_run: datetime
    last_run: Optional[datetime]
    job_function: str  # e.g., "sync_service.sync_incremental"
    parameters: Dict[str, Any]
    enabled: bool
    metrics: JobMetrics = field(default_factory=JobMetrics)
    task: Optional[asyncio.Task] = None
    
    def is_due(self) -> bool:
        """Check if job is due to run"""
        return self.enabled and datetime.now() >= self.next_run
    
    def calculate_next_run(self) -> datetime:
        """Calculate next run time based on interval"""
        return datetime.now() + timedelta(seconds=self.schedule_interval)
    
    @property
    def success_rate(self) -> float:
        """Calculate job success rate"""
        if self.metrics.total_runs == 0:
            return 1.0
        return self.metrics.successful_runs / self.metrics.total_runs


# ============================================================================
# Scheduler Service
# ============================================================================

class UBECSchedulerService:
    """
    Automated task scheduler for UBEC Protocol.
    
    Manages periodic execution of system tasks with database-driven
    configuration, health monitoring, and error recovery.
    
    Attributes:
        registry: ServiceRegistry instance for dependency injection
        db_manager: Database manager for job persistence
        jobs: Dictionary of active jobs
        _running: Flag indicating if scheduler is active
        _main_task: Main scheduler loop task
        _initialized: Initialization status
    """
    
    def __init__(self, service_registry):
        """
        Initialize scheduler service.
        
        DO NOT call directly. Use create_scheduler_service() factory.
        
        Args:
            service_registry: ServiceRegistry instance
        """
        self.registry = service_registry
        self.db_manager = None
        self.logger = logger
        
        # Job management
        self.jobs: Dict[str, ScheduledJob] = {}
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        
        # Configuration (will be loaded from database/config)
        self.check_interval = 60  # seconds between schedule checks
        self.max_concurrent_jobs = 5
        self.error_threshold = 3  # failures before circuit breaker opens
        self.circuit_recovery_time = 300  # seconds before retry
        
        # Lifecycle
        self._initialized = False
        
        self.logger.info("UBECSchedulerService initialized")
    
    # ========================================================================
    # Lifecycle Management
    # ========================================================================
    
    async def initialize(self) -> None:
        """
        Initialize scheduler service.
        
        Loads configuration, sets up database connection, and loads jobs.
        Called by service registry during system startup.
        """
        try:
            self.logger.info("Initializing UBECSchedulerService")
            
            # Get dependencies from registry
            self.db_manager = await self.registry.get('database')
            config_service = await self.registry.get('config')
            
            # Load configuration (NO AWAIT - config.get() is synchronous)
            # Config service provides cached values via dictionary-style access
            self.check_interval = config_service.get(
                'scheduler_check_interval',
                60  # default value
            )
            self.max_concurrent_jobs = config_service.get(
                'scheduler_max_concurrent_jobs',
                5  # default value
            )
            self.error_threshold = config_service.get(
                'scheduler_error_threshold',
                3  # default value
            )
            self.circuit_recovery_time = config_service.get(
                'scheduler_circuit_recovery_time',
                300  # default value
            )
            
            # Load jobs from database
            await self._load_jobs()
            
            self._initialized = True
            self.logger.info(
                f"✓ Scheduler initialized with {len(self.jobs)} jobs"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize scheduler: {e}", exc_info=True)
            raise
    
    async def start(self) -> None:
        """
        Start the scheduler.
        
        Begins the main scheduling loop as a background task.
        Non-blocking - returns immediately after starting.
        """
        if not self._initialized:
            raise RuntimeError("Scheduler not initialized. Call initialize() first.")
        
        if self._running:
            self.logger.warning("Scheduler already running")
            return
        
        self._running = True
        self._main_task = asyncio.create_task(self._scheduler_loop())
        self.logger.info("✓ Scheduler started")
    
    async def stop(self) -> None:
        """
        Stop the scheduler gracefully.
        
        Waits for currently running jobs to complete before stopping.
        """
        if not self._running:
            self.logger.warning("Scheduler not running")
            return
        
        self.logger.info("Stopping scheduler...")
        self._running = False
        
        # Cancel main loop
        if self._main_task:
            self._main_task.cancel()
            try:
                await self._main_task
            except asyncio.CancelledError:
                pass
        
        # Wait for running jobs to complete
        running_jobs = [
            job.task for job in self.jobs.values()
            if job.task and not job.task.done()
        ]
        
        if running_jobs:
            self.logger.info(f"Waiting for {len(running_jobs)} jobs to complete...")
            await asyncio.gather(*running_jobs, return_exceptions=True)
        
        self.logger.info("✓ Scheduler stopped")
    
    async def wait_for_completion(self) -> None:
        """
        Wait for scheduler to complete (until manually stopped).
        
        This method blocks until the scheduler is stopped via stop() or
        an interrupt signal. Useful for keeping the scheduler running in
        standalone mode.
        
        Example:
            scheduler = await registry.get('scheduler')
            await scheduler.start()
            await scheduler.wait_for_completion()  # Blocks until Ctrl+C
        """
        if not self._running:
            self.logger.warning("Scheduler not running, nothing to wait for")
            return
        
        if not self._main_task:
            self.logger.error("Scheduler main task not found")
            return
        
        try:
            # Wait for the main scheduler loop to complete
            await self._main_task
        except asyncio.CancelledError:
            self.logger.info("Scheduler cancelled")
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}", exc_info=True)
    
    async def close(self) -> None:
        """
        Clean up resources.
        
        Called by service registry during system shutdown.
        """
        await self.stop()
        self._initialized = False
        self.logger.info("✓ Scheduler closed")
    
    # ========================================================================
    # Job Loading and Management
    # ========================================================================
    
    def _parse_job_parameters(self, params_value: Any) -> Dict[str, Any]:
        """
        Parse job parameters from database value.
        
        Handles multiple formats to ensure parameters are always a dict:
        - None/NULL → {}
        - Dict → return as-is
        - String (JSON) → parse to dict
        - String (non-JSON) → {}
        - Other types → {} with warning
        
        This implements Principle #12 (Method Singularity) by providing
        a single, reusable parameter parsing method for all job loads.
        
        Args:
            params_value: Raw parameters value from database JSONB column
            
        Returns:
            Dict[str, Any]: Parsed parameters dictionary (never None)
            
        Example:
            >>> params = self._parse_job_parameters(None)
            >>> assert params == {}
            
            >>> params = self._parse_job_parameters('{"timeout": 300}')
            >>> assert params == {'timeout': 300}
            
            >>> params = self._parse_job_parameters({'timeout': 300})
            >>> assert params == {'timeout': 300}
        """
        # Handle None/NULL from database
        if params_value is None:
            return {}
        
        # Already a dict - return as-is (expected case)
        if isinstance(params_value, dict):
            return params_value
        
        # String value - attempt JSON parsing
        if isinstance(params_value, str):
            # Empty string → empty dict
            if not params_value.strip():
                return {}
            
            try:
                parsed = json.loads(params_value)
                if isinstance(parsed, dict):
                    return parsed
                else:
                    # Parsed successfully but not a dict
                    self.logger.warning(
                        f"Parameters parsed to {type(parsed).__name__}, "
                        f"expected dict. Returning empty dict."
                    )
                    return {}
            except (json.JSONDecodeError, TypeError) as e:
                # Invalid JSON
                self.logger.warning(
                    f"Failed to parse parameters as JSON: {e}. "
                    f"Returning empty dict."
                )
                return {}
        
        # Unexpected type (shouldn't happen with JSONB column)
        self.logger.warning(
            f"Unexpected parameter type: {type(params_value).__name__}. "
            f"Expected dict or JSON string. Returning empty dict."
        )
        return {}
    
    async def _load_jobs(self) -> None:
        """
        Load jobs from database with robust parameter parsing.
        
        Reads scheduler_jobs table and creates ScheduledJob instances.
        Implements proper error handling and parameter validation.
        
        Principle #4: Database is single source of truth.
        Principle #12: Uses shared _parse_job_parameters() method.
        """
        query = """
            SELECT 
                id,
                job_name,
                schedule_interval,
                next_run,
                last_run,
                job_function,
                parameters,
                enabled
            FROM ubec_main.scheduler_jobs
            ORDER BY job_name
        """
        
        try:
            # Use database manager's fetch method (Principle #12: Method Singularity)
            rows = await self.db_manager.fetch_all(query)
            
            if rows:
                for row in rows:
                    try:
                        # Parse interval (handle both seconds and cron-like strings)
                        interval_str = row['schedule_interval']
                        interval_seconds = self._parse_interval(interval_str)
                        
                        # CRITICAL FIX: Properly parse parameters using new parser
                        raw_parameters = row['parameters']
                        parsed_parameters = self._parse_job_parameters(raw_parameters)
                        
                        job = ScheduledJob(
                            id=row['id'],
                            job_name=row['job_name'],
                            schedule_interval=interval_seconds,
                            next_run=row['next_run'],
                            last_run=row['last_run'],
                            job_function=row['job_function'],
                            parameters=parsed_parameters,  # ← FIXED: Use parsed version
                            enabled=row['enabled']
                        )
                        
                        self.jobs[job.job_name] = job
                        self.logger.debug(
                            f"Loaded job: {job.job_name} "
                            f"(interval={interval_seconds}s, enabled={job.enabled}, "
                            f"params={len(parsed_parameters)} keys)"
                        )
                        
                    except Exception as e:
                        # Log error but continue with other jobs
                        job_name = row.get('job_name', 'unknown')
                        self.logger.error(
                            f"Error loading job '{job_name}': {e}",
                            exc_info=True
                        )
                        # Don't raise - continue loading other jobs
                        continue
                
                self.logger.info(f"Loaded {len(self.jobs)} jobs from database")
            else:
                self.logger.warning("No jobs found in database")
                
        except Exception as e:
            self.logger.error(f"Error loading jobs: {e}", exc_info=True)
            raise
    
    def _parse_interval(self, interval_str: str) -> int:
        """
        Parse interval string to seconds.
        
        Supports:
        - Direct seconds: "300"
        - Minutes: "5m"
        - Hours: "2h"
        - Days: "1d"
        
        Args:
            interval_str: Interval string from database
            
        Returns:
            Interval in seconds
        """
        try:
            # Try direct integer parsing first
            return int(interval_str)
        except ValueError:
            pass
        
        # Parse time units
        interval_str = interval_str.strip().lower()
        
        if interval_str.endswith('s'):
            return int(interval_str[:-1])
        elif interval_str.endswith('m'):
            return int(interval_str[:-1]) * 60
        elif interval_str.endswith('h'):
            return int(interval_str[:-1]) * 3600
        elif interval_str.endswith('d'):
            return int(interval_str[:-1]) * 86400
        else:
            raise ValueError(f"Invalid interval format: {interval_str}")
    
    async def reload_jobs(self) -> None:
        """
        Reload jobs from database.
        
        Allows dynamic job configuration changes without restart.
        """
        self.logger.info("Reloading jobs from database...")
        old_job_count = len(self.jobs)
        
        # Clear existing jobs
        self.jobs.clear()
        
        # Reload from database
        await self._load_jobs()
        
        self.logger.info(
            f"Jobs reloaded: {old_job_count} -> {len(self.jobs)}"
        )
    
    # ========================================================================
    # Main Scheduler Loop
    # ========================================================================
    
    async def _scheduler_loop(self) -> None:
        """
        Main scheduler loop.
        
        Continuously checks for due jobs and executes them.
        Runs until stopped or cancelled.
        """
        self.logger.info("Scheduler loop started")
        
        while self._running:
            try:
                # Check circuit breakers
                await self._check_circuit_breakers()
                
                # Find due jobs
                due_jobs = [
                    job for job in self.jobs.values()
                    if job.is_due() and (job.task is None or job.task.done())
                ]
                
                if due_jobs:
                    self.logger.info(f"Found {len(due_jobs)} due jobs")
                
                # Execute due jobs (respecting concurrency limit)
                for job in due_jobs[:self.max_concurrent_jobs]:
                    job.task = asyncio.create_task(self._execute_job(job))
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                self.logger.info("Scheduler loop cancelled")
                break
            except Exception as e:
                self.logger.error(
                    f"Error in scheduler loop: {e}",
                    exc_info=True
                )
                await asyncio.sleep(60)  # Wait before retry
        
        self.logger.info("Scheduler loop stopped")
    
    async def _execute_job(self, job: ScheduledJob) -> None:
        """
        Execute a scheduled job with proper parameter handling.
        
        Handles job execution, error recovery, metrics tracking, and
        database updates. Includes robust parameter type checking.
        
        Args:
            job: ScheduledJob instance to execute
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Executing job: {job.job_name}")
            
            # Get service and method
            service, method = await self._resolve_job_function(job.job_function)
            
            # CRITICAL FIX: Safe timeout extraction with type checking
            # Ensure parameters is a dict before accessing
            if not isinstance(job.parameters, dict):
                self.logger.warning(
                    f"Job '{job.job_name}' has invalid parameters type: "
                    f"{type(job.parameters).__name__}. Using defaults."
                )
                timeout_seconds = 3600  # 1 hour default
                execution_params = {}
            else:
                # Extract timeout, don't pass it to the method
                timeout_seconds = job.parameters.get('timeout', 3600)
                
                # CRITICAL FIX: Create execution parameters without timeout
                # The 'timeout' parameter is for asyncio.wait_for, not the job method
                execution_params = {
                    k: v for k, v in job.parameters.items() 
                    if k != 'timeout'
                }
            
            self.logger.debug(
                f"Executing {job.job_function} "
                f"(timeout={timeout_seconds}s, params={execution_params})"
            )
            
            # Execute with timeout
            await asyncio.wait_for(
                method(**execution_params),  # ← FIXED: Pass cleaned parameters
                timeout=timeout_seconds
            )
            
            # Record success
            duration = (datetime.now() - start_time).total_seconds() * 1000
            await self._record_success(job, duration)
            
            self.logger.info(
                f"✓ Job '{job.job_name}' completed ({duration:.0f}ms)"
            )
            
        except asyncio.TimeoutError:
            error_msg = f"Job '{job.job_name}' timed out after {timeout_seconds}s"
            self.logger.error(error_msg)
            await self._record_failure(job, error_msg)
            
        except Exception as e:
            error_msg = f"Job '{job.job_name}' failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            await self._record_failure(job, error_msg)
        
        finally:
            # Update next run time
            job.next_run = job.calculate_next_run()
            await self._update_job_schedule(job)
    
    async def _resolve_job_function(
        self,
        function_path: str
    ) -> tuple[Any, Callable]:
        """
        Resolve job function from string path.
        
        Supports format: "service_name.method_name"
        
        Args:
            function_path: String like "sync_service.sync_incremental"
            
        Returns:
            Tuple of (service instance, method callable)
            
        Example:
            service, method = await resolve_job_function("sync.sync_incremental")
            result = await method(param1="value1")
        """
        try:
            parts = function_path.split('.')
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid function path: {function_path}. "
                    "Expected format: 'service_name.method_name'"
                )
            
            service_name, method_name = parts
            
            # Get service from registry
            service = await self.registry.get(service_name)
            
            # Get method from service
            if not hasattr(service, method_name):
                raise AttributeError(
                    f"Service '{service_name}' has no method '{method_name}'"
                )
            
            method = getattr(service, method_name)
            
            if not callable(method):
                raise TypeError(
                    f"'{service_name}.{method_name}' is not callable"
                )
            
            return service, method
            
        except Exception as e:
            self.logger.error(
                f"Error resolving job function '{function_path}': {e}"
            )
            raise
    
    # ========================================================================
    # Metrics and Health Tracking
    # ========================================================================
    
    async def _record_success(self, job: ScheduledJob, duration_ms: float) -> None:
        """
        Record successful job execution.
        
        Updates metrics and resets circuit breaker.
        """
        job.metrics.total_runs += 1
        job.metrics.successful_runs += 1
        job.metrics.last_duration_ms = duration_ms
        job.metrics.total_duration_ms += duration_ms
        job.metrics.avg_duration_ms = (
            job.metrics.total_duration_ms / job.metrics.total_runs
        )
        job.metrics.consecutive_failures = 0
        
        # Close circuit breaker on success
        if job.metrics.circuit_state != CircuitState.CLOSED:
            job.metrics.circuit_state = CircuitState.CLOSED
            self.logger.info(f"Circuit breaker closed for job: {job.job_name}")
        
        job.last_run = datetime.now()
    
    async def _record_failure(self, job: ScheduledJob, error_msg: str) -> None:
        """
        Record failed job execution.
        
        Updates metrics and potentially opens circuit breaker.
        """
        job.metrics.total_runs += 1
        job.metrics.failed_runs += 1
        job.metrics.consecutive_failures += 1
        job.metrics.last_error = error_msg
        job.metrics.last_error_time = datetime.now()
        
        # Check circuit breaker threshold
        if job.metrics.consecutive_failures >= self.error_threshold:
            job.metrics.circuit_state = CircuitState.OPEN
            job.enabled = False
            
            self.logger.error(
                f"Circuit breaker opened for job '{job.job_name}' "
                f"after {self.error_threshold} consecutive failures"
            )
            
            # Update database
            await self._disable_job(job)
    
    async def _check_circuit_breakers(self) -> None:
        """
        Check circuit breakers and attempt recovery.
        
        Transitions OPEN -> HALF_OPEN after recovery time.
        """
        for job in self.jobs.values():
            if job.metrics.circuit_state == CircuitState.OPEN:
                if job.metrics.last_error_time:
                    elapsed = (
                        datetime.now() - job.metrics.last_error_time
                    ).total_seconds()
                    
                    if elapsed >= self.circuit_recovery_time:
                        job.metrics.circuit_state = CircuitState.HALF_OPEN
                        job.enabled = True
                        
                        self.logger.info(
                            f"Circuit breaker entering HALF_OPEN for: {job.job_name}"
                        )
                        
                        # Update database
                        await self._enable_job(job)
    
    # ========================================================================
    # Database Operations
    # ========================================================================
    
    async def _update_job_schedule(self, job: ScheduledJob) -> None:
        """Update job schedule in database."""
        query = """
            UPDATE ubec_main.scheduler_jobs
            SET 
                next_run = $1,
                last_run = $2,
                updated_at = NOW()
            WHERE id = $3
        """
        
        try:
            await self.db_manager.execute(
                query,
                (job.next_run, job.last_run, job.id)
            )
        except Exception as e:
            self.logger.error(
                f"Error updating job schedule for '{job.job_name}': {e}"
            )
    
    async def _disable_job(self, job: ScheduledJob) -> None:
        """Disable job in database."""
        query = """
            UPDATE ubec_main.scheduler_jobs
            SET enabled = false, updated_at = NOW()
            WHERE id = $1
        """
        
        try:
            await self.db_manager.execute(query, (job.id,))
            self.logger.info(f"Job '{job.job_name}' disabled in database")
        except Exception as e:
            self.logger.error(f"Error disabling job '{job.job_name}': {e}")
    
    async def _enable_job(self, job: ScheduledJob) -> None:
        """Enable job in database."""
        query = """
            UPDATE ubec_main.scheduler_jobs
            SET enabled = true, updated_at = NOW()
            WHERE id = $1
        """
        
        try:
            await self.db_manager.execute(query, (job.id,))
            self.logger.info(f"Job '{job.job_name}' enabled in database")
        except Exception as e:
            self.logger.error(f"Error enabling job '{job.job_name}': {e}")
    
    # ========================================================================
    # Health Check (ServiceHealthCheck Compatible)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for monitoring.
        
        Returns detailed status of scheduler and all jobs.
        Compatible with ServiceHealthCheck utility (Principle #12).
        
        ENHANCED: Now explicitly detects NOT RUNNING state when scheduler
        is initialized but start() has not been called.
        
        Returns:
            Health status dictionary with scheduler and job metrics
        """
        try:
            if not self._initialized:
                return {
                    'service': 'UBECSchedulerService',
                    'status': 'initializing',
                    'initialized': False
                }
            
            # ENHANCEMENT: Check if scheduler is initialized but not started
            if self._initialized and not self._running:
                return {
                    'service': 'UBECSchedulerService',
                    'status': 'not_started',
                    'initialized': True,
                    'running': False,
                    'message': (
                        'Scheduler is initialized but not started. '
                        'Call scheduler.start() to begin job execution.'
                    ),
                    'jobs_loaded': len(self.jobs),
                    'timestamp': datetime.now().isoformat()
                }
            
            # Calculate aggregate metrics
            total_jobs = len(self.jobs)
            enabled_jobs = sum(1 for j in self.jobs.values() if j.enabled)
            running_jobs = sum(
                1 for j in self.jobs.values()
                if j.task and not j.task.done()
            )
            
            total_runs = sum(j.metrics.total_runs for j in self.jobs.values())
            total_failures = sum(j.metrics.failed_runs for j in self.jobs.values())
            
            overall_success_rate = (
                1.0 if total_runs == 0
                else (total_runs - total_failures) / total_runs
            )
            
            # Job details
            jobs_status = [
                {
                    'name': job.job_name,
                    'enabled': job.enabled,
                    'next_run': job.next_run.isoformat() if job.next_run else None,
                    'last_run': job.last_run.isoformat() if job.last_run else None,
                    'success_rate': job.success_rate,
                    'avg_duration_ms': job.metrics.avg_duration_ms,
                    'circuit_state': job.metrics.circuit_state.value,
                    'consecutive_failures': job.metrics.consecutive_failures
                }
                for job in self.jobs.values()
            ]
            
            # ENHANCEMENT: Determine status considering _running state
            if not self._running:
                status = 'not_started'
            elif overall_success_rate >= 0.9 and running_jobs < self.max_concurrent_jobs:
                status = 'healthy'
            elif overall_success_rate >= 0.7:
                status = 'degraded'
            else:
                status = 'unhealthy'
            
            return {
                'service': 'UBECSchedulerService',
                'status': status,
                'initialized': self._initialized,
                'running': self._running,
                'metrics': {
                    'total_jobs': total_jobs,
                    'enabled_jobs': enabled_jobs,
                    'running_jobs': running_jobs,
                    'total_runs': total_runs,
                    'total_failures': total_failures,
                    'overall_success_rate': overall_success_rate
                },
                'jobs': jobs_status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            return {
                'service': 'UBECSchedulerService',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_job_status(self, job_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed status of specific job.
        
        Args:
            job_name: Name of job to query
            
        Returns:
            Job status dictionary or None if not found
        """
        job = self.jobs.get(job_name)
        if not job:
            return None
        
        return {
            'job_name': job.job_name,
            'enabled': job.enabled,
            'schedule_interval': job.schedule_interval,
            'next_run': job.next_run.isoformat() if job.next_run else None,
            'last_run': job.last_run.isoformat() if job.last_run else None,
            'metrics': {
                'total_runs': job.metrics.total_runs,
                'successful_runs': job.metrics.successful_runs,
                'failed_runs': job.metrics.failed_runs,
                'success_rate': job.success_rate,
                'avg_duration_ms': job.metrics.avg_duration_ms,
                'last_duration_ms': job.metrics.last_duration_ms,
                'consecutive_failures': job.metrics.consecutive_failures,
                'circuit_state': job.metrics.circuit_state.value,
                'last_error': job.metrics.last_error,
                'last_error_time': (
                    job.metrics.last_error_time.isoformat()
                    if job.metrics.last_error_time else None
                )
            }
        }


# ============================================================================
# Service Factory Function
# ============================================================================

async def create_scheduler_service(registry) -> UBECSchedulerService:
    """
    Factory function to create scheduler service instance.
    
    This is the proper way to instantiate the service for use in the
    service registry. Follows factory pattern (Principle #2).
    
    Args:
        registry: ServiceRegistry instance providing dependencies
        
    Returns:
        Initialized UBECSchedulerService instance
        
    Example:
        # In main.py service registration
        registry.register_factory(
            'scheduler',
            create_scheduler_service,
            dependencies=['database', 'config', 'sync', 'analytics']
        )
    """
    service = UBECSchedulerService(registry)
    await service.initialize()
    return service


# ============================================================================
# Module Guard - NO STANDALONE EXECUTION
# Principle #2: Service Pattern - Only main.py can execute
# ============================================================================

if __name__ == "__main__":
    raise RuntimeError(
        "This module implements the service pattern and cannot be run directly. "
        "Use: python main.py serve"
    )
