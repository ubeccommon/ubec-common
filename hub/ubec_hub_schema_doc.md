# UBEC Hub — Database Schema Documentation

> **Schema:** `ubec_hub`  
> **Generated:** 2026-03-06 14:07 UTC  
> **Source:** `generate_schema_doc.py`  
> Upload this file to project knowledge to keep AI sessions current.

---

## Enum Types

- **`activity_scope`** → `personal`, `living_lab`, `watershed`, `bioregional`, `network`
- **`field_type`** → `text`, `integer`, `decimal`, `boolean`, `date`, `datetime`, `select`, `multiselect`, `scale`, `geo_point`, `image_ref`, `pattern_ref`
- **`proxemic_zone`** → `intimate`, `personal`, `social`, `public`
- **`reward_status`** → `pending`, `submitted`, `confirmed`, `failed`
- **`token_type`** → `UBEC`, `UBECrc`, `UBECgpi`, `UBECtt`

---

## Tables

**Total tables:** 22

| Table | Rows |
|-------|-----:|
| `activities` | 1 |
| `activity_fields` | 13 |
| `audit_log` | 0 |
| `bioregions` | 0 |
| `deletion_requests` | 0 |
| `device_sensors` | 0 |
| `devices` | 0 |
| `gdpr_consents` | 0 |
| `living_lab_stewards` | 0 |
| `living_labs` | 0 |
| `observation_responses` | 0 |
| `observations` | 1 |
| `pattern_catalogue` | 0 |
| `permissions` | 14 |
| `readings` | 0 |
| `role_permissions` | 10 |
| `roles` | 4 |
| `steward_roles` | 2 |
| `steward_sessions` | 4 |
| `stewards` | 1 |
| `token_rewards` | 0 |
| `watersheds` | 0 |

---

## Table Details

### `activities`

*1 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `name` | `varchar(255)` | **no** | `` |
| `slug` | `varchar(100)` | **no** | `` |
| `description` | `text` | yes | `` |
| `scope` | `activity_scope` | **no** | `'personal'::activity_scope` |
| `living_lab_id` | `uuid` | yes | `` |
| `watershed_id` | `uuid` | yes | `` |
| `bioregion_id` | `uuid` | yes | `` |
| `created_by` | `uuid` | **no** | `` |
| `proxemic_zone` | `proxemic_zone` | **no** | `'personal'::proxemic_zone` |
| `starts_at` | `timestamp with time zone` | yes | `` |
| `ends_at` | `timestamp with time zone` | yes | `` |
| `is_active` | `boolean` | **no** | `true` |
| `is_template` | `boolean` | **no** | `false` |
| `pattern_id` | `uuid` | yes | `` |
| `metadata` | `jsonb` | **no** | `'{}'::jsonb` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |
| `updated_at` | `timestamp with time zone` | **no** | `now()` |

**Indexes:**

- `activities_slug_key` UNIQUE on (`slug`)
- `idx_activities_active` on (`is_active`) WHERE (is_active = true)
- `idx_activities_bioregion` on (`bioregion_id`) WHERE (bioregion_id IS NOT NULL)
- `idx_activities_created_by` on (`created_by`)
- `idx_activities_living_lab` on (`living_lab_id`) WHERE (living_lab_id IS NOT NULL)
- `idx_activities_scope` on (`scope`)
- `idx_activities_template` on (`is_template`) WHERE (is_template = true)
- `idx_activities_watershed` on (`watershed_id`) WHERE (watershed_id IS NOT NULL)
- **UNIQUE** `activities_slug_key`: `UNIQUE (slug)`

---

### `activity_fields`

*13 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `activity_id` | `uuid` | **no** | `` |
| `name` | `varchar(100)` | **no** | `` |
| `label` | `varchar(255)` | **no** | `` |
| `label_de` | `varchar(255)` | yes | `` |
| `label_pl` | `varchar(255)` | yes | `` |
| `description` | `text` | yes | `` |
| `field_type` | `field_type` | **no** | `` |
| `is_required` | `boolean` | **no** | `false` |
| `display_order` | `smallint` | **no** | `0` |
| `options` | `jsonb` | yes | `` |
| `scale_config` | `jsonb` | yes | `` |
| `unit` | `varchar(50)` | yes | `` |
| `validation` | `jsonb` | yes | `` |
| `pattern_scope` | `uuid` | yes | `` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |

**Indexes:**

- `activity_fields_activity_id_name_key` UNIQUE on (`activity_id, name`)
- `idx_activity_fields_activity` on (`activity_id`)
- `idx_activity_fields_order` on (`activity_id, display_order`)
- **UNIQUE** `activity_fields_activity_id_name_key`: `UNIQUE (activity_id, name)`

---

### `audit_log`

*0 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `steward_id` | `uuid` | yes | `` |
| `action` | `varchar(100)` | **no** | `` |
| `entity_type` | `varchar(100)` | yes | `` |
| `entity_id` | `uuid` | yes | `` |
| `old_values` | `jsonb` | yes | `` |
| `new_values` | `jsonb` | yes | `` |
| `ip_address` | `inet` | yes | `` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |

**Indexes:**

- `idx_audit_log_created` on (`created_at`)
- `idx_audit_log_entity` on (`entity_type, entity_id`)
- `idx_audit_log_steward` on (`steward_id`) WHERE (steward_id IS NOT NULL)

---

### `bioregions`

*0 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `name` | `varchar(255)` | **no** | `` |
| `code` | `varchar(50)` | **no** | `` |
| `description` | `text` | yes | `` |
| `boundary` | `geography` | yes | `` |
| `center_point` | `geography` | yes | `` |
| `area_km2` | `numeric(15,2)` | yes | `` |
| `metadata` | `jsonb` | **no** | `'{}'::jsonb` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |
| `updated_at` | `timestamp with time zone` | **no** | `now()` |

**Indexes:**

- `bioregions_code_key` UNIQUE on (`code`)
- `idx_bioregions_boundary` on (`boundary`)
- `idx_bioregions_code` on (`code`)
- **UNIQUE** `bioregions_code_key`: `UNIQUE (code)`

---

### `deletion_requests`

*0 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `steward_id` | `uuid` | **no** | `` |
| `requested_at` | `timestamp with time zone` | **no** | `now()` |
| `reason` | `text` | yes | `` |
| `status` | `varchar(50)` | **no** | `'pending'::character varying` |
| `processed_by` | `uuid` | yes | `` |
| `processed_at` | `timestamp with time zone` | yes | `` |
| `notes` | `text` | yes | `` |

**Indexes:**

- `idx_deletion_requests_status` on (`status`)
- `idx_deletion_requests_steward` on (`steward_id`)
- **CHECK** `deletion_requests_status_check`: `CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'in_progress'::character varying, 'completed'::character varying, 'rejected'::character varying])::text[])))`

---

### `device_sensors`

*0 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `device_id` | `uuid` | **no** | `` |
| `phenomenon` | `varchar(100)` | **no** | `` |
| `unit` | `varchar(50)` | yes | `` |
| `sensor_type` | `varchar(100)` | yes | `` |
| `accuracy` | `numeric(8,4)` | yes | `` |
| `min_value` | `numeric(12,4)` | yes | `` |
| `max_value` | `numeric(12,4)` | yes | `` |
| `metadata` | `jsonb` | **no** | `'{}'::jsonb` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |

**Indexes:**

- `idx_device_sensors_device` on (`device_id`)

---

### `devices`

*0 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `sensebox_id` | `varchar(100)` | yes | `` |
| `external_id` | `varchar(255)` | yes | `` |
| `name` | `varchar(255)` | **no** | `` |
| `description` | `text` | yes | `` |
| `device_type` | `varchar(100)` | **no** | `` |
| `steward_id` | `uuid` | yes | `` |
| `living_lab_id` | `uuid` | yes | `` |
| `location` | `geography` | yes | `` |
| `altitude_m` | `numeric(8,2)` | yes | `` |
| `status` | `varchar(50)` | **no** | `'active'::character varying` |
| `last_seen` | `timestamp with time zone` | yes | `` |
| `metadata` | `jsonb` | **no** | `'{}'::jsonb` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |
| `updated_at` | `timestamp with time zone` | **no** | `now()` |

**Indexes:**

- `devices_sensebox_id_key` UNIQUE on (`sensebox_id`)
- `idx_devices_living_lab` on (`living_lab_id`) WHERE (living_lab_id IS NOT NULL)
- `idx_devices_location` on (`location`) WHERE (location IS NOT NULL)
- `idx_devices_sensebox_id` on (`sensebox_id`) WHERE (sensebox_id IS NOT NULL)
- `idx_devices_status` on (`status`)
- `idx_devices_steward` on (`steward_id`) WHERE (steward_id IS NOT NULL)
- **CHECK** `devices_device_type_check`: `CHECK (((device_type)::text = ANY ((ARRAY['sensebox'::character varying, 'custom'::character varying, 'manual'::character varying, 'weather_station'::character varying, 'other'::character varying])::text[])))`
- **CHECK** `devices_status_check`: `CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying, 'maintenance'::character varying, 'decommissioned'::character varying])::text[])))`
- **UNIQUE** `devices_sensebox_id_key`: `UNIQUE (sensebox_id)`

---

### `gdpr_consents`

*0 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `steward_id` | `uuid` | **no** | `` |
| `consent_type` | `varchar(100)` | **no** | `` |
| `version` | `varchar(20)` | **no** | `` |
| `given` | `boolean` | **no** | `` |
| `ip_address` | `inet` | yes | `` |
| `user_agent` | `text` | yes | `` |
| `given_at` | `timestamp with time zone` | **no** | `now()` |
| `withdrawn_at` | `timestamp with time zone` | yes | `` |

**Indexes:**

- `idx_gdpr_consents_active` on (`steward_id, consent_type`) WHERE (withdrawn_at IS NULL)
- `idx_gdpr_consents_steward` on (`steward_id`)
- `idx_gdpr_consents_type` on (`consent_type`)

---

### `living_lab_stewards`

*0 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `living_lab_id` | `uuid` | **no** | `` |
| `steward_id` | `uuid` | **no** | `` |
| `role` | `varchar(50)` | **no** | `'steward'::character varying` |
| `joined_at` | `timestamp with time zone` | **no** | `now()` |
| `invited_by` | `uuid` | yes | `` |
| `is_active` | `boolean` | **no** | `true` |

**Indexes:**

- `idx_lab_stewards_steward` on (`steward_id`)
- **CHECK** `living_lab_stewards_role_check`: `CHECK (((role)::text = ANY ((ARRAY['steward'::character varying, 'lead_steward'::character varying, 'observer'::character varying])::text[])))`

---

### `living_labs`

*0 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `name` | `varchar(255)` | **no** | `` |
| `slug` | `varchar(100)` | **no** | `` |
| `description` | `text` | yes | `` |
| `watershed_id` | `uuid` | yes | `` |
| `bioregion_id` | `uuid` | yes | `` |
| `location` | `geography` | yes | `` |
| `boundary` | `geography` | yes | `` |
| `address` | `text` | yes | `` |
| `country_code` | `char(2)` | yes | `` |
| `proxemic_zone` | `proxemic_zone` | **no** | `'social'::proxemic_zone` |
| `is_active` | `boolean` | **no** | `true` |
| `metadata` | `jsonb` | **no** | `'{}'::jsonb` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |
| `updated_at` | `timestamp with time zone` | **no** | `now()` |

**Indexes:**

- `idx_living_labs_active` on (`is_active`) WHERE (is_active = true)
- `idx_living_labs_bioregion` on (`bioregion_id`)
- `idx_living_labs_location` on (`location`)
- `idx_living_labs_slug` on (`slug`)
- `idx_living_labs_watershed` on (`watershed_id`)
- `living_labs_slug_key` UNIQUE on (`slug`)
- **UNIQUE** `living_labs_slug_key`: `UNIQUE (slug)`

---

### `observation_responses`

*0 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `observation_id` | `uuid` | **no** | `` |
| `field_id` | `uuid` | **no** | `` |
| `value_text` | `text` | yes | `` |
| `value_pattern` | `uuid` | yes | `` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |

**Indexes:**

- `idx_obs_responses_field` on (`field_id`)
- `idx_obs_responses_observation` on (`observation_id`)
- `idx_obs_responses_pattern` on (`value_pattern`) WHERE (value_pattern IS NOT NULL)
- `observation_responses_observation_id_field_id_key` UNIQUE on (`observation_id, field_id`)
- **UNIQUE** `observation_responses_observation_id_field_id_key`: `UNIQUE (observation_id, field_id)`

---

### `observations`

*1 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `activity_id` | `uuid` | **no** | `` |
| `steward_id` | `uuid` | **no** | `` |
| `observed_at` | `timestamp with time zone` | **no** | `` |
| `location` | `geography` | yes | `` |
| `location_note` | `text` | yes | `` |
| `proxemic_zone` | `proxemic_zone` | **no** | `` |
| `qualitative_notes` | `text` | **no** | `` |
| `device_id` | `uuid` | yes | `` |
| `language` | `char(2)` | **no** | `'en'::bpchar` |
| `is_validated` | `boolean` | **no** | `false` |
| `validated_by` | `uuid` | yes | `` |
| `validated_at` | `timestamp with time zone` | yes | `` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |
| `updated_at` | `timestamp with time zone` | **no** | `now()` |

**Indexes:**

- `idx_observations_activity` on (`activity_id`)
- `idx_observations_device` on (`device_id`) WHERE (device_id IS NOT NULL)
- `idx_observations_location` on (`location`) WHERE (location IS NOT NULL)
- `idx_observations_observed_at` on (`observed_at`)
- `idx_observations_proxemic` on (`proxemic_zone`)
- `idx_observations_steward` on (`steward_id`)
- **CHECK** `observations_language_check`: `CHECK ((language = ANY (ARRAY['de'::bpchar, 'en'::bpchar, 'pl'::bpchar])))`

---

### `pattern_catalogue`

*0 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `code` | `varchar(50)` | yes | `` |
| `name` | `varchar(255)` | **no** | `` |
| `name_local` | `varchar(255)` | yes | `` |
| `language` | `char(2)` | **no** | `'en'::bpchar` |
| `problem` | `text` | **no** | `` |
| `solution` | `text` | **no** | `` |
| `discussion` | `text` | yes | `` |
| `cultural_context` | `text` | yes | `` |
| `bioregion_id` | `uuid` | yes | `` |
| `source` | `varchar(100)` | yes | `` |
| `source_reference` | `text` | yes | `` |
| `contributed_by` | `uuid` | yes | `` |
| `is_canonical` | `boolean` | **no** | `false` |
| `larger_patterns` | `uuid[]` | yes | `` |
| `smaller_patterns` | `uuid[]` | yes | `` |
| `proxemic_zone` | `proxemic_zone` | **no** | `'public'::proxemic_zone` |
| `is_active` | `boolean` | **no** | `true` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |
| `updated_at` | `timestamp with time zone` | **no** | `now()` |

**Indexes:**

- `idx_patterns_bioregion` on (`bioregion_id`) WHERE (bioregion_id IS NOT NULL)
- `idx_patterns_canonical` on (`is_canonical`) WHERE (is_canonical = true)
- `idx_patterns_code` on (`code`) WHERE (code IS NOT NULL)
- `idx_patterns_source` on (`source`)
- `pattern_catalogue_code_key` UNIQUE on (`code`)
- **UNIQUE** `pattern_catalogue_code_key`: `UNIQUE (code)`

---

### `permissions`

*14 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `name` | `varchar(100)` | **no** | `` |
| `display_name` | `varchar(255)` | **no** | `` |
| `description` | `text` | yes | `` |
| `category` | `varchar(50)` | yes | `` |
| `is_system` | `boolean` | **no** | `false` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |

**Indexes:**

- `permissions_name_key` UNIQUE on (`name`)
- **UNIQUE** `permissions_name_key`: `UNIQUE (name)`

---

### `readings`

*0 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `device_id` | `uuid` | **no** | `` |
| `sensor_id` | `uuid` | yes | `` |
| `phenomenon` | `varchar(100)` | **no** | `` |
| `value` | `numeric(12,4)` | **no** | `` |
| `unit` | `varchar(50)` | yes | `` |
| `recorded_at` | `timestamp with time zone` | **no** | `` |
| `is_valid` | `boolean` | **no** | `true` |
| `quality_note` | `text` | yes | `` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |

**Indexes:**

- `idx_readings_device` on (`device_id, recorded_at`)
- `idx_readings_phenomenon` on (`phenomenon, recorded_at`)
- `idx_readings_sensor` on (`sensor_id, recorded_at`) WHERE (sensor_id IS NOT NULL)

---

### `role_permissions`

*10 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `role_id` | `uuid` | **no** | `` |
| `permission_id` | `uuid` | **no** | `` |

---

### `roles`

*4 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `name` | `varchar(50)` | **no** | `` |
| `display_name` | `varchar(100)` | **no** | `` |
| `description` | `text` | yes | `` |
| `is_system` | `boolean` | **no** | `false` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |

**Indexes:**

- `roles_name_key` UNIQUE on (`name`)
- **UNIQUE** `roles_name_key`: `UNIQUE (name)`

---

### `steward_roles`

*2 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `steward_id` | `uuid` | **no** | `` |
| `role_id` | `uuid` | **no** | `` |
| `granted_by` | `uuid` | yes | `` |
| `granted_at` | `timestamp with time zone` | **no** | `now()` |

---

### `steward_sessions`

*4 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `steward_id` | `uuid` | **no** | `` |
| `token_hash` | `varchar(64)` | **no** | `` |
| `ip_address` | `inet` | yes | `` |
| `user_agent` | `text` | yes | `` |
| `expires_at` | `timestamp with time zone` | **no** | `` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |
| `last_used_at` | `timestamp with time zone` | **no** | `now()` |
| `is_revoked` | `boolean` | **no** | `false` |

**Indexes:**

- `idx_sessions_active` on (`steward_id, is_revoked`) WHERE (is_revoked = false)
- `idx_sessions_expires` on (`expires_at`)
- `idx_sessions_steward` on (`steward_id`)
- `idx_sessions_token_hash` on (`token_hash`)
- `steward_sessions_token_hash_key` UNIQUE on (`token_hash`)
- **UNIQUE** `steward_sessions_token_hash_key`: `UNIQUE (token_hash)`

---

### `stewards`

*1 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `email` | `varchar(255)` | **no** | `` |
| `password_hash` | `varchar(255)` | **no** | `` |
| `full_name` | `varchar(255)` | yes | `` |
| `display_name` | `varchar(100)` | yes | `` |
| `stellar_public_key` | `varchar(56)` | yes | `` |
| `preferred_language` | `char(2)` | yes | `'en'::bpchar` |
| `is_active` | `boolean` | **no** | `true` |
| `email_verified` | `boolean` | **no** | `false` |
| `gdpr_consent_given` | `boolean` | **no** | `false` |
| `gdpr_consent_at` | `timestamp with time zone` | yes | `` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |
| `updated_at` | `timestamp with time zone` | **no** | `now()` |
| `verification_token` | `varchar(255)` | yes | `` |
| `reset_token` | `varchar(255)` | yes | `` |
| `reset_token_expires` | `timestamp with time zone` | yes | `` |

**Indexes:**

- `idx_stewards_active` on (`is_active`) WHERE (is_active = true)
- `idx_stewards_email` on (`email`)
- `idx_stewards_reset_token` on (`reset_token`) WHERE (reset_token IS NOT NULL)
- `idx_stewards_stellar` on (`stellar_public_key`) WHERE (stellar_public_key IS NOT NULL)
- `idx_stewards_verification_token` on (`verification_token`) WHERE (verification_token IS NOT NULL)
- `stewards_email_key` UNIQUE on (`email`)
- `stewards_stellar_public_key_key` UNIQUE on (`stellar_public_key`)
- **CHECK** `stewards_preferred_language_check`: `CHECK ((preferred_language = ANY (ARRAY['de'::bpchar, 'en'::bpchar, 'pl'::bpchar])))`
- **UNIQUE** `stewards_email_key`: `UNIQUE (email)`
- **UNIQUE** `stewards_stellar_public_key_key`: `UNIQUE (stellar_public_key)`

---

### `token_rewards`

*0 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `steward_id` | `uuid` | **no** | `` |
| `trigger_type` | `varchar(100)` | **no** | `` |
| `trigger_id` | `uuid` | yes | `` |
| `token_type` | `token_type` | **no** | `` |
| `amount` | `numeric(18,7)` | **no** | `` |
| `stellar_tx_hash` | `varchar(64)` | yes | `` |
| `stellar_ledger` | `bigint` | yes | `` |
| `status` | `reward_status` | **no** | `'pending'::reward_status` |
| `failure_reason` | `text` | yes | `` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |
| `confirmed_at` | `timestamp with time zone` | yes | `` |

**Indexes:**

- `idx_rewards_status` on (`status`)
- `idx_rewards_steward` on (`steward_id`)
- `idx_rewards_trigger` on (`trigger_type, trigger_id`)
- `idx_rewards_tx_hash` on (`stellar_tx_hash`) WHERE (stellar_tx_hash IS NOT NULL)

---

### `watersheds`

*0 rows*

**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | **no** | `uuid_generate_v4()` |
| `name` | `varchar(255)` | **no** | `` |
| `code` | `varchar(50)` | yes | `` |
| `bioregion_id` | `uuid` | yes | `` |
| `boundary` | `geography` | yes | `` |
| `area_km2` | `numeric(15,2)` | yes | `` |
| `metadata` | `jsonb` | **no** | `'{}'::jsonb` |
| `created_at` | `timestamp with time zone` | **no** | `now()` |
| `updated_at` | `timestamp with time zone` | **no** | `now()` |

**Indexes:**

- `idx_watersheds_bioregion` on (`bioregion_id`)
- `idx_watersheds_boundary` on (`boundary`)
- `watersheds_code_key` UNIQUE on (`code`)
- **UNIQUE** `watersheds_code_key`: `UNIQUE (code)`

---

## Functions

| Function | Arguments | Returns | Language |
|----------|-----------|---------|----------|
| `set_updated_at` | — | `trigger` | plpgsql |

---


*This project uses the services of Claude and Anthropic PBC to inform our*
*decisions and recommendations.*
*Generated by generate_schema_doc.py · 2026-03-06 14:07 UTC*
