# UBEC Population MapServer Deployment Guide

**Attribution**: This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## Table of Contents

1. [Overview](#overview)
2. [Mapfile Layers](#mapfile-layers)
3. [Installation & Configuration](#installation--configuration)
4. [Testing the Service](#testing-the-service)
5. [WMS Request Examples](#wms-request-examples)
6. [Nginx Configuration](#nginx-configuration)
7. [Caddy Integration](#caddy-integration)
8. [Client Integration Examples](#client-integration-examples)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The UBEC Population mapfile (`population.map`) provides comprehensive visualization of WorldPop 2025 population data through 8 distinct layers:

- **Raster Layers**: Display raw population density data
- **Vector Layers**: Show bioregion boundaries with population statistics
- **Label Layers**: Provide context and readability
- **Point Layers**: Simplified representation for overview maps

### Key Features

✅ Multiple visualization styles (classified, heat map, raw)  
✅ Population and density-based classifications  
✅ Automatic labeling with smart scaling  
✅ WMS/WFS compliant  
✅ Optimized for performance  
✅ GetFeatureInfo support for attribute queries  

---

## Mapfile Layers

### Layer 1: population_raster_raw
**Type**: Raster  
**Purpose**: Display raw WorldPop 2025 population density data  
**Visualization**: Grayscale gradient (white to red)  
**Use Case**: Technical analysis, data validation

### Layer 2: population_raster_classified
**Type**: Raster  
**Purpose**: Population density with 10 classification levels  
**Visualization**: Green gradient (light to dark)  
**Classes**:
- No Population (0)
- Very Low (1-10 per pixel)
- Low (10-50)
- Medium-Low (50-100)
- Medium (100-250)
- Medium-High (250-500)
- High (500-1000)
- Very High (1000-2500)
- Urban (2500-5000)
- Dense Urban (>5000)

**Use Case**: General population distribution visualization

### Layer 3: population_heatmap
**Type**: Raster  
**Purpose**: Heat map style visualization  
**Visualization**: Blue (low) to red (high) gradient  
**Use Case**: Presentations, public-facing maps

### Layer 4: bioregion_population_boundaries
**Type**: Polygon  
**Purpose**: Display bioregion boundaries only (no fill)  
**Style**: Dark blue outline, 2px width  
**Use Case**: Overlay on other layers for context

### Layer 5: bioregion_population_classified
**Type**: Polygon  
**Purpose**: Bioregions classified by total population  
**Classes**:
- < 10,000
- 10,000 - 50,000
- 50,000 - 100,000
- 100,000 - 250,000
- 250,000 - 500,000
- 500,000 - 1,000,000
- > 1,000,000

**Attributes Available**: bioregion_name, population_estimate, density  
**Use Case**: Policy planning, resource allocation

### Layer 6: bioregion_density_classified
**Type**: Polygon  
**Purpose**: Bioregions classified by population density (per km²)  
**Classes**:
- Very Low (< 10/km²)
- Low (10-25/km²)
- Medium (25-50/km²)
- Medium-High (50-100/km²)
- High (100-200/km²)
- Very High (200-500/km²)
- Urban (> 500/km²)

**Use Case**: Urban planning, infrastructure needs assessment

### Layer 7: bioregion_labels
**Type**: Polygon with labels  
**Purpose**: Display bioregion names with population figures  
**Label Format**: 
- Large values: "1.5M", "2.3M"
- Medium values: "500K", "750K"
- Small values: Actual number

**Smart Scaling**: Labels adjust size based on population  
**Use Case**: Reference maps, reports

### Layer 8: bioregion_population_points
**Type**: Point  
**Purpose**: Centroid-based point representation  
**Symbol**: Circles scaled by population  
**Use Case**: Overview maps, simplified visualizations

---

## Installation & Configuration

### Step 1: Copy Mapfile to Server

```bash
# Copy mapfile to MapServer directory
sudo cp /path/to/population.map /opt/mapserver/maps/

# Set proper permissions
sudo chown www-data:www-data /opt/mapserver/maps/population.map
sudo chmod 644 /opt/mapserver/maps/population.map
```

### Step 2: Update Database Credentials

Edit the mapfile and replace placeholder credentials:

```bash
sudo nano /opt/mapserver/maps/population.map
```

Replace all instances of:
- `user='ubec_admin'` with your database username
- `password='your_password'` with your actual password
- `host=localhost` with your database host if different

**Security Note**: For production, consider using `.pgpass` file instead of embedding passwords.

### Step 3: Update WMS Metadata

In the mapfile, update these fields:

```mapfile
WEB
    METADATA
        "wms_onlineresource" "https://your-domain.com/cgi-bin/mapserv?map=/opt/mapserver/maps/population.map"
        "ows_contactorganization" "Your Organization"
        "ows_contactperson" "Your Name"
        "ows_contactelectronicmailaddress" "your-email@domain.com"
    END
END
```

### Step 4: Set Environment Variables

```bash
# Create MapServer environment configuration
sudo nano /etc/apache2/envvars
# OR for Nginx:
sudo nano /etc/nginx/fastcgi_params
```

Add:
```bash
export MS_MAPFILE=/opt/mapserver/maps/population.map
export MS_MAP_PATTERN="^/opt/mapserver/maps/"
export MS_MODE=MAP
```

---

## Testing the Service

### Test 1: GetCapabilities Request

```bash
# Test WMS GetCapabilities
curl "http://localhost/cgi-bin/mapserv?map=/opt/mapserver/maps/population.map&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities" | xmllint --format -
```

**Expected Output**: Well-formed XML listing all 8 layers

### Test 2: GetMap Request (Raster Layer)

```bash
# Request population raster for Europe
curl "http://localhost/cgi-bin/mapserv?map=/opt/mapserver/maps/population.map&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=population_raster_classified&CRS=EPSG:4326&BBOX=35,35,70,70&WIDTH=800&HEIGHT=600&FORMAT=image/png" -o test_raster.png

# View the result
xdg-open test_raster.png  # Linux
# OR: open test_raster.png  # Mac
```

### Test 3: GetMap Request (Vector Layer)

```bash
# Request bioregion boundaries with population
curl "http://localhost/cgi-bin/mapserv?map=/opt/mapserver/maps/population.map&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=bioregion_population_classified&CRS=EPSG:4326&BBOX=-180,-90,180,90&WIDTH=1200&HEIGHT=800&FORMAT=image/png" -o test_vector.png
```

### Test 4: GetFeatureInfo Request

```bash
# Click on a location to get population info
curl "http://localhost/cgi-bin/mapserv?map=/opt/mapserver/maps/population.map&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo&LAYERS=bioregion_population_classified&QUERY_LAYERS=bioregion_population_classified&CRS=EPSG:4326&BBOX=-180,-90,180,90&WIDTH=1200&HEIGHT=800&INFO_FORMAT=text/html&I=600&J=400"
```

### Test 5: Multiple Layers

```bash
# Combine raster and vector layers
curl "http://localhost/cgi-bin/mapserv?map=/opt/mapserver/maps/population.map&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=population_raster_classified,bioregion_population_boundaries,bioregion_labels&CRS=EPSG:4326&BBOX=10,50,20,55&WIDTH=800&HEIGHT=600&FORMAT=image/png" -o test_combined.png
```

---

## WMS Request Examples

### Basic GetCapabilities

```
https://your-domain.com/cgi-bin/mapserv?
  map=/opt/mapserver/maps/population.map&
  SERVICE=WMS&
  VERSION=1.3.0&
  REQUEST=GetCapabilities
```

### GetMap - Population Raster (Global)

```
https://your-domain.com/cgi-bin/mapserv?
  map=/opt/mapserver/maps/population.map&
  SERVICE=WMS&
  VERSION=1.3.0&
  REQUEST=GetMap&
  LAYERS=population_raster_classified&
  CRS=EPSG:4326&
  BBOX=-180,-90,180,90&
  WIDTH=1200&
  HEIGHT=800&
  FORMAT=image/png&
  TRANSPARENT=TRUE
```

### GetMap - Bioregions by Population

```
https://your-domain.com/cgi-bin/mapserv?
  map=/opt/mapserver/maps/population.map&
  SERVICE=WMS&
  VERSION=1.3.0&
  REQUEST=GetMap&
  LAYERS=bioregion_population_classified&
  CRS=EPSG:4326&
  BBOX=-180,-90,180,90&
  WIDTH=1200&
  HEIGHT=800&
  FORMAT=image/png&
  TRANSPARENT=TRUE
```

### GetMap - Heat Map with Labels

```
https://your-domain.com/cgi-bin/mapserv?
  map=/opt/mapserver/maps/population.map&
  SERVICE=WMS&
  VERSION=1.3.0&
  REQUEST=GetMap&
  LAYERS=population_heatmap,bioregion_labels&
  CRS=EPSG:4326&
  BBOX=-180,-90,180,90&
  WIDTH=1200&
  HEIGHT=800&
  FORMAT=image/png&
  TRANSPARENT=TRUE
```

### GetFeatureInfo - Query Population

```
https://your-domain.com/cgi-bin/mapserv?
  map=/opt/mapserver/maps/population.map&
  SERVICE=WMS&
  VERSION=1.3.0&
  REQUEST=GetFeatureInfo&
  LAYERS=bioregion_population_classified&
  QUERY_LAYERS=bioregion_population_classified&
  CRS=EPSG:4326&
  BBOX=-180,-90,180,90&
  WIDTH=1200&
  HEIGHT=800&
  INFO_FORMAT=text/html&
  I=600&
  J=400&
  FEATURE_COUNT=10
```

---

## Nginx Configuration

### Method 1: Using FastCGI (Recommended)

```nginx
# /etc/nginx/sites-available/ubec-population

server {
    listen 80;
    server_name population.ubec.network;
    
    root /var/www/html;
    
    # MapServer CGI endpoint
    location /cgi-bin/mapserv {
        gzip off;
        
        # FastCGI parameters
        include fastcgi_params;
        fastcgi_pass unix:/var/run/fcgiwrap.socket;
        fastcgi_param SCRIPT_FILENAME /usr/lib/cgi-bin/mapserv;
        fastcgi_param QUERY_STRING $query_string;
        fastcgi_param REQUEST_METHOD $request_method;
        fastcgi_param CONTENT_TYPE $content_type;
        fastcgi_param CONTENT_LENGTH $content_length;
        
        # MapServer specific
        fastcgi_param MS_MAPFILE /opt/mapserver/maps/population.map;
        fastcgi_param MS_MAP_PATTERN "^/opt/mapserver/maps/";
        
        # Timeouts for large requests
        fastcgi_read_timeout 300;
        fastcgi_send_timeout 300;
    }
    
    # WMS endpoint (user-friendly URL)
    location /wms/population {
        rewrite ^/wms/population(.*)$ /cgi-bin/mapserv?map=/opt/mapserver/maps/population.map$1 last;
    }
    
    # CORS headers for web clients
    location ~* \.(png|jpg|jpeg|gif)$ {
        add_header Access-Control-Allow-Origin "*";
        add_header Access-Control-Allow-Methods "GET, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type";
    }
    
    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Logging
    access_log /var/log/nginx/ubec-population-access.log;
    error_log /var/log/nginx/ubec-population-error.log warn;
}
```

Enable and test:
```bash
sudo ln -s /etc/nginx/sites-available/ubec-population /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Method 2: Using Nginx with MapServer Standalone

```nginx
server {
    listen 80;
    server_name population.ubec.network;
    
    location /wms/population {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Caching for GetCapabilities
        proxy_cache population_cache;
        proxy_cache_valid 200 1h;
        proxy_cache_key "$request_uri";
    }
}
```

---

## Caddy Integration

### Caddyfile Configuration

```caddy
# /etc/caddy/Caddyfile

population.ubec.network {
    # Reverse proxy to MapServer
    reverse_proxy /cgi-bin/mapserv localhost:8080 {
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
    
    # User-friendly WMS endpoint
    rewrite /wms/population/* /cgi-bin/mapserv?map=/opt/mapserver/maps/population.map&{query}
    
    # CORS headers
    header {
        Access-Control-Allow-Origin "*"
        Access-Control-Allow-Methods "GET, OPTIONS"
        Access-Control-Allow-Headers "Content-Type"
    }
    
    # Compression
    encode gzip
    
    # Logging
    log {
        output file /var/log/caddy/ubec-population.log
        format json
    }
}
```

Apply configuration:
```bash
sudo systemctl reload caddy
```

---

## Client Integration Examples

### OpenLayers (JavaScript)

```javascript
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import TileWMS from 'ol/source/TileWMS';
import {fromLonLat} from 'ol/proj';

// Create population raster layer
const populationRaster = new TileLayer({
    source: new TileWMS({
        url: 'https://your-domain.com/cgi-bin/mapserv',
        params: {
            'map': '/opt/mapserver/maps/population.map',
            'LAYERS': 'population_raster_classified',
            'VERSION': '1.3.0'
        },
        serverType: 'mapserver',
        crossOrigin: 'anonymous'
    }),
    opacity: 0.7
});

// Create bioregion boundaries layer
const bioregionBoundaries = new TileLayer({
    source: new TileWMS({
        url: 'https://your-domain.com/cgi-bin/mapserv',
        params: {
            'map': '/opt/mapserver/maps/population.map',
            'LAYERS': 'bioregion_population_classified,bioregion_labels',
            'VERSION': '1.3.0',
            'TRANSPARENT': true
        },
        serverType: 'mapserver',
        crossOrigin: 'anonymous'
    })
});

// Create map
const map = new Map({
    target: 'map',
    layers: [
        populationRaster,
        bioregionBoundaries
    ],
    view: new View({
        center: fromLonLat([0, 0]),
        zoom: 2
    })
});

// GetFeatureInfo on click
map.on('singleclick', function(evt) {
    const viewResolution = map.getView().getResolution();
    const url = bioregionBoundaries.getSource().getFeatureInfoUrl(
        evt.coordinate,
        viewResolution,
        'EPSG:3857',
        {'INFO_FORMAT': 'application/json'}
    );
    
    if (url) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log('Population data:', data);
                // Display in popup or sidebar
            });
    }
});
```

### Leaflet (JavaScript)

```javascript
import L from 'leaflet';

// Create map
const map = L.map('map').setView([0, 0], 2);

// Add base layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Add population raster layer
const populationRaster = L.tileLayer.wms('https://your-domain.com/cgi-bin/mapserv', {
    map: '/opt/mapserver/maps/population.map',
    layers: 'population_raster_classified',
    format: 'image/png',
    transparent: true,
    version: '1.3.0',
    opacity: 0.6
}).addTo(map);

// Add bioregion layer
const bioregions = L.tileLayer.wms('https://your-domain.com/cgi-bin/mapserv', {
    map: '/opt/mapserver/maps/population.map',
    layers: 'bioregion_population_classified,bioregion_labels',
    format: 'image/png',
    transparent: true,
    version: '1.3.0'
}).addTo(map);

// Layer control
const overlays = {
    "Population Density": populationRaster,
    "Bioregions": bioregions
};
L.control.layers(null, overlays).addTo(map);

// GetFeatureInfo on click
map.on('click', function(e) {
    const bbox = map.getBounds().toBBoxString();
    const size = map.getSize();
    const point = map.latLngToContainerPoint(e.latlng, map.getZoom());
    
    const url = `https://your-domain.com/cgi-bin/mapserv?` +
        `map=/opt/mapserver/maps/population.map&` +
        `SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo&` +
        `LAYERS=bioregion_population_classified&` +
        `QUERY_LAYERS=bioregion_population_classified&` +
        `BBOX=${bbox}&WIDTH=${size.x}&HEIGHT=${size.y}&` +
        `CRS=EPSG:4326&INFO_FORMAT=application/json&` +
        `I=${Math.floor(point.x)}&J=${Math.floor(point.y)}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.features && data.features.length > 0) {
                const props = data.features[0].properties;
                L.popup()
                    .setLatLng(e.latlng)
                    .setContent(`
                        <strong>${props.bioregion_name}</strong><br>
                        Population: ${props.population_estimate.toLocaleString()}<br>
                        Density: ${props.density} per km²
                    `)
                    .openOn(map);
            }
        });
});
```

### QGIS Integration

1. **Add WMS Layer**:
   - Layer → Add Layer → Add WMS/WMTS Layer
   - New connection
   - URL: `https://your-domain.com/cgi-bin/mapserv?map=/opt/mapserver/maps/population.map`
   - Click "Connect"

2. **Select Layers**:
   - Choose from 8 available layers
   - Add to project

3. **Style in QGIS**:
   - Right-click layer → Properties → Symbology
   - Adjust transparency, blend modes

---

## Performance Optimization

### 1. Enable Raster Overviews

```bash
# Create overviews for faster rendering
psql -U ubec_admin -d ubec -h localhost << 'EOF'
SELECT AddRasterConstraints('phenomenal', 'population_raster_2025', 'rast');
SELECT AddOverviewConstraints('phenomenal', 'population_raster_2025', 'rast', 'o_2', 'o_4', 'o_8');
EOF
```

### 2. Tile Caching with MapCache

```xml
<!-- mapcache.xml -->
<mapcache>
    <cache name="disk" type="disk">
        <base>/var/cache/mapcache</base>
    </cache>
    
    <source name="population" type="wms">
        <getmap>
            <params>
                <map>/opt/mapserver/maps/population.map</map>
            </params>
        </getmap>
        <http>
            <url>http://localhost/cgi-bin/mapserv</url>
        </http>
    </source>
    
    <tileset name="population_tiles">
        <source>population</source>
        <cache>disk</cache>
        <grid>WGS84</grid>
        <format>PNG</format>
        <metatile>5 5</metatile>
        <metabuffer>10</metabuffer>
        <expires>86400</expires>
    </tileset>
    
    <service type="wms" enabled="true"/>
    <service type="wmts" enabled="true"/>
    <service type="tms" enabled="true"/>
</mapcache>
```

### 3. Nginx Caching

```nginx
# Add to http block
proxy_cache_path /var/cache/nginx/population 
    levels=1:2 
    keys_zone=population_cache:10m 
    max_size=1g 
    inactive=60m 
    use_temp_path=off;

# In location block
proxy_cache population_cache;
proxy_cache_valid 200 1h;
proxy_cache_key "$request_uri";
proxy_cache_bypass $http_cache_control;
add_header X-Cache-Status $upstream_cache_status;
```

### 4. Database Query Optimization

```sql
-- Ensure spatial indexes exist
CREATE INDEX IF NOT EXISTS population_raster_2025_rast_gist_idx 
ON phenomenal.population_raster_2025 
USING GIST (ST_ConvexHull(rast));

CREATE INDEX IF NOT EXISTS bioregion_boundaries_geom_gist_idx 
ON phenomenal.bioregion_boundaries 
USING GIST (geom);

-- Cluster tables by spatial index
CLUSTER phenomenal.population_raster_2025 USING population_raster_2025_rast_gist_idx;
CLUSTER phenomenal.bioregion_boundaries USING bioregion_boundaries_geom_gist_idx;

-- Update statistics
ANALYZE phenomenal.population_raster_2025;
ANALYZE phenomenal.bioregion_boundaries;
```

---

## Troubleshooting

### Issue: MapServer Returns Error

**Error**: `msLoadMap(): Unable to access file`

**Solution**:
```bash
# Check file permissions
ls -la /opt/mapserver/maps/population.map

# Fix permissions
sudo chown www-data:www-data /opt/mapserver/maps/population.map
sudo chmod 644 /opt/mapserver/maps/population.map

# Check MS_MAP_PATTERN
export MS_MAP_PATTERN="^/opt/mapserver/maps/"
```

### Issue: Database Connection Failed

**Error**: `Connection to database failed`

**Diagnosis**:
```bash
# Test database connection
psql -U ubec_admin -d ubec -h localhost -c "SELECT COUNT(*) FROM phenomenal.population_raster_2025;"

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

**Solution**:
- Verify credentials in mapfile
- Check pg_hba.conf for access rules
- Ensure PostGIS extensions are loaded

### Issue: Blank/White Images

**Diagnosis**:
```bash
# Enable MapServer debugging
export MS_ERRORFILE="/tmp/mapserver.log"
export MS_DEBUGLEVEL=5

# Make request and check log
curl "..." -o test.png
cat /tmp/mapserver.log
```

**Common Causes**:
1. BBOX outside data extent
2. CRS mismatch
3. No data in requested area
4. Styling issue

### Issue: Slow Performance

**Diagnosis**:
```bash
# Check query time
\timing on
SELECT ST_Clip(rast, 1, ST_MakeEnvelope(0,0,10,10,4326), true)
FROM phenomenal.population_raster_2025
WHERE ST_Intersects(rast, ST_MakeEnvelope(0,0,10,10,4326));
```

**Solutions**:
1. Add/rebuild spatial indexes
2. Implement tile caching
3. Use overviews for raster data
4. Reduce GetMap size for testing

### Issue: CORS Errors in Browser

**Error**: `Access-Control-Allow-Origin header missing`

**Solution (Nginx)**:
```nginx
location /cgi-bin/mapserv {
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type" always;
    
    if ($request_method = 'OPTIONS') {
        return 204;
    }
    
    # ... rest of configuration
}
```

---

## Maintenance Checklist

### Daily
- [ ] Monitor MapServer error logs
- [ ] Check disk space for tile cache
- [ ] Review access logs for unusual patterns

### Weekly
- [ ] Clear old cache files
- [ ] Check database connection pool
- [ ] Review performance metrics

### Monthly
- [ ] ANALYZE database tables
- [ ] VACUUM database
- [ ] Rebuild spatial indexes if needed
- [ ] Update MapServer if security patches available

### Quarterly
- [ ] Review and update WMS metadata
- [ ] Test all layers and GetFeatureInfo
- [ ] Performance optimization review
- [ ] Documentation updates

---

## Additional Resources

### MapServer Documentation
- Official Docs: https://mapserver.org/documentation.html
- WMS Reference: https://mapserver.org/ogc/wms_server.html
- Raster Data: https://mapserver.org/input/raster.html

### Testing Tools
- QGIS: Full-featured WMS client
- OpenLayers Examples: https://openlayers.org/en/latest/examples/
- Leaflet Examples: https://leafletjs.com/examples.html

### Performance Tools
- MapCache: https://mapserver.org/mapcache/
- pgBouncer: Connection pooling for PostgreSQL
- Varnish: HTTP caching

---

## Support

For issues or questions:
1. Check MapServer logs: `/var/log/mapserver/`
2. Check Nginx logs: `/var/log/nginx/`
3. Check PostgreSQL logs: `/var/log/postgresql/`
4. Review this documentation
5. Contact UBEC technical team

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-21  
**Mapfile Version**: population.map v1.0

*This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.*
