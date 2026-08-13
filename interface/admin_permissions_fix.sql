-- ============================================================================
-- UBEC Protocol - Admin Permissions Schema FIX
-- ============================================================================
-- Fixes for installation issues:
--   1. users_role_check constraint doesn't include 'super_admin'
--   2. FILTER syntax not supported (PostgreSQL version compatibility)
--   3. v_application_stats view failed to create
--
-- Run with: psql -U ubec_ui_user -d ubec_ui_interface -h localhost -f admin_permissions_fix.sql
-- ============================================================================

SET search_path TO ubec_ui, public;

-- ============================================================================
-- 1. FIX: Update users role CHECK constraint to include super_admin
-- ============================================================================

-- First, check current constraint
SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'ubec_ui.users'::regclass 
  AND conname LIKE '%role%';

-- Drop the existing constraint
ALTER TABLE ubec_ui.users DROP CONSTRAINT IF EXISTS users_role_check;

-- Add new constraint with all valid roles including super_admin
ALTER TABLE ubec_ui.users ADD CONSTRAINT users_role_check 
CHECK (role IN ('applicant', 'reviewer', 'admin', 'super_admin'));

-- Verify constraint was updated
DO $$
BEGIN
    RAISE NOTICE 'Updated role constraint to include: applicant, reviewer, admin, super_admin';
END $$;

-- ============================================================================
-- 2. FIX: Create v_application_stats view with CASE WHEN (PostgreSQL compatible)
-- ============================================================================

-- Drop if partially created
DROP VIEW IF EXISTS ubec_ui.v_application_stats;

-- Create view using CASE WHEN for broader PostgreSQL compatibility
CREATE OR REPLACE VIEW ubec_ui.v_application_stats AS
SELECT
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count,
    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_count,
    COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected_count,
    COUNT(CASE WHEN status = 'under_review' THEN 1 END) as under_review_count,
    COUNT(*) as total_count,
    SUM(CASE WHEN status = 'pending' THEN requested_amount ELSE 0 END) as pending_amount,
    SUM(CASE WHEN status = 'approved' THEN approved_amount ELSE 0 END) as approved_amount,
    AVG(
        CASE WHEN decided_at IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (decided_at - submitted_at))/86400 
        ELSE NULL END
    )::INTEGER as avg_days_to_decision
FROM ubec_ui.applications;

COMMENT ON VIEW ubec_ui.v_application_stats IS 
'Aggregated application statistics';

-- Grant permissions
GRANT SELECT ON ubec_ui.v_application_stats TO ubec_ui_user;

DO $$
BEGIN
    RAISE NOTICE 'Created v_application_stats view with PostgreSQL-compatible syntax';
END $$;

-- ============================================================================
-- 3. FIX: Now insert the super_admin user
-- ============================================================================

-- Insert or update admin@ubec.network as super_admin
INSERT INTO ubec_ui.users (
    email, 
    password_hash, 
    full_name, 
    display_name, 
    role, 
    is_active, 
    is_verified, 
    is_admin,
    password_changed_at
) VALUES (
    'stewardship@ubec.network',
    '$2b$12$0xWojIz6F/ovWFJK0xgTmeFLqLNFXEeyQVZV5x1IX55N9urT6cCMS',
    'System Administrator',
    'Admin',
    'super_admin',
    true,
    true,
    true,
    NULL
)
ON CONFLICT (email) DO UPDATE SET
    role = 'super_admin',
    is_admin = true,
    is_active = true,
    updated_at = CURRENT_TIMESTAMP;

DO $$
BEGIN
    RAISE NOTICE 'Created/updated admin@ubec.network with super_admin role';
END $$;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Show admin users
SELECT email, role, is_admin, is_active 
FROM ubec_ui.users 
WHERE role IN ('reviewer', 'admin', 'super_admin') OR is_admin = true;

-- Show application stats (test the view)
SELECT * FROM ubec_ui.v_application_stats;

-- Show constraint
SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'ubec_ui.users'::regclass 
  AND conname LIKE '%role%';

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Fix script completed successfully!';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';
END $$;
