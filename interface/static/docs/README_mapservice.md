# UBEC Mapservice

**Bioregional Mapping Platform for the Ubuntu Bioregional Economic Commons**

[![Platform](https://img.shields.io/badge/Platform-Mapbender%204.2.x-blue)](https://mapbender.org)
[![MapServer](https://img.shields.io/badge/MapServer-8.2.2-green)](https://mapserver.org)
[![License](https://img.shields.io/badge/License-UBEC%20Protocol-orange)](https://ubec.network)

**Live Service:** https://mapservice.ubec.network  
**Application:** https://mapservice.ubec.network/application/ubec_wms

---

## Overview

The UBEC Mapservice is a web-based geographic information system (GIS) providing interactive mapping capabilities for the UBEC Protocol bioregional network. Built on the open-source Mapbender framework with MapServer WMS backend, it enables communities to:

- 🗺️ **Visualize** bioregion boundaries, watersheds, and ecoregions
- ✏️ **Draw** and submit bioregion boundary proposals
- 📍 **Map** Points of Interest (POIs) within bioregions
- 📊 **Analyze** population and ecological data layers
- 🌍 **Export** geographic data for external use

### Philosophy

> "I am because we are" - Ubuntu

This mapping service embodies the Ubuntu philosophy by enabling communities to collaboratively define their bioregional boundaries based on shared ecological and hydrological characteristics rather than arbitrary political divisions.

---

## Quick Start

### Accessing the Map Interface

1. **Open** https://mapservice.ubec.network/application/ubec_wms
2. **Navigate** using pan/zoom tools
3. **Enable layers** in the sidebar (watersheds, ecoregions, terrain)
4. **Search** for your location
5. **Use tools** to measure, draw, and analyze

### Mapping Your Bioregion

1. Enable the **Watersheds** and **Ecoregions** layers
2. Locate your area using the search function
3. Open the **"Bioregion Mapping"** tool in the sidepane
4. Select the **Draw Polygon** tool
5. Click points around your boundary (4+ points minimum)
6. Double-click to complete the polygon
7. Fill in the metadata form
8. Click **Save** to submit

For detailed instructions, see the [Bioregion Mapping Guide](docs/guides/UBEC_Bioregion_Mapping_Guide.md).

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Internet Users                             │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Caddy Reverse Proxy (HTTPS)                    │
│                    mapservice.ubec.network                        │
├──────────────────────────────────────────────────────────────────┤
│  Routes:                                                          │
│  ├── /wms*, /cgi-bin/*  ──────────► MapServer (port 8080)        │
│  ├── *.css, *.js, *.png ──────────► Static File Server           │
│  └── /* (PHP)           ──────────► PHP-FPM (unix socket)        │
└──────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   MapServer     │  │   Mapbender     │  │   PostgreSQL    │
│   8.2.2         │  │   4.2.x         │  │   + PostGIS     │
│   ────────────  │  │   ────────────  │  │   ────────────  │
│   WMS/WFS       │  │   Symfony 6.x   │  │   Database: ubec│
│   fcgiwrap      │  │   PHP 8.1-FPM   │  │   Schema:       │
│   Port: 8080    │  │   Custom Bundle │  │   - ubec_main   │
│                 │  │   - UBECBundle  │  │   - phenomenal  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Web Server | Caddy | Latest |
| Application | Mapbender | 4.2.x |
| Map Server | MapServer | 8.2.2 |
| PHP Runtime | PHP-FPM | 8.1 |
| Framework | Symfony | 6.x |
| Database | PostgreSQL | 15.13+ |
| Spatial | PostGIS | Latest |
| OS | Ubuntu | 24.04 LTS |

---

## Features

### Map Layers

| Layer | Data Source | Description |
|-------|-------------|-------------|
| **Watersheds** | FEOW HydroSHEDS | River basins and drainage areas |
| **Ecoregions** | Ecoregions2017 | 14 biome types with ecological zones |
| **Population** | WorldPop 2025 | Population density raster |
| **Bioregions** | UBEC Protocol | Community-submitted boundaries |
| **POIs** | UBEC Protocol | Points of interest within bioregions |
| **Terrain** | Multiple | Elevation and topographic data |

### Tools Available

- **Navigation:** Pan, zoom, home extent, search
- **Measurement:** Distance, area, coordinates
- **Selection:** Feature info, identify
- **Digitizer:** Draw polygons, add points, edit geometries
- **Export:** Print, download, share

### Digitizer Forms

**Bioregion Boundary Submission:**
- Bioregion name and code
- Description and rationale
- Primary watershed reference
- Ecoregion code
- Submitter contact information
- Status workflow (proposed → approved → active)

**Point of Interest Submission:**
- POI name and code
- Type and category
- Description
- Image upload
- Contact information
- Visibility setting (public/bioregion/private)

---

## Installation

### Prerequisites

- Ubuntu 24.04 LTS server
- PostgreSQL 15+ with PostGIS
- PHP 8.1+ with required extensions
- Caddy web server
- MapServer 8.x with fcgiwrap
- Mapbender 4.2.x installed

### Deploy Custom Bundle

```bash
# Navigate to Mapbender installation
cd /srv/ubec-www/mapbender/application

# Create bundle directory structure
mkdir -p src/UBEC/MapbenderBundle/{DependencyInjection,Resources/{config,public/{css,images}},Template}

# Copy bundle files (from project repository)
# ... UBECMapbenderBundle.php
# ... UBECMapbenderExtension.php
# ... services.xml
# ... UBECFullscreen.php
# ... ubec_test.css
# ... ubec_logo.png

# Register bundle in config/bundles.php
# Add: UBEC\MapbenderBundle\UBECMapbenderBundle::class => ['all' => true],

# Deploy assets (important: copy, don't symlink)
sudo cp -r src/UBEC/MapbenderBundle/Resources/public/* public/bundles/ubecmapbender/
sudo chown -R www-data:www-data public/bundles/ubecmapbender/

# Clear cache
sudo -u www-data php bin/console cache:clear --env=prod
```

### Configure Caddy

Add to `/etc/caddy/Caddyfile`:

```caddy
mapservice.ubec.network {
    root * /srv/ubec-www/mapbender/application/public
    
    # MapServer WMS endpoints
    handle /wms* {
        reverse_proxy localhost:8080
    }
    handle /cgi-bin/mapserv* {
        reverse_proxy localhost:8080
    }
    
    # Serve static files FIRST
    @static {
        file
        path *.css *.js *.png *.jpg *.jpeg *.gif *.ico *.svg *.woff *.woff2 *.ttf *.eot
    }
    handle @static {
        file_server
    }
    
    # PHP through FastCGI
    php_fastcgi unix//run/php/php8.1-fpm.sock {
        env SCRIPT_FILENAME /srv/ubec-www/mapbender/application/public/index.php
        env SCRIPT_NAME /index.php
        env PATH_INFO {path}
        split .php
    }
    
    encode gzip
    
    header {
        X-Frame-Options "SAMEORIGIN"
        X-Content-Type-Options "nosniff"
    }
    
    log {
        output file /var/log/caddy/mapbender_access.log
        format json
    }
}
```

Reload: `sudo systemctl reload caddy`

### Configure Database Connection

In Mapbender `parameters.yml`:

```yaml
ubec:
    driver: pdo_pgsql
    host: localhost
    dbname: ubec
    user: ubec_map
    password: YOUR_SECURE_PASSWORD
    charset: UTF8
```

---

## Configuration

### Assign Template to Application

**Via Admin Interface:**
1. Go to `https://mapservice.ubec.network/manager`
2. Navigate to **Applications** → **ubec_wms**
3. In **Template** dropdown, select "UBEC Bioregion Mapping"
4. Save

**Via Database:**
```bash
sudo -u www-data php bin/console doctrine:query:sql \
  "UPDATE mb_core_application SET template = 'UBEC\\\\MapbenderBundle\\\\Template\\\\UBECFullscreen' WHERE slug = 'ubec_wms'"
```

### Configure Digitizer Element

1. Login to Mapbender backend (`/manager`)
2. Applications → ubec_wms → Layouts → Sidepane
3. Add Element → Digitizer
4. Configure with YAML:

```yaml
schemes:
    bioregion_boundaries:
        featureType:
            connection: ubec
            schema: phenomenal     # ← CRITICAL
            table: bioregion_boundaries
            uniqueId: gid
            geomType: polygon
            geomField: geom
            srid: 4326
        # ... additional form configuration
```

---

## Custom Styling

### Design System

The UBEC Mapservice uses an Ubuntu-inspired earth-tone design system with CSS custom properties:

```css
:root {
    /* Holonic Category Colors */
    --ubuntu-exemplar: #B08BBB;    /* Soft Amethyst */
    --ubuntu-integrator: #8FBC8F;  /* Sage Green */
    --ubuntu-contributor: #87CEEB; /* Sky Blue */
    --ubuntu-participant: #E8A87C; /* Soft Terracotta */
    --ubuntu-observer: #9CB4CC;    /* Soft Slate */
    
    /* Four Element Token Colors */
    --ubec-air: #B8D4E8;           /* Light Sky Blue - UBEC */
    --ubec-water: #7FC7C4;         /* Soft Teal - UBECrc */
    --ubec-earth: #8AA67E;         /* Moss Green - UBECgpi */
    --ubec-fire: #F4A896;          /* Soft Coral - UBECtt */
    
    /* Gradients */
    --ubuntu-gradient-earth-sky: linear-gradient(135deg, #8AA67E 0%, #87CEEB 100%);
    --ubuntu-gradient-sage-amethyst: linear-gradient(135deg, #8FBC8F 0%, #B08BBB 100%);
}
```

### Modifying Styles

1. Edit `/srv/ubec-www/mapbender/application/src/UBEC/MapbenderBundle/Resources/public/css/ubec_test.css`
2. Deploy changes:
```bash
sudo cp -r src/UBEC/MapbenderBundle/Resources/public/* public/bundles/ubecmapbender/
sudo chown -R www-data:www-data public/bundles/ubecmapbender/
sudo -u www-data php bin/console cache:clear --env=prod
```
3. Hard refresh browser (`Ctrl+Shift+R`)

---

## Database Schema

### PHENOMENAL Schema Tables

**bioregion_boundaries:**
```sql
CREATE TABLE phenomenal.bioregion_boundaries (
    gid SERIAL PRIMARY KEY,
    bioregion_code VARCHAR(50) UNIQUE,
    bioregion_name VARCHAR(255),
    description TEXT,
    geom GEOMETRY(POLYGON, 4326),
    area_sqkm NUMERIC,             -- Auto-calculated
    perimeter_km NUMERIC,          -- Auto-calculated
    centroid GEOMETRY(POINT, 4326), -- Auto-calculated
    primary_watershed VARCHAR(255),
    ecoregion_code VARCHAR(50),
    status VARCHAR(20) DEFAULT 'proposed',
    submitter_name VARCHAR(255),
    submitter_email VARCHAR(255),
    submission_date TIMESTAMP DEFAULT NOW(),
    last_modified TIMESTAMP DEFAULT NOW()
);
```

**points_of_interest:**
```sql
CREATE TABLE phenomenal.points_of_interest (
    gid SERIAL PRIMARY KEY,
    poi_code VARCHAR(50) UNIQUE,
    poi_name VARCHAR(255),
    poi_type VARCHAR(50),
    category VARCHAR(100),
    geom GEOMETRY(POINT, 4326),
    latitude NUMERIC,              -- Auto-extracted
    longitude NUMERIC,             -- Auto-extracted
    bioregion_code VARCHAR(50),    -- Auto-assigned
    description TEXT,
    image_url TEXT,
    media_urls TEXT[],
    contact_info JSONB,
    visibility VARCHAR(20) DEFAULT 'public',
    status VARCHAR(20) DEFAULT 'active',
    submitter_name VARCHAR(255),
    submitter_email VARCHAR(255),
    submission_date TIMESTAMP DEFAULT NOW()
);
```

### Spatial Indexes

```sql
-- Bioregion indexes
CREATE INDEX idx_bioregion_geom ON phenomenal.bioregion_boundaries USING GIST (geom);
CREATE INDEX idx_bioregion_status ON phenomenal.bioregion_boundaries (status);
CREATE INDEX idx_bioregion_code ON phenomenal.bioregion_boundaries (bioregion_code);

-- POI indexes
CREATE INDEX idx_poi_geom ON phenomenal.points_of_interest USING GIST (geom);
CREATE INDEX idx_poi_bioregion ON phenomenal.points_of_interest (bioregion_code);
CREATE INDEX idx_poi_type ON phenomenal.points_of_interest (poi_type);
```

---

## Maintenance

### Common Operations

**Clear Symfony Cache:**
```bash
sudo -u www-data php bin/console cache:clear --env=prod
```

**Restart PHP-FPM:**
```bash
sudo systemctl restart php8.1-fpm
```

**Check Template Registration:**
```bash
sudo -u www-data php bin/console debug:container --tag=mapbender.template
```

**Validate Container:**
```bash
sudo -u www-data php bin/console lint:container
```

### Backup Procedures

```bash
# Bundle backup
cp -r src/UBEC/MapbenderBundle ~/backups/UBECMapbenderBundle_$(date +%Y%m%d)

# Mapbender database
pg_dump mapbender > ~/backups/mapbender_$(date +%Y%m%d).sql

# UBEC phenomenal schema
pg_dump -n phenomenal ubec > ~/backups/phenomenal_$(date +%Y%m%d).sql
```

### Asset Deployment Script

Create `/srv/ubec-www/mapbender/application/deploy_ubec_assets.sh`:

```bash
#!/bin/bash
set -e

APP_DIR="/srv/ubec-www/mapbender/application"
BUNDLE_SRC="$APP_DIR/src/UBEC/MapbenderBundle/Resources/public"
BUNDLE_DEST="$APP_DIR/public/bundles/ubecmapbender"

echo "Deploying UBEC assets..."

sudo rm -rf "$BUNDLE_DEST"
sudo mkdir -p "$BUNDLE_DEST"
sudo cp -r "$BUNDLE_SRC"/* "$BUNDLE_DEST"/
sudo chown -R www-data:www-data "$BUNDLE_DEST"

cd "$APP_DIR"
sudo -u www-data php bin/console cache:clear --env=prod

echo "UBEC assets deployed successfully!"
echo "Remember to hard-refresh your browser (Ctrl+Shift+R)"
```

---

## Troubleshooting

### CSS Not Loading

1. Check file exists:
```bash
curl -I https://mapservice.ubec.network/bundles/ubecmapbender/css/ubec_test.css
```

2. Verify file permissions:
```bash
ls -la public/bundles/ubecmapbender/css/
```

3. Ensure assets are copied (not symlinked):
```bash
sudo rm -f public/bundles/ubecmapbender
sudo mkdir -p public/bundles/ubecmapbender
sudo cp -r src/UBEC/MapbenderBundle/Resources/public/* public/bundles/ubecmapbender/
```

### Template Not Appearing

1. Check bundle registration:
```bash
sudo -u www-data php bin/console debug:container --tag=mapbender.template
```

2. Verify services.xml syntax:
```bash
sudo -u www-data php bin/console lint:container
```

3. Check PHP errors:
```bash
sudo tail -50 /var/log/php8.1-fpm.log
```

### Digitizer Issues

| Issue | Solution |
|-------|----------|
| "Table not found" | Verify `schema: phenomenal` in YAML |
| "Permission denied" | Re-run setup SQL with grants |
| Digitizer not visible | Check element added to sidepane |
| Can't save | Update parameters.yml password |

### MapServer Issues

```bash
# Test GetCapabilities
curl "http://localhost:8080/cgi-bin/mapserv?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities"

# Check fcgiwrap
sudo systemctl status fcgiwrap

# Check MapServer logs
sudo tail -f /var/log/mapserver/mapserver.log
```

---

## File Structure

```
/srv/ubec-www/mapbender/application/
├── bin/
│   └── console                       # Symfony CLI
├── config/
│   ├── bundles.php                   # Bundle registration
│   └── parameters.yml                # Database connections
├── public/
│   ├── bundles/
│   │   └── ubecmapbender/           # Deployed UBEC assets
│   │       ├── css/
│   │       │   └── ubec_test.css
│   │       └── images/
│   │           └── ubec_logo.png
│   └── index.php
├── src/
│   └── UBEC/
│       └── MapbenderBundle/          # Custom bundle source
│           ├── DependencyInjection/
│           ├── Resources/
│           ├── Template/
│           └── UBECMapbenderBundle.php
├── var/
│   ├── cache/                        # Symfony cache
│   └── log/
└── vendor/                           # Composer dependencies
```

---

## API Integration

The mapservice integrates with the UBEC Protocol backend API for:

- Bioregion data retrieval
- POI listings
- Population statistics
- Ecoregion information
- Watershed data

See the [Backend Client](backend_client.py) for implementation details.

---

## Contributing

When contributing to the mapservice:

1. Follow the 12 Design Principles (see project documentation)
2. Use the established design system colors
3. Copy assets instead of symlinking
4. Test thoroughly before deploying
5. Update documentation with changes

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Custom Bundle Guide](MAPBENDER_CUSTOM_BUNDLE_GUIDE.md) | Complete bundle implementation guide |
| [Bioregion Mapping Guide](docs/guides/UBEC_Bioregion_Mapping_Guide.md) | User guide for mapping interface |
| [PHENOMENAL Schema Reference](PHENOMENAL_Schema_Quick_Reference.md) | Database schema documentation |
| [Population MapServer Guide](docs/guides/UBEC_Population_MapServer_Deployment_Guide.md) | WMS layer deployment |

---

## License

This project is part of the UBEC Protocol and is subject to its licensing terms.

---

## Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

*Last Updated: November 28, 2025*  
*Version: 1.0.0*
