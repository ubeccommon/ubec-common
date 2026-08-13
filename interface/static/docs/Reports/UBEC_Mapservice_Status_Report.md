# UBEC Mapservice Status Report

**Report Date:** November 28, 2025  
**Service URL:** https://mapservice.ubec.network  
**Version:** 1.0.0  

**Attribution:** This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## Executive Summary

The UBEC Mapservice is a comprehensive bioregional mapping platform built on Mapbender 4.2.x and MapServer 8.2.2, providing interactive visualization and data collection capabilities for the UBEC Protocol's bioregional network. The service enables community mapping of bioregion boundaries, points of interest, and geographic analysis using authoritative watershed (FEOW HydroSHEDS) and ecoregion (Ecoregions2017) datasets.

### Overall Status: **OPERATIONAL** ✅

| Component | Status | Notes |
|-----------|--------|-------|
| Mapbender Application | ✅ Operational | Version 4.2.x |
| MapServer WMS | ✅ Operational | Version 8.2.2, port 8080 |
| Custom UBEC Bundle | ✅ Deployed | UBECMapbenderBundle |
| Digitizer (Bioregions) | ⚠️ Configuration Pending | Database tables ready |
| Digitizer (POIs) | ⚠️ Configuration Pending | Database tables ready |
| Caddy Reverse Proxy | ✅ Operational | Static file serving configured |
| Database Schema | ✅ Deployed | PHENOMENAL schema |

---

## 1. Architecture Overview

### 1.1 System Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         UBEC Mapservice Architecture                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Internet                                                                 │
│      │                                                                    │
│      ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  Caddy Reverse Proxy (HTTPS)                                        │ │
│  │  mapservice.ubec.network                                            │ │
│  │  ├── /wms*, /cgi-bin/mapserv* → localhost:8080 (MapServer)         │ │
│  │  ├── *.css, *.js, *.png (Static) → file_server                     │ │
│  │  └── /* (PHP) → php8.1-fpm.sock                                    │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                           │                                               │
│           ┌───────────────┼───────────────┐                              │
│           ▼               ▼               ▼                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────────────┐ │
│  │  MapServer  │ │  Mapbender  │ │  PostgreSQL + PostGIS               │ │
│  │  WMS/WFS    │ │  4.2.x      │ │  Database: ubec                     │ │
│  │  Port: 8080 │ │  PHP-FPM    │ │  Schemas: ubec_main, phenomenal     │ │
│  │  fcgiwrap   │ │  Symfony    │ │  User: ubec_map (read-only)         │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────────────────┘ │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| Web Server | Caddy | Latest | HTTPS, reverse proxy, static files |
| Application | Mapbender | 4.2.x | Web mapping framework |
| Map Server | MapServer | 8.2.2 | WMS/WFS service |
| CGI Handler | fcgiwrap | Latest | FastCGI for MapServer |
| PHP Runtime | PHP-FPM | 8.1 | Symfony execution |
| Framework | Symfony | 6.x | Application framework |
| Database | PostgreSQL | 15.13+ | Data persistence |
| Spatial | PostGIS | Latest | Geographic queries |

### 1.3 Domain Configuration

| Domain | Purpose | Backend |
|--------|---------|---------|
| `mapservice.ubec.network` | Primary service URL | Caddy → Mapbender |
| `/wms*` | WMS layer requests | → MapServer (8080) |
| `/cgi-bin/mapserv*` | MapServer CGI | → MapServer (8080) |
| `/application/*` | Mapbender applications | → PHP-FPM |
| `/manager` | Mapbender admin | → PHP-FPM |

---

## 2. Deployed Components

### 2.1 Custom UBEC Bundle

**Location:** `/srv/ubec-www/mapbender/application/src/UBEC/MapbenderBundle/`

**Structure:**
```
src/UBEC/MapbenderBundle/
├── DependencyInjection/
│   └── UBECMapbenderExtension.php      # Service loading
├── Resources/
│   ├── config/
│   │   └── services.xml                # Template registration
│   └── public/
│       ├── css/
│       │   ├── ubec_fullscreen.scss    # Full SCSS styling
│       │   └── ubec_test.css           # Plain CSS (production)
│       └── images/
│           └── ubec_logo.png           # Custom logo
├── Template/
│   └── UBECFullscreen.php              # Custom template class
└── UBECMapbenderBundle.php             # Bundle definition
```

**Template Class Features:**
- Extends Mapbender's Fullscreen template
- Adds custom UBEC CSS after parent styles
- Title: "UBEC Bioregion Mapping"

### 2.2 Styling System

**Design Philosophy:** Ubuntu earth-tone palette with holonic category colors

**CSS Variables Defined:**
- Holonic Category Colors (5 levels)
- Four Element Token Colors (Air, Water, Earth, Fire)
- Functional Colors (success, warning, error, info)
- Gradients (earth-sky, sage-amethyst, sage-sky)
- Spacing, typography, effects system

**Key Color Mappings:**
| Category | Color | Hex | CSS Variable |
|----------|-------|-----|--------------|
| Exemplar | Soft Amethyst | #B08BBB | `--ubuntu-exemplar` |
| Integrator | Sage Green | #8FBC8F | `--ubuntu-integrator` |
| Contributor | Sky Blue | #87CEEB | `--ubuntu-contributor` |
| Participant | Soft Terracotta | #E8A87C | `--ubuntu-participant` |
| Observer | Soft Slate | #9CB4CC | `--ubuntu-observer` |

### 2.3 Database Schema (PHENOMENAL)

**Database:** ubec  
**Schema:** phenomenal  
**User:** ubec_map (read-only access)

**Tables:**
| Table | Purpose | Key Fields |
|-------|---------|------------|
| `bioregion_boundaries` | Polygon geometries | gid, bioregion_code, geom, area_sqkm, status |
| `points_of_interest` | Point geometries | gid, poi_code, geom, bioregion_code, poi_type |

**Automatic Features (Triggers):**
- Area calculation (sq km) on boundary save
- Perimeter calculation (km) on boundary save
- Centroid extraction on boundary save
- Latitude/longitude extraction on POI save
- Bioregion assignment on POI save (spatial containment)

**Views Available:**
- `phenomenal.bioregion_stats` - Summary statistics
- `phenomenal.approved_bioregions` - Filtered approved entries
- `phenomenal.recent_submissions` - Last 30 days
- `phenomenal.active_pois` - Active POIs only
- `phenomenal.poi_stats` - POI statistics by type/category

---

## 3. Configuration Status

### 3.1 Mapbender Application

**Application URL:** `https://mapservice.ubec.network/application/ubec_wms`  
**Admin URL:** `https://mapservice.ubec.network/manager`

**Template Assignment:**
- Target Template: `UBEC\MapbenderBundle\Template\UBECFullscreen`
- Status: Available in template dropdown

### 3.2 Digitizer Configuration (Pending)

**Bioregion Digitizer:**
- YAML Config: `digitizer_phenomenal_configuration.yaml`
- Key Setting: `schema: phenomenal` (CRITICAL)
- Element Location: Sidepane

**POI Digitizer:**
- YAML Config: `poi_digitizer_phenomenal_configuration.yaml`
- Features: Image upload, rich metadata, category selection
- Element Location: Sidepane

**Configuration Required:**
```yaml
schemes:
    bioregion_boundaries:
        featureType:
            connection: ubec
            schema: phenomenal  # ← CRITICAL - Must be set
            table: bioregion_boundaries
            uniqueId: gid
            geomType: polygon
            geomField: geom
            srid: 4326
```

### 3.3 WMS Layers Available

**MapServer Layers (8 layers):**
| Layer Name | Type | Purpose |
|------------|------|---------|
| `population_raster_raw` | Raster | Raw WorldPop data |
| `population_raster_classified` | Raster | Classified density (green gradient) |
| `population_heatmap` | Raster | Heat map visualization |
| `bioregion_population_boundaries` | Vector | Bioregion outlines |
| `bioregion_population_classified` | Vector | Population-based classification |
| `bioregion_density_classified` | Vector | Density-based classification |
| `bioregion_labels` | Vector | Name and population labels |
| `bioregion_population_points` | Vector | Centroid point symbols |

**Reference Data Layers:**
- Ecoregions2017 (14 biome types)
- FEOW HydroSHEDS watersheds
- WorldPop 2025 population raster

---

## 4. Pending Tasks

### 4.1 Critical (Security)

| Priority | Task | Status |
|----------|------|--------|
| 🔴 HIGH | Change ubec_map database password | **Pending** |
| 🔴 HIGH | Update Mapbender parameters.yml with new password | **Pending** |

**Action Required:**
```sql
ALTER USER ubec_map WITH PASSWORD 'your_secure_password_here';
```

### 4.2 Integration Tasks

| Priority | Task | Status | Estimated Time |
|----------|------|--------|----------------|
| 🟡 Medium | Add Bioregion Digitizer element | Pending | 2 hours |
| 🟡 Medium | Add POI Digitizer element | Pending | 1 hour |
| 🟡 Medium | Test digitizer workflow | Pending | 2 hours |
| 🟢 Low | Deploy mapping guide documentation | Pending | 1 hour |
| 🟢 Low | Update bioregion guide with links | Pending | 30 min |

### 4.3 Digitizer Setup Steps

1. Login to Mapbender backend (`/manager`)
2. Navigate to Applications → ubec_wms → Layouts → Sidepane
3. Add Element → Digitizer
4. Configure:
   - Title: "Bioregion Mapping"
   - Paste YAML from `digitizer_phenomenal_configuration.yaml`
5. Repeat for POI digitizer
6. Clear Symfony cache
7. Test end-to-end workflow

---

## 5. Testing Verification

### 5.1 Service Endpoints

**Test Commands:**
```bash
# Test Mapbender application
curl -I https://mapservice.ubec.network/application/ubec_wms

# Test WMS GetCapabilities
curl "https://mapservice.ubec.network/cgi-bin/mapserv?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities"

# Test static CSS serving
curl -I https://mapservice.ubec.network/bundles/ubecmapbender/css/ubec_test.css

# Test admin access
curl -I https://mapservice.ubec.network/manager
```

### 5.2 Database Connectivity

```sql
-- Test as ubec_map user
psql -U ubec_map -d ubec

-- Verify schema access
\dt phenomenal.*

-- Check permissions
SELECT table_name, privilege_type
FROM information_schema.table_privileges
WHERE grantee = 'ubec_map'
  AND table_schema = 'phenomenal';
```

### 5.3 Digitizer Test Workflow

1. Access: `https://mapservice.ubec.network/application/ubec_wms`
2. Open "Bioregion Mapping" in sidepane
3. Click "Draw Polygon" tool
4. Draw 4-5 points, double-click to finish
5. Fill metadata form
6. Click Save
7. Verify in database:
```sql
SELECT bioregion_name, area_sqkm, status 
FROM phenomenal.bioregion_boundaries 
ORDER BY submission_date DESC LIMIT 1;
```

---

## 6. Maintenance Procedures

### 6.1 After CSS/Asset Changes

```bash
cd /srv/ubec-www/mapbender/application
sudo cp -r src/UBEC/MapbenderBundle/Resources/public/* public/bundles/ubecmapbender/
sudo chown -R www-data:www-data public/bundles/ubecmapbender/
sudo -u www-data php bin/console cache:clear --env=prod
```

### 6.2 After PHP/Template Changes

```bash
sudo -u www-data php bin/console cache:clear --env=prod
sudo systemctl restart php8.1-fpm
```

### 6.3 Backup Procedures

```bash
# Backup bundle
cp -r src/UBEC/MapbenderBundle ~/backups/UBECMapbenderBundle_$(date +%Y%m%d)

# Backup Mapbender database
pg_dump mapbender > ~/backups/mapbender_$(date +%Y%m%d).sql

# Backup UBEC database (phenomenal schema)
pg_dump -n phenomenal ubec > ~/backups/phenomenal_$(date +%Y%m%d).sql
```

---

## 7. Known Issues

| Issue | Impact | Workaround |
|-------|--------|------------|
| Caddy doesn't follow symlinks | Static files may not load | Use `cp` instead of symlinks for assets |
| SCSS may not compile | Styling incomplete | Use plain CSS (`ubec_test.css`) |
| UTF-8 encoding for emojis | Display issues | Explicit charset headers |

---

## 8. Related Documentation

| Document | Purpose | Location |
|----------|---------|----------|
| Custom Bundle Guide | Full bundle implementation | `MAPBENDER_CUSTOM_BUNDLE_GUIDE.md` |
| Bioregion Mapping Guide | User-facing mapping instructions | `docs/guides/UBEC_Bioregion_Mapping_Guide.md` |
| PHENOMENAL Quick Reference | Database schema reference | `PHENOMENAL_Schema_Quick_Reference.md` |
| Population MapServer Guide | WMS deployment guide | `UBEC_Population_MapServer_Deployment_Guide.md` |

---

## 9. Contact & Support

**For Technical Issues:**
1. Check Mapbender logs: `/var/log/mapbender/`
2. Check PHP logs: `/var/log/php8.1-fpm.log`
3. Check Caddy logs: `/var/log/caddy/mapbender_access.log`
4. Verify database permissions

**Symfony Commands:**
```bash
# Check registered templates
sudo -u www-data php bin/console debug:container --tag=mapbender.template

# Validate container
sudo -u www-data php bin/console lint:container

# Clear cache
sudo -u www-data php bin/console cache:clear --env=prod
```

---

*This report was generated with the assistance of Claude and Anthropic PBC.*
