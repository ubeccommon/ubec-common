# UBEC Holonic Visualizer - Enhanced Version 6.0.0

## Path A: Complete Visualization Features - IMPLEMENTED ✅

This document describes the enhanced UBEC Holonic Visualizer with complete Path A visualization features.

---

## 🎯 Executive Summary

The Enhanced UBEC Holonic Visualizer (v6.0.0) is a comprehensive async visualization service that creates production-ready charts, graphs, and reports from holonic evaluation data. This version completes **Path A: Complete Visualization Features** with 10 distinct visualization types and advanced analytics capabilities.

### Version History
- **v5.0.0**: Core async refactor with basic visualizations
- **v6.0.0**: Enhanced with advanced analytics and Path A completion

---

## ✅ All 12 Design Principles - VERIFIED

| Principle | Status | Implementation |
|-----------|--------|----------------|
| 1. Modular Design | ✅ | Self-contained service with clear boundaries |
| 2. Service Pattern | ✅ | Factory function, no standalone execution |
| 3. Service Registry | ✅ | Dependencies via constructor injection |
| 4. Single Source of Truth | ✅ | Database is authoritative for all data |
| 5. Strict Async | ✅ | ALL I/O operations use async/await |
| 6. No Sync Fallbacks | ✅ | Pure async implementation throughout |
| 7. Per-Asset Monitoring | ✅ | Individual account visualization and tracking |
| 8. No Duplicate Config | ✅ | Centralized configuration management |
| 9. Integrated Rate Limiting | ✅ | Built-in for database operations |
| 10. Separation of Concerns | ✅ | Visualization logic fully isolated |
| 11. Comprehensive Documentation | ✅ | Full docstrings and attribution |
| 12. Method Singularity | ✅ | Each visualization implemented exactly once |

---

## 🎨 Complete Feature Set (10 Visualization Types)

### Core Visualizations (Original)

1. **Score Distribution Histogram**
   - Composite score distribution across all accounts
   - Category threshold markers
   - Mean and median indicators
   - Statistical overlays

2. **Holonic Dimensions Radar Chart**
   - 5-dimensional spider chart
   - Network average profile
   - Top N account comparisons
   - Color-coded by performance

3. **Category Distribution Pie Chart**
   - Donut-style visualization
   - Category proportions with percentages
   - Consistent color scheme
   - Account counts

### Advanced Visualizations (NEW in v6.0.0)

4. **Time-Series Trend Analysis** 🆕
   - Network-wide metric evolution over time
   - Daily averages with confidence intervals
   - Min-max range visualization
   - Trend line with slope calculation
   - Configurable time periods (7-365 days)

5. **Correlation Matrix Heatmap** 🆕
   - Dimension correlation analysis
   - Statistical relationships between metrics
   - Color-coded correlation coefficients
   - Identifies co-moving dimensions

6. **Comparative Category Analysis** 🆕
   - Side-by-side category comparison
   - Grouped bar charts by dimension
   - Average scores per category
   - Performance profile analysis

7. **Network Visualization Graph** 🆕
   - Transaction relationship network
   - Node sizing by composite score
   - Edge weighting by transaction volume
   - Category-based color coding
   - Interactive-ready with NetworkX

8. **Account Detail View** 🆕
   - Individual account deep-dive
   - Multi-panel dashboard (4 panels)
   - Historical score trends
   - Dimension evolution
   - Current performance radar
   - Category distribution

9. **Element-Specific Dashboards** 🆕
   - Four-element system support (Air, Water, Earth, Fire)
   - Element color schemes
   - Custom element metrics
   - Unified ecosystem view

10. **Enhanced HTML Reports** 🆕
    - Comprehensive multi-section reports
    - Embedded base64 images
    - Responsive design
    - Print-ready formatting
    - Advanced analytics section

---

## 🚀 Usage Examples

### Basic Usage

```python
from core.holonic.ubec_holonic_visualizer import create_holonic_visualizer

# Create visualizer instance
visualizer = await create_holonic_visualizer(
    db_manager=async_db,
    config={
        'db_schema': 'ubec_main',
        'element_mode': False  # Set True for 4-element system
    }
)

# Generate basic report
report_path = await visualizer.generate_html_report('./reports')
print(f"Report saved to: {report_path}")
```

### Core Visualizations

```python
# Score distribution
score_chart = await visualizer.create_score_distribution_chart()

# Radar chart (top 5 accounts)
radar_chart = await visualizer.create_radar_chart(top_n=5)

# Category distribution
category_chart = await visualizer.create_category_distribution_chart()

# Save to specific file
await visualizer.create_score_distribution_chart('/path/to/chart.png')
```

### Advanced Analytics

```python
# Time-series analysis (30 days)
trend_chart = await visualizer.create_time_series_chart(
    days=30,
    metric='composite_score'
)

# Correlation analysis
correlation = await visualizer.create_correlation_matrix()

# Comparative analysis
comparison = await visualizer.create_comparative_analysis_chart(
    categories=['Exemplar', 'Integrator', 'Contributor']
)

# Network visualization (requires NetworkX)
network_viz = await visualizer.create_network_visualization(
    min_transaction_count=10,
    max_nodes=100
)

# Account detail view
detail_view = await visualizer.create_account_detail_view(
    account_id='0x123...',
    days=90
)
```

### Enhanced HTML Reports

```python
# Generate comprehensive report with all visualizations
report = await visualizer.generate_html_report(
    output_dir='./reports',
    include_advanced=True  # Include time-series, correlations, etc.
)

# Generate basic report only
report = await visualizer.generate_html_report(
    output_dir='./reports',
    include_advanced=False
)
```

### Data Loading

```python
# Load evaluation data (most recent per account)
data = await visualizer.load_evaluation_data(limit=100)

# Load time-series data (30 days, all accounts)
time_series = await visualizer.load_time_series_data(days=30)

# Load time-series for specific account
account_history = await visualizer.load_time_series_data(
    days=90,
    account_id='0x123...'
)

# Load network data
network = await visualizer.load_network_data(
    min_transaction_count=5
)
```

### Health Checks

```python
# Check service health
health = await visualizer.health_check()
print(health)
# Output:
# {
#     'service': 'UBECHolonicVisualizer',
#     'version': '6.0.0',
#     'status': 'healthy',
#     'database': 'connected',
#     'data_loaded': True,
#     'networkx_available': True,
#     'timestamp': '2025-10-14T...'
# }
```

---

## 📊 Visualization Details

### 1. Score Distribution Chart
**Purpose**: Show distribution of composite scores across network  
**Key Features**:
- 30-bin histogram with smart binning
- Category threshold vertical lines with labels
- Color-coded bars by category ranges
- Mean line (red) and median line (green)
- Statistical annotations

**Best For**: Understanding score spread and central tendency

### 2. Radar Chart
**Purpose**: Compare multidimensional performance  
**Key Features**:
- 5 holonic dimensions (pentagon)
- Network average (blue, bold)
- Top N accounts (rainbow colors)
- Filled areas for visual comparison
- Configurable account count

**Best For**: Profile comparison and dimension balance

### 3. Category Distribution
**Purpose**: Show account distribution across categories  
**Key Features**:
- Donut-style pie chart
- Consistent category colors
- Percentage and count labels
- Slight wedge separation for clarity
- Legend with detailed counts

**Best For**: Category proportions and distribution

### 4. Time-Series Trend
**Purpose**: Track metric evolution over time  
**Key Features**:
- Daily average line plot
- ±1 standard deviation band
- Min-max range shading
- Linear trend line with slope
- Configurable time period (7-365 days)
- Supports all metrics

**Best For**: Trend analysis and temporal patterns

### 5. Correlation Matrix
**Purpose**: Understand relationships between dimensions  
**Key Features**:
- Heatmap visualization (coolwarm colormap)
- -1 to +1 correlation range
- Numerical correlation coefficients
- Color-coded cell background
- Symmetric matrix

**Best For**: Identifying co-dependencies and relationships

### 6. Comparative Analysis
**Purpose**: Compare categories across dimensions  
**Key Features**:
- Grouped bar chart
- Side-by-side category comparison
- All 5 dimensions
- Value labels on bars
- Category color consistency

**Best For**: Category performance profiles

### 7. Network Visualization
**Purpose**: Show transaction relationships  
**Key Features**:
- Directed graph (NetworkX)
- Node size by composite score
- Edge width by transaction count
- Category-based node colors
- Spring layout algorithm
- Configurable node limit
- High-score node labels

**Best For**: Understanding network structure and hubs

### 8. Account Detail View
**Purpose**: Deep-dive into individual account  
**Key Features**:
- 4-panel dashboard
- Panel 1: Composite score trend
- Panel 2: All dimension scores over time
- Panel 3: Current radar profile
- Panel 4: Category distribution
- Configurable history period

**Best For**: Individual account analysis and monitoring

### 9. Element Dashboards
**Purpose**: Four-element ecosystem view  
**Key Features**:
- Element-specific color schemes
- Unified dashboard layout
- Cross-element comparisons
- Element balance visualization

**Best For**: Four-element system management

### 10. Enhanced HTML Reports
**Purpose**: Comprehensive documentation and sharing  
**Key Features**:
- Multi-section layout
- Embedded images (base64)
- Responsive CSS design
- Executive summary
- Detailed metrics tables
- Top 20 accounts ranking
- Advanced analytics section
- Print-ready formatting
- Professional styling

**Best For**: Stakeholder reports and documentation

---

## 🎨 Color Schemes

### Category Colors
```python
CATEGORY_COLORS = {
    'Exemplar': '#8b5cf6',      # Purple
    'Integrator': '#10b981',    # Green
    'Contributor': '#3b82f6',   # Blue
    'Participant': '#f59e0b',   # Orange
    'Observer': '#9ca3af'       # Gray
}
```

### Element Colors (Four-Element System)
```python
ELEMENT_COLORS = {
    'air': '#87CEEB',      # Sky Blue
    'water': '#4682B4',    # Steel Blue
    'earth': '#8B4513',    # Saddle Brown
    'fire': '#FF4500'      # Orange Red
}
```

### Dimension Colors
```python
DIMENSION_COLORS = [
    '#667eea',  # Autonomy
    '#764ba2',  # Multi-scale
    '#f093fb',  # Regenerative
    '#4facfe',  # Network
    '#00f2fe'   # Ubuntu
]
```

---

## 🔧 Configuration Options

### Factory Function Parameters

```python
visualizer = await create_holonic_visualizer(
    db_manager=async_db,        # Required: Async database manager
    config={
        'db_schema': 'ubec_main',    # Required: Database schema
        'element_mode': False         # Optional: Enable 4-element features
    }
)
```

### Chart-Specific Parameters

```python
# Radar chart
await visualizer.create_radar_chart(
    output_file='./radar.png',  # Optional: Save location
    top_n=5                      # Number of top accounts
)

# Time-series
await visualizer.create_time_series_chart(
    output_file=None,           # Optional: None for base64
    days=30,                    # History period
    metric='composite_score'    # Metric to plot
)

# Network visualization
await visualizer.create_network_visualization(
    output_file=None,
    min_transaction_count=5,    # Edge threshold
    max_nodes=100               # Node limit
)

# Account detail
await visualizer.create_account_detail_view(
    account_id='0x123...',      # Target account
    output_file=None,
    days=90                     # History period
)
```

---

## 📈 Output Formats

### Base64 Encoded Images
When `output_file=None`, images are returned as base64-encoded strings:
```python
img_data = await visualizer.create_score_distribution_chart()
# Returns: "data:image/png;base64,iVBORw0KGg..."
```

### File Output
When `output_file` is specified, images are saved to disk:
```python
path = await visualizer.create_score_distribution_chart('/path/to/chart.png')
# Returns: "/path/to/chart.png"
```

### HTML Reports
HTML reports are always saved to disk:
```python
report_path = await visualizer.generate_html_report('./reports')
# Returns: "./reports/ubec_holonic_report_20251014_123456.html"
```

---

## 🔍 Database Queries

### Evaluation Data Query
```sql
-- Most recent evaluation per account
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
        holonic_category,
        raw_metrics
    FROM ubec_main.holonic_metrics
    ORDER BY account_id, evaluation_date DESC
)
SELECT * FROM latest_evals
ORDER BY composite_score DESC
```

### Time-Series Query
```sql
-- Historical evaluations
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
FROM ubec_main.holonic_metrics
WHERE evaluation_date >= $1  -- cutoff date
ORDER BY evaluation_date ASC
```

### Network Data Query
```sql
-- Transaction relationships
SELECT 
    from_address,
    to_address,
    COUNT(*) as transaction_count,
    SUM(value) as total_value
FROM ubec_main.transactions
WHERE from_address != to_address
GROUP BY from_address, to_address
HAVING COUNT(*) >= $1  -- min transaction count
ORDER BY transaction_count DESC
LIMIT 1000
```

---

## 🧪 Testing and Validation

### Health Check
```python
health = await visualizer.health_check()
assert health['status'] == 'healthy'
assert health['database'] == 'connected'
```

### Data Validation
```python
# Load and verify data
data = await visualizer.load_evaluation_data()
assert data['status'] == 'success'
assert data['evaluated_count'] > 0
assert len(data['results']) > 0
```

### Visualization Generation
```python
# Test all core visualizations
score_chart = await visualizer.create_score_distribution_chart()
assert score_chart is not None

radar = await visualizer.create_radar_chart()
assert radar is not None

category = await visualizer.create_category_distribution_chart()
assert category is not None
```

---

## 🐛 Error Handling

All methods include comprehensive error handling:

```python
try:
    chart = await visualizer.create_score_distribution_chart()
    if chart is None:
        logger.warning("No data available for visualization")
except Exception as e:
    logger.error(f"Error creating chart: {e}", exc_info=True)
```

### Common Error Scenarios

1. **No Data Available**
   - Returns `None` gracefully
   - Logs warning message
   - Does not raise exception

2. **Database Connection Lost**
   - Detected in `health_check()`
   - Returns error status
   - Includes error message

3. **Invalid Configuration**
   - Raises `ValueError` at initialization
   - Clear error messages
   - Configuration validation

4. **NetworkX Not Available**
   - Graceful degradation
   - Network visualization disabled
   - Warning logged

---

## 📦 Dependencies

### Required
```
matplotlib>=3.5.0
numpy>=1.21.0
scipy>=1.7.0
seaborn>=0.11.0
asyncpg>=0.27.0
```

### Optional
```
networkx>=2.6.0  # For network visualization
pandas>=1.3.0    # For correlation matrix
```

---

## 🚀 Performance Considerations

### Data Loading
- **Caching**: Data cached in memory after first load
- **Limits**: Use `limit` parameter for large datasets
- **Async**: All database operations are non-blocking

### Image Generation
- **Resolution**: 300 DPI for high-quality output
- **Format**: PNG with optimal compression
- **Memory**: Figures closed after generation

### HTML Reports
- **Base64**: Images embedded for portability
- **Size**: Can be large with many visualizations
- **Generation**: Fully async, non-blocking

---

## 🔐 Security Considerations

### Data Privacy
- Account IDs truncated in visualizations
- No sensitive data in chart labels
- Database credentials via secure manager

### SQL Injection Prevention
- All queries use parameterized statements
- No string concatenation for parameters
- Input validation on all parameters

---

## 🌐 Integration Examples

### Main.py Integration
```python
from core.holonic.ubec_holonic_visualizer import create_holonic_visualizer

async def generate_reports(db_manager, config):
    """Generate holonic reports in main orchestrator."""
    visualizer = await create_holonic_visualizer(
        db_manager=db_manager,
        config=config
    )
    
    # Generate comprehensive report
    report = await visualizer.generate_html_report(
        output_dir='./reports',
        include_advanced=True
    )
    
    logger.info(f"Report generated: {report}")
    
    await visualizer.close()
```

### CLI Integration
```python
async def visualize_command(args):
    """CLI command for visualization."""
    db = await create_database_manager(config)
    
    visualizer = await create_holonic_visualizer(
        db_manager=db,
        config={'db_schema': args.schema}
    )
    
    if args.report:
        await visualizer.generate_html_report(args.output)
    
    if args.chart_type == 'score_dist':
        await visualizer.create_score_distribution_chart(args.output)
    
    await visualizer.close()
    await db.close()
```

### Service Registry Integration
```python
# In service registry
async def initialize_services():
    services = {
        'database': await create_database_manager(config),
        'visualizer': None  # Lazy initialization
    }
    
    # Lazy load visualizer when needed
    async def get_visualizer():
        if services['visualizer'] is None:
            services['visualizer'] = await create_holonic_visualizer(
                db_manager=services['database'],
                config=config['visualizer']
            )
        return services['visualizer']
    
    services['get_visualizer'] = get_visualizer
    return services
```

---

## 📚 Additional Resources

### Related Modules
- `ubec_holonic_evaluator.py`: Generates the metrics data
- `ubec_database_manager.py`: Provides data access
- `ubec_main_protocol.py`: Orchestrates services

### Documentation
- Design Principles: See project root `README.md`
- Database Schema: See `docs/database_schema.md`
- API Reference: See inline docstrings

---

## 🎓 Best Practices

### 1. Always Use Async/Await
```python
# ✅ Correct
chart = await visualizer.create_score_distribution_chart()

# ❌ Wrong
chart = visualizer.create_score_distribution_chart()  # Missing await
```

### 2. Handle None Returns
```python
# ✅ Correct
chart = await visualizer.create_score_distribution_chart()
if chart is None:
    logger.warning("No data available")
    return

# ❌ Wrong
chart = await visualizer.create_score_distribution_chart()
display_chart(chart)  # May crash if None
```

### 3. Close Resources
```python
# ✅ Correct
visualizer = await create_holonic_visualizer(db, config)
try:
    report = await visualizer.generate_html_report()
finally:
    await visualizer.close()

# ❌ Wrong
visualizer = await create_holonic_visualizer(db, config)
report = await visualizer.generate_html_report()
# Resources not closed
```

### 4. Use Appropriate Limits
```python
# ✅ Correct - Limit for performance
data = await visualizer.load_evaluation_data(limit=1000)

# ⚠️ Caution - May be slow for large datasets
data = await visualizer.load_evaluation_data()  # No limit
```

### 5. Configure Based on Use Case
```python
# ✅ Production configuration
config = {
    'db_schema': 'ubec_main',
    'element_mode': True
}

# ✅ Development configuration
config = {
    'db_schema': 'ubec_test',
    'element_mode': False
}
```

---

## 🔄 Migration from v5.0.0

### Breaking Changes
None - Fully backward compatible

### New Features
All new visualizations are additive and optional:
```python
# Old code still works
report = await visualizer.generate_html_report()

# New features available
trend = await visualizer.create_time_series_chart()
network = await visualizer.create_network_visualization()
```

### Recommended Updates
Consider enabling advanced features:
```python
# Old
report = await visualizer.generate_html_report('./reports')

# New - Include advanced analytics
report = await visualizer.generate_html_report(
    output_dir='./reports',
    include_advanced=True
)
```

---

## ✅ Checklist for Implementation

- [x] All 12 design principles enforced
- [x] Pure async/await implementation
- [x] No duplicate code or methods
- [x] Comprehensive error handling
- [x] Full docstring coverage
- [x] Attribution in all files
- [x] Service pattern with factory
- [x] Service registry compatible
- [x] Database as single source of truth
- [x] No sync fallbacks
- [x] Integrated rate limiting
- [x] Clear separation of concerns
- [x] Production-ready quality

---

## 📞 Support and Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

**UBEC Protocol Team**  
Version: 6.0.0 (Enhanced)  
Date: October 14, 2025

---

## 🎉 Path A: COMPLETE

All visualization features for Path A have been successfully implemented and tested. The enhanced visualizer provides comprehensive analytics capabilities while maintaining strict adherence to all 12 design principles.
