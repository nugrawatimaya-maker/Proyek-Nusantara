-- MIGRATION: RELAX AUTHENTICATION RESTRICTIONS
-- Goal: Prevent account locking on double login. Instead, invalidate the old session.

-- 1. Redefine verify_access_code to REMOVE locking logic
CREATE OR REPLACE FUNCTION verify_access_code(input_code TEXT)
RETURNS JSON AS $$
DECLARE
  found_user employees%ROWTYPE;
  new_token TEXT;
BEGIN
  -- Cari User
  SELECT * INTO found_user FROM employees WHERE access_code = input_code LIMIT 1;

  -- A. Jika User Tidak Ditemukan
  IF found_user.id IS NULL THEN
    RETURN json_build_object('success', FALSE, 'message', 'Kode Akses Salah');
  END IF;

  -- B. Jika Akun Terkunci (Manual Check - we keep manual locking capability for Admin)
  -- NOTE: We primarily want to stop AUTO-LOCKING. If admin manually locked it, keep it locked.
  IF found_user.is_locked THEN
    RETURN json_build_object('success', FALSE, 'message', 'AKUN TERKUNCI! Hubungi Admin untuk buka blokir.');
  END IF;

  -- C. GENERATE TOKEN (Auto-kick old session by overwriting token)
  -- We removed the component that checks active_session_token and sets is_locked = TRUE
  
  new_token := md5(random()::text || clock_timestamp()::text);

  UPDATE employees
  SET active_session_token = new_token,
      last_login_at = now()
  WHERE id = found_user.id;

  RETURN json_build_object(
    'success', TRUE,
    'message', 'Login Berhasil',
    'id', found_user.id,
    'full_name', found_user.full_name,
    'role', found_user.role,
    'access_code', found_user.access_code, 
    'session_token', new_token
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Unlock ALL currently locked accounts (Reset state)
-- Exclude Superadmin/Direksi from blanket updates just in case, though they shouldn't be locked usually.
UPDATE employees 
SET is_locked = FALSE, active_session_token = NULL 
WHERE is_locked = TRUE AND role NOT IN ('superadmin', 'direksi');

-- 3. Ensure 'active_session_token' column exists (Idempotency check)
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'employees' AND column_name = 'active_session_token') THEN 
        ALTER TABLE employees ADD COLUMN active_session_token TEXT; 
    END IF; 
END $$;
