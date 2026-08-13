# UBEC Bioregion Mapping - PHENOMENAL Schema Quick Reference

## Critical Configuration Difference

### Standard Setup vs Your Setup

| Aspect | Standard Setup | YOUR Setup (PHENOMENAL) |
|--------|----------------|-------------------------|
| **Database** | ubec | ubec ✅ |
| **Schema** | ubec_data (NEW) | phenomenal ✅ (EXISTING) |
| **Table** | ubec_data.bioregion_boundaries | phenomenal.bioregion_boundaries |
| **User** | ubec_map | ubec_map ✅ |
| **SQL Script** | ubec_digitizer_setup.sql | ubec_digitizer_phenomenal_setup.sql ✅ |
| **YAML Config** | digitizer_configuration.yaml | digitizer_phenomenal_configuration.yaml ✅ |

### The Key Difference: Schema Parameter

**Standard Config** (creates new schema):
```yaml
featureType:
    connection: search_db
    table: bioregion_boundaries
    # No schema parameter - uses default
```

**YOUR Config** (uses existing PHENOMENAL schema):
```yaml
featureType:
    connection: ubec  # Your existing database connection
    schema: phenomenal  # ← THIS IS CRITICAL
    table: bioregion_boundaries
```

**Why It Matters**: Without `schema: phenomenal`, Mapbender defaults to the `ubec_main` schema and won't find your tables!

---

## Database Tables Created

### Bioregion Boundaries
```sql
phenomenal.bioregion_boundaries
├── gid (PRIMARY KEY)
├── bioregion_code (UNIQUE)
├── bioregion_name
├── description
├── geom (POLYGON)
├── area_sqkm (auto-calculated)
├── perimeter_km (auto-calculated)
├── centroid (auto-calculated)
├── primary_watershed
├── ecoregion_code
├── status (proposed/approved/active/inactive)
└── submitter info + dates
```

### Points of Interest
```sql
phenomenal.points_of_interest
├── gid (PRIMARY KEY)
├── poi_code (UNIQUE)
├── poi_name
├── poi_type
├── category
├── geom (POINT)
├── latitude (auto-extracted)
├── longitude (auto-extracted)
├── bioregion_code (auto-assigned!)
├── description
├── image_url
├── media_urls[]
├── contact_info (JSONB)
├── visibility (public/bioregion/private)
└── submitter info + dates
```

---

## Mapbender Configuration Checklist

### 1. Database Connection (Verify Existing)
```yaml
# In Mapbender parameters.yml
ubec:
    driver: pdo_pgsql
    host: localhost
    dbname: ubec
    user: ubec_map
    password: [CHANGE THIS!]
    charset: UTF8
```

**⚠️ CRITICAL**: Change the ubec_map password!
```sql
ALTER USER ubec_map WITH PASSWORD 'your_secure_password_here';
```

### 2. Bioregion Digitizer Element
- **Application**: ubec_wms
- **Location**: Sidepane
- **Element Type**: Digitizer
- **Title**: "Bioregion Mapping"
- **YAML**: Copy entire contents of `digitizer_phenomenal_configuration.yaml`

**Key YAML Sections**:
```yaml
schemes:
    bioregion_boundaries:
        featureType:
            connection: ubec
            schema: phenomenal  # ← CRITICAL!
            table: bioregion_boundaries
            uniqueId: gid
            geomType: polygon
            geomField: geom
            srid: 4326
```

### 3. POI Digitizer Element
- **Application**: ubec_wms
- **Location**: Sidepane
- **Element Type**: Digitizer
- **Title**: "Points of Interest"
- **YAML**: Copy entire contents of `poi_digitizer_phenomenal_configuration.yaml`

---

## Testing the Setup

### Test 1: Database Connectivity
```sql
-- Test connection as ubec_map user
psql -U ubec_map -d ubec

-- Verify you can see the tables
\dt phenomenal.*

-- Check permissions
SELECT table_name, privilege_type
FROM information_schema.table_privileges
WHERE grantee = 'ubec_map'
  AND table_schema = 'phenomenal';
```

### Test 2: Mapbender Digitizer
1. Visit: https://mapbender.ubec.network/application/ubec_wms
2. Click "Bioregion Mapping" in sidepane
3. Should see digitizer interface with:
   - Draw polygon tool
   - Form fields for metadata
   - Map controls

### Test 3: Draw Test Boundary
1. Click "Draw Polygon" tool
2. Click 4-5 points on map
3. Double-click to finish
4. Fill form:
   - Bioregion Name: "Test PHENOMENAL Setup"
   - Status: Proposed
   - Primary Watershed: "Test Watershed"
   - Your name and email
5. Click **Save**

### Test 4: Verify in Database
```sql
SELECT 
    bioregion_name,
    area_sqkm,
    status,
    submission_date,
    ST_AsText(geom) as geometry_wkt
FROM phenomenal.bioregion_boundaries
ORDER BY submission_date DESC
LIMIT 1;
```

Should see your test bioregion with auto-calculated area!

### Test 5: Clean Up
```sql
DELETE FROM phenomenal.bioregion_boundaries
WHERE bioregion_name = 'Test PHENOMENAL Setup';
```

---

## Spatial Features

### Auto-Calculated Fields
When you save a bioregion boundary, triggers automatically calculate:
- **area_sqkm**: Polygon area in square kilometers
- **perimeter_km**: Polygon perimeter in kilometers
- **centroid**: Geographic center point of the polygon

### POI Auto-Assignment
When you add a POI, triggers automatically:
- Extract **latitude** and **longitude** from geometry
- Assign **bioregion_code** based on spatial containment

**Example**:
```sql
-- Add a POI
INSERT INTO phenomenal.points_of_interest (
    poi_name, geom, poi_type
) VALUES (
    'Community Garden',
    ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326),
    'farm'
);

-- Check what happened
SELECT 
    poi_name,
    latitude,      -- Auto-extracted!
    longitude,     -- Auto-extracted!
    bioregion_code -- Auto-assigned!
FROM phenomenal.points_of_interest
WHERE poi_name = 'Community Garden';
```

---

## Common Issues & Solutions

### Issue 1: "Table not found"
**Cause**: Mapbender looking in wrong schema  
**Solution**: Verify `schema: phenomenal` in YAML config

### Issue 2: "Permission denied"
**Cause**: ubec_map user lacks permissions  
**Solution**: Re-run the setup SQL script which grants permissions

### Issue 3: Digitizer doesn't appear
**Cause**: Element not properly configured  
**Solution**: Check element is added to sidepane, not content

### Issue 4: Can't save boundaries
**Cause**: Database password changed but not updated in Mapbender  
**Solution**: Update `parameters.yml` with new password, restart PHP-FPM

### Issue 5: Geometry validation fails
**Cause**: Invalid polygon (self-intersections, too few points)  
**Solution**: Draw cleaner polygon with at least 4 points, no crossings

---

## Views for Analytics

### Bioregion Statistics
```sql
SELECT * FROM phenomenal.bioregion_stats;
```

Returns:
- Total number of bioregions
- Count by status (proposed/approved/active/inactive)
- Total area covered
- Average bioregion size
- Submission trends

### Approved Bioregions Only
```sql
SELECT * FROM phenomenal.approved_bioregions;
```

Filters to show only bioregions with status = 'approved'

### Recent Submissions
```sql
SELECT * FROM phenomenal.recent_submissions;
```

Shows bioregions submitted in the last 30 days

### Active POIs
```sql
SELECT * FROM phenomenal.active_pois;
```

Shows only POIs with status = 'active'

### POI Statistics
```sql
SELECT * FROM phenomenal.poi_stats;
```

Returns counts grouped by type, category, and bioregion

---

## Next Steps

1. **Security First**: Change ubec_map password
2. **Configure Mapbender**: Add digitizer elements
3. **Test Workflow**: Draw test bioregion, verify database
4. **Deploy Documentation**: Make mapping guide accessible to users
5. **Create APIs**: Build endpoints for programmatic access
6. **Dashboard Integration**: Add bioregion metrics to main dashboard

---

## File Locations Reference

**Documentation**:
- User Guide: `docs/guides/UBEC_Bioregion_Mapping_Guide.md`
- Bioregion Guide: `docs/guides/UBEC_Bioregion_Guide.md` (add link to mapping guide)

**Configuration**:
- Bioregion YAML: `digitizer_phenomenal_configuration.yaml`
- POI YAML: `poi_digitizer_phenomenal_configuration.yaml`
- Mapbender Config: `/etc/mapbender/parameters.yml` (or wherever your Mapbender is configured)

**SQL Scripts** (already executed):
- `ubec_digitizer_phenomenal_setup.sql` ✅
- `ubec_poi_phenomenal_setup.sql` ✅

**Interface**:
- Mapbender URL: https://mapbender.ubec.network/application/ubec_wms

---

## Contact for Issues

If you encounter problems:
1. Check this quick reference first
2. Review the complete setup guide
3. Verify database permissions
4. Check Mapbender logs: `/var/log/mapbender/`
5. Test database connectivity directly

---

*Quick Reference Created: November 14, 2025*  
*Schema: phenomenal (existing analytics schema)*  
*Tables: bioregion_boundaries, points_of_interest*
