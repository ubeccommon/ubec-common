-- ============================================================================
-- UBEC Protocol - Set Single Admin User
-- ============================================================================
-- Keep only stewardship@ubec.network as super_admin
-- ============================================================================

SET search_path TO ubec_ui, public;

-- Remove admin privileges from other users
UPDATE ubec_ui.users 
SET role = 'applicant',
    is_admin = false,
    updated_at = CURRENT_TIMESTAMP
WHERE email IN ('admin@ubec.network', 'reviewer@ubec.network');

-- Ensure stewardship@ubec.network is super_admin
UPDATE ubec_ui.users 
SET role = 'super_admin',
    is_admin = true,
    is_active = true,
    updated_at = CURRENT_TIMESTAMP
WHERE email = 'stewardship@ubec.network';

-- Verify
SELECT 'Admin users:' as info;
SELECT id, email, role, is_admin, is_active
FROM ubec_ui.users 
WHERE role IN ('reviewer', 'admin', 'super_admin') 
   OR is_admin = true;

SELECT 'All users:' as info;
SELECT id, email, role, is_admin
FROM ubec_ui.users
ORDER BY id;

DO $$
BEGIN
    RAISE NOTICE 'Only stewardship@ubec.network is now super_admin';
END $$;
