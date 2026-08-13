#!/usr/bin/env python3
"""
UBEC Protocol Suite - Holonic Visualizer Service
=================================================
Comprehensive visualization of UBEC holonic evaluation results.

Creates charts, graphs, and HTML reports from holonic metrics data with advanced
analytics capabilities.

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Self-contained visualization service
    ✅ #2  Service Pattern: Factory-based instantiation, no standalone execution
    ✅ #3  Service Registry: Accessed through centralized registry
    ✅ #4  Single Source of Truth: Database is authoritative
    ✅ #5  Strict Async Operations: ALL I/O operations use async/await
    ✅ #6  No Sync Fallbacks: Pure async implementation with explicit feature detection
    ✅ #7  Per-Asset Monitoring: Individual account visualization with health checks
    ✅ #8  No Duplicate Configuration: Database-backed configuration
    ✅ #9  Integrated Rate Limiting: Built-in for database operations
    ✅ #10 Separation of Concerns: Visualization logic isolated
    ✅ #11 Comprehensive Documentation: Full docstrings and attribution
    ✅ #12 Method Singularity: Uses ServiceHealthCheck utility for health monitoring
════════════════════════════════════════════════════════════════════════════

Key Features:
- Score distribution histograms
- Holonic dimension radar charts
- Category distribution pie charts
- Network visualization graphs (when transaction data available)
- Time-series trend analysis
- Comparative category analysis
- Correlation matrices
- Account detail views
- Element-specific dashboards
- Comprehensive HTML reports
- Ubuntu dynamic pastel earth tone color palette (v13.0.0)

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team with Claude AI assistance
Version: 13.5.0 (Complete Visualization Suite)
Date: November 29, 2025

Changelog:
    v13.5.0 - COMPREHENSIVE: Complete visualization suite implementation
            - ✅ ADDED: load_time_series_data() - Historical data loading
            - ✅ ADDED: load_network_data() - Transaction network data loading
            - ✅ ADDED: create_time_series_chart() - Trend analysis over time
            - ✅ ADDED: create_correlation_matrix() - Dimension correlation heatmap
            - ✅ ADDED: create_comparative_analysis_chart() - Category comparison
            - ✅ ADDED: create_network_visualization() - Transaction network graph
            - ✅ ADDED: create_account_detail_view() - Individual account dashboard
            - ✅ ENHANCED: generate_html_report() now includes ALL chart types
            - ✅ ENHANCED: _build_html_report() with advanced analytics section
            - 🎯 IMPLEMENTS: All 10 visualization types from v6.0.0 spec
            - ⚡ ASYNC: All methods fully async-compatible
            - 🎨 STYLE: Ubuntu dynamic pastel earth tone color palette
            - 📊 OUTPUT: Charts embedded as base64 PNG images in HTML
            - 🔒 COMPLIANT: All 12 design principles maintained
    v13.4.0 - ENHANCEMENT: Charts now embedded in HTML reports
            - Fixed: Removed non-existent ServiceHealthCheck.database_dependent_health() call
            - Implemented proper standardized health check pattern
            - Runs custom checks directly with proper error handling
            - Returns proper status dictionary with all required fields
            - Resolves AttributeError on health check operations
            - Maintains Principle #12 compliance with direct implementation
    v13.3.0 - CRITICAL FIX: Added generate_html_report method for scheduler
            - ✅ ADDED: generate_html_report() async method
            - ✅ FIXED: Scheduler job 'report_generation' can now execute
            - 🎯 IMPLEMENTS: Full HTML report generation with data visualization
            - ✅ COMPLIANT: All 12 design principles maintained
            - 📊 ENHANCED: Comprehensive report with evaluation summary
            - ⚡ ASYNC: Pure async implementation for scheduler compatibility
            - 🔒 SECURE: Explicit schema names in all database queries
    v13.2.2 - Health Check Return Pattern Verification
    v13.2.1 - Bool Return Fix (check_data_access)
    v13.2.0 - ServiceHealthCheck Integration
    v13.1.5 - Type Conversion & Schema Fix
"""

import asyncio
import base64
import io
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from decimal import Decimal

# Visualization imports with feature detection
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server use
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.gridspec import GridSpec
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

# Optional NetworkX for network visualizations
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None


# ═════════════════════════════════════════════════════════════════════════════
# Ubuntu Color Palette (v13.0.0)
# ═════════════════════════════════════════════════════════════════════════════

UBUNTU_COLORS = {
    # Holonic Category Colors (Dynamic Pastel Earth Tones)
    'categories': {
        'Exemplar': '#B08BBB',      # 🟣 Soft Amethyst - Wisdom & Leadership
        'Integrator': '#8FBC8F',    # 🟢 Sage Green - Growth & Balance
        'Contributor': '#87CEEB',   # 🔵 Sky Blue - Clarity & Cooperation
        'Participant': '#E8A87C',   # 🟠 Soft Terracotta - Community & Warmth
        'Observer': '#9CB4CC'       # ⚪ Soft Slate - Neutrality & Potential
    },
    
    # Element Colors (Four-Element Protocol)
    'elements': {
        'Earth': '#8AA67E',     # Moss Green - Grounding & Stability
        'Water': '#87CEEB',     # Sky Blue - Flow & Adaptability  
        'Air': '#D4B5D9',       # Lavender - Communication & Ideas
        'Fire': '#E8A87C'       # Soft Terracotta - Transformation & Energy
    },
    
    # Gradients for backgrounds and transitions
    'gradients': {
        'earth_to_sky': ['#8AA67E', '#87CEEB'],      # Earth → Sky Blue
        'sage_to_amethyst': ['#8FBC8F', '#B08BBB']   # Sage Green → Amethyst
    },
    
    # Accent colors for highlights and emphasis
    'accents': {
        'growth': '#8FBC8F',     # Sage Green - Growth & Development
        'wisdom': '#B08BBB',     # Soft Amethyst - Wisdom & Insight
        'community': '#E8A87C',  # Soft Terracotta - Community & Connection
        'earth': '#8AA67E'       # Moss Green - Earth & Grounding
    },
    
    # Neutral colors for text, backgrounds, and UI elements
    'neutral': {
        'background': '#FAFAF9',  # Warm White
        'text': '#2D3436',        # Charcoal
        'border': '#E8E6E3',      # Soft Gray
        'grid': '#D3D1CE',        # Medium Gray
        'connection': '#9CB4CC'   # Soft Slate (for links/connections)
    }
}


# ═════════════════════════════════════════════════════════════════════════════
# HolonicVisualizer Service Class
# ═════════════════════════════════════════════════════════════════════════════

class HolonicVisualizer:
    """
    Comprehensive visualization service for UBEC holonic metrics.
    
    This service creates charts, graphs, and HTML reports from holonic evaluation
    data using the Ubuntu color palette and design principles.
    
    Design Pattern:
        Service class instantiated via factory function only.
        Integrates with service registry for database access.
        Follows async-first architecture.
    
    Attributes:
        db_manager: Async database manager from service registry
        config: Configuration dictionary
        logger: Logging instance
        db_schema: Database schema name (default: 'public')
        output_dir: Directory for generated reports and charts
        element_mode: Whether four-element protocol is enabled
        transactions_table_available: Whether transaction data exists
        schema_features_verified: Whether schema verification completed
        report_data: Cached evaluation data
        time_series_data: Cached time-series data
    """
    
    def __init__(
        self,
        db_manager: Any,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize HolonicVisualizer with dependencies.
        
        Args:
            db_manager: Async database manager instance
            config: Configuration dictionary
            logger: Optional logger instance
        """
        self.db_manager = db_manager
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Configuration
        self.db_schema = config.get('db_schema', 'public')
        self.output_dir = Path(config.get('output_dir', './visualizations'))
        self.element_mode = config.get('element_mode', False)
        
        # Feature availability flags (set during initialization)
        self.transactions_table_available = False
        self.schema_features_verified = False
        
        # Cached data
        self.report_data = None
        self.time_series_data = None
        
        # Tracking for health checks
        self._initialized = False
        self._charts_generated = 0
        self._last_visualization = None
        
        self.logger.info(
            f"HolonicVisualizer initialized | "
            f"schema={self.db_schema} | "
            f"element_mode={self.element_mode} | "
            f"color_palette=Ubuntu_v13.0.0"
        )
    
    # ═════════════════════════════════════════════════════════════════════════
    # Lifecycle Methods
    # ═════════════════════════════════════════════════════════════════════════
    
    async def _verify_schema_features(self) -> bool:
        """
        Verify available database schema features.
        
        Detects presence of optional tables like stellar_operations for advanced
        visualizations. Implements Principle #6 (No Sync Fallbacks) and
        Principle #1 (Precision in Implementation).
        
        Returns:
            bool: True if schema features verified successfully
        """
        try:
            # Check for transactions table (Principle #4: Explicit schema names)
            query = """
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_schema = $1 
                    AND table_name = 'stellar_operations'
                ) as table_exists
            """
            
            result = await self.db_manager.fetch_one(query, (self.db_schema,))
            
            if result:
                self.transactions_table_available = result['table_exists']
                self.logger.info(
                    f"Schema features verified | "
                    f"transactions_available={self.transactions_table_available}"
                )
                self.schema_features_verified = True
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Could not verify schema features: {e}")
            self.schema_features_verified = False
            return False
    
    async def initialize(self) -> bool:
        """
        Initialize the visualizer service.
        
        Principle #5: Async initialization operation.
        Principle #4: Database is single source of truth.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing HolonicVisualizer...")
            
            # Verify schema features
            await self._verify_schema_features()
            
            # Create output directory if it doesn't exist
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            self._initialized = True
            self.logger.info("✓ HolonicVisualizer initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize HolonicVisualizer: {e}", exc_info=True)
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of the visualizer service.
        
        Implements standardized health check pattern following Principle #12.
        This implementation builds health status directly without using
        non-existent utility methods.
        
        Principle #5: Async operation for database checks.
        Principle #12: Method Singularity - Direct implementation without duplication.
        
        Returns:
            Dict with health status and diagnostic information:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy',
                'message': str,
                'timestamp': str (ISO format),
                'details': {...}
            }
        """
        try:
            # Initialize details dictionary
            details = {
                'initialized': self._initialized,
                'schema': self.db_schema,
                'matplotlib_available': MATPLOTLIB_AVAILABLE,
                'numpy_available': NUMPY_AVAILABLE,
                'networkx_available': NETWORKX_AVAILABLE,
                'transactions_available': self.transactions_table_available,
                'charts_generated': self._charts_generated,
                'database_connected': False,
                'output_dir_writable': False
            }
            
            # Track check failures
            failures = []
            
            # Check 1: Matplotlib availability
            if not MATPLOTLIB_AVAILABLE:
                failures.append("matplotlib_unavailable")
                self.logger.warning("Matplotlib is not available - chart generation disabled")
            
            # Check 2: Database access
            try:
                query = f"""
                    SELECT COUNT(*) as count
                    FROM {self.db_schema}.holonic_metrics
                    LIMIT 1
                """
                result = await self.db_manager.fetch_one(query, ())
                
                if result is not None:
                    details['database_connected'] = True
                else:
                    failures.append("database_no_result")
                    
            except Exception as e:
                failures.append("database_access")
                details['database_error'] = str(e)
                self.logger.error(f"Database connectivity check failed: {e}")
            
            # Check 3: Output directory
            try:
                if not self.output_dir.exists():
                    failures.append("output_dir_missing")
                elif not self.output_dir.is_dir():
                    failures.append("output_dir_not_directory")
                else:
                    # Test write access
                    test_file = self.output_dir / '.health_check'
                    try:
                        test_file.touch()
                        test_file.unlink()
                        details['output_dir_writable'] = True
                    except Exception as e:
                        failures.append("output_dir_not_writable")
                        details['output_dir_error'] = str(e)
                        
            except Exception as e:
                failures.append("output_dir_check")
                details['output_dir_error'] = str(e)
            
            # Determine overall status
            if not self._initialized:
                status = 'unhealthy'
                message = 'Service not initialized'
            elif 'database_access' in failures or not details['database_connected']:
                status = 'unhealthy'
                message = 'Database not accessible'
            elif 'output_dir_not_writable' in failures:
                status = 'degraded'
                message = 'Output directory not writable - reports cannot be saved'
            elif 'matplotlib_unavailable' in failures:
                status = 'degraded'
                message = 'Matplotlib unavailable - chart generation disabled'
            elif len(failures) > 0:
                status = 'degraded'
                message = f'Service operational with {len(failures)} warning(s)'
            else:
                status = 'healthy'
                message = 'Service fully operational'
            
            # Add failure details if any
            if failures:
                details['failures'] = failures
            
            return {
                'status': status,
                'message': message,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'details': details
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            return {
                'status': 'unhealthy',
                'message': f'Health check error: {str(e)}',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': str(e)
            }
    
    # ═════════════════════════════════════════════════════════════════════════
    # Data Loading Methods
    # ═════════════════════════════════════════════════════════════════════════
    
    async def load_evaluation_data(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Load holonic evaluation data from database.
        
        Principle #4: Database is single source of truth (explicit schema).
        Principle #5: Async database operation.
        
        Args:
            limit: Optional limit on number of accounts to load
        
        Returns:
            Dict containing evaluation data, statistics, and metadata
        """
        try:
            # Build query with explicit schema name (Principle #4)
            query = f"""
                WITH latest_evals AS (
                    SELECT DISTINCT ON (account_id) 
                        account_id,
                        evaluation_date,
                        autonomy_integration_score,
                        multi_scale_score,
                        regenerative_impact_score,
                        network_contribution_score,
                        ubuntu_alignment_score,
                        composite_score,
                        holonic_category
                    FROM {self.db_schema}.holonic_metrics
                    ORDER BY account_id, evaluation_date DESC
                )
                SELECT * FROM latest_evals
                ORDER BY composite_score DESC NULLS LAST
            """
            
            # Add limit if specified
            if limit:
                query += f" LIMIT {int(limit)}"
            
            # Execute query (Principle #5: Async operation)
            results = await self.db_manager.fetch_all(query, ())
            
            if not results:
                self.logger.warning("No evaluation data found in database")
                return {
                    'accounts': [],
                    'categories': {},
                    'statistics': {},
                    'dimension_stats': {},
                    'evaluated_count': 0
                }
            
            # Convert to list of dicts
            accounts = [dict(row) for row in results]
            
            # Calculate category distribution
            categories = {}
            for account in accounts:
                cat = account['holonic_category']
                categories[cat] = categories.get(cat, 0) + 1
            
            # Calculate summary statistics
            scores = [float(a['composite_score']) for a in accounts if a['composite_score'] is not None]
            
            if scores:
                statistics = {
                    'mean': float(sum(scores) / len(scores)),
                    'min': float(min(scores)),
                    'max': float(max(scores)),
                    'count': len(scores)
                }
                
                # Calculate percentiles if numpy available
                if NUMPY_AVAILABLE:
                    statistics['median'] = float(np.median(scores))
                    statistics['p25'] = float(np.percentile(scores, 25))
                    statistics['p75'] = float(np.percentile(scores, 75))
            else:
                statistics = {
                    'mean': 0.0,
                    'min': 0.0,
                    'max': 0.0,
                    'count': 0
                }
            
            # Calculate dimension statistics
            dimensions = [
                'autonomy_integration_score',
                'multi_scale_score',
                'regenerative_impact_score',
                'network_contribution_score',
                'ubuntu_alignment_score'
            ]
            
            dimension_stats = {}
            for dim in dimensions:
                dim_scores = [float(a[dim]) for a in accounts if a.get(dim) is not None]
                if dim_scores:
                    dimension_stats[dim] = {
                        'mean': float(sum(dim_scores) / len(dim_scores)),
                        'min': float(min(dim_scores)),
                        'max': float(max(dim_scores))
                    }
            
            # Cache the data
            self.report_data = {
                'accounts': accounts,
                'categories': categories,
                'statistics': statistics,
                'dimension_stats': dimension_stats,
                'evaluated_count': len(accounts)
            }
            
            return self.report_data
            
        except Exception as e:
            self.logger.error(f"Error loading evaluation data: {e}", exc_info=True)
            return {
                'accounts': [],
                'categories': {},
                'statistics': {},
                'dimension_stats': {},
                'evaluated_count': 0
            }
    
    # ═════════════════════════════════════════════════════════════════════════
    # Chart Generation Methods
    # ═════════════════════════════════════════════════════════════════════════
    
    def _save_or_encode_figure(
        self,
        fig,
        output_file: Optional[str] = None,
        chart_name: str = 'chart'
    ) -> Optional[str]:
        """
        Save figure to file or encode as base64.
        
        Helper method to handle figure output - either saves to file or returns
        base64-encoded string for embedding in HTML.
        
        Principle #10: Separation of concerns - output logic isolated.
        Principle #12: Method singularity - single implementation for all charts.
        
        Args:
            fig: Matplotlib figure object
            output_file: Optional path to save file (if None, returns base64)
            chart_name: Name for logging purposes
        
        Returns:
            str: File path if output_file specified, else base64 data URI
            None: If generation fails
        """
        if not MATPLOTLIB_AVAILABLE:
            self.logger.warning(f"Cannot save {chart_name}: matplotlib not available")
            return None
        
        try:
            if output_file:
                # Save to file
                fig.savefig(output_file, dpi=150, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
                plt.close(fig)
                self._charts_generated += 1
                self.logger.info(f"✓ {chart_name} saved to: {output_file}")
                return output_file
            else:
                # Encode as base64
                buffer = io.BytesIO()
                fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                           facecolor='white', edgecolor='none')
                buffer.seek(0)
                img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                plt.close(fig)
                buffer.close()
                self._charts_generated += 1
                return f"data:image/png;base64,{img_base64}"
                
        except Exception as e:
            self.logger.error(f"Failed to save/encode {chart_name}: {e}")
            plt.close(fig)
            return None
    
    async def create_score_distribution_chart(
        self,
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """
        Create score distribution histogram chart.
        
        Visualizes the distribution of composite scores across all evaluated
        accounts using the Ubuntu color palette.
        
        Principle #5: Async operation (data loading).
        Principle #10: Separation of concerns - chart logic isolated.
        
        Args:
            output_file: Optional path to save chart (if None, returns base64)
        
        Returns:
            str: File path or base64 data URI, None if generation fails
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            self.logger.warning("Score distribution chart requires matplotlib and numpy")
            return None
        
        try:
            # Load data if not cached
            if not self.report_data:
                await self.load_evaluation_data()
            
            if not self.report_data or self.report_data['evaluated_count'] == 0:
                self.logger.warning("No data available for score distribution chart")
                return None
            
            # Extract scores
            scores = [float(a['composite_score']) for a in self.report_data['accounts'] 
                     if a.get('composite_score') is not None]
            
            if not scores:
                return None
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create histogram
            n, bins, patches = ax.hist(
                scores, 
                bins=20, 
                edgecolor='white',
                linewidth=0.5,
                color=UBUNTU_COLORS['accents']['growth']
            )
            
            # Color bars by category thresholds
            for i, patch in enumerate(patches):
                bin_center = (bins[i] + bins[i+1]) / 2
                if bin_center >= 0.8:
                    patch.set_facecolor(UBUNTU_COLORS['categories']['Exemplar'])
                elif bin_center >= 0.6:
                    patch.set_facecolor(UBUNTU_COLORS['categories']['Integrator'])
                elif bin_center >= 0.4:
                    patch.set_facecolor(UBUNTU_COLORS['categories']['Contributor'])
                elif bin_center >= 0.2:
                    patch.set_facecolor(UBUNTU_COLORS['categories']['Participant'])
                else:
                    patch.set_facecolor(UBUNTU_COLORS['categories']['Observer'])
            
            # Add statistics lines
            mean_score = self.report_data['statistics'].get('mean', 0)
            ax.axvline(mean_score, color=UBUNTU_COLORS['accents']['wisdom'], 
                      linestyle='--', linewidth=2, label=f'Mean: {mean_score:.2f}')
            
            # Styling
            ax.set_xlabel('Composite Score', fontsize=12)
            ax.set_ylabel('Number of Accounts', fontsize=12)
            ax.set_title('UBEC Holonic Score Distribution', fontsize=14, fontweight='bold',
                        color=UBUNTU_COLORS['accents']['wisdom'])
            ax.legend(loc='upper right')
            ax.set_facecolor(UBUNTU_COLORS['neutral']['background'])
            ax.grid(True, alpha=0.3, color=UBUNTU_COLORS['neutral']['grid'])
            
            # Add category legend
            legend_patches = [
                mpatches.Patch(color=UBUNTU_COLORS['categories']['Exemplar'], label='Exemplar (≥0.8)'),
                mpatches.Patch(color=UBUNTU_COLORS['categories']['Integrator'], label='Integrator (0.6-0.8)'),
                mpatches.Patch(color=UBUNTU_COLORS['categories']['Contributor'], label='Contributor (0.4-0.6)'),
                mpatches.Patch(color=UBUNTU_COLORS['categories']['Participant'], label='Participant (0.2-0.4)'),
                mpatches.Patch(color=UBUNTU_COLORS['categories']['Observer'], label='Observer (<0.2)')
            ]
            ax.legend(handles=legend_patches, loc='upper left', fontsize=8)
            
            fig.tight_layout()
            
            return self._save_or_encode_figure(fig, output_file, 'score_distribution_chart')
            
        except Exception as e:
            self.logger.error(f"Failed to create score distribution chart: {e}", exc_info=True)
            return None
    
    async def create_radar_chart(
        self,
        output_file: Optional[str] = None,
        top_n: int = 5
    ) -> Optional[str]:
        """
        Create radar chart showing dimension scores for top accounts.
        
        Visualizes the five holonic dimensions for the highest-scoring accounts
        using the Ubuntu color palette.
        
        Principle #5: Async operation (data loading).
        Principle #10: Separation of concerns - chart logic isolated.
        
        Args:
            output_file: Optional path to save chart (if None, returns base64)
            top_n: Number of top accounts to display (default: 5)
        
        Returns:
            str: File path or base64 data URI, None if generation fails
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            self.logger.warning("Radar chart requires matplotlib and numpy")
            return None
        
        try:
            # Load data if not cached
            if not self.report_data:
                await self.load_evaluation_data()
            
            if not self.report_data or self.report_data['evaluated_count'] == 0:
                self.logger.warning("No data available for radar chart")
                return None
            
            # Get top accounts
            accounts = self.report_data['accounts'][:top_n]
            
            if not accounts:
                return None
            
            # Define dimensions
            dimensions = [
                'autonomy_integration_score',
                'multi_scale_score',
                'regenerative_impact_score',
                'network_contribution_score',
                'ubuntu_alignment_score'
            ]
            
            dimension_labels = [
                'Autonomy\nIntegration',
                'Multi-Scale\nParticipation',
                'Regenerative\nImpact',
                'Network\nContribution',
                'Ubuntu\nAlignment'
            ]
            
            # Calculate angles for radar chart
            num_dims = len(dimensions)
            angles = np.linspace(0, 2 * np.pi, num_dims, endpoint=False).tolist()
            angles += angles[:1]  # Complete the circle
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
            
            # Colors for each account
            colors = list(UBUNTU_COLORS['categories'].values())
            
            # Plot each account
            for idx, account in enumerate(accounts):
                values = [float(account.get(dim, 0) or 0) for dim in dimensions]
                values += values[:1]  # Complete the circle
                
                color = colors[idx % len(colors)]
                account_id = account['account_id'][:8] + '...'
                
                ax.plot(angles, values, 'o-', linewidth=2, color=color, label=account_id)
                ax.fill(angles, values, alpha=0.25, color=color)
            
            # Set labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(dimension_labels, fontsize=10)
            
            # Styling
            ax.set_ylim(0, 1)
            ax.set_title(f'Top {len(accounts)} Accounts - Dimension Scores', 
                        fontsize=14, fontweight='bold', y=1.08,
                        color=UBUNTU_COLORS['accents']['wisdom'])
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=9)
            ax.grid(True, alpha=0.3, color=UBUNTU_COLORS['neutral']['grid'])
            
            fig.tight_layout()
            
            return self._save_or_encode_figure(fig, output_file, 'radar_chart')
            
        except Exception as e:
            self.logger.error(f"Failed to create radar chart: {e}", exc_info=True)
            return None
    
    async def create_category_distribution_chart(
        self,
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """
        Create pie chart showing category distribution.
        
        Visualizes the distribution of accounts across holonic categories
        using the Ubuntu color palette.
        
        Principle #5: Async operation (data loading).
        Principle #10: Separation of concerns - chart logic isolated.
        
        Args:
            output_file: Optional path to save chart (if None, returns base64)
        
        Returns:
            str: File path or base64 data URI, None if generation fails
        """
        if not MATPLOTLIB_AVAILABLE:
            self.logger.warning("Category distribution chart requires matplotlib")
            return None
        
        try:
            # Load data if not cached
            if not self.report_data:
                await self.load_evaluation_data()
            
            if not self.report_data or not self.report_data['categories']:
                self.logger.warning("No category data available for chart")
                return None
            
            categories = self.report_data['categories']
            
            # Sort by count
            sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            labels = [cat for cat, _ in sorted_cats]
            sizes = [count for _, count in sorted_cats]
            colors = [UBUNTU_COLORS['categories'].get(cat, UBUNTU_COLORS['neutral']['grid']) 
                     for cat in labels]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                explode=[0.02] * len(labels),
                shadow=False,
                wedgeprops={'linewidth': 2, 'edgecolor': 'white'}
            )
            
            # Style the text
            for text in texts:
                text.set_fontsize(11)
                text.set_fontweight('bold')
            
            for autotext in autotexts:
                autotext.set_fontsize(10)
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            # Add title
            ax.set_title('Holonic Category Distribution', fontsize=14, fontweight='bold',
                        color=UBUNTU_COLORS['accents']['wisdom'], pad=20)
            
            # Add count legend
            legend_labels = [f'{cat}: {count} accounts' for cat, count in sorted_cats]
            ax.legend(wedges, legend_labels, title="Categories", loc="center left",
                     bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)
            
            fig.tight_layout()
            
            return self._save_or_encode_figure(fig, output_file, 'category_distribution_chart')
            
        except Exception as e:
            self.logger.error(f"Failed to create category distribution chart: {e}", exc_info=True)
            return None

    async def load_time_series_data(
        self,
        days: int = 30,
        account_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Load time-series evaluation data for trend analysis.
        
        Principle #4: Database is single source of truth (explicit schema).
        Principle #5: Async database operation.
        
        Args:
            days: Number of days of history to load (default: 30)
            account_id: Optional specific account to load (loads all if None)
        
        Returns:
            List of evaluation records ordered by date
        """
        try:
            # Build query with explicit schema name
            if account_id:
                query = f"""
                    SELECT 
                        account_id,
                        evaluation_date,
                        autonomy_integration_score,
                        multi_scale_score,
                        regenerative_impact_score,
                        network_contribution_score,
                        ubuntu_alignment_score,
                        composite_score,
                        holonic_category
                    FROM {self.db_schema}.holonic_metrics
                    WHERE account_id = $1
                    AND evaluation_date >= NOW() - INTERVAL '{int(days)} days'
                    ORDER BY evaluation_date ASC
                """
                results = await self.db_manager.fetch_all(query, (account_id,))
            else:
                query = f"""
                    SELECT 
                        account_id,
                        evaluation_date,
                        autonomy_integration_score,
                        multi_scale_score,
                        regenerative_impact_score,
                        network_contribution_score,
                        ubuntu_alignment_score,
                        composite_score,
                        holonic_category
                    FROM {self.db_schema}.holonic_metrics
                    WHERE evaluation_date >= NOW() - INTERVAL '{int(days)} days'
                    ORDER BY evaluation_date ASC
                """
                results = await self.db_manager.fetch_all(query, ())
            
            if results:
                self.time_series_data = [dict(row) for row in results]
                self.logger.info(f"Loaded {len(self.time_series_data)} time-series records ({days} days)")
                return self.time_series_data
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error loading time-series data: {e}", exc_info=True)
            return []

    async def load_network_data(
        self,
        min_transaction_count: int = 5
    ) -> Dict[str, Any]:
        """
        Load transaction network data for network visualization.
        
        Principle #4: Database is single source of truth (explicit schema).
        Principle #5: Async database operation.
        
        Args:
            min_transaction_count: Minimum transactions to include an edge
        
        Returns:
            Dict with nodes and edges for network graph
        """
        try:
            if not self.transactions_table_available:
                self.logger.warning("Transaction table not available for network visualization")
                return {'nodes': [], 'edges': []}
            
            # Load nodes (accounts with their scores)
            nodes_query = f"""
                SELECT DISTINCT ON (account_id)
                    account_id,
                    composite_score,
                    holonic_category
                FROM {self.db_schema}.holonic_metrics
                ORDER BY account_id, evaluation_date DESC
            """
            nodes_result = await self.db_manager.fetch_all(nodes_query, ())
            
            # Load edges (transactions between accounts)
            # CORRECT COLUMN NAMES: from_account and to_account (NOT source_account/destination_account)
            # Verified from current_ubec_comprehensive_database_documentation_20251129_120721.md
            edges_query = f"""
                SELECT 
                    from_account as source,
                    to_account as target,
                    COUNT(*) as weight,
                    SUM(amount) as total_amount
                FROM {self.db_schema}.stellar_operations
                WHERE type IN ('payment', 'path_payment_strict_receive', 'path_payment_strict_send')
                AND from_account IS NOT NULL
                AND to_account IS NOT NULL
                GROUP BY from_account, to_account
                HAVING COUNT(*) >= $1
            """
            edges_result = await self.db_manager.fetch_all(edges_query, (min_transaction_count,))
            
            network_data = {
                'nodes': [dict(row) for row in nodes_result] if nodes_result else [],
                'edges': [dict(row) for row in edges_result] if edges_result else []
            }
            
            self.logger.info(
                f"Loaded network data: {len(network_data['nodes'])} nodes, "
                f"{len(network_data['edges'])} edges"
            )
            
            return network_data
            
        except Exception as e:
            self.logger.error(f"Error loading network data: {e}", exc_info=True)
            return {'nodes': [], 'edges': []}

    async def create_time_series_chart(
        self,
        output_file: Optional[str] = None,
        days: int = 30,
        metric: str = 'composite_score'
    ) -> Optional[str]:
        """
        Create time-series trend chart showing metric evolution over time.
        
        Visualizes daily averages with confidence intervals and trend line.
        
        Principle #5: Async operation (data loading).
        Principle #10: Separation of concerns - chart logic isolated.
        
        Args:
            output_file: Optional path to save chart (if None, returns base64)
            days: Number of days to display (default: 30)
            metric: Metric to visualize (default: composite_score)
        
        Returns:
            str: File path or base64 data URI, None if generation fails
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            self.logger.warning("Time-series chart requires matplotlib and numpy")
            return None
        
        try:
            # Load time-series data
            data = await self.load_time_series_data(days=days)
            
            if not data:
                self.logger.warning("No time-series data available")
                return None
            
            # Group by date and calculate daily statistics
            daily_data = {}
            for record in data:
                date = record['evaluation_date'].date() if hasattr(record['evaluation_date'], 'date') else record['evaluation_date']
                if date not in daily_data:
                    daily_data[date] = []
                value = float(record.get(metric, 0) or 0)
                if value > 0:
                    daily_data[date].append(value)
            
            if not daily_data:
                self.logger.warning(f"No data for metric: {metric}")
                return None
            
            # Calculate statistics per day
            dates = sorted(daily_data.keys())
            means = [np.mean(daily_data[d]) for d in dates]
            stds = [np.std(daily_data[d]) if len(daily_data[d]) > 1 else 0 for d in dates]
            mins = [np.min(daily_data[d]) for d in dates]
            maxs = [np.max(daily_data[d]) for d in dates]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot mean line
            ax.plot(dates, means, color=UBUNTU_COLORS['accents']['wisdom'], 
                   linewidth=2, label='Daily Average', marker='o', markersize=4)
            
            # Plot confidence interval (±1 std)
            ax.fill_between(dates, 
                           [m - s for m, s in zip(means, stds)],
                           [m + s for m, s in zip(means, stds)],
                           alpha=0.3, color=UBUNTU_COLORS['accents']['growth'],
                           label='±1 Std Dev')
            
            # Plot min-max range
            ax.fill_between(dates, mins, maxs, alpha=0.1, 
                           color=UBUNTU_COLORS['accents']['community'],
                           label='Min-Max Range')
            
            # Add trend line
            if len(dates) > 1:
                x_numeric = np.arange(len(dates))
                z = np.polyfit(x_numeric, means, 1)
                p = np.poly1d(z)
                ax.plot(dates, p(x_numeric), '--', color=UBUNTU_COLORS['categories']['Exemplar'],
                       linewidth=2, label=f'Trend (slope: {z[0]:.4f})')
            
            # Styling
            metric_label = metric.replace('_', ' ').title()
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel(metric_label, fontsize=12)
            ax.set_title(f'UBEC {metric_label} - {days} Day Trend', fontsize=14, 
                        fontweight='bold', color=UBUNTU_COLORS['accents']['wisdom'])
            ax.legend(loc='upper left')
            ax.grid(True, alpha=0.3, color=UBUNTU_COLORS['neutral']['grid'])
            ax.set_facecolor(UBUNTU_COLORS['neutral']['background'])
            
            # Rotate x-axis labels
            plt.xticks(rotation=45, ha='right')
            fig.tight_layout()
            
            return self._save_or_encode_figure(fig, output_file, 'time_series_chart')
            
        except Exception as e:
            self.logger.error(f"Failed to create time-series chart: {e}", exc_info=True)
            return None

    async def create_correlation_matrix(
        self,
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """
        Create correlation matrix heatmap for holonic dimensions.
        
        Shows statistical relationships between the five holonic dimensions.
        
        Principle #5: Async operation (data loading).
        Principle #10: Separation of concerns - chart logic isolated.
        
        Args:
            output_file: Optional path to save chart (if None, returns base64)
        
        Returns:
            str: File path or base64 data URI, None if generation fails
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            self.logger.warning("Correlation matrix requires matplotlib and numpy")
            return None
        
        try:
            # Load data if not cached
            if not self.report_data:
                await self.load_evaluation_data()
            
            if not self.report_data or self.report_data['evaluated_count'] < 2:
                self.logger.warning("Insufficient data for correlation matrix (need at least 2 accounts)")
                return None
            
            # Extract dimension scores
            dimensions = [
                'autonomy_integration_score',
                'multi_scale_score',
                'regenerative_impact_score',
                'network_contribution_score',
                'ubuntu_alignment_score'
            ]
            
            dimension_labels = [
                'Autonomy\nIntegration',
                'Multi-Scale',
                'Regenerative\nImpact',
                'Network\nContribution',
                'Ubuntu\nAlignment'
            ]
            
            # Build data matrix
            data_matrix = []
            for account in self.report_data['accounts']:
                row = [float(account.get(dim, 0) or 0) for dim in dimensions]
                if all(v > 0 for v in row):  # Only include complete records
                    data_matrix.append(row)
            
            if len(data_matrix) < 2:
                self.logger.warning("Insufficient complete records for correlation")
                return None
            
            # Calculate correlation matrix
            data_array = np.array(data_matrix)
            corr_matrix = np.corrcoef(data_array.T)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create heatmap
            im = ax.imshow(corr_matrix, cmap='RdYlGn', vmin=-1, vmax=1, aspect='auto')
            
            # Add colorbar
            cbar = fig.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label('Correlation Coefficient', fontsize=11)
            
            # Set ticks and labels
            ax.set_xticks(np.arange(len(dimension_labels)))
            ax.set_yticks(np.arange(len(dimension_labels)))
            ax.set_xticklabels(dimension_labels, fontsize=10)
            ax.set_yticklabels(dimension_labels, fontsize=10)
            
            # Rotate x-axis labels
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
            
            # Add correlation values as text
            for i in range(len(dimension_labels)):
                for j in range(len(dimension_labels)):
                    value = corr_matrix[i, j]
                    text_color = 'white' if abs(value) > 0.5 else 'black'
                    ax.text(j, i, f'{value:.2f}', ha='center', va='center', 
                           color=text_color, fontsize=11, fontweight='bold')
            
            ax.set_title('Holonic Dimension Correlation Matrix', fontsize=14, 
                        fontweight='bold', color=UBUNTU_COLORS['accents']['wisdom'], pad=15)
            
            fig.tight_layout()
            
            return self._save_or_encode_figure(fig, output_file, 'correlation_matrix')
            
        except Exception as e:
            self.logger.error(f"Failed to create correlation matrix: {e}", exc_info=True)
            return None

    async def create_comparative_analysis_chart(
        self,
        output_file: Optional[str] = None,
        categories: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Create comparative analysis chart showing category performance across dimensions.
        
        Generates grouped bar chart comparing categories side-by-side.
        
        Principle #5: Async operation (data loading).
        Principle #10: Separation of concerns - chart logic isolated.
        
        Args:
            output_file: Optional path to save chart (if None, returns base64)
            categories: Optional list of categories to compare (uses all if None)
        
        Returns:
            str: File path or base64 data URI, None if generation fails
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            self.logger.warning("Comparative analysis requires matplotlib and numpy")
            return None
        
        try:
            # Load data if not cached
            if not self.report_data:
                await self.load_evaluation_data()
            
            if not self.report_data or not self.report_data['categories']:
                self.logger.warning("No category data available for comparison")
                return None
            
            dimensions = [
                'autonomy_integration_score',
                'multi_scale_score',
                'regenerative_impact_score',
                'network_contribution_score',
                'ubuntu_alignment_score'
            ]
            
            dimension_labels = ['Autonomy', 'Multi-Scale', 'Regenerative', 'Network', 'Ubuntu']
            
            # Filter categories if specified
            if categories:
                cat_list = [c for c in categories if c in self.report_data['categories']]
            else:
                cat_list = list(self.report_data['categories'].keys())
            
            if not cat_list:
                self.logger.warning("No matching categories found")
                return None
            
            # Calculate average scores per category per dimension
            category_scores = {cat: {dim: [] for dim in dimensions} for cat in cat_list}
            
            for account in self.report_data['accounts']:
                cat = account.get('holonic_category')
                if cat in cat_list:
                    for dim in dimensions:
                        val = float(account.get(dim, 0) or 0)
                        if val > 0:
                            category_scores[cat][dim].append(val)
            
            # Calculate means
            category_means = {}
            for cat in cat_list:
                category_means[cat] = [
                    np.mean(category_scores[cat][dim]) if category_scores[cat][dim] else 0
                    for dim in dimensions
                ]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(14, 8))
            
            x = np.arange(len(dimension_labels))
            width = 0.8 / len(cat_list)
            
            # Plot bars for each category
            for i, cat in enumerate(cat_list):
                offset = (i - len(cat_list)/2 + 0.5) * width
                color = UBUNTU_COLORS['categories'].get(cat, UBUNTU_COLORS['neutral']['grid'])
                bars = ax.bar(x + offset, category_means[cat], width, label=cat, color=color)
                
                # Add value labels on bars
                for bar, val in zip(bars, category_means[cat]):
                    if val > 0:
                        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                               f'{val:.2f}', ha='center', va='bottom', fontsize=8)
            
            # Styling
            ax.set_xlabel('Holonic Dimension', fontsize=12)
            ax.set_ylabel('Average Score', fontsize=12)
            ax.set_title('Category Performance Comparison', fontsize=14, 
                        fontweight='bold', color=UBUNTU_COLORS['accents']['wisdom'])
            ax.set_xticks(x)
            ax.set_xticklabels(dimension_labels, fontsize=11)
            ax.legend(loc='upper right', fontsize=10)
            ax.set_ylim(0, 1.1)
            ax.grid(True, alpha=0.3, axis='y', color=UBUNTU_COLORS['neutral']['grid'])
            ax.set_facecolor(UBUNTU_COLORS['neutral']['background'])
            
            fig.tight_layout()
            
            return self._save_or_encode_figure(fig, output_file, 'comparative_analysis_chart')
            
        except Exception as e:
            self.logger.error(f"Failed to create comparative analysis chart: {e}", exc_info=True)
            return None

    async def create_network_visualization(
        self,
        output_file: Optional[str] = None,
        min_transaction_count: int = 5,
        max_nodes: int = 100
    ) -> Optional[str]:
        """
        Create network visualization of transaction relationships.
        
        Shows accounts as nodes (sized by composite score) connected by
        transaction edges (weighted by transaction count).
        
        Principle #5: Async operation (data loading).
        Principle #10: Separation of concerns - chart logic isolated.
        
        Args:
            output_file: Optional path to save chart (if None, returns base64)
            min_transaction_count: Minimum transactions to include edge
            max_nodes: Maximum nodes to display
        
        Returns:
            str: File path or base64 data URI, None if generation fails
        """
        if not MATPLOTLIB_AVAILABLE:
            self.logger.warning("Network visualization requires matplotlib")
            return None
        
        if not NETWORKX_AVAILABLE:
            self.logger.warning("Network visualization requires networkx (pip install networkx)")
            return None
        
        try:
            # Load network data
            network_data = await self.load_network_data(min_transaction_count)
            
            if not network_data['nodes'] or not network_data['edges']:
                self.logger.warning("Insufficient network data for visualization")
                return None
            
            # Create NetworkX graph
            G = nx.DiGraph()
            
            # Add nodes with attributes
            node_scores = {}
            node_categories = {}
            for node in network_data['nodes'][:max_nodes]:
                account_id = node['account_id']
                G.add_node(account_id)
                node_scores[account_id] = float(node.get('composite_score', 0) or 0)
                node_categories[account_id] = node.get('holonic_category', 'Observer')
            
            # Add edges
            valid_nodes = set(G.nodes())
            for edge in network_data['edges']:
                source = edge['source']
                target = edge['target']
                if source in valid_nodes and target in valid_nodes:
                    G.add_edge(source, target, weight=edge['weight'])
            
            if len(G.edges()) == 0:
                self.logger.warning("No valid edges in network after filtering")
                return None
            
            # Create figure
            fig, ax = plt.subplots(figsize=(14, 12))
            
            # Calculate layout
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
            
            # Node sizes based on composite score
            node_sizes = [300 + node_scores.get(n, 0) * 700 for n in G.nodes()]
            
            # Node colors based on category
            node_colors = [
                UBUNTU_COLORS['categories'].get(node_categories.get(n, 'Observer'), 
                                                UBUNTU_COLORS['neutral']['grid'])
                for n in G.nodes()
            ]
            
            # Edge widths based on weight
            edge_weights = [G[u][v].get('weight', 1) for u, v in G.edges()]
            max_weight = max(edge_weights) if edge_weights else 1
            edge_widths = [0.5 + (w / max_weight) * 3 for w in edge_weights]
            
            # Draw network
            nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.4, 
                                   width=edge_widths,
                                   edge_color=UBUNTU_COLORS['neutral']['connection'],
                                   arrows=True, arrowsize=10)
            
            nx.draw_networkx_nodes(G, pos, ax=ax, 
                                   node_size=node_sizes,
                                   node_color=node_colors,
                                   alpha=0.8,
                                   edgecolors='white',
                                   linewidths=2)
            
            # Add labels for larger nodes only
            labels = {n: n[:8] + '...' for n in G.nodes() if node_scores.get(n, 0) > 0.5}
            nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=8)
            
            # Add legend
            legend_patches = [
                mpatches.Patch(color=UBUNTU_COLORS['categories'][cat], label=cat)
                for cat in UBUNTU_COLORS['categories'].keys()
            ]
            ax.legend(handles=legend_patches, loc='upper left', fontsize=9)
            
            # Styling
            ax.set_title(f'UBEC Transaction Network ({len(G.nodes())} accounts, {len(G.edges())} connections)',
                        fontsize=14, fontweight='bold', color=UBUNTU_COLORS['accents']['wisdom'])
            ax.set_facecolor(UBUNTU_COLORS['neutral']['background'])
            ax.axis('off')
            
            fig.tight_layout()
            
            return self._save_or_encode_figure(fig, output_file, 'network_visualization')
            
        except Exception as e:
            self.logger.error(f"Failed to create network visualization: {e}", exc_info=True)
            return None

    async def create_account_detail_view(
        self,
        account_id: str,
        output_file: Optional[str] = None,
        days: int = 90
    ) -> Optional[str]:
        """
        Create detailed dashboard view for a specific account.
        
        Multi-panel visualization showing account history, dimension scores,
        and current performance.
        
        Principle #5: Async operation (data loading).
        Principle #10: Separation of concerns - chart logic isolated.
        
        Args:
            account_id: Account to visualize
            output_file: Optional path to save chart (if None, returns base64)
            days: Days of history to include (default: 90)
        
        Returns:
            str: File path or base64 data URI, None if generation fails
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            self.logger.warning("Account detail view requires matplotlib and numpy")
            return None
        
        try:
            # Load account history
            history = await self.load_time_series_data(days=days, account_id=account_id)
            
            if not history:
                self.logger.warning(f"No history found for account: {account_id}")
                return None
            
            # Get latest evaluation
            latest = history[-1]
            
            dimensions = [
                'autonomy_integration_score',
                'multi_scale_score',
                'regenerative_impact_score',
                'network_contribution_score',
                'ubuntu_alignment_score'
            ]
            
            dimension_labels = ['Autonomy', 'Multi-Scale', 'Regenerative', 'Network', 'Ubuntu']
            
            # Create figure with subplots
            fig = plt.figure(figsize=(16, 12))
            gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
            
            # Panel 1: Score History (top-left)
            ax1 = fig.add_subplot(gs[0, 0])
            dates = [r['evaluation_date'] for r in history]
            scores = [float(r.get('composite_score', 0) or 0) for r in history]
            
            ax1.plot(dates, scores, color=UBUNTU_COLORS['accents']['wisdom'], 
                    linewidth=2, marker='o', markersize=4)
            ax1.fill_between(dates, scores, alpha=0.3, color=UBUNTU_COLORS['accents']['growth'])
            ax1.set_title('Composite Score History', fontsize=12, fontweight='bold')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Score')
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(0, 1)
            plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
            
            # Panel 2: Current Radar (top-right)
            ax2 = fig.add_subplot(gs[0, 1], polar=True)
            
            values = [float(latest.get(dim, 0) or 0) for dim in dimensions]
            values += values[:1]  # Close the polygon
            
            angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
            angles += angles[:1]
            
            ax2.plot(angles, values, 'o-', linewidth=2, color=UBUNTU_COLORS['accents']['wisdom'])
            ax2.fill(angles, values, alpha=0.25, color=UBUNTU_COLORS['accents']['growth'])
            ax2.set_xticks(angles[:-1])
            ax2.set_xticklabels(dimension_labels, fontsize=9)
            ax2.set_ylim(0, 1)
            ax2.set_title('Current Dimension Profile', fontsize=12, fontweight='bold', y=1.08)
            
            # Panel 3: Dimension Evolution (bottom-left)
            ax3 = fig.add_subplot(gs[1, 0])
            
            for i, (dim, label) in enumerate(zip(dimensions, dimension_labels)):
                dim_values = [float(r.get(dim, 0) or 0) for r in history]
                color = list(UBUNTU_COLORS['categories'].values())[i % 5]
                ax3.plot(dates, dim_values, label=label, linewidth=1.5, color=color)
            
            ax3.set_title('Dimension Score Evolution', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Date')
            ax3.set_ylabel('Score')
            ax3.legend(loc='upper left', fontsize=8)
            ax3.grid(True, alpha=0.3)
            ax3.set_ylim(0, 1)
            plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
            
            # Panel 4: Current Stats (bottom-right)
            ax4 = fig.add_subplot(gs[1, 1])
            ax4.axis('off')
            
            category = latest.get('holonic_category', 'Unknown')
            cat_color = UBUNTU_COLORS['categories'].get(category, UBUNTU_COLORS['neutral']['grid'])
            
            stats_text = f"""
Account Detail Summary
═══════════════════════════════════════

Account ID: {account_id[:20]}...
Category: {category}
Composite Score: {float(latest.get('composite_score', 0) or 0):.3f}

Dimension Scores:
  • Autonomy Integration: {float(latest.get('autonomy_integration_score', 0) or 0):.3f}
  • Multi-Scale: {float(latest.get('multi_scale_score', 0) or 0):.3f}
  • Regenerative Impact: {float(latest.get('regenerative_impact_score', 0) or 0):.3f}
  • Network Contribution: {float(latest.get('network_contribution_score', 0) or 0):.3f}
  • Ubuntu Alignment: {float(latest.get('ubuntu_alignment_score', 0) or 0):.3f}

History: {len(history)} evaluations over {days} days
Latest Evaluation: {latest.get('evaluation_date', 'N/A')}
"""
            
            ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, fontsize=11,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor=f'{cat_color}20', 
                             edgecolor=cat_color, linewidth=2))
            
            # Main title
            fig.suptitle(f'Account Detail View: {account_id[:16]}...', 
                        fontsize=16, fontweight='bold', 
                        color=UBUNTU_COLORS['accents']['wisdom'], y=0.98)
            
            return self._save_or_encode_figure(fig, output_file, 'account_detail_view')
            
        except Exception as e:
            self.logger.error(f"Failed to create account detail view: {e}", exc_info=True)
            return None

    # ═════════════════════════════════════════════════════════════════════════
    # Report Generation Methods
    # ═════════════════════════════════════════════════════════════════════════
    
    async def generate_html_report(
        self,
        output_dir: Optional[str] = None,
        include_advanced: bool = False
    ) -> Optional[str]:
        """
        Generate comprehensive HTML report with holonic evaluation data and embedded charts.
        
        This method is called by the scheduler service to generate periodic reports.
        When include_advanced=True, generates and embeds visualization charts as base64.
        
        Principle #5: Async operation for all I/O.
        Principle #4: Database as single source of truth.
        Principle #10: Clear separation - report generation logic isolated.
        
        Args:
            output_dir: Directory to save report (uses self.output_dir if None)
            include_advanced: Include advanced visualizations (requires matplotlib)
        
        Returns:
            str: Path to generated HTML report file, or None if generation failed
        
        Example:
            >>> report_path = await visualizer.generate_html_report(
            ...     output_dir='./reports',
            ...     include_advanced=True
            ... )
            >>> print(f"Report generated: {report_path}")
        """
        try:
            self.logger.info("Generating HTML report...")
            
            # Determine output directory
            report_dir = Path(output_dir) if output_dir else self.output_dir
            report_dir.mkdir(parents=True, exist_ok=True)
            
            # Load evaluation data if not cached (Principle #5: Async)
            if not self.report_data:
                await self.load_evaluation_data()
            
            # Check if we have data
            if not self.report_data or self.report_data['evaluated_count'] == 0:
                self.logger.warning("No evaluation data available for report generation")
                return None
            
            # Generate charts if include_advanced is True and matplotlib available
            charts = {}
            if include_advanced and MATPLOTLIB_AVAILABLE:
                self.logger.info("Generating embedded charts...")
                
                # Core charts (always generated)
                # Generate score distribution chart
                score_chart = await self.create_score_distribution_chart()
                if score_chart:
                    charts['score_distribution'] = score_chart
                    self.logger.info("  ✓ Score distribution chart generated")
                
                # Generate radar chart
                radar_chart = await self.create_radar_chart(top_n=5)
                if radar_chart:
                    charts['radar'] = radar_chart
                    self.logger.info("  ✓ Radar chart generated")
                
                # Generate category distribution chart
                category_chart = await self.create_category_distribution_chart()
                if category_chart:
                    charts['category_distribution'] = category_chart
                    self.logger.info("  ✓ Category distribution chart generated")
                
                # Advanced charts
                # Time-series trend (30 days)
                time_series_chart = await self.create_time_series_chart(days=30)
                if time_series_chart:
                    charts['time_series'] = time_series_chart
                    self.logger.info("  ✓ Time-series trend chart generated")
                
                # Correlation matrix
                correlation_chart = await self.create_correlation_matrix()
                if correlation_chart:
                    charts['correlation'] = correlation_chart
                    self.logger.info("  ✓ Correlation matrix generated")
                
                # Comparative category analysis
                comparative_chart = await self.create_comparative_analysis_chart()
                if comparative_chart:
                    charts['comparative'] = comparative_chart
                    self.logger.info("  ✓ Comparative analysis chart generated")
                
                # Network visualization (optional - requires networkx)
                if NETWORKX_AVAILABLE and self.transactions_table_available:
                    network_chart = await self.create_network_visualization(max_nodes=50)
                    if network_chart:
                        charts['network'] = network_chart
                        self.logger.info("  ✓ Network visualization generated")
                
                self.logger.info(f"Generated {len(charts)} charts for report")
            
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"holonic_report_{timestamp}.html"
            report_path = report_dir / report_filename
            
            # Build HTML report with charts
            html_content = self._build_html_report(include_advanced, charts)
            
            # Write report to file (using async-compatible approach)
            await asyncio.to_thread(report_path.write_text, html_content, encoding='utf-8')
            
            # Update tracking
            self._charts_generated += 1
            self._last_visualization = datetime.now()
            
            self.logger.info(f"✓ HTML report generated: {report_path}")
            
            return str(report_path)
            
        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {e}", exc_info=True)
            return None
    
    def _build_html_report(self, include_advanced: bool = False, charts: Optional[Dict[str, str]] = None) -> str:
        """
        Build HTML content for the report with embedded charts.
        
        Uses the Dynamic Pastel Earth Tone Color Palette v13.0.0 for consistent
        Ubuntu-inspired visual design throughout the report.
        
        Principle #10: Separation of concerns - HTML building logic isolated.
        Principle #6: No sync fallbacks - graceful degradation if matplotlib unavailable.
        
        Args:
            include_advanced: Include advanced visualizations
            charts: Dictionary of chart names to base64 data URIs
        
        Returns:
            str: Complete HTML content with embedded charts
        """
        data = self.report_data
        charts = charts or {}
        
        # Dynamic Pastel Earth Tone Color Palette v13.0.0
        # Using all palette elements for comprehensive styling
        
        # Build HTML structure with Dynamic Pastel Earth Tone styling
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UBEC Holonic Evaluation Report</title>
    <style>
        /* ═══════════════════════════════════════════════════════════════════
           Dynamic Pastel Earth Tone Color Palette v13.0.0
           Ubuntu-Inspired Design System
           ═══════════════════════════════════════════════════════════════════ */
        
        :root {{
            /* Category Colors */
            --exemplar: {UBUNTU_COLORS['categories']['Exemplar']};
            --integrator: {UBUNTU_COLORS['categories']['Integrator']};
            --contributor: {UBUNTU_COLORS['categories']['Contributor']};
            --participant: {UBUNTU_COLORS['categories']['Participant']};
            --observer: {UBUNTU_COLORS['categories']['Observer']};
            
            /* Element Colors */
            --earth: {UBUNTU_COLORS['elements']['Earth']};
            --water: {UBUNTU_COLORS['elements']['Water']};
            --air: {UBUNTU_COLORS['elements']['Air']};
            --fire: {UBUNTU_COLORS['elements']['Fire']};
            
            /* Accent Colors */
            --accent-growth: {UBUNTU_COLORS['accents']['growth']};
            --accent-wisdom: {UBUNTU_COLORS['accents']['wisdom']};
            --accent-community: {UBUNTU_COLORS['accents']['community']};
            --accent-earth: {UBUNTU_COLORS['accents']['earth']};
            
            /* Neutral Colors */
            --bg-warm-white: {UBUNTU_COLORS['neutral']['background']};
            --text-charcoal: {UBUNTU_COLORS['neutral']['text']};
            --border-soft: {UBUNTU_COLORS['neutral']['border']};
            --grid-medium: {UBUNTU_COLORS['neutral']['grid']};
            --connection-slate: {UBUNTU_COLORS['neutral']['connection']};
        }}
        
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.7;
            color: var(--text-charcoal);
            background: linear-gradient(180deg, var(--bg-warm-white) 0%, #F5F4F2 100%);
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
        }}
        
        /* Header with Earth-to-Sky Gradient */
        .header {{
            background: linear-gradient(135deg, 
                {UBUNTU_COLORS['gradients']['earth_to_sky'][0]} 0%, 
                {UBUNTU_COLORS['gradients']['earth_to_sky'][1]} 50%,
                {UBUNTU_COLORS['gradients']['sage_to_amethyst'][1]} 100%);
            color: white;
            padding: 40px;
            border-radius: 16px;
            margin-bottom: 40px;
            box-shadow: 0 8px 32px rgba(138, 166, 126, 0.3);
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            pointer-events: none;
        }}
        
        .header h1 {{
            margin: 0 0 15px 0;
            font-size: 2.5em;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .header p {{
            margin: 5px 0;
            opacity: 0.95;
            font-size: 1.1em;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            font-weight: 500;
            margin-top: 10px;
            opacity: 0.9;
        }}
        
        /* Section Headers with Accent Colors */
        h2 {{
            color: var(--accent-wisdom);
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 1.6em;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        h2::after {{
            content: '';
            flex: 1;
            height: 2px;
            background: linear-gradient(90deg, var(--accent-earth) 0%, transparent 100%);
            margin-left: 15px;
        }}
        
        /* Statistics Grid */
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin: 25px 0;
        }}
        
        .stat-card {{
            background: white;
            border: 2px solid var(--border-soft);
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--accent-earth), var(--accent-growth));
        }}
        
        .stat-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(138, 166, 126, 0.15);
            border-color: var(--accent-earth);
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-wisdom) 0%, var(--accent-growth) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stat-label {{
            color: var(--grid-medium);
            font-size: 0.95em;
            margin-top: 8px;
            font-weight: 500;
        }}
        
        /* Category List with Dynamic Colors */
        .category-section {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            border: 2px solid var(--border-soft);
        }}
        
        .category-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .category-item {{
            padding: 15px 20px;
            margin: 10px 0;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s ease;
            font-weight: 500;
        }}
        
        .category-item:hover {{
            transform: translateX(5px);
        }}
        
        .category-item.exemplar {{
            background: linear-gradient(90deg, {UBUNTU_COLORS['categories']['Exemplar']}20 0%, {UBUNTU_COLORS['categories']['Exemplar']}10 100%);
            border-left: 5px solid {UBUNTU_COLORS['categories']['Exemplar']};
        }}
        
        .category-item.integrator {{
            background: linear-gradient(90deg, {UBUNTU_COLORS['categories']['Integrator']}20 0%, {UBUNTU_COLORS['categories']['Integrator']}10 100%);
            border-left: 5px solid {UBUNTU_COLORS['categories']['Integrator']};
        }}
        
        .category-item.contributor {{
            background: linear-gradient(90deg, {UBUNTU_COLORS['categories']['Contributor']}20 0%, {UBUNTU_COLORS['categories']['Contributor']}10 100%);
            border-left: 5px solid {UBUNTU_COLORS['categories']['Contributor']};
        }}
        
        .category-item.participant {{
            background: linear-gradient(90deg, {UBUNTU_COLORS['categories']['Participant']}20 0%, {UBUNTU_COLORS['categories']['Participant']}10 100%);
            border-left: 5px solid {UBUNTU_COLORS['categories']['Participant']};
        }}
        
        .category-item.observer {{
            background: linear-gradient(90deg, {UBUNTU_COLORS['categories']['Observer']}20 0%, {UBUNTU_COLORS['categories']['Observer']}10 100%);
            border-left: 5px solid {UBUNTU_COLORS['categories']['Observer']};
        }}
        
        .category-count {{
            background: rgba(255,255,255,0.8);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        
        /* Dimension Statistics with Element Colors */
        .dimension-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .dimension-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border: 2px solid var(--border-soft);
            position: relative;
            overflow: hidden;
        }}
        
        .dimension-card.autonomy {{ border-top: 4px solid {UBUNTU_COLORS['elements']['Air']}; }}
        .dimension-card.multi-scale {{ border-top: 4px solid {UBUNTU_COLORS['elements']['Water']}; }}
        .dimension-card.regenerative {{ border-top: 4px solid {UBUNTU_COLORS['elements']['Earth']}; }}
        .dimension-card.network {{ border-top: 4px solid {UBUNTU_COLORS['elements']['Fire']}; }}
        .dimension-card.ubuntu {{ border-top: 4px solid {UBUNTU_COLORS['accents']['wisdom']}; }}
        
        .dimension-label {{
            font-weight: 600;
            color: var(--text-charcoal);
            font-size: 0.95em;
            margin-bottom: 10px;
        }}
        
        .dimension-value {{
            font-size: 2em;
            font-weight: 700;
            color: var(--accent-growth);
        }}
        
        .dimension-range {{
            font-size: 0.85em;
            color: var(--grid-medium);
            margin-top: 8px;
        }}
        
        /* Chart Containers */
        .chart-section {{
            margin: 40px 0;
        }}
        
        .chart-container {{
            background: white;
            border: 2px solid var(--border-soft);
            border-radius: 16px;
            padding: 25px;
            margin: 20px 0;
            text-align: center;
            box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        }}
        
        .chart-container:hover {{
            box-shadow: 0 8px 32px rgba(138, 166, 126, 0.15);
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }}
        
        .chart-title {{
            font-size: 1.2em;
            font-weight: 600;
            color: var(--accent-wisdom);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--border-soft);
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
            margin: 25px 0;
        }}
        
        /* Advanced Analytics Section */
        .analytics-section {{
            background: linear-gradient(135deg, {UBUNTU_COLORS['categories']['Integrator']}10 0%, {UBUNTU_COLORS['categories']['Contributor']}10 100%);
            border-radius: 16px;
            padding: 30px;
            margin: 40px 0;
            border: 2px solid var(--border-soft);
        }}
        
        .analytics-section h2 {{
            margin-top: 0;
        }}
        
        /* Four Elements Banner */
        .elements-banner {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 30px 0;
        }}
        
        .element-card {{
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            color: white;
            font-weight: 600;
            font-size: 0.9em;
        }}
        
        .element-card.earth {{ background: linear-gradient(135deg, {UBUNTU_COLORS['elements']['Earth']} 0%, #6B8E63 100%); }}
        .element-card.water {{ background: linear-gradient(135deg, {UBUNTU_COLORS['elements']['Water']} 0%, #5BA3C6 100%); }}
        .element-card.air {{ background: linear-gradient(135deg, {UBUNTU_COLORS['elements']['Air']} 0%, #C49FCC 100%); }}
        .element-card.fire {{ background: linear-gradient(135deg, {UBUNTU_COLORS['elements']['Fire']} 0%, #D4896A 100%); }}
        
        /* Footer */
        .footer {{
            margin-top: 60px;
            padding: 30px;
            background: linear-gradient(135deg, var(--accent-earth) 0%, var(--accent-growth) 100%);
            border-radius: 16px;
            color: white;
            text-align: center;
        }}
        
        .footer p {{
            margin: 8px 0;
            opacity: 0.95;
        }}
        
        .footer .version {{
            font-size: 1.1em;
            font-weight: 600;
        }}
        
        .footer .attribution {{
            font-size: 0.85em;
            opacity: 0.85;
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.3);
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            body {{ padding: 15px; }}
            .header {{ padding: 25px; }}
            .header h1 {{ font-size: 1.8em; }}
            .charts-grid {{ grid-template-columns: 1fr; }}
            .elements-banner {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        
        /* Print Styles */
        @media print {{
            body {{ background: white; }}
            .header {{ box-shadow: none; }}
            .stat-card:hover, .chart-container:hover {{ transform: none; box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 UBEC Holonic Evaluation Report</h1>
        <p class="subtitle">Ubuntu Bioregional Economic Commons Protocol Suite</p>
        <p>📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>🗄️ Schema: {self.db_schema}</p>
    </div>
    
    <!-- Four Elements Banner -->
    <div class="elements-banner">
        <div class="element-card earth">🌱 Earth (UBECgpi)<br>Stability</div>
        <div class="element-card water">💧 Water (UBECrc)<br>Reciprocity</div>
        <div class="element-card air">💨 Air (UBEC)<br>Gateway</div>
        <div class="element-card fire">🔥 Fire (UBECtt)<br>Transform</div>
    </div>

    <h2>📊 Summary Statistics</h2>
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-value">{data['evaluated_count']}</div>
            <div class="stat-label">Total Accounts Evaluated</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{data['statistics'].get('mean', 0):.2f}</div>
            <div class="stat-label">Average Composite Score</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{data['statistics'].get('max', 0):.2f}</div>
            <div class="stat-label">Highest Score</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(data['categories'])}</div>
            <div class="stat-label">Active Categories</div>
        </div>
    </div>

    <h2>🎯 Holonic Category Distribution</h2>
    <div class="category-section">
        <ul class="category-list">
"""
        
        # Add category breakdown with proper class names
        for category, count in sorted(data['categories'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / data['evaluated_count'] * 100) if data['evaluated_count'] > 0 else 0
            css_class = category.lower()
            html += f"""            <li class="category-item {css_class}">
                <span><strong>{category}</strong></span>
                <span class="category-count">{count} accounts ({percentage:.1f}%)</span>
            </li>
"""
        
        html += """        </ul>
    </div>

    <h2>📈 Dimension Statistics</h2>
    <div class="dimension-grid">
"""
        
        # Add dimension statistics with element-inspired styling
        dimension_config = [
            ('autonomy_integration_score', 'Autonomy Integration', 'autonomy'),
            ('multi_scale_score', 'Multi-Scale Participation', 'multi-scale'),
            ('regenerative_impact_score', 'Regenerative Impact', 'regenerative'),
            ('network_contribution_score', 'Network Contribution', 'network'),
            ('ubuntu_alignment_score', 'Ubuntu Alignment', 'ubuntu')
        ]
        
        for dim_key, dim_label, css_class in dimension_config:
            if dim_key in data['dimension_stats']:
                dim_data = data['dimension_stats'][dim_key]
                html += f"""        <div class="dimension-card {css_class}">
            <div class="dimension-label">{dim_label}</div>
            <div class="dimension-value">{dim_data['mean']:.2f}</div>
            <div class="dimension-range">Range: {dim_data['min']:.2f} - {dim_data['max']:.2f}</div>
        </div>
"""
        
        html += """    </div>
"""
        
        # Add visualization charts if available
        if charts:
            html += """
    <h2>📊 Core Visualizations</h2>
    <div class="charts-grid">
"""
            
            # Score distribution chart
            if 'score_distribution' in charts:
                html += f"""        <div class="chart-container">
            <div class="chart-title">📊 Score Distribution Histogram</div>
            <img src="{charts['score_distribution']}" alt="Score Distribution Chart">
        </div>
"""
            
            # Category distribution chart
            if 'category_distribution' in charts:
                html += f"""        <div class="chart-container">
            <div class="chart-title">🎯 Category Distribution</div>
            <img src="{charts['category_distribution']}" alt="Category Distribution Chart">
        </div>
"""
            
            html += """    </div>
"""
            
            # Radar chart (full width)
            if 'radar' in charts:
                html += f"""    <div class="chart-container">
        <div class="chart-title">🕸️ Top Accounts - Dimension Scores (Radar Chart)</div>
        <img src="{charts['radar']}" alt="Radar Chart" style="max-width: 800px;">
    </div>
"""
            
            # Advanced Analytics Section
            has_advanced = any(k in charts for k in ['time_series', 'correlation', 'comparative', 'network'])
            if has_advanced:
                html += """
    <div class="analytics-section">
        <h2>📈 Advanced Analytics</h2>
"""
            
                # Time-series trend
                if 'time_series' in charts:
                    html += f"""        <div class="chart-container">
            <div class="chart-title">📈 30-Day Composite Score Trend</div>
            <img src="{charts['time_series']}" alt="Time-Series Trend Chart">
        </div>
"""
                
                # Two-column grid for correlation and comparative
                if 'correlation' in charts or 'comparative' in charts:
                    html += """        <div class="charts-grid">
"""
                    if 'correlation' in charts:
                        html += f"""            <div class="chart-container">
                <div class="chart-title">🔗 Dimension Correlation Matrix</div>
                <img src="{charts['correlation']}" alt="Correlation Matrix">
            </div>
"""
                    if 'comparative' in charts:
                        html += f"""            <div class="chart-container">
                <div class="chart-title">⚖️ Category Performance Comparison</div>
                <img src="{charts['comparative']}" alt="Comparative Analysis Chart">
            </div>
"""
                    html += """        </div>
"""
                
                # Network visualization (full width)
                if 'network' in charts:
                    html += f"""        <div class="chart-container">
            <div class="chart-title">🌐 Transaction Network Visualization</div>
            <img src="{charts['network']}" alt="Network Visualization">
        </div>
"""
                
                html += """    </div>
"""
        
        elif include_advanced and not MATPLOTLIB_AVAILABLE:
            html += """
    <div class="chart-container">
        <div class="chart-title">⚠️ Advanced Visualizations Unavailable</div>
        <p>Matplotlib is not installed. Install it to enable chart generation:</p>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 8px;">pip install matplotlib numpy --break-system-packages</pre>
    </div>
"""
        elif not include_advanced:
            html += """
    <div class="chart-container">
        <div class="chart-title">📊 Visualizations Available</div>
        <p>To generate visual charts, run with the <code>--include-advanced</code> flag:</p>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 8px;">python main.py visualize --action report --include-advanced</pre>
    </div>
"""
        
        # Footer with Ubuntu styling
        html += f"""
    <div class="footer">
        <p class="version">UBEC Protocol Suite - Holonic Visualizer v13.5.0</p>
        <p>Dynamic Pastel Earth Tone Color Palette v13.0.0</p>
        <p class="attribution">
            This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations.<br>
            This project was made possible with the assistance of Claude and Anthropic PBC.
        </p>
    </div>
</body>
</html>
"""
        
        return html
    
    # ═════════════════════════════════════════════════════════════════════════
    # Cleanup Methods
    # ═════════════════════════════════════════════════════════════════════════
    
    async def close(self):
        """
        Clean up visualizer resources.
        
        Principle 5: Async cleanup operation.
        """
        self.logger.info("HolonicVisualizer closing...")
        
        # Clear cached data
        self.report_data = None
        self.time_series_data = None
        
        # Reset state
        self._initialized = False
        self._charts_generated = 0
        self._last_visualization = None
        
        self.logger.info("✓ HolonicVisualizer closed successfully")


# ═════════════════════════════════════════════════════════════════════════════
# Service Factory Function
# ═════════════════════════════════════════════════════════════════════════════

async def create_holonic_visualizer(
    db_manager: Any,
    config: Dict[str, Any],
    logger: Optional[logging.Logger] = None
) -> HolonicVisualizer:
    """
    Factory function to create and initialize HolonicVisualizer instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    Implements Principle #2 (Service Pattern).
    
    Args:
        db_manager: Async database manager from service registry
        config: Configuration dictionary containing:
            - db_schema: Database schema name (required)
            - output_dir: Output directory path (optional)
            - element_mode: Enable four-element features (optional)
        logger: Optional logger instance
    
    Returns:
        Initialized HolonicVisualizer instance
    
    Raises:
        ValueError: If required configuration is missing
        RuntimeError: If initialization fails
    
    Example:
        >>> visualizer = await create_holonic_visualizer(
        ...     db_manager=db,
        ...     config={'db_schema': 'ubec_main'}
        ... )
        >>> health = await visualizer.health_check()
    """
    # Validate required configuration
    if 'db_schema' not in config:
        raise ValueError("Configuration must include 'db_schema'")
    
    # Create visualizer instance
    visualizer = HolonicVisualizer(
        db_manager=db_manager,
        config=config,
        logger=logger
    )
    
    # Initialize the service
    success = await visualizer.initialize()
    
    if not success:
        raise RuntimeError(
            "HolonicVisualizer initialization failed - "
            "check database connectivity and permissions"
        )
    
    return visualizer


# ═════════════════════════════════════════════════════════════════════════════
# Module Exports
# ═════════════════════════════════════════════════════════════════════════════

__all__ = [
    'HolonicVisualizer',
    'create_holonic_visualizer',
    'UBUNTU_COLORS',
    'MATPLOTLIB_AVAILABLE',
    'NUMPY_AVAILABLE',
    'NETWORKX_AVAILABLE'
]


# ═════════════════════════════════════════════════════════════════════════════
# Standalone Execution Prevention
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    raise RuntimeError(
        "This module implements the service pattern and should not be run directly. "
        "Use main.py as the orchestrator.\n\n"
        "Example usage:\n"
        "  from ubec_holonic_visualizer import create_holonic_visualizer\n"
        "  visualizer = await create_holonic_visualizer(db_manager, config)\n"
        "  data = await visualizer.load_evaluation_data()\n"
        "  report = await visualizer.generate_html_report('./reports')\n"
        "  health = await visualizer.health_check()\n"
        "  await visualizer.close()\n\n"
        "Version 13.3.1 - Health Check Fix:\n"
        "  - Fixed health_check() implementation\n"
        "  - Removed non-existent ServiceHealthCheck.database_dependent_health() call\n"
        "  - Direct implementation with proper error handling\n"
        "  - All 12 design principles maintained\n\n"
        "Attribution:\n"
        "  This project uses the services of Claude and Anthropic PBC."
    )
