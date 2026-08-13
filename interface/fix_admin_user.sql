-- ============================================================================
-- UBEC Protocol - Fix admin@ubec.network User
-- ============================================================================
-- Restores admin@ubec.network to super_admin role
-- ============================================================================

SET search_path TO ubec_ui, public;

-- Update admin@ubec.network to super_admin with proper flags
UPDATE ubec_ui.users 
SET role = 'super_admin',
    is_admin = true,
    is_active = true,
    updated_at = CURRENT_TIMESTAMP
WHERE email = 'admin@ubec.network';

-- Verify the constraint exists
SELECT 'Checking constraint:' as info;
SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'ubec_ui.users'::regclass 
  AND contype = 'c';

-- Show all admin users now
SELECT 'Admin users after fix:' as info;
SELECT id, email, role, is_admin, is_active
FROM ubec_ui.users 
WHERE role IN ('reviewer', 'admin', 'super_admin') 
   OR is_admin = true
ORDER BY id;

-- Show all users
SELECT 'All users:' as info;
SELECT id, email, role, is_admin, is_active
FROM ubec_ui.users
ORDER BY id;

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE 'admin@ubec.network restored to super_admin';
    RAISE NOTICE '';
END $$;
