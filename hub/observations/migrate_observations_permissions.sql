-- Migration: observations module permissions
-- Run once after deploying the observations module.
-- Idempotent — safe to run multiple times.
-- Date: 2026-03-06

SET search_path = ubec_hub, public;

-- ── Permissions ───────────────────────────────────────────────────────────────

INSERT INTO permissions (name, display_name, description, category, is_system)
VALUES
    (
        'observations:create',
        'Submit Observations',
        'Submit new observations for any activity',
        'observations',
        true
    ),
    (
        'observations:validate',
        'Validate Observations',
        'Mark observations as validated — lead steward and admin only',
        'observations',
        true
    )
ON CONFLICT (name) DO NOTHING;

-- ── Role assignments ──────────────────────────────────────────────────────────
-- member      → observations:create
-- contributor → observations:create
-- admin       → observations:create, observations:validate

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name IN ('member', 'contributor')
  AND p.name = 'observations:create'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'admin'
  AND p.name IN ('observations:create', 'observations:validate')
ON CONFLICT DO NOTHING;

-- ── Verify ────────────────────────────────────────────────────────────────────

SELECT
    r.name AS role,
    p.name AS permission
FROM role_permissions rp
JOIN roles       r ON r.id = rp.role_id
JOIN permissions p ON p.id = rp.permission_id
WHERE p.category = 'observations'
ORDER BY r.name, p.name;
