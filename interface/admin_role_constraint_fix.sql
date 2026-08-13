-- ============================================================================
-- UBEC Protocol - Role Constraint Diagnostic and Fix
-- ============================================================================
-- The CHECK constraint couldn't be added because some rows have invalid roles.
-- This script will:
--   1. Find all unique role values in the users table
--   2. Update any invalid roles to 'applicant'
--   3. Add the CHECK constraint
-- ============================================================================

SET search_path TO ubec_ui, public;

-- ============================================================================
-- 1. DIAGNOSTIC: Show all unique roles in the users table
-- ============================================================================

SELECT 'Current role values in users table:' as info;

SELECT role, COUNT(*) as user_count 
FROM ubec_ui.users 
GROUP BY role 
ORDER BY role;

-- Show users with potentially invalid roles
SELECT 'Users with roles NOT in (applicant, reviewer, admin, super_admin):' as info;

SELECT id, email, role, is_admin, created_at
FROM ubec_ui.users
WHERE role NOT IN ('applicant', 'reviewer', 'admin', 'super_admin')
   OR role IS NULL;

-- ============================================================================
-- 2. FIX: Update any invalid roles to 'applicant' (default safe role)
-- ============================================================================

-- Update NULL roles to 'applicant'
UPDATE ubec_ui.users 
SET role = 'applicant' 
WHERE role IS NULL;

-- Update any other invalid roles to 'applicant'
-- (This preserves is_admin flag if they should still have admin access)
UPDATE ubec_ui.users 
SET role = 'applicant' 
WHERE role NOT IN ('applicant', 'reviewer', 'admin', 'super_admin');

-- Show what we have now
SELECT 'After cleanup - role distribution:' as info;

SELECT role, COUNT(*) as user_count 
FROM ubec_ui.users 
GROUP BY role 
ORDER BY role;

-- ============================================================================
-- 3. ADD CONSTRAINT: Now safe to add the CHECK constraint
-- ============================================================================

-- Drop if exists (in case partial state)
ALTER TABLE ubec_ui.users DROP CONSTRAINT IF EXISTS users_role_check;

-- Add the constraint
ALTER TABLE ubec_ui.users ADD CONSTRAINT users_role_check 
CHECK (role IN ('applicant', 'reviewer', 'admin', 'super_admin'));

-- Verify constraint exists
SELECT 'Constraint verification:' as info;

SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'ubec_ui.users'::regclass 
  AND conname = 'users_role_check';

-- ============================================================================
-- 4. VERIFY: Show admin users
-- ============================================================================

SELECT 'Admin users:' as info;

SELECT id, email, role, is_admin, is_active, last_login_at
FROM ubec_ui.users 
WHERE role IN ('reviewer', 'admin', 'super_admin') 
   OR is_admin = true
ORDER BY 
    CASE role 
        WHEN 'super_admin' THEN 1 
        WHEN 'admin' THEN 2 
        WHEN 'reviewer' THEN 3 
        ELSE 4 
    END;

-- ============================================================================
-- DONE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Role constraint fix completed!';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Valid roles are now: applicant, reviewer, admin, super_admin';
    RAISE NOTICE '';
END $$;
