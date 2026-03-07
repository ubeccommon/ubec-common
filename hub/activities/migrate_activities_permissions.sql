-- Migration: activities module permissions
-- Run once after deploying the activities module.
-- Idempotent — safe to run multiple times.
-- Date: 2026-03-06

SET search_path = ubec_hub, public;

-- ── Permissions ───────────────────────────────────────────────────────────────

INSERT INTO permissions (name, display_name, description, category, is_system)
VALUES
    (
        'activities:read',
        'View Activities',
        'List and view activities and their fields',
        'activities',
        true
    ),
    (
        'activities:create',
        'Create Activities',
        'Create new activities and add fields',
        'activities',
        true
    ),
    (
        'activities:manage',
        'Manage Activities',
        'Update, deactivate, and seed activities; manage fields',
        'activities',
        true
    )
ON CONFLICT (name) DO NOTHING;

-- ── Role assignments ──────────────────────────────────────────────────────────
-- member      → activities:read
-- contributor → activities:read, activities:create
-- admin       → activities:read, activities:create, activities:manage

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'member'
  AND p.name = 'activities:read'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'contributor'
  AND p.name IN ('activities:read', 'activities:create')
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'admin'
  AND p.name IN ('activities:read', 'activities:create', 'activities:manage')
ON CONFLICT DO NOTHING;

-- ── Verify ────────────────────────────────────────────────────────────────────

SELECT
    r.name        AS role,
    p.name        AS permission
FROM role_permissions rp
JOIN roles       r ON r.id = rp.role_id
JOIN permissions p ON p.id = rp.permission_id
WHERE p.category = 'activities'
ORDER BY r.name, p.name;
