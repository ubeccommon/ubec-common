#!/usr/bin/env python3
"""
UBEC Protocol Suite - API-Based Visualization Report Generator v2.1.0
======================================================================
Standalone tool to generate holonic evaluation reports by fetching data
from the UBEC API Gateway using the enhanced holonic-scores endpoint.

NEW IN v2.1.0 - ADVANCED ANALYTICS:
- Dimension Correlation Matrix: Shows relationships between dimensions
- Category Performance Comparison: Compares dimensions across categories
- 30-Day Trend Chart: Daily averages with std dev and min/max bands
- Enhanced documentation with analytics guide section

NEW IN v2.0.0 - BACKEND API v2.7.0 INTEGRATION:
- Uses /v1/holonic-scores?include_accounts=true for full dimension data
- Retrieves all 5 holonic dimensions per account (visualization-ready)
- Retrieves all 4 Ubuntu principle scores per account (element-specific)
- Leverages backend statistics (category_distribution, score_statistics)
- Supports pagination for large account sets
- Supports category filtering (Observer, Participant, Contributor, Integrator, Exemplar)

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Self-contained visualization tool
    ✅ #5  Strict Async Operations: ALL I/O operations use async/await
    ✅ #10 Separation of Concerns: API client isolated from visualization
    ✅ #11 Comprehensive Documentation: Full docstrings and attribution
════════════════════════════════════════════════════════════════════════════

Usage:
    python ubec_api_report_generator.py --api-url https://api.ubec.network
    python ubec_api_report_generator.py --api-url https://api.ubec.network --limit 500
    python ubec_api_report_generator.py --api-url https://api.ubec.network --category Contributor

API Endpoints Used (v2.7.0):
    - GET /v1/holonic-scores?include_accounts=true - Full holonic data with dimensions
    - GET /v1/network - Network health metrics
    - GET /v1/token-audit/UBEC - Token distribution data
    - GET /v1/transactions/recent - Recent transaction data

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team with Claude AI assistance
Version: 2.0.0
Date: November 30, 2025
"""

import argparse
import asyncio
import base64
import io
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# HTTP client
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("ERROR: aiohttp is required. Install with: pip install aiohttp --break-system-packages")

# Visualization imports
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.gridspec import GridSpec
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("WARNING: matplotlib not available. Install with: pip install matplotlib --break-system-packages")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("WARNING: numpy not available. Install with: pip install numpy --break-system-packages")

# PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, 
        Table, TableStyle, PageBreak, KeepTogether, Flowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("WARNING: reportlab not available for PDF. Install with: pip install reportlab --break-system-packages")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Dynamic Pastel Earth Tone Color Palette v13.0.0
# ═══════════════════════════════════════════════════════════════════════════════

UBUNTU_COLORS = {
    'categories': {
        'Exemplar': '#B08BBB',      # 🟣 Soft Amethyst
        'Integrator': '#8FBC8F',    # 🟢 Sage Green
        'Contributor': '#87CEEB',   # 🔵 Sky Blue
        'Participant': '#E8A87C',   # 🟠 Soft Terracotta
        'Observer': '#9CB4CC',      # ⚪ Soft Slate
    },
    'elements': {
        'Earth': '#8AA67E',         # 🌍 UBECgpi - Mutualism
        'Water': '#87CEEB',         # 💧 UBECrc - Reciprocity
        'Air': '#D4B5D9',           # 🌬️ UBEC - Diversity
        'Fire': '#E8A87C'           # 🔥 UBECtt - Regeneration
    },
    'dimensions': {
        'autonomy_integration': '#8FBC8F',    # Sage Green
        'multi_scale': '#87CEEB',              # Sky Blue
        'regenerative_impact': '#E8A87C',      # Soft Terracotta
        'network_contribution': '#B08BBB',     # Soft Amethyst
        'ubuntu_alignment': '#8AA67E'          # Earth Green
    },
    'gradients': {
        'earth_to_sky': ['#8AA67E', '#87CEEB'],
        'sage_to_amethyst': ['#8FBC8F', '#B08BBB']
    },
    'accents': {
        'growth': '#8FBC8F',
        'wisdom': '#B08BBB',
        'community': '#E8A87C',
        'earth': '#8AA67E'
    },
    'neutral': {
        'background': '#FAFAF9',
        'text': '#2D3436',
        'border': '#E8E6E3',
        'grid': '#D3D1CE',
        'connection': '#9CB4CC'
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# API Client Class - Updated for v2.7.0
# ═══════════════════════════════════════════════════════════════════════════════

class UBECApiClient:
    """
    Async client for UBEC API Gateway v2.7.0.
    
    Uses the enhanced /v1/holonic-scores?include_accounts=true endpoint
    to fetch full dimension scores for visualization.
    """
    
    def __init__(self, base_url: str, timeout: int = 60):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the UBEC API (e.g., https://api.ubec.network)
            timeout: Request timeout in seconds (increased for large datasets)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_holonic_scores_with_accounts(
        self, 
        limit: int = 100,
        offset: int = 0,
        category: str = None
    ) -> Dict[str, Any]:
        """
        Fetch holonic evaluation data with individual account scores.
        
        NEW IN v2.0.0: Uses include_accounts=true for full dimension data.
        
        Args:
            limit: Maximum accounts to return (1-500)
            offset: Pagination offset
            category: Optional filter by holonic category
            
        Returns:
            Dict containing:
            - accounts: Array with per-account dimension scores
            - summary: Category distribution, score statistics, dimension stats
            - pagination: Limit, offset, total, has_more
        """
        params = {
            "include_accounts": "true",
            "limit": min(max(1, limit), 500),
            "offset": max(0, offset)
        }
        if category:
            params["category"] = category
        
        url = f"{self.base_url}/v1/holonic-scores"
        logger.info(f"Fetching holonic data from: {url} (include_accounts=true, limit={limit})")
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"API error {response.status}: {text[:200]}")
                    return {}
                
                data = await response.json()
                accounts = data.get('accounts', [])
                pagination = data.get('pagination', {})
                logger.info(f"Received {len(accounts)} accounts (total: {pagination.get('total', 'unknown')})")
                return data
                
        except Exception as e:
            logger.error(f"Error fetching holonic data: {e}")
            return {}
    
    async def get_all_holonic_accounts(
        self,
        max_accounts: int = 500,
        category: str = None
    ) -> Dict[str, Any]:
        """
        Fetch all holonic accounts with pagination handling.
        
        Args:
            max_accounts: Maximum total accounts to fetch
            category: Optional filter by holonic category
            
        Returns:
            Combined data from all pages
        """
        all_accounts = []
        offset = 0
        batch_size = min(100, max_accounts)
        summary = {}
        
        while len(all_accounts) < max_accounts:
            data = await self.get_holonic_scores_with_accounts(
                limit=batch_size,
                offset=offset,
                category=category
            )
            
            if not data:
                break
            
            accounts = data.get('accounts', [])
            if not accounts:
                break
            
            all_accounts.extend(accounts)
            summary = data.get('summary', summary)
            
            pagination = data.get('pagination', {})
            if not pagination.get('has_more', False):
                break
            
            offset += len(accounts)
            logger.info(f"Fetched {len(all_accounts)} accounts so far...")
        
        return {
            'accounts': all_accounts[:max_accounts],
            'summary': summary,
            'pagination': {
                'total_fetched': len(all_accounts[:max_accounts]),
                'max_requested': max_accounts
            }
        }
    
    async def get_network_status(self) -> Dict[str, Any]:
        """
        Fetch network status and health metrics.
        
        Note: Uses /v1/network (not /v1/network-status which was removed in v2.6.0)
        
        Returns:
            Dict containing network statistics
        """
        url = f"{self.base_url}/v1/network"
        logger.info(f"Fetching network status from: {url}")
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Network status API error: {response.status}")
                    return {}
                
                data = await response.json()
                return data
        except Exception as e:
            logger.warning(f"Could not fetch network status: {e}")
            return {}
    
    async def get_token_audit(self, token_code: str = "UBEC") -> Dict[str, Any]:
        """
        Fetch comprehensive token audit data.
        
        Args:
            token_code: Token to audit (UBEC, UBECrc, UBECgpi, UBECtt)
            
        Returns:
            Dict containing token audit with supply breakdown
        """
        url = f"{self.base_url}/v1/token-audit/{token_code}"
        logger.info(f"Fetching token audit from: {url}")
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Token audit API error: {response.status}")
                    return {}
                
                data = await response.json()
                return data
        except Exception as e:
            logger.warning(f"Could not fetch token audit: {e}")
            return {}
    
    async def get_recent_transactions(self, limit: int = 50) -> Dict[str, Any]:
        """
        Fetch recent transactions from API.
        
        Args:
            limit: Maximum number of transactions to fetch
            
        Returns:
            Dict containing transactions list
        """
        url = f"{self.base_url}/v1/transactions/recent"
        params = {"limit": limit}
        logger.info(f"Fetching transactions from: {url}")
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"Transactions API error: {response.status}")
                    return {'transactions': []}
                
                data = await response.json()
                logger.info(f"Received {len(data.get('transactions', []))} transactions")
                return data
        except Exception as e:
            logger.warning(f"Could not fetch transactions: {e}")
            return {'transactions': []}


# ═══════════════════════════════════════════════════════════════════════════════
# Visualization Generator Class - Updated for v2.7.0 data structure
# ═══════════════════════════════════════════════════════════════════════════════

class APIVisualizationGenerator:
    """
    Generates visualization charts and HTML reports from API data.
    
    Updated for v2.7.0 to use full dimension scores from
    /v1/holonic-scores?include_accounts=true endpoint.
    """
    
    def __init__(self, output_dir: str = './reports'):
        """
        Initialize visualization generator.
        
        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.charts_generated = 0
    
    async def fetch_holonic_scores(
        self,
        api_url: str,
        limit: int = 100,
        category: str = None
    ) -> Dict[str, Any]:
        """
        Fetch holonic scores from API with pagination.
        
        Args:
            api_url: Base URL of the API
            limit: Maximum accounts to fetch
            category: Optional category filter
            
        Returns:
            API response data with accounts and summary
        """
        if not AIOHTTP_AVAILABLE:
            logger.error("aiohttp not available")
            return {}
        
        async with UBECApiClient(api_url) as client:
            return await client.get_all_holonic_accounts(
                max_accounts=limit,
                category=category
            )
    
    async def fetch_network_status(self, api_url: str) -> Optional[Dict]:
        """Fetch network status from API."""
        if not AIOHTTP_AVAILABLE:
            return None
        
        async with UBECApiClient(api_url) as client:
            return await client.get_network_status()
    
    async def fetch_token_audit(self, api_url: str) -> Optional[Dict]:
        """Fetch token audit data from API."""
        if not AIOHTTP_AVAILABLE:
            return None
        
        async with UBECApiClient(api_url) as client:
            return await client.get_token_audit("UBEC")
        
    def _save_or_encode_figure(self, fig, chart_name: str = 'chart') -> Optional[str]:
        """Encode figure as base64 for HTML embedding."""
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        try:
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)
            buffer.close()
            self.charts_generated += 1
            logger.info(f"  ✓ {chart_name} generated")
            return f"data:image/png;base64,{img_base64}"
        except Exception as e:
            logger.error(f"Failed to encode {chart_name}: {e}")
            plt.close(fig)
            return None
    
    def create_score_distribution_chart(self, accounts: List[Dict]) -> Optional[str]:
        """Create score distribution histogram using composite_score."""
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            return None
        
        scores = []
        for a in accounts:
            score = a.get('composite_score', 0)
            if score:
                scores.append(float(score))
        
        if not scores:
            logger.warning("No composite scores available for distribution chart")
            return None
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        n, bins, patches = ax.hist(scores, bins=20, edgecolor='white', linewidth=0.5)
        
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
        
        mean_score = np.mean(scores)
        median_score = np.median(scores)
        
        ax.axvline(mean_score, color=UBUNTU_COLORS['accents']['wisdom'],
                  linestyle='--', linewidth=2, label=f'Mean: {mean_score:.3f}')
        ax.axvline(median_score, color=UBUNTU_COLORS['accents']['growth'],
                  linestyle=':', linewidth=2, label=f'Median: {median_score:.3f}')
        
        ax.set_xlabel('Composite Score', fontsize=12)
        ax.set_ylabel('Number of Accounts', fontsize=12)
        ax.set_title('UBEC Holonic Score Distribution', fontsize=14, fontweight='bold',
                    color=UBUNTU_COLORS['accents']['wisdom'])
        
        legend_patches = [
            mpatches.Patch(color=UBUNTU_COLORS['categories']['Exemplar'], label='Exemplar (≥0.8)'),
            mpatches.Patch(color=UBUNTU_COLORS['categories']['Integrator'], label='Integrator (0.6-0.8)'),
            mpatches.Patch(color=UBUNTU_COLORS['categories']['Contributor'], label='Contributor (0.4-0.6)'),
            mpatches.Patch(color=UBUNTU_COLORS['categories']['Participant'], label='Participant (0.2-0.4)'),
            mpatches.Patch(color=UBUNTU_COLORS['categories']['Observer'], label='Observer (<0.2)')
        ]
        ax.legend(handles=legend_patches + [
            plt.Line2D([0], [0], color=UBUNTU_COLORS['accents']['wisdom'], linestyle='--', label=f'Mean: {mean_score:.3f}'),
            plt.Line2D([0], [0], color=UBUNTU_COLORS['accents']['growth'], linestyle=':', label=f'Median: {median_score:.3f}')
        ], loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_facecolor(UBUNTU_COLORS['neutral']['background'])
        
        fig.tight_layout()
        return self._save_or_encode_figure(fig, 'score_distribution_chart')
    
    def create_category_distribution_chart(self, summary: Dict) -> Optional[str]:
        """Create category distribution pie chart from API summary."""
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        category_dist = summary.get('category_distribution', {})
        if not category_dist:
            logger.warning("No category distribution data available")
            return None
        
        # Sort by category hierarchy
        category_order = ['Exemplar', 'Integrator', 'Contributor', 'Participant', 'Observer']
        labels = []
        sizes = []
        colors = []
        
        for cat in category_order:
            if cat in category_dist:
                labels.append(cat)
                sizes.append(category_dist[cat])
                colors.append(UBUNTU_COLORS['categories'].get(cat, UBUNTU_COLORS['neutral']['grid']))
        
        if not sizes:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors,
            autopct='%1.1f%%', startangle=90,
            explode=[0.02] * len(labels),
            wedgeprops={'linewidth': 2, 'edgecolor': 'white'}
        )
        
        for text in texts:
            text.set_fontsize(11)
            text.set_fontweight('bold')
        
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Holonic Category Distribution', fontsize=14, fontweight='bold',
                    color=UBUNTU_COLORS['accents']['wisdom'], pad=20)
        
        total = sum(sizes)
        legend_labels = [f'{l}: {s} accounts ({s/total*100:.1f}%)' for l, s in zip(labels, sizes)]
        ax.legend(wedges, legend_labels, title="Categories", loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)
        
        fig.tight_layout()
        return self._save_or_encode_figure(fig, 'category_distribution_chart')
    
    def create_dimension_radar_chart(self, accounts: List[Dict], top_n: int = 12) -> Optional[str]:
        """
        Create radar chart showing 5 holonic dimensions for top accounts.
        
        NEW IN v2.0.0: Uses dimension_scores from include_accounts=true response.
        NEW IN v2.1.0: Increased to 12 accounts with extended color palette.
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            return None
        
        # Sort by composite_score
        sorted_accounts = sorted(accounts, key=lambda a: float(a.get('composite_score', 0)), reverse=True)
        top_accounts = sorted_accounts[:top_n]
        
        if not top_accounts:
            return None
        
        # Check if dimension scores are available (from v2.7.0 include_accounts=true)
        has_dimensions = False
        for account in top_accounts:
            dim_scores = account.get('dimension_scores', {})
            if dim_scores and any(v for v in dim_scores.values() if v):
                has_dimensions = True
                break
        
        if not has_dimensions:
            logger.warning("Radar chart skipped: dimension_scores not in API response")
            logger.info("  Ensure you're using API v2.7.0+ with include_accounts=true")
            return None
        
        # Define the 5 holonic dimensions
        dimensions = ['autonomy_integration', 'multi_scale', 'regenerative_impact', 
                     'network_contribution', 'ubuntu_alignment']
        dimension_labels = ['Autonomy-\nIntegration', 'Multi-Scale', 'Regenerative\nImpact', 
                           'Network\nContribution', 'Ubuntu\nAlignment']
        
        num_dims = len(dimensions)
        angles = np.linspace(0, 2 * np.pi, num_dims, endpoint=False).tolist()
        angles += angles[:1]
        
        # Larger figure for more accounts
        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(polar=True))
        
        # Extended color palette for 12 accounts (distinct colors)
        extended_colors = [
            '#B08BBB',  # Soft Amethyst (Exemplar)
            '#8FBC8F',  # Sage Green (Integrator)
            '#87CEEB',  # Sky Blue (Contributor)
            '#E8A87C',  # Soft Terracotta (Participant)
            '#9CB4CC',  # Soft Slate (Observer)
            '#D4A574',  # Warm Sand
            '#A8D8B9',  # Mint
            '#C9A9D8',  # Lavender
            '#F5C6AA',  # Peach
            '#98C1D9',  # Steel Blue
            '#E6B89C',  # Apricot
            '#B5D8B5',  # Seafoam
        ]
        
        for idx, account in enumerate(top_accounts):
            dim_scores = account.get('dimension_scores', {})
            values = [float(dim_scores.get(dim, 0) or 0) for dim in dimensions]
            values += values[:1]
            
            color = extended_colors[idx % len(extended_colors)]
            account_id = account.get('account_id', 'Unknown')[:10] + '..'
            category = account.get('holonic_category', 'Unknown')[:3]  # Abbreviated
            score = account.get('composite_score', 0)
            
            ax.plot(angles, values, 'o-', linewidth=2, color=color, markersize=4,
                   label=f'{account_id} ({category}, {score:.2f})')
            ax.fill(angles, values, alpha=0.1, color=color)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimension_labels, fontsize=10)
        ax.set_ylim(0, 1)
        ax.set_title(f'Top {len(top_accounts)} Accounts - 5 Holonic Dimensions',
                    fontsize=14, fontweight='bold', y=1.08,
                    color=UBUNTU_COLORS['accents']['wisdom'])
        
        # Legend with smaller font and two columns for 12 accounts
        ax.legend(loc='upper right', bbox_to_anchor=(1.45, 1.0), fontsize=8, ncol=1)
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        return self._save_or_encode_figure(fig, 'dimension_radar_chart')
    
    def create_ubuntu_principles_chart(self, accounts: List[Dict], top_n: int = 12) -> Optional[str]:
        """
        Create radar chart showing 4 Ubuntu principles for top accounts.
        
        NEW IN v2.0.0: Uses ubuntu_principles from include_accounts=true response.
        NEW IN v2.1.0: Increased to 12 accounts with extended color palette.
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            return None
        
        sorted_accounts = sorted(accounts, key=lambda a: float(a.get('composite_score', 0)), reverse=True)
        top_accounts = sorted_accounts[:top_n]
        
        if not top_accounts:
            return None
        
        # Check if ubuntu_principles are available
        has_principles = False
        for account in top_accounts:
            principles = account.get('ubuntu_principles', {})
            if principles and any(v for v in principles.values() if v):
                has_principles = True
                break
        
        if not has_principles:
            logger.warning("Ubuntu principles chart skipped: ubuntu_principles not in API response")
            return None
        
        # Define the 4 Ubuntu principles (elements) - text labels for matplotlib compatibility
        principles = ['diversity', 'reciprocity', 'mutualism', 'regeneration']
        principle_labels = ['Diversity\n(Air/UBEC)', 'Reciprocity\n(Water/UBECrc)', 
                           'Mutualism\n(Earth/UBECgpi)', 'Regeneration\n(Fire/UBECtt)']
        
        num_principles = len(principles)
        angles = np.linspace(0, 2 * np.pi, num_principles, endpoint=False).tolist()
        angles += angles[:1]
        
        # Larger figure for more accounts
        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(polar=True))
        
        # Extended color palette for 12 accounts (distinct colors)
        extended_colors = [
            '#B08BBB',  # Soft Amethyst
            '#8FBC8F',  # Sage Green
            '#87CEEB',  # Sky Blue
            '#E8A87C',  # Soft Terracotta
            '#9CB4CC',  # Soft Slate
            '#D4A574',  # Warm Sand
            '#A8D8B9',  # Mint
            '#C9A9D8',  # Lavender
            '#F5C6AA',  # Peach
            '#98C1D9',  # Steel Blue
            '#E6B89C',  # Apricot
            '#B5D8B5',  # Seafoam
        ]
        
        for idx, account in enumerate(top_accounts):
            ubuntu_principles = account.get('ubuntu_principles', {})
            values = [float(ubuntu_principles.get(p, 0) or 0) for p in principles]
            values += values[:1]
            
            color = extended_colors[idx % len(extended_colors)]
            account_id = account.get('account_id', 'Unknown')[:10] + '..'
            category = account.get('holonic_category', 'Unknown')[:3]
            score = account.get('composite_score', 0)
            
            ax.plot(angles, values, 'o-', linewidth=2, color=color, markersize=4,
                   label=f'{account_id} ({category}, {score:.2f})')
            ax.fill(angles, values, alpha=0.1, color=color)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(principle_labels, fontsize=10)
        ax.set_ylim(0, 1)
        ax.set_title(f'Top {len(top_accounts)} Accounts - 4 Ubuntu Principles',
                    fontsize=14, fontweight='bold', y=1.08,
                    color=UBUNTU_COLORS['accents']['wisdom'])
        ax.legend(loc='upper right', bbox_to_anchor=(1.45, 1.0), fontsize=8, ncol=1)
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        return self._save_or_encode_figure(fig, 'ubuntu_principles_chart')
    
    def create_dimension_statistics_chart(self, summary: Dict) -> Optional[str]:
        """
        Create bar chart showing dimension statistics from API summary.
        
        NEW IN v2.0.0: Uses dimension_statistics from include_accounts=true response.
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            return None
        
        dim_stats = summary.get('dimension_statistics', {})
        if not dim_stats:
            logger.warning("Dimension statistics chart skipped: no dimension_statistics in summary")
            return None
        
        dimensions = ['autonomy_integration', 'multi_scale', 'regenerative_impact',
                     'network_contribution', 'ubuntu_alignment']
        dim_labels = ['Autonomy-\nIntegration', 'Multi-Scale', 'Regenerative\nImpact',
                     'Network\nContribution', 'Ubuntu\nAlignment']
        
        means = []
        mins = []
        maxs = []
        
        for dim in dimensions:
            stats = dim_stats.get(dim, {})
            means.append(float(stats.get('mean', 0) or 0))
            mins.append(float(stats.get('min', 0) or 0))
            maxs.append(float(stats.get('max', 0) or 0))
        
        x = np.arange(len(dimensions))
        width = 0.6
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = [UBUNTU_COLORS['dimensions'].get(dim, UBUNTU_COLORS['neutral']['grid']) 
                 for dim in dimensions]
        
        bars = ax.bar(x, means, width, color=colors, edgecolor='white', linewidth=1)
        
        # Add error bars for min/max range
        for i, (mean, min_val, max_val) in enumerate(zip(means, mins, maxs)):
            ax.plot([i, i], [min_val, max_val], color='gray', linewidth=2, alpha=0.5)
            ax.plot([i-0.1, i+0.1], [min_val, min_val], color='gray', linewidth=2)
            ax.plot([i-0.1, i+0.1], [max_val, max_val], color='gray', linewidth=2)
        
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Network-Wide Dimension Statistics\n(Mean with Min-Max Range)',
                    fontsize=14, fontweight='bold', color=UBUNTU_COLORS['accents']['wisdom'])
        ax.set_xticks(x)
        ax.set_xticklabels(dim_labels, fontsize=10)
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_facecolor(UBUNTU_COLORS['neutral']['background'])
        
        # Add value labels on bars
        for bar, mean in zip(bars, means):
            height = bar.get_height()
            ax.annotate(f'{mean:.3f}',
                       xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        fig.tight_layout()
        return self._save_or_encode_figure(fig, 'dimension_statistics_chart')
    
    def create_top_accounts_chart(self, accounts: List[Dict], top_n: int = 12) -> Optional[str]:
        """Create horizontal bar chart of top accounts by composite score."""
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            return None
        
        sorted_accounts = sorted(accounts, key=lambda a: float(a.get('composite_score', 0)), reverse=True)
        top_accounts = sorted_accounts[:top_n]
        
        if not top_accounts:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        y_positions = np.arange(len(top_accounts))
        scores = [float(a.get('composite_score', 0)) for a in top_accounts]
        categories = [a.get('holonic_category', 'Unknown') for a in top_accounts]
        account_ids = [a.get('account_id', 'Unknown')[:12] + '...' for a in top_accounts]
        
        colors = [UBUNTU_COLORS['categories'].get(cat, UBUNTU_COLORS['neutral']['grid']) 
                 for cat in categories]
        
        bars = ax.barh(y_positions, scores, color=colors, edgecolor='white', linewidth=1)
        
        ax.set_yticks(y_positions)
        ax.set_yticklabels([f'{acc}\n({cat})' for acc, cat in zip(account_ids, categories)], fontsize=9)
        ax.set_xlabel('Composite Score', fontsize=12)
        ax.set_title(f'Top {len(top_accounts)} Accounts by Holonic Score',
                    fontsize=14, fontweight='bold', color=UBUNTU_COLORS['accents']['wisdom'])
        ax.set_xlim(0, 1)
        ax.grid(True, alpha=0.3, axis='x')
        ax.set_facecolor(UBUNTU_COLORS['neutral']['background'])
        ax.invert_yaxis()
        
        # Add value labels
        for bar, score in zip(bars, scores):
            width = bar.get_width()
            ax.annotate(f'{score:.3f}',
                       xy=(width, bar.get_y() + bar.get_height()/2),
                       xytext=(5, 0), textcoords="offset points",
                       ha='left', va='center', fontsize=10, fontweight='bold')
        
        fig.tight_layout()
        return self._save_or_encode_figure(fig, 'top_accounts_chart')
    
    def create_correlation_matrix_chart(self, accounts: List[Dict]) -> Optional[str]:
        """
        Create correlation matrix heatmap showing relationships between dimensions.
        
        Shows how the 5 holonic dimensions correlate with each other across all accounts.
        Strong positive correlations (green/yellow) indicate dimensions that tend to 
        increase together. Negative correlations (red/orange) indicate inverse relationships.
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            return None
        
        # Check if dimension scores are available
        dimensions = ['autonomy_integration', 'multi_scale', 'regenerative_impact',
                     'network_contribution', 'ubuntu_alignment']
        
        # Extract dimension scores into arrays
        dim_data = {dim: [] for dim in dimensions}
        valid_count = 0
        
        for account in accounts:
            dim_scores = account.get('dimension_scores', {})
            if dim_scores and any(dim_scores.get(d) for d in dimensions):
                valid_count += 1
                for dim in dimensions:
                    dim_data[dim].append(float(dim_scores.get(dim, 0) or 0))
        
        if valid_count < 10:
            logger.warning(f"Correlation matrix skipped: only {valid_count} accounts with dimension scores")
            return None
        
        # Build correlation matrix
        dim_arrays = [np.array(dim_data[dim]) for dim in dimensions]
        n_dims = len(dimensions)
        corr_matrix = np.zeros((n_dims, n_dims))
        
        for i in range(n_dims):
            for j in range(n_dims):
                if np.std(dim_arrays[i]) > 0 and np.std(dim_arrays[j]) > 0:
                    corr_matrix[i, j] = np.corrcoef(dim_arrays[i], dim_arrays[j])[0, 1]
                else:
                    corr_matrix[i, j] = 1.0 if i == j else 0.0
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Custom colormap: red (negative) -> yellow (zero) -> green (positive)
        from matplotlib.colors import LinearSegmentedColormap
        colors = ['#c0392b', '#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60']
        cmap = LinearSegmentedColormap.from_list('correlation', colors, N=256)
        
        im = ax.imshow(corr_matrix, cmap=cmap, vmin=-1, vmax=1, aspect='auto')
        
        # Labels
        dim_labels = ['Autonomy-\nIntegration', 'Multi-Scale', 'Regenerative\nImpact',
                     'Network\nContribution', 'Ubuntu\nAlignment']
        
        ax.set_xticks(np.arange(n_dims))
        ax.set_yticks(np.arange(n_dims))
        ax.set_xticklabels(dim_labels, fontsize=9, rotation=45, ha='right')
        ax.set_yticklabels(dim_labels, fontsize=9)
        
        # Add correlation values as text
        for i in range(n_dims):
            for j in range(n_dims):
                value = corr_matrix[i, j]
                text_color = 'white' if abs(value) > 0.5 else 'black'
                ax.text(j, i, f'{value:.2f}', ha='center', va='center',
                       color=text_color, fontsize=11, fontweight='bold')
        
        ax.set_title('Holonic Dimension Correlation Matrix',
                    fontsize=14, fontweight='bold', color=UBUNTU_COLORS['accents']['wisdom'], pad=20)
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Correlation Coefficient', fontsize=10)
        
        fig.tight_layout()
        return self._save_or_encode_figure(fig, 'correlation_matrix_chart')
    
    def create_category_performance_chart(self, accounts: List[Dict]) -> Optional[str]:
        """
        Create grouped bar chart comparing dimension performance across categories.
        
        Shows how each holonic category performs on average across the 5 dimensions.
        Useful for understanding what differentiates Exemplars from Observers.
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            return None
        
        dimensions = ['autonomy_integration', 'multi_scale', 'regenerative_impact',
                     'network_contribution', 'ubuntu_alignment']
        dim_labels = ['Autonomy', 'Multi-Scale', 'Regenerative', 'Network', 'Ubuntu']
        
        categories = ['Exemplar', 'Integrator', 'Contributor', 'Participant', 'Observer']
        
        # Calculate average dimension scores per category
        category_dim_scores = {cat: {dim: [] for dim in dimensions} for cat in categories}
        
        for account in accounts:
            cat = account.get('holonic_category', 'Observer')
            if cat not in categories:
                cat = 'Observer'
            
            dim_scores = account.get('dimension_scores', {})
            for dim in dimensions:
                score = dim_scores.get(dim, 0) if dim_scores else 0
                if score:
                    category_dim_scores[cat][dim].append(float(score))
        
        # Calculate averages
        category_averages = {}
        for cat in categories:
            category_averages[cat] = []
            for dim in dimensions:
                scores = category_dim_scores[cat][dim]
                avg = np.mean(scores) if scores else 0
                category_averages[cat].append(avg)
        
        # Check if we have data
        if all(sum(category_averages[cat]) == 0 for cat in categories):
            logger.warning("Category performance chart skipped: no dimension data by category")
            return None
        
        # Create grouped bar chart
        fig, ax = plt.subplots(figsize=(14, 8))
        
        x = np.arange(len(dimensions))
        width = 0.15
        multiplier = 0
        
        for cat in categories:
            offset = width * multiplier
            color = UBUNTU_COLORS['categories'].get(cat, '#999')
            bars = ax.bar(x + offset, category_averages[cat], width, label=cat, 
                         color=color, edgecolor='white', linewidth=0.5)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                if height > 0.02:
                    ax.annotate(f'{height:.2f}',
                               xy=(bar.get_x() + bar.get_width()/2, height),
                               xytext=(0, 2), textcoords="offset points",
                               ha='center', va='bottom', fontsize=7, fontweight='bold')
            
            multiplier += 1
        
        ax.set_ylabel('Average Score', fontsize=12)
        ax.set_xlabel('Holonic Dimension', fontsize=12)
        ax.set_title('Category Performance Comparison',
                    fontsize=14, fontweight='bold', color=UBUNTU_COLORS['accents']['wisdom'])
        ax.set_xticks(x + width * 2)
        ax.set_xticklabels(dim_labels, fontsize=11)
        ax.set_ylim(0, 1.0)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_facecolor(UBUNTU_COLORS['neutral']['background'])
        
        fig.tight_layout()
        return self._save_or_encode_figure(fig, 'category_performance_chart')
    
    def create_trend_chart(self, accounts: List[Dict]) -> Optional[str]:
        """
        Create 30-day composite score trend chart.
        
        Shows daily average scores with standard deviation band and min/max range.
        Includes trend line to show overall direction.
        
        Note: Uses evaluation_date from accounts to group by date.
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            return None
        
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        # Group scores by evaluation date
        date_scores = defaultdict(list)
        
        for account in accounts:
            eval_date = account.get('evaluation_date')
            score = account.get('composite_score', 0)
            
            if eval_date and score:
                # Parse date (handle both string and datetime)
                if isinstance(eval_date, str):
                    try:
                        date_obj = datetime.fromisoformat(eval_date.replace('Z', '+00:00'))
                        date_key = date_obj.strftime('%Y-%m-%d')
                    except:
                        continue
                else:
                    date_key = eval_date.strftime('%Y-%m-%d')
                
                date_scores[date_key].append(float(score))
        
        if len(date_scores) < 3:
            logger.warning(f"Trend chart skipped: only {len(date_scores)} unique dates")
            return None
        
        # Sort by date and calculate statistics
        sorted_dates = sorted(date_scores.keys())[-30:]  # Last 30 days
        
        dates = []
        means = []
        stds = []
        mins = []
        maxs = []
        
        for date_str in sorted_dates:
            scores = date_scores[date_str]
            dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
            means.append(np.mean(scores))
            stds.append(np.std(scores))
            mins.append(min(scores))
            maxs.append(max(scores))
        
        means = np.array(means)
        stds = np.array(stds)
        mins = np.array(mins)
        maxs = np.array(maxs)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # Plot min/max range (outer band)
        ax.fill_between(dates, mins, maxs, alpha=0.2, 
                       color=UBUNTU_COLORS['accents']['community'], label='Min-Max Range')
        
        # Plot std dev band (inner band)
        ax.fill_between(dates, means - stds, means + stds, alpha=0.3,
                       color=UBUNTU_COLORS['accents']['growth'], label='±1 Std Dev')
        
        # Plot mean line
        ax.plot(dates, means, 'o-', linewidth=2, markersize=6,
               color=UBUNTU_COLORS['accents']['wisdom'], label='Daily Average')
        
        # Add trend line
        x_numeric = np.arange(len(dates))
        if len(x_numeric) > 1:
            z = np.polyfit(x_numeric, means, 1)
            p = np.poly1d(z)
            trend_line = p(x_numeric)
            slope = z[0]
            ax.plot(dates, trend_line, '--', linewidth=2,
                   color=UBUNTU_COLORS['accents']['wisdom'], alpha=0.7,
                   label=f'Trend (slope: {slope:.4f})')
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Composite Score', fontsize=12)
        ax.set_title('UBEC Composite Score - 30 Day Trend',
                    fontsize=14, fontweight='bold', color=UBUNTU_COLORS['accents']['wisdom'])
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_facecolor(UBUNTU_COLORS['neutral']['background'])
        
        # Format x-axis dates
        fig.autofmt_xdate()
        
        fig.tight_layout()
        return self._save_or_encode_figure(fig, 'trend_chart')
    
    def build_html_report(
        self,
        api_data: Dict,
        charts: Dict[str, str],
        api_url: str,
        network_data: Dict = None,
        token_audit: Dict = None
    ) -> str:
        """Build complete HTML report with all charts and data."""
        accounts = api_data.get('accounts', [])
        summary = api_data.get('summary', {})
        pagination = api_data.get('pagination', {})
        
        # Calculate statistics
        scores = [float(a.get('composite_score', 0)) for a in accounts if a.get('composite_score')]
        stats = {
            'count': len(accounts),
            'total_evaluated': summary.get('total_evaluated', len(accounts)),
            'mean': np.mean(scores) if scores else 0,
            'median': np.median(scores) if scores else 0,
            'min': min(scores) if scores else 0,
            'max': max(scores) if scores else 0,
            'std': np.std(scores) if scores else 0
        }
        
        # Get score statistics from API if available
        score_stats = summary.get('score_statistics', {})
        if score_stats:
            stats['mean'] = score_stats.get('mean', stats['mean'])
            stats['median'] = score_stats.get('median', stats['median'])
            stats['min'] = score_stats.get('min', stats['min'])
            stats['max'] = score_stats.get('max', stats['max'])
        
        # Category distribution
        category_dist = summary.get('category_distribution', {})
        category_html = ""
        category_order = ['Exemplar', 'Integrator', 'Contributor', 'Participant', 'Observer']
        for cat in category_order:
            if cat in category_dist:
                count = category_dist[cat]
                pct = (count / stats['count'] * 100) if stats['count'] > 0 else 0
                color = UBUNTU_COLORS['categories'].get(cat, '#ccc')
                category_html += f'''
                <div class="category-item" style="background: {color}20; border-left: 4px solid {color};">
                    <span class="category-name" style="color: {color}; font-weight: 600;">{cat}</span>
                    <span class="category-count">{count} accounts ({pct:.1f}%)</span>
                </div>'''
        
        # Ubuntu principles summary
        ubuntu_principles = summary.get('ubuntu_principles', {})
        principles_html = ""
        if ubuntu_principles:
            for principle, data in ubuntu_principles.items():
                avg = data.get('average', 0) if isinstance(data, dict) else data
                element = {'diversity': 'Air', 'reciprocity': 'Water', 
                          'mutualism': 'Earth', 'regeneration': 'Fire'}.get(principle, '')
                emoji = {'diversity': '🌬️', 'reciprocity': '💧', 
                        'mutualism': '🌍', 'regeneration': '🔥'}.get(principle, '•')
                color = UBUNTU_COLORS['elements'].get(element, '#ccc')
                principles_html += f'''
                <div class="principle-item" style="border-left: 4px solid {color}; padding-left: 15px; margin: 10px 0;">
                    <span class="principle-name">{emoji} {principle.title()} ({element})</span>
                    <span class="principle-value" style="color: {color}; font-weight: 700; font-size: 1.2em;">{avg:.3f}</span>
                </div>'''
        
        # Network data section
        network_html = ""
        if network_data:
            network = network_data.get('network', {})
            network_html = f'''
            <h2>🌐 Network Status</h2>
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-value">{network.get('participants', 0):,}</div>
                    <div class="stat-label">Total Participants</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{network.get('transactions', 0):,}</div>
                    <div class="stat-label">Total Transactions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{network.get('bioregions', 0)}</div>
                    <div class="stat-label">Active Bioregions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{network.get('health', 'Unknown').title()}</div>
                    <div class="stat-label">Network Health</div>
                </div>
            </div>'''
        
        # Token audit section
        token_html = ""
        if token_audit:
            audit_summary = token_audit.get('summary', {})
            token_html = f'''
            <h2>🪙 UBEC Token Audit</h2>
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-value">{audit_summary.get('total_issued', 0)/1000000:.1f}M</div>
                    <div class="stat-label">Total UBEC Issued</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{audit_summary.get('total_in_accounts', 0)/1000000:.1f}M</div>
                    <div class="stat-label">In Accounts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{audit_summary.get('total_in_liquidity_pools', 0)/1000000:.1f}M</div>
                    <div class="stat-label">In Liquidity Pools</div>
                </div>
            </div>'''
        
        # Charts HTML
        charts_html = ""
        chart_sections = [
            ('score_distribution', 'Score Distribution', 'Histogram of holonic composite scores across all evaluated accounts'),
            ('category_distribution', 'Category Distribution', 'Breakdown of accounts by holonic category'),
            ('dimension_radar', 'Holonic Dimensions (Top Accounts)', 'Radar chart showing 5 dimension scores for top performers'),
            ('ubuntu_principles', 'Ubuntu Principles (Top Accounts)', 'Radar chart showing 4 Ubuntu element scores'),
            ('dimension_statistics', 'Network Dimension Statistics', 'Mean scores with min/max range for each dimension'),
            ('top_accounts', 'Top Accounts', 'Highest scoring accounts in the network'),
        ]
        
        for chart_key, title, description in chart_sections:
            if chart_key in charts and charts[chart_key]:
                charts_html += f'''
                <div class="chart-container">
                    <div class="chart-title">{title}</div>
                    <p style="color: #666; margin-bottom: 15px;">{description}</p>
                    <img src="{charts[chart_key]}" alt="{title}">
                </div>'''
        
        # Advanced Analytics Charts HTML
        advanced_charts_html = ""
        advanced_chart_sections = [
            ('correlation_matrix', 'Dimension Correlation Matrix', 
             'Shows relationships between the 5 holonic dimensions. Green/yellow = positive correlation (dimensions that increase together). Red/orange = negative correlation (inverse relationship). Values near 0 indicate independent dimensions.'),
            ('category_performance', 'Category Performance Comparison',
             'Compares average dimension scores across holonic categories. Shows what differentiates Exemplars from Observers and reveals category-specific strengths and development areas.'),
            ('trend', '30-Day Composite Score Trend',
             'Daily average scores over the past 30 days with confidence bands. Green band = ±1 standard deviation (typical range). Pink band = min/max (full range). Dashed line shows overall trend direction.'),
        ]
        
        for chart_key, title, description in advanced_chart_sections:
            if chart_key in charts and charts[chart_key]:
                advanced_charts_html += f'''
                <div class="chart-container">
                    <div class="chart-title">{title}</div>
                    <p class="chart-description">{description}</p>
                    <img src="{charts[chart_key]}" alt="{title}">
                </div>'''
        
        if not advanced_charts_html:
            advanced_charts_html = '<p style="color: #888; text-align: center; padding: 20px;">Advanced analytics charts require sufficient historical data with dimension scores.</p>'
        
        # Build full HTML
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UBEC Holonic Evaluation Report</title>
    <style>
        :root {{
            --bg-warm-white: #FAFAF9;
            --text-primary: #2D3436;
            --border-soft: #E8E6E3;
            --accent-growth: {UBUNTU_COLORS['accents']['growth']};
            --accent-wisdom: {UBUNTU_COLORS['accents']['wisdom']};
            --accent-earth: {UBUNTU_COLORS['accents']['earth']};
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background: linear-gradient(180deg, var(--bg-warm-white) 0%, #F5F4F2 100%);
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
        }}
        
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
        }}
        
        .header h1 {{ margin: 0 0 15px 0; font-size: 2.5em; }}
        .header p {{ margin: 5px 0; opacity: 0.95; }}
        .header .api-source {{
            background: rgba(255,255,255,0.2);
            padding: 8px 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-family: monospace;
            font-size: 0.9em;
        }}
        
        .doc-link {{
            display: inline-block;
            background: rgba(255,255,255,0.25);
            color: white;
            padding: 5px 12px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.85em;
            margin: 3px;
            transition: background 0.2s;
        }}
        .doc-link:hover {{
            background: rgba(255,255,255,0.4);
        }}
        
        .info-link {{
            color: var(--accent-wisdom);
            text-decoration: none;
            border-bottom: 1px dotted var(--accent-wisdom);
        }}
        .info-link:hover {{
            border-bottom-style: solid;
        }}
        
        h2 {{
            color: var(--accent-wisdom);
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 1.6em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-help {{
            font-size: 0.6em;
            font-weight: normal;
            opacity: 0.8;
        }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 25px 0;
        }}
        
        .stat-card {{
            background: white;
            border: 2px solid var(--border-soft);
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--accent-earth), var(--accent-growth));
        }}
        
        .stat-value {{
            font-size: 2.2em;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-wisdom) 0%, var(--accent-growth) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stat-label {{
            color: #888;
            font-size: 0.9em;
            margin-top: 8px;
        }}
        
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
            cursor: help;
            transition: transform 0.2s;
        }}
        .element-card:hover {{
            transform: translateY(-3px);
        }}
        
        .element-card.earth {{ background: linear-gradient(135deg, {UBUNTU_COLORS['elements']['Earth']} 0%, #6B8E63 100%); }}
        .element-card.water {{ background: linear-gradient(135deg, {UBUNTU_COLORS['elements']['Water']} 0%, #5BA3C6 100%); }}
        .element-card.air {{ background: linear-gradient(135deg, {UBUNTU_COLORS['elements']['Air']} 0%, #C49FCC 100%); }}
        .element-card.fire {{ background: linear-gradient(135deg, {UBUNTU_COLORS['elements']['Fire']} 0%, #D4896A 100%); }}
        
        .category-section {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            border: 2px solid var(--border-soft);
            margin: 20px 0;
        }}
        
        .category-item {{
            padding: 15px 20px;
            margin: 10px 0;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .chart-container {{
            background: white;
            border: 2px solid var(--border-soft);
            border-radius: 16px;
            padding: 25px;
            margin: 20px 0;
            text-align: center;
        }}
        
        .chart-container img {{ max-width: 100%; height: auto; border-radius: 8px; }}
        
        .chart-title {{
            font-size: 1.2em;
            font-weight: 600;
            color: var(--accent-wisdom);
            margin-bottom: 10px;
        }}
        
        .chart-description {{
            color: #666;
            margin-bottom: 15px;
            font-size: 0.95em;
        }}
        
        .chart-help {{
            margin-top: 15px;
            padding: 12px;
            background: #f8f8f8;
            border-radius: 8px;
            font-size: 0.85em;
            color: #666;
            text-align: left;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
            margin: 25px 0;
        }}
        
        .guide-section {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
            border-left: 4px solid var(--accent-wisdom);
        }}
        
        .guide-section h3 {{
            color: var(--accent-wisdom);
            margin-bottom: 15px;
        }}
        
        .guide-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .guide-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid var(--border-soft);
        }}
        
        .guide-item h4 {{
            color: var(--accent-earth);
            margin-bottom: 8px;
            font-size: 0.95em;
        }}
        
        .guide-item p {{
            font-size: 0.85em;
            color: #666;
        }}
        
        .footer {{
            margin-top: 60px;
            padding: 30px;
            background: linear-gradient(135deg, var(--accent-earth) 0%, var(--accent-growth) 100%);
            border-radius: 16px;
            color: white;
            text-align: center;
        }}
        
        .footer .version {{ font-size: 1.1em; font-weight: 600; }}
        .footer .attribution {{ font-size: 0.85em; opacity: 0.85; margin-top: 20px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.3); }}
        
        @media (max-width: 768px) {{
            body {{ padding: 15px; }}
            .header {{ padding: 25px; }}
            .header h1 {{ font-size: 1.8em; }}
            .charts-grid {{ grid-template-columns: 1fr; }}
            .elements-banner {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 UBEC Holonic Evaluation Report</h1>
        <p class="subtitle">Ubuntu Bioregional Economic Commons Protocol Suite</p>
        <p>📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>📊 Data Source: API v2.7.0 (include_accounts=true)</p>
        <p>👥 Accounts Analyzed: {stats['count']:,} of {stats['total_evaluated']:,} evaluated</p>
        <div class="api-source">🔗 {api_url}</div>
        <div style="margin-top: 15px;">
            <a href="#guide-section" class="doc-link">📖 Quick Reference Guide</a>
            <a href="#understanding-scores" class="doc-link">📊 Understanding Scores</a>
            <a href="#category-info" class="doc-link">🏷️ Category Definitions</a>
            <a href="#dimensions-info" class="doc-link">📐 The 5 Dimensions</a>
        </div>
    </div>
    
    <div class="elements-banner" id="elements-info">
        <div class="element-card air" title="Click for more info about Air/Diversity">
            🌬️ Air (UBEC)<br>
            <small>Diversity</small>
        </div>
        <div class="element-card water" title="Click for more info about Water/Reciprocity">
            💧 Water (UBECrc)<br>
            <small>Reciprocity</small>
        </div>
        <div class="element-card earth" title="Click for more info about Earth/Mutualism">
            🌍 Earth (UBECgpi)<br>
            <small>Mutualism</small>
        </div>
        <div class="element-card fire" title="Click for more info about Fire/Regeneration">
            🔥 Fire (UBECtt)<br>
            <small>Regeneration</small>
        </div>
    </div>

    <div class="guide-section" id="elements-guide">
        <h3>🌿 The Four Ubuntu Elements</h3>
        <p>The UBEC protocol is built on four interconnected tokens, each representing a fundamental Ubuntu principle:</p>
        <div class="guide-grid">
            <div class="guide-item">
                <h4>🌬️ Air - UBEC (Diversity)</h4>
                <p>Gateway token embodying strength through diversity. Measures variety of engagement across the ecosystem.</p>
            </div>
            <div class="guide-item">
                <h4>💧 Water - UBECrc (Reciprocity)</h4>
                <p>Reciprocity credits tracking balanced exchange. Measures giving and receiving within the community.</p>
            </div>
            <div class="guide-item">
                <h4>🌍 Earth - UBECgpi (Mutualism)</h4>
                <p>Ground project investment for collaborative projects. Measures contribution to mutual benefit.</p>
            </div>
            <div class="guide-item">
                <h4>🔥 Fire - UBECtt (Regeneration)</h4>
                <p>Transformation token for renewal and growth. Measures contribution to ecosystem regeneration.</p>
            </div>
        </div>
    </div>

    <h2 id="understanding-scores">📊 Summary Statistics <span class="section-help">(<a href="#score-guide" class="info-link">What do these mean?</a>)</span></h2>
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-value">{stats['count']:,}</div>
            <div class="stat-label">Accounts in Report</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['mean']:.3f}</div>
            <div class="stat-label">Mean Composite Score</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['median']:.3f}</div>
            <div class="stat-label">Median Score</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['max']:.3f}</div>
            <div class="stat-label">Highest Score</div>
        </div>
    </div>
    
    <div class="guide-section" id="score-guide">
        <h3>📊 Understanding the Composite Score</h3>
        <p>The composite score (0.0 - 1.0) is calculated as a weighted average of five holonic dimensions. Here's how to interpret the statistics:</p>
        <div class="guide-grid">
            <div class="guide-item">
                <h4>Mean Score</h4>
                <p>Average across all accounts. A healthy network typically shows 0.3-0.5 mean.</p>
            </div>
            <div class="guide-item">
                <h4>Median Score</h4>
                <p>Middle value - 50% of accounts score above, 50% below. Close to mean indicates balanced distribution.</p>
            </div>
            <div class="guide-item">
                <h4>Score Range</h4>
                <p><strong>0.8-1.0:</strong> Exemplar | <strong>0.6-0.8:</strong> Integrator | <strong>0.4-0.6:</strong> Contributor | <strong>0.2-0.4:</strong> Participant | <strong>&lt;0.2:</strong> Observer</p>
            </div>
        </div>
    </div>
    
    {network_html}
    
    {token_html}
    
    <h2 id="category-info">🏷️ Category Distribution <span class="section-help">(<a href="#category-guide" class="info-link">Category definitions</a>)</span></h2>
    <div class="category-section">
        {category_html if category_html else '<p>No category data available</p>'}
    </div>
    
    <div class="guide-section" id="category-guide">
        <h3>🏷️ Holonic Categories Explained</h3>
        <p>Accounts are classified into five categories based on their composite scores and engagement patterns:</p>
        <div class="guide-grid">
            <div class="guide-item" style="border-left: 4px solid {UBUNTU_COLORS['categories']['Exemplar']};">
                <h4>🟣 Exemplar (≥0.80)</h4>
                <p>Highest integration. Leaders, mentors, stewards. Excellence across all dimensions.</p>
            </div>
            <div class="guide-item" style="border-left: 4px solid {UBUNTU_COLORS['categories']['Integrator']};">
                <h4>🟢 Integrator (0.60-0.79)</h4>
                <p>Strong balance of autonomy and participation. Active cross-bioregion engagement.</p>
            </div>
            <div class="guide-item" style="border-left: 4px solid {UBUNTU_COLORS['categories']['Contributor']};">
                <h4>🔵 Contributor (0.40-0.59)</h4>
                <p>Active ecosystem engagement. Growing holonic capacity and Ubuntu alignment.</p>
            </div>
            <div class="guide-item" style="border-left: 4px solid {UBUNTU_COLORS['categories']['Participant']};">
                <h4>🟠 Participant (0.20-0.39)</h4>
                <p>Learning and growing. Developing transaction history and network connections.</p>
            </div>
            <div class="guide-item" style="border-left: 4px solid {UBUNTU_COLORS['categories']['Observer']};">
                <h4>⚪ Observer (&lt;0.20)</h4>
                <p>New or minimal engagement. Welcome to increase participation over time.</p>
            </div>
        </div>
    </div>
    
    <h2>🌿 Ubuntu Principles (Network Averages) <span class="section-help">(<a href="#elements-guide" class="info-link">Element details</a>)</span></h2>
    <div class="category-section">
        {principles_html if principles_html else '<p>No principles data available</p>'}
    </div>
    
    <h2 id="dimensions-info">📈 Visualizations <span class="section-help">(<a href="#dimensions-guide" class="info-link">Understanding dimensions</a>)</span></h2>
    
    <div class="guide-section" id="dimensions-guide">
        <h3>📐 The Five Holonic Dimensions</h3>
        <p>Each account is evaluated across five dimensions that together determine the composite score:</p>
        <div class="guide-grid">
            <div class="guide-item">
                <h4>Autonomy-Integration (20%)</h4>
                <p>Balance between independence and interdependence. Neither isolated nor overly dependent.</p>
            </div>
            <div class="guide-item">
                <h4>Multi-Scale (20%)</h4>
                <p>Participation across individual, local, network, and ecosystem scales.</p>
            </div>
            <div class="guide-item">
                <h4>Regenerative Impact (20%)</h4>
                <p>Contribution to ecosystem growth, renewal, and support for new participants.</p>
            </div>
            <div class="guide-item">
                <h4>Network Contribution (20%)</h4>
                <p>Value added through transactions, liquidity, and connectivity enhancement.</p>
            </div>
            <div class="guide-item">
                <h4>Ubuntu Alignment (20%)</h4>
                <p>Overall alignment with the four Ubuntu principles (Diversity, Reciprocity, Mutualism, Regeneration).</p>
            </div>
        </div>
    </div>
    
    <div class="charts-grid">
        {charts_html if charts_html else '<p>No charts generated</p>'}
    </div>
    
    <h2 id="advanced-analytics">📈 Advanced Analytics <span class="section-help">(<a href="#analytics-guide" class="info-link">Understanding advanced metrics</a>)</span></h2>
    
    <div class="guide-section" id="analytics-guide">
        <h3>📊 Advanced Analytics Explained</h3>
        <p>These visualizations provide deeper insights into network dynamics and dimension relationships:</p>
        <div class="guide-grid">
            <div class="guide-item">
                <h4>Correlation Matrix</h4>
                <p>Shows relationships between dimensions. Green = positive correlation (increase together). Red = negative correlation (inverse relationship). Values near 0 = independent.</p>
            </div>
            <div class="guide-item">
                <h4>Category Performance</h4>
                <p>Compares dimension scores across categories. Shows what differentiates Exemplars from Observers and identifies category-specific strengths/weaknesses.</p>
            </div>
            <div class="guide-item">
                <h4>30-Day Trend</h4>
                <p>Daily score averages with confidence bands. Green band = ±1 std dev (typical range). Pink band = min/max (full range). Dashed line = trend direction.</p>
            </div>
            <div class="guide-item">
                <h4>Interpreting Trends</h4>
                <p><strong>Positive slope:</strong> Network improving. <strong>Negative slope:</strong> Declining engagement. <strong>Wide bands:</strong> High variance. <strong>Narrowing bands:</strong> Convergence.</p>
            </div>
        </div>
    </div>
    
    <div class="charts-grid">
        {advanced_charts_html}
    </div>
    
    <div class="guide-section" id="guide-section">
        <h3>📖 Quick Reference: Using This Report for Decision Making</h3>
        <div class="guide-grid">
            <div class="guide-item">
                <h4>For Stewards</h4>
                <p>Use category distribution to assess community health. Identify Exemplars for leadership. Target support for Participant/Observer conversion.</p>
            </div>
            <div class="guide-item">
                <h4>For Participants</h4>
                <p>Compare your scores to network averages. Identify strongest/weakest dimensions. Track improvement over time.</p>
            </div>
            <div class="guide-item">
                <h4>For Analysts</h4>
                <p>Monitor mean score trends. Analyze category distribution changes. Research factors predicting advancement.</p>
            </div>
            <div class="guide-item">
                <h4>Healthy Network Signs</h4>
                <p>Mean close to median. No category >50%. Presence of Exemplars. Active Contributor base.</p>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p class="version">UBEC Protocol Suite - API Report Generator v2.1.0</p>
        <p>Dynamic Pastel Earth Tone Color Palette v13.0.0</p>
        <p>Backend API v2.7.0 • Gateway v1.6.0</p>
        <p style="margin-top: 10px;"><a href="UBEC_HOLONIC_REPORT_GUIDE.md" style="color: white; opacity: 0.9;">📖 Full Documentation Guide (Markdown)</a></p>
        <p class="attribution">
            This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations.<br>
            This project was made possible with the assistance of Claude and Anthropic PBC.
        </p>
    </div>
</body>
</html>'''
        
        return html
    
    def build_pdf_report(
        self,
        api_data: Dict,
        charts: Dict[str, str],
        api_url: str,
        network_data: Dict = None,
        token_audit: Dict = None
    ) -> Optional[str]:
        """
        Build professional dashboard-style PDF report matching HTML design.
        
        v2.2.0 Improvements:
        - Tighter chart layout with reduced whitespace
        - Consistent gradient section headers throughout
        - Better page breaks to avoid orphaned content
        - Larger charts filling more page width
        - Full documentation/methodology section
        """
        if not REPORTLAB_AVAILABLE:
            logger.warning("PDF generation skipped: reportlab not available")
            return None
        
        from reportlab.lib.pagesizes import A4
        from reportlab.graphics.shapes import Drawing, Rect, String, Line
        from reportlab.graphics import renderPDF
        from reportlab.lib.colors import Color, linearlyInterpolatedColor
        
        accounts = api_data.get('accounts', [])
        summary = api_data.get('summary', {})
        
        # Calculate statistics
        scores = [float(a.get('composite_score', 0)) for a in accounts if a.get('composite_score')]
        stats = {
            'count': len(accounts),
            'total_evaluated': summary.get('total_evaluated', len(accounts)),
            'mean': np.mean(scores) if scores else 0,
            'median': np.median(scores) if scores else 0,
            'min': min(scores) if scores else 0,
            'max': max(scores) if scores else 0,
        }
        score_stats = summary.get('score_statistics', {})
        if score_stats:
            stats['mean'] = score_stats.get('mean', stats['mean'])
            stats['median'] = score_stats.get('median', stats['median'])
        
        category_dist = summary.get('category_distribution', {})
        ubuntu_principles = summary.get('ubuntu_principles', {})
        
        # Setup PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"holonic_api_report_{timestamp}.pdf"
        pdf_path = self.output_dir / pdf_filename
        
        # Color palette matching HTML
        COLORS = {
            'gradient_start': HexColor('#8BC34A'),
            'gradient_end': HexColor('#87CEEB'),
            'earth_green': HexColor('#8AA67E'),
            'amethyst': HexColor('#B08BBB'),
            'sage': HexColor('#8FBC8F'),
            'sky_blue': HexColor('#87CEEB'),
            'terracotta': HexColor('#E8A87C'),
            'slate': HexColor('#9CB4CC'),
            'dark_text': HexColor('#2D3436'),
            'light_text': HexColor('#666666'),
            'card_bg': HexColor('#FFFFFF'),
            'page_bg': HexColor('#F8F9FA'),
            'border': HexColor('#E8E6E3'),
        }
        
        # ═══════════════════════════════════════════════════════════════════
        # CUSTOM FLOWABLES
        # ═══════════════════════════════════════════════════════════════════
        
        class GradientHeader(Flowable):
            """Main report header with gradient background and globe icon."""
            def __init__(self, width, height, text, subtitle=None):
                Flowable.__init__(self)
                self.width = width
                self.height = height
                self.text = text
                self.subtitle = subtitle
            
            def draw(self):
                steps = 50
                for i in range(steps):
                    ratio = i / steps
                    r = 0.545 + ratio * (0.529 - 0.545)
                    g = 0.765 + ratio * (0.808 - 0.765)
                    b = 0.290 + ratio * (0.922 - 0.290)
                    self.canv.setFillColorRGB(r, g, b)
                    y = self.height - (i + 1) * (self.height / steps)
                    self.canv.rect(0, y, self.width, self.height / steps + 1, fill=1, stroke=0)
                
                self.canv.setFillColor(white)
                self.canv.setStrokeColor(white)
                self.canv.circle(35, self.height - 35, 18, fill=0, stroke=1)
                self.canv.setLineWidth(1)
                self.canv.line(17, self.height - 35, 53, self.height - 35)
                self.canv.line(22, self.height - 27, 48, self.height - 27)
                self.canv.line(22, self.height - 43, 48, self.height - 43)
                self.canv.arc(27, self.height - 53, 43, self.height - 17, 0, 180)
                
                self.canv.setFillColor(white)
                self.canv.setFont('Helvetica-Bold', 26)
                self.canv.drawString(65, self.height - 40, self.text)
                
                if self.subtitle:
                    self.canv.setFont('Helvetica-Oblique', 11)
                    self.canv.drawString(65, self.height - 56, self.subtitle)
        
        class SectionHeader(Flowable):
            """Section header with gradient background."""
            def __init__(self, width, height, text, icon=None):
                Flowable.__init__(self)
                self.width = width
                self.height = height
                self.text = text
                self.icon = icon
            
            def draw(self):
                steps = 30
                for i in range(steps):
                    ratio = i / steps
                    r = 0.545 + ratio * (0.529 - 0.545)
                    g = 0.765 + ratio * (0.808 - 0.765)
                    b = 0.290 + ratio * (0.922 - 0.290)
                    self.canv.setFillColorRGB(r, g, b)
                    x = i * (self.width / steps)
                    self.canv.rect(x, 0, self.width / steps + 1, self.height, fill=1, stroke=0)
                
                self.canv.setFillColor(white)
                self.canv.setFont('Helvetica-Bold', 13)
                x_offset = 12
                if self.icon:
                    self.canv.drawString(x_offset, self.height/2 - 4, self.icon)
                    x_offset = 30
                self.canv.drawString(x_offset, self.height/2 - 4, self.text)
        
        class StatCard(Flowable):
            """Statistics card with colored top border."""
            def __init__(self, width, height, value, label, color):
                Flowable.__init__(self)
                self.width = width
                self.height = height
                self.value = value
                self.label = label
                self.color = color
            
            def draw(self):
                self.canv.setFillColor(self.color)
                self.canv.rect(0, self.height - 4, self.width, 4, fill=1, stroke=0)
                self.canv.setFillColor(white)
                self.canv.setStrokeColor(HexColor('#E8E6E3'))
                self.canv.rect(0, 0, self.width, self.height - 4, fill=1, stroke=1)
                
                self.canv.setFillColor(HexColor('#2D3436'))
                self.canv.setFont('Helvetica-Bold', 22)
                text_width = self.canv.stringWidth(str(self.value), 'Helvetica-Bold', 22)
                self.canv.drawString((self.width - text_width) / 2, self.height - 32, str(self.value))
                
                self.canv.setFillColor(HexColor('#666666'))
                self.canv.setFont('Helvetica', 8)
                text_width = self.canv.stringWidth(self.label, 'Helvetica', 8)
                self.canv.drawString((self.width - text_width) / 2, 8, self.label)
        
        class ElementCard(Flowable):
            """Element card showing token/principle relationship."""
            def __init__(self, width, height, element, token, principle, color, icon):
                Flowable.__init__(self)
                self.width = width
                self.height = height
                self.element = element
                self.token = token
                self.principle = principle
                self.color = color
                self.icon = icon
            
            def draw(self):
                self.canv.setFillColor(self.color)
                self.canv.rect(0, 0, 4, self.height, fill=1, stroke=0)
                self.canv.setFillColor(white)
                self.canv.setStrokeColor(HexColor('#E8E6E3'))
                self.canv.rect(4, 0, self.width - 4, self.height, fill=1, stroke=1)
                
                self.canv.setFillColor(self.color)
                self.canv.circle(22, self.height/2, 11, fill=1, stroke=0)
                self.canv.setFillColor(white)
                self.canv.setFont('Helvetica-Bold', 11)
                self.canv.drawCentredString(22, self.height/2 - 4, self.icon)
                
                self.canv.setFillColor(HexColor('#2D3436'))
                self.canv.setFont('Helvetica-Bold', 10)
                self.canv.drawString(40, self.height - 16, f"{self.element} - {self.token}")
                
                self.canv.setFillColor(HexColor('#666666'))
                self.canv.setFont('Helvetica', 8)
                self.canv.drawString(40, 8, self.principle)
        
        class CategoryRow(Flowable):
            """Category table row with color dot."""
            def __init__(self, width, height, name, count, pct, score_range, color, is_header=False):
                Flowable.__init__(self)
                self.width = width
                self.height = height
                self.name = name
                self.count = count
                self.pct = pct
                self.score_range = score_range
                self.color = color
                self.is_header = is_header
            
            def draw(self):
                if self.is_header:
                    self.canv.setFillColor(HexColor('#F8F9FA'))
                else:
                    self.canv.setFillColor(white)
                self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)
                
                self.canv.setStrokeColor(HexColor('#E8E6E3'))
                self.canv.line(0, 0, self.width, 0)
                
                if self.is_header:
                    self.canv.setFillColor(HexColor('#666666'))
                    self.canv.setFont('Helvetica-Bold', 9)
                else:
                    self.canv.setFillColor(self.color)
                    self.canv.circle(15, self.height/2, 5, fill=1, stroke=0)
                    self.canv.setFillColor(HexColor('#2D3436'))
                    self.canv.setFont('Helvetica', 10)
                
                col_x = [30, 200, 280, 380]
                self.canv.drawString(col_x[0], self.height/2 - 4, str(self.name))
                self.canv.drawRightString(col_x[1], self.height/2 - 4, str(self.count))
                self.canv.drawRightString(col_x[2], self.height/2 - 4, str(self.pct))
                self.canv.drawString(col_x[3], self.height/2 - 4, str(self.score_range))
        
        # ═══════════════════════════════════════════════════════════════════
        # BUILD DOCUMENT
        # ═══════════════════════════════════════════════════════════════════
        
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.35*inch,
            bottomMargin=0.35*inch
        )
        
        page_width = A4[0] - 1*inch
        styles = getSampleStyleSheet()
        
        body_style = ParagraphStyle(
            'Body', parent=styles['Normal'],
            fontSize=10, textColor=COLORS['dark_text'],
            spaceAfter=6, leading=13
        )
        
        small_style = ParagraphStyle(
            'Small', parent=styles['Normal'],
            fontSize=9, textColor=COLORS['light_text'],
            spaceAfter=3
        )
        
        subsection_style = ParagraphStyle(
            'Subsection', parent=styles['Normal'],
            fontSize=11, textColor=COLORS['amethyst'],
            fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=4
        )
        
        heading3_style = ParagraphStyle(
            'Heading3', parent=styles['Normal'],
            fontSize=10, textColor=COLORS['sage'],
            fontName='Helvetica-Bold', spaceBefore=8, spaceAfter=4
        )
        
        story = []
        
        # ═══════════════════════════════════════════════════════════════════
        # PAGE 1: HEADER, ELEMENTS, SUMMARY, CATEGORIES, PRINCIPLES
        # ═══════════════════════════════════════════════════════════════════
        
        story.append(GradientHeader(page_width, 65, "UBEC Holonic Evaluation Report", 
                                    '"Measuring Ubuntu Philosophy in Action"'))
        story.append(Spacer(1, 8))
        
        meta_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')} | API v2.7.0 | {stats['count']:,} of {stats['total_evaluated']:,} accounts"
        story.append(Paragraph(f'<font color="#666666" size="9">{meta_text}</font>', body_style))
        story.append(Spacer(1, 12))
        
        elements = [
            ('Air', 'UBEC', 'Diversity', COLORS['amethyst'], 'A'),
            ('Water', 'UBECrc', 'Reciprocity', COLORS['sky_blue'], 'W'),
            ('Earth', 'UBECgpi', 'Mutualism', COLORS['sage'], 'E'),
            ('Fire', 'UBECtt', 'Regeneration', COLORS['terracotta'], 'F'),
        ]
        
        card_width = (page_width - 24) / 4
        element_cards = [ElementCard(card_width, 45, e, t, p, c, i) for e, t, p, c, i in elements]
        
        elem_table = Table([element_cards], colWidths=[card_width + 8] * 4)
        elem_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(elem_table)
        story.append(Spacer(1, 15))
        
        story.append(SectionHeader(page_width, 26, "Summary Statistics", "■"))
        story.append(Spacer(1, 8))
        
        stat_card_width = (page_width - 24) / 4
        stat_cards = [
            StatCard(stat_card_width, 55, f"{stats['count']:,}", "Accounts Analyzed", COLORS['amethyst']),
            StatCard(stat_card_width, 55, f"{stats['mean']:.3f}", "Mean Score", COLORS['sage']),
            StatCard(stat_card_width, 55, f"{stats['median']:.3f}", "Median Score", COLORS['sky_blue']),
            StatCard(stat_card_width, 55, f"{stats['max']:.3f}", "Top Score", COLORS['terracotta']),
        ]
        
        stats_table = Table([stat_cards], colWidths=[stat_card_width + 8] * 4)
        stats_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 15))
        
        story.append(SectionHeader(page_width, 26, "Category Distribution", "■"))
        story.append(Spacer(1, 8))
        
        cat_rows = [CategoryRow(page_width, 22, "Category", "Count", "Percentage", "Score Range", white, is_header=True)]
        
        category_info = [
            ('Exemplar', '≥0.80', COLORS['amethyst']),
            ('Integrator', '0.60-0.79', COLORS['sage']),
            ('Contributor', '0.40-0.59', COLORS['sky_blue']),
            ('Participant', '0.20-0.39', COLORS['terracotta']),
            ('Observer', '<0.20', COLORS['slate']),
        ]
        
        for cat, score_range, color in category_info:
            count = category_dist.get(cat, 0)
            pct = f"{(count / stats['total_evaluated'] * 100):.1f}%" if stats['total_evaluated'] > 0 else "0%"
            cat_rows.append(CategoryRow(page_width, 26, cat, f"{count:,}", pct, score_range, color))
        
        for row in cat_rows:
            story.append(row)
        
        story.append(Spacer(1, 15))
        
        story.append(SectionHeader(page_width, 26, "Ubuntu Principles (Network Averages)", "■"))
        story.append(Spacer(1, 8))
        
        prin_data = [['Principle', 'Element', 'Average Score', 'Status']]
        principle_map = [
            ('Diversity', 'diversity', 'Air/UBEC', COLORS['amethyst']),
            ('Reciprocity', 'reciprocity', 'Water/UBECrc', COLORS['sky_blue']),
            ('Mutualism', 'mutualism', 'Earth/UBECgpi', COLORS['sage']),
            ('Regeneration', 'regeneration', 'Fire/UBECtt', COLORS['terracotta']),
        ]
        
        for name, key, element, color in principle_map:
            if key in ubuntu_principles:
                data = ubuntu_principles[key]
                avg = data.get('average', 0) if isinstance(data, dict) else data
                status = 'Strong' if avg >= 0.5 else 'Developing' if avg >= 0.2 else 'Emerging'
                prin_data.append([name, element, f"{avg:.3f}", status])
        
        if len(prin_data) > 1:
            prin_table = Table(prin_data, colWidths=[page_width/4] * 4)
            prin_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), COLORS['sky_blue']),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BACKGROUND', (0, 1), (-1, -1), white),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(prin_table)
        
        story.append(PageBreak())
        
        # ═══════════════════════════════════════════════════════════════════
        # PAGE 2: VISUALIZATIONS
        # ═══════════════════════════════════════════════════════════════════
        
        story.append(SectionHeader(page_width, 26, "Visualizations", "■"))
        story.append(Spacer(1, 8))
        
        # Two distribution charts side by side
        row_charts = []
        for chart_key in ['score_distribution', 'category_distribution']:
            if chart_key in charts and charts[chart_key]:
                try:
                    img_data = charts[chart_key]
                    if img_data.startswith('data:image'):
                        img_data = img_data.split(',')[1]
                    img_bytes = base64.b64decode(img_data)
                    img_buffer = io.BytesIO(img_bytes)
                    img = RLImage(img_buffer, width=page_width/2 - 8, height=2.5*inch)
                    row_charts.append(img)
                except:
                    pass
        
        if row_charts:
            chart_table = Table([row_charts], colWidths=[page_width/2] * len(row_charts))
            story.append(chart_table)
            story.append(Spacer(1, 10))
        
        # Two radar charts side by side
        radar_charts = []
        radar_labels = []
        
        if 'dimension_radar' in charts and charts['dimension_radar']:
            try:
                img_data = charts['dimension_radar']
                if img_data.startswith('data:image'):
                    img_data = img_data.split(',')[1]
                img_bytes = base64.b64decode(img_data)
                img_buffer = io.BytesIO(img_bytes)
                img = RLImage(img_buffer, width=page_width/2 - 8, height=3.2*inch)
                radar_charts.append(img)
                radar_labels.append(Paragraph('<b>Holonic Dimensions (Top 12)</b><br/><font size="8" color="#666666">5 dimension scores for top performers</font>', body_style))
            except:
                pass
        
        if 'ubuntu_principles' in charts and charts['ubuntu_principles']:
            try:
                img_data = charts['ubuntu_principles']
                if img_data.startswith('data:image'):
                    img_data = img_data.split(',')[1]
                img_bytes = base64.b64decode(img_data)
                img_buffer = io.BytesIO(img_bytes)
                img = RLImage(img_buffer, width=page_width/2 - 8, height=3.2*inch)
                radar_charts.append(img)
                radar_labels.append(Paragraph('<b>Ubuntu Principles Alignment</b><br/><font size="8" color="#666666">Four Ubuntu element alignment</font>', body_style))
            except:
                pass
        
        if radar_labels:
            label_table = Table([radar_labels], colWidths=[page_width/2] * len(radar_labels))
            story.append(label_table)
        
        if radar_charts:
            radar_table = Table([radar_charts], colWidths=[page_width/2] * len(radar_charts))
            story.append(radar_table)
        
        story.append(PageBreak())
        
        # ═══════════════════════════════════════════════════════════════════
        # PAGE 3: Dimension Statistics & Top Accounts
        # ═══════════════════════════════════════════════════════════════════
        
        if 'dimension_statistics' in charts and charts['dimension_statistics']:
            story.append(SectionHeader(page_width, 26, "Network Dimension Statistics", "■"))
            story.append(Spacer(1, 6))
            story.append(Paragraph('Average scores for each dimension with min/max range.', small_style))
            try:
                img_data = charts['dimension_statistics']
                if img_data.startswith('data:image'):
                    img_data = img_data.split(',')[1]
                img_bytes = base64.b64decode(img_data)
                img_buffer = io.BytesIO(img_bytes)
                img = RLImage(img_buffer, width=page_width, height=3.5*inch)
                img.hAlign = 'CENTER'
                story.append(img)
            except:
                pass
            story.append(Spacer(1, 12))
        
        if 'top_accounts' in charts and charts['top_accounts']:
            story.append(SectionHeader(page_width, 26, "Top 12 Accounts", "■"))
            story.append(Spacer(1, 6))
            story.append(Paragraph('Highest scoring accounts in the network.', small_style))
            try:
                img_data = charts['top_accounts']
                if img_data.startswith('data:image'):
                    img_data = img_data.split(',')[1]
                img_bytes = base64.b64decode(img_data)
                img_buffer = io.BytesIO(img_bytes)
                img = RLImage(img_buffer, width=page_width, height=3.5*inch)
                img.hAlign = 'CENTER'
                story.append(img)
            except:
                pass
        
        story.append(PageBreak())
        
        # ═══════════════════════════════════════════════════════════════════
        # PAGE 4: ADVANCED ANALYTICS
        # ═══════════════════════════════════════════════════════════════════
        
        story.append(SectionHeader(page_width, 26, "Advanced Analytics", "■"))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            'Deep analytical insights into network dynamics, dimension relationships, and temporal trends.',
            body_style
        ))
        story.append(Spacer(1, 8))
        
        if 'correlation_matrix' in charts and charts['correlation_matrix']:
            story.append(Paragraph('<b>Dimension Correlation Matrix</b>', subsection_style))
            story.append(Paragraph(
                'Heatmap showing statistical correlations between holonic dimensions. '
                'Green/yellow = positive correlation, Red/orange = inverse relationship.',
                small_style
            ))
            try:
                img_data = charts['correlation_matrix']
                if img_data.startswith('data:image'):
                    img_data = img_data.split(',')[1]
                img_bytes = base64.b64decode(img_data)
                img_buffer = io.BytesIO(img_bytes)
                img = RLImage(img_buffer, width=page_width, height=3.3*inch)
                img.hAlign = 'CENTER'
                story.append(img)
            except:
                pass
            story.append(Spacer(1, 10))
        
        if 'category_performance' in charts and charts['category_performance']:
            story.append(Paragraph('<b>Category Performance Comparison</b>', subsection_style))
            story.append(Paragraph(
                'Grouped bar chart comparing dimension scores across all five holonic categories.',
                small_style
            ))
            try:
                img_data = charts['category_performance']
                if img_data.startswith('data:image'):
                    img_data = img_data.split(',')[1]
                img_bytes = base64.b64decode(img_data)
                img_buffer = io.BytesIO(img_bytes)
                img = RLImage(img_buffer, width=page_width, height=3.3*inch)
                img.hAlign = 'CENTER'
                story.append(img)
            except:
                pass
        
        story.append(PageBreak())
        
        # ═══════════════════════════════════════════════════════════════════
        # PAGE 5: TREND + METHODOLOGY
        # ═══════════════════════════════════════════════════════════════════
        
        if 'trend' in charts and charts['trend']:
            story.append(SectionHeader(page_width, 26, "30-Day Composite Score Trend", "■"))
            story.append(Spacer(1, 6))
            story.append(Paragraph(
                'Time series showing daily averages with confidence bands. Positive slope = improving network health.',
                small_style
            ))
            try:
                img_data = charts['trend']
                if img_data.startswith('data:image'):
                    img_data = img_data.split(',')[1]
                img_bytes = base64.b64decode(img_data)
                img_buffer = io.BytesIO(img_bytes)
                img = RLImage(img_buffer, width=page_width, height=3*inch)
                img.hAlign = 'CENTER'
                story.append(img)
            except:
                pass
            story.append(Spacer(1, 15))
        
        # ═══════════════════════════════════════════════════════════════════
        # METHODOLOGY SECTION
        # ═══════════════════════════════════════════════════════════════════
        
        story.append(SectionHeader(page_width, 26, "Methodology & Documentation", "■"))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph('<b>Composite Score Calculation</b>', heading3_style))
        story.append(Paragraph(
            'The composite holonic score is calculated as a weighted average of five dimensions, '
            'each contributing equally (20%):',
            body_style
        ))
        
        formula_data = [
            ['Dimension', 'Weight', 'Description'],
            ['Autonomy-Integration', '20%', 'Balance between independence and interdependence'],
            ['Multi-Scale', '20%', 'Participation across individual, local, network, ecosystem'],
            ['Regenerative Impact', '20%', 'Contribution to ecosystem growth and renewal'],
            ['Network Contribution', '20%', 'Value added through transactions and connectivity'],
            ['Ubuntu Alignment', '20%', 'Alignment with the four Ubuntu principles'],
        ]
        
        formula_table = Table(formula_data, colWidths=[1.8*inch, 0.7*inch, 3.5*inch])
        formula_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['sage']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(formula_table)
        story.append(Spacer(1, 12))
        
        story.append(Paragraph('<b>Holonic Category Thresholds</b>', heading3_style))
        
        cat_explain_data = [
            ['Category', 'Score Range', 'Description'],
            ['Exemplar', '≥0.80', 'Highest integration, community leadership'],
            ['Integrator', '0.60-0.79', 'Strong multi-dimensional engagement'],
            ['Contributor', '0.40-0.59', 'Active ecosystem participation'],
            ['Participant', '0.20-0.39', 'Learning and growing within ecosystem'],
            ['Observer', '<0.20', 'New to ecosystem, minimal engagement'],
        ]
        
        cat_table = Table(cat_explain_data, colWidths=[1.3*inch, 1*inch, 3.7*inch])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['amethyst']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(cat_table)
        story.append(Spacer(1, 12))
        
        story.append(Paragraph('<b>Data Sources</b>', heading3_style))
        story.append(Paragraph(
            f'<b>API Endpoint:</b> {api_url}/v1/holonic-scores?include_accounts=true<br/>'
            f'<b>Backend API Version:</b> v2.7.0<br/>'
            f'<b>Report Generator Version:</b> v2.2.0<br/>'
            f'<b>Data Retrieved:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}',
            body_style
        ))
        
        story.append(Spacer(1, 20))
        
        # ═══════════════════════════════════════════════════════════════════
        # FOOTER
        # ═══════════════════════════════════════════════════════════════════
        
        footer_data = [
            ['UBEC Protocol Suite - API Report Generator v2.2.0'],
            ['Dynamic Pastel Earth Tone Color Palette v13.0.0 | Backend API v2.7.0'],
            [''],
            ['This project uses the services of Claude and Anthropic PBC'],
            ['to inform our decisions and recommendations.'],
        ]
        
        footer_table = Table(footer_data, colWidths=[page_width])
        footer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#F5F4F2')),
            ('TEXTCOLOR', (0, 0), (-1, 1), COLORS['earth_green']),
            ('TEXTCOLOR', (0, 3), (-1, -1), COLORS['light_text']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(footer_table)
        
        # Build PDF
        try:
            doc.build(story)
            logger.info(f"✓ PDF report saved: {pdf_path}")
            return str(pdf_path)
        except Exception as e:
            logger.error(f"Failed to build PDF: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _interpret_score(self, score: float) -> str:
        """Return interpretation text for a score."""
        if score >= 0.8:
            return 'Exceptional - Exemplar level'
        elif score >= 0.6:
            return 'Strong - Integrator level'
        elif score >= 0.4:
            return 'Active - Contributor level'
        elif score >= 0.2:
            return 'Developing - Participant level'
        else:
            return 'Emerging - Observer level'
    
    def _get_category_for_score(self, score: float) -> str:
        """Return category name for a score."""
        if score >= 0.8:
            return 'Exemplar'
        elif score >= 0.6:
            return 'Integrator'
        elif score >= 0.4:
            return 'Contributor'
        elif score >= 0.2:
            return 'Participant'
        else:
            return 'Observer'
    
    async def generate_report(
        self,
        api_data: Dict,
        api_url: str,
        network_data: Dict = None,
        token_audit: Dict = None,
        output_format: str = 'html'
    ) -> Optional[str]:
        """
        Generate complete report with all charts.
        
        Args:
            api_data: Data from /v1/holonic-scores?include_accounts=true
            api_url: API URL for attribution
            network_data: Optional network status data
            token_audit: Optional token audit data
            output_format: Output format - 'html', 'pdf', or 'both'
            
        Returns:
            Path to generated report file (or HTML path if both)
        """
        accounts = api_data.get('accounts', [])
        summary = api_data.get('summary', {})
        
        if not accounts:
            logger.error("No account data available for report generation")
            return None
        
        logger.info(f"Generating charts for {len(accounts)} accounts...")
        charts = {}
        
        # Score distribution (uses composite_score)
        score_chart = self.create_score_distribution_chart(accounts)
        if score_chart:
            charts['score_distribution'] = score_chart
        
        # Category distribution (from API summary)
        category_chart = self.create_category_distribution_chart(summary)
        if category_chart:
            charts['category_distribution'] = category_chart
        
        # Dimension radar chart (uses dimension_scores from v2.7.0)
        radar_chart = self.create_dimension_radar_chart(accounts)
        if radar_chart:
            charts['dimension_radar'] = radar_chart
        
        # Ubuntu principles radar (uses ubuntu_principles from v2.7.0)
        principles_chart = self.create_ubuntu_principles_chart(accounts)
        if principles_chart:
            charts['ubuntu_principles'] = principles_chart
        
        # Dimension statistics bar chart (from API summary)
        dim_stats_chart = self.create_dimension_statistics_chart(summary)
        if dim_stats_chart:
            charts['dimension_statistics'] = dim_stats_chart
        
        # Top accounts chart
        top_accounts_chart = self.create_top_accounts_chart(accounts)
        if top_accounts_chart:
            charts['top_accounts'] = top_accounts_chart
        
        # === ADVANCED ANALYTICS ===
        
        # Correlation matrix (dimension relationships)
        correlation_chart = self.create_correlation_matrix_chart(accounts)
        if correlation_chart:
            charts['correlation_matrix'] = correlation_chart
        
        # Category performance comparison
        category_perf_chart = self.create_category_performance_chart(accounts)
        if category_perf_chart:
            charts['category_performance'] = category_perf_chart
        
        # 30-day trend chart
        trend_chart = self.create_trend_chart(accounts)
        if trend_chart:
            charts['trend'] = trend_chart
        
        logger.info(f"Generated {len(charts)} charts")
        
        html_path = None
        pdf_path = None
        
        # Generate HTML report
        if output_format in ('html', 'both'):
            html_content = self.build_html_report(api_data, charts, api_url, network_data, token_audit)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"holonic_api_report_{timestamp}.html"
            report_path = self.output_dir / report_filename
            report_path.write_text(html_content, encoding='utf-8')
            html_path = str(report_path)
            logger.info(f"✓ HTML report saved: {html_path}")
        
        # Generate PDF report
        if output_format in ('pdf', 'both'):
            pdf_path = self.build_pdf_report(api_data, charts, api_url, network_data, token_audit)
        
        # Return primary path
        if output_format == 'both':
            if html_path:
                logger.info(f"Reports generated: {html_path}")
            if pdf_path:
                logger.info(f"                   {pdf_path}")
            return html_path or pdf_path
        elif output_format == 'pdf':
            return pdf_path
        else:
            return html_path


# Alias for backward compatibility
HolonicReportGenerator = APIVisualizationGenerator


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    """Main entry point for API-based report generation."""
    parser = argparse.ArgumentParser(
        description='Generate UBEC Holonic Visualization Report from API v2.7.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ubec_api_report_generator.py --api-url https://api.ubec.network
  python ubec_api_report_generator.py --api-url https://api.ubec.network --limit 500
  python ubec_api_report_generator.py --api-url https://api.ubec.network --format pdf
  python ubec_api_report_generator.py --api-url https://api.ubec.network --format both

NEW IN v2.1.0:
  - PDF output format with --format pdf or --format both
  - Dashboard-style PDF with gradient headers and custom cards
  - Advanced analytics: correlation matrix, category performance, trend chart
  - 12 accounts shown in radar charts (was 5)

Attribution:
  This project uses the services of Claude and Anthropic PBC.
        """
    )
    
    parser.add_argument(
        '--api-url',
        type=str,
        default='https://api.ubec.network',
        help='Base URL of the UBEC API Gateway (default: https://api.ubec.network)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='./reports',
        help='Output directory for reports (default: ./reports)'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['html', 'pdf', 'both'],
        default='html',
        help='Output format: html, pdf, or both (default: html)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='Maximum number of accounts to fetch (default: 100, max: 500)'
    )
    
    parser.add_argument(
        '--category',
        type=str,
        choices=['Observer', 'Participant', 'Contributor', 'Integrator', 'Exemplar'],
        help='Filter by holonic category'
    )
    
    parser.add_argument(
        '--include-network',
        action='store_true',
        help='Include network status data in report'
    )
    
    parser.add_argument(
        '--include-audit',
        action='store_true',
        help='Include UBEC token audit data in report'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger(__name__).setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Check dependencies
    if not AIOHTTP_AVAILABLE:
        print("ERROR: aiohttp is required. Install with: pip install aiohttp --break-system-packages")
        sys.exit(1)
    
    if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
        print("WARNING: matplotlib/numpy not available. Charts will not be generated.")
    
    if args.format in ('pdf', 'both') and not REPORTLAB_AVAILABLE:
        print("WARNING: reportlab not available. PDF output disabled.")
        print("Install with: pip install reportlab --break-system-packages")
        if args.format == 'pdf':
            print("Falling back to HTML format.")
            args.format = 'html'
    
    print("=" * 70)
    print("UBEC API Report Generator v2.1.0")
    print("Using Backend API v2.7.0 (include_accounts=true)")
    print("Dynamic Pastel Earth Tone Color Palette v13.0.0")
    print("=" * 70)
    print(f"API URL: {args.api_url}")
    print(f"Output: {args.output}")
    print(f"Format: {args.format.upper()}")
    print(f"Limit: {args.limit} accounts")
    if args.category:
        print(f"Category Filter: {args.category}")
    print("=" * 70)
    
    # Initialize generator
    generator = HolonicReportGenerator(output_dir=args.output)
    
    try:
        # Fetch data from API
        api_data = await generator.fetch_holonic_scores(
            api_url=args.api_url,
            limit=args.limit,
            category=args.category
        )
        
        if not api_data:
            print("ERROR: Failed to fetch holonic scores from API")
            sys.exit(1)
        
        # Fetch optional data
        network_data = None
        token_audit = None
        
        if args.include_network:
            network_data = await generator.fetch_network_status(args.api_url)
        
        if args.include_audit:
            token_audit = await generator.fetch_token_audit(args.api_url)
        
        # Generate report
        report_path = await generator.generate_report(
            api_data=api_data,
            api_url=args.api_url,
            network_data=network_data,
            token_audit=token_audit,
            output_format=args.format
        )
        
        if report_path:
            print(f"\n✓ Report generated successfully: {report_path}")
        else:
            print("\n✗ Report generation failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
