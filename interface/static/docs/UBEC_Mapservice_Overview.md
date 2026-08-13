# UBEC Mapservice Overview

**Service:** mapservice.ubec.network  
**Purpose:** Bioregional Mapping Platform for UBEC Protocol  
**Document Version:** 1.0.0  
**Date:** November 28, 2025

---

## What is the UBEC Mapservice?

The UBEC Mapservice is the geographic information system (GIS) component of the UBEC Protocol, providing a web-based platform for communities to visualize, define, and submit bioregion boundaries. It serves as the spatial foundation for the bioregional economic commons, enabling place-based organization around natural features rather than arbitrary political boundaries.

### Core Capabilities

| Capability | Description |
|------------|-------------|
| **Visualization** | Interactive map with watershed, ecoregion, and population layers |
| **Boundary Drawing** | Digitizer tools for creating and editing bioregion polygons |
| **POI Mapping** | Points of interest submission within bioregions |
| **Data Export** | Print, download, and share map views |
| **Analysis** | Measurement, area calculation, feature identification |

---

## Technical Foundation

### Platform Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     UBEC MAPSERVICE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Frontend                    Backend                            │
│   ────────                    ───────                            │
│   • Mapbender 4.2.x          • MapServer 8.2.2 (WMS/WFS)        │
│   • OpenLayers mapping       • PostgreSQL + PostGIS             │
│   • Custom UBEC template     • PHENOMENAL schema                │
│   • Ubuntu earth-tone CSS    • Spatial triggers                 │
│                                                                  │
│   Infrastructure                                                 │
│   ──────────────                                                 │
│   • Caddy reverse proxy (HTTPS)                                  │
│   • PHP 8.1-FPM (Symfony 6.x)                                   │
│   • fcgiwrap (MapServer CGI)                                    │
│   • Ubuntu 24.04 LTS                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Technologies

| Layer | Technology | Role |
|-------|------------|------|
| Web Mapping | Mapbender 4.2.x | Application framework, UI, digitizer |
| Map Server | MapServer 8.2.2 | WMS layer rendering, GetFeatureInfo |
| Database | PostgreSQL 15 + PostGIS | Spatial data storage, triggers |
| Web Server | Caddy | HTTPS, reverse proxy, static files |
| Runtime | PHP 8.1-FPM + Symfony | Application logic |

---

## Data Layers

### Reference Data (Read-Only)

| Layer | Source | Purpose |
|-------|--------|---------|
| **Watersheds** | FEOW HydroSHEDS | River basins for boundary identification |
| **Ecoregions** | Ecoregions2017 | 14 biome types, ecological zones |
| **Population** | WorldPop 2025 | Population density analysis |
| **Terrain** | Various | Elevation, topography |

### User-Generated Data (Editable)

| Layer | Table | Purpose |
|-------|-------|---------|
| **Bioregion Boundaries** | `phenomenal.bioregion_boundaries` | Community-submitted polygons |
| **Points of Interest** | `phenomenal.points_of_interest` | Locations within bioregions |

---

## Custom Branding

### UBEC Design System

The mapservice uses a custom Symfony bundle (`UBECMapbenderBundle`) implementing Ubuntu-inspired styling:

**Color Palette:**
- **Holonic Categories:** 5 levels from Observer (slate) to Exemplar (amethyst)
- **Element Tokens:** Air (sky blue), Water (teal), Earth (moss), Fire (coral)
- **Gradients:** Earth-to-sky, Sage-to-amethyst transitions

**Visual Identity:**
- Custom logo replacement
- Earth-tone toolbar and sidepane
- Branded form styling
- Consistent typography

---

## Database Schema

### PHENOMENAL Schema

The mapservice writes to the `phenomenal` schema in the `ubec` database:

**bioregion_boundaries:**
- Polygon geometries (SRID 4326)
- Auto-calculated: area_sqkm, perimeter_km, centroid
- Status workflow: proposed → approved → active → inactive
- Metadata: submitter info, timestamps

**points_of_interest:**
- Point geometries (SRID 4326)
- Auto-extracted: latitude, longitude
- Auto-assigned: bioregion_code (spatial containment)
- Rich metadata: images, contact info, visibility

### Spatial Features

| Feature | Implementation |
|---------|----------------|
| Area Calculation | Trigger on INSERT/UPDATE |
| Perimeter Calculation | Trigger on INSERT/UPDATE |
| Centroid Extraction | Trigger on INSERT/UPDATE |
| POI Bioregion Assignment | Spatial containment trigger |
| Geometry Validation | Check constraint |

---

## Service Endpoints

### Primary URLs

| URL | Purpose |
|-----|---------|
| `https://mapservice.ubec.network/` | Service root |
| `https://mapservice.ubec.network/application/ubec_wms` | Main map application |
| `https://mapservice.ubec.network/manager` | Admin interface |

### WMS Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/wms?SERVICE=WMS&REQUEST=GetCapabilities` | Layer discovery |
| `/wms?SERVICE=WMS&REQUEST=GetMap&LAYERS=...` | Map tile rendering |
| `/wms?SERVICE=WMS&REQUEST=GetFeatureInfo&...` | Feature queries |

---

## Integration Points

### Backend API (Port 8000)

The mapservice integrates with the UBEC Protocol backend API for:
- Bioregion statistics
- Token holder data
- Network metrics
- Holonic scores

### Frontend Dashboard (Port 8001)

The main UBEC dashboard links to mapservice for:
- Bioregion visualization
- Geographic context
- Community mapping tools

### Stellar Blockchain

Bioregion data flows to blockchain for:
- Token distribution by region
- Community verification
- Governance participation

---

## Operational Status

### Current State (November 2025)

| Component | Status |
|-----------|--------|
| Mapbender Application | ✅ Operational |
| MapServer WMS | ✅ Operational |
| Custom UBEC Bundle | ✅ Deployed |
| Database Schema | ✅ Created |
| Digitizer Configuration | ⚠️ Pending Setup |
| User Documentation | ✅ Available |

### Pending Tasks

1. **Security:** Change ubec_map database password
2. **Configuration:** Add digitizer elements to application
3. **Testing:** End-to-end boundary submission workflow
4. **Documentation:** Deploy user-facing mapping guide

---

## User Workflow

### Mapping a Bioregion

```
┌─────────────────────────────────────────────────────────────────┐
│                    BIOREGION MAPPING WORKFLOW                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. ACCESS                                                       │
│     └── Visit mapservice.ubec.network/application/ubec_wms      │
│                                                                  │
│  2. EXPLORE                                                      │
│     ├── Enable watershed layer                                  │
│     ├── Enable ecoregion layer                                  │
│     └── Navigate to your area                                   │
│                                                                  │
│  3. IDENTIFY                                                     │
│     ├── Follow watershed divides                                │
│     ├── Note ecoregion transitions                              │
│     └── Consider community connections                          │
│                                                                  │
│  4. DRAW                                                         │
│     ├── Open "Bioregion Mapping" in sidepane                   │
│     ├── Select "Draw Polygon" tool                             │
│     └── Click points around boundary (4+ points)               │
│                                                                  │
│  5. SUBMIT                                                       │
│     ├── Complete metadata form                                  │
│     ├── Add description and rationale                          │
│     └── Click "Save"                                           │
│                                                                  │
│  6. REVIEW                                                       │
│     ├── Boundary enters "proposed" status                      │
│     ├── Community review process                               │
│     └── Approved → Active status                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Files

### Bundle Structure

```
/srv/ubec-www/mapbender/application/src/UBEC/MapbenderBundle/
├── UBECMapbenderBundle.php           # Bundle definition
├── DependencyInjection/
│   └── UBECMapbenderExtension.php    # Service loading
├── Resources/
│   ├── config/services.xml            # Template registration
│   └── public/
│       ├── css/ubec_test.css          # Custom styling
│       └── images/ubec_logo.png       # Brand logo
└── Template/
    └── UBECFullscreen.php             # Custom template class
```

### Configuration Files

| File | Purpose |
|------|---------|
| `/etc/caddy/Caddyfile` | Web server configuration |
| `config/bundles.php` | Symfony bundle registration |
| `parameters.yml` | Database connections |
| `digitizer_phenomenal_configuration.yaml` | Digitizer element config |

---

## Maintenance Summary

### Regular Tasks

| Frequency | Task |
|-----------|------|
| After CSS changes | Deploy assets, clear cache |
| After PHP changes | Clear Symfony cache, restart PHP-FPM |
| Weekly | Check logs for errors |
| Monthly | Database backup |

### Key Commands

```bash
# Deploy assets
sudo cp -r src/UBEC/MapbenderBundle/Resources/public/* public/bundles/ubecmapbender/

# Clear cache
sudo -u www-data php bin/console cache:clear --env=prod

# Check templates
sudo -u www-data php bin/console debug:container --tag=mapbender.template

# Restart PHP
sudo systemctl restart php8.1-fpm
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| README_mapservice.md | Full README with installation instructions |
| UBEC_Mapservice_Status_Report.md | Detailed status and configuration |
| MAPBENDER_CUSTOM_BUNDLE_GUIDE.md | Step-by-step bundle creation |
| PHENOMENAL_Schema_Quick_Reference.md | Database schema reference |
| UBEC_Bioregion_Mapping_Guide.md | User-facing mapping instructions |

---

## Contact & Support

For issues with the mapservice:

1. Check application logs: `/var/log/caddy/mapbender_access.log`
2. Check PHP logs: `/var/log/php8.1-fpm.log`
3. Check MapServer logs: `/var/log/mapserver/`
4. Verify database connectivity
5. Clear Symfony cache

---

*This overview was created with the assistance of Claude and Anthropic PBC.*

*Attribution: This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.*
