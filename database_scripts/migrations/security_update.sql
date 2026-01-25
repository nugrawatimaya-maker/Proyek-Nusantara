-- 1. Tambah Kolom Pendukung di Tabel Employees
ALTER TABLE employees ADD COLUMN IF NOT EXISTS active_session_token TEXT;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT FALSE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;

-- DROP FUNCTION OLD VERSION (To avoid return type conflict)
DROP FUNCTION IF EXISTS verify_access_code(text);
DROP FUNCTION IF EXISTS admin_list_employees(text);

-- 2. Fungsi Login Utama (Refined: Returns JSON)
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

  -- B. Jika Akun Terkunci
  IF found_user.is_locked THEN
    RETURN json_build_object('success', FALSE, 'message', 'AKUN TERKUNCI! Hubungi Admin untuk buka blokir.');
  END IF;

  -- C. Cek Double Login (Kecuali Superadmin)
  IF found_user.role <> 'superadmin' AND found_user.active_session_token IS NOT NULL THEN
    -- Ada sesi aktif! KUNCI AKUN INI SEKARANG.
    UPDATE employees 
    SET is_locked = TRUE, active_session_token = NULL 
    WHERE id = found_user.id;

    RETURN json_build_object('success', FALSE, 'message', 'LOGIN GANDA TERDETEKSI! Akun otomatis DIKUNCI demi keamanan.');
  END IF;

  -- D. Login Sukses -> Generate Token Baru
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

-- 3. Fungsi Cek Sesi (Heartbeat)
CREATE OR REPLACE FUNCTION check_session_validity(p_user_id BIGINT, p_token TEXT)
RETURNS BOOLEAN AS $$
DECLARE
  is_valid BOOLEAN;
  is_locked_status BOOLEAN;
BEGIN
  -- Cek apakah user terkunci
  SELECT is_locked INTO is_locked_status FROM employees WHERE id = p_user_id;
  
  IF is_locked_status THEN
    RETURN FALSE;
  END IF;

  -- Cek apakah token cocok
  SELECT (active_session_token = p_token) INTO is_valid 
  FROM employees 
  WHERE id = p_user_id;

  RETURN COALESCE(is_valid, FALSE);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4. Fungsi Admin Unlock
CREATE OR REPLACE FUNCTION admin_unlock_account(p_admin_code TEXT, p_target_id BIGINT)
RETURNS JSON AS $$
DECLARE
  admin_data employees%ROWTYPE;
BEGIN
  -- Cek Admin
  SELECT * INTO admin_data FROM employees WHERE access_code = p_admin_code AND role IN ('superadmin', 'direksi') LIMIT 1;
  
  IF admin_data.id IS NULL THEN
    RETURN json_build_object('success', FALSE, 'message', 'Unauthorized Admin');
  END IF;

  -- Unlock Target
  UPDATE employees 
  SET is_locked = FALSE, active_session_token = NULL 
  WHERE id = p_target_id;

  RETURN json_build_object('success', TRUE, 'message', 'Akun berhasil dibuka kembali');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. Fungsi List Employees (Update untuk return is_locked)
CREATE OR REPLACE FUNCTION admin_list_employees(p_admin_code TEXT)
RETURNS TABLE (
  id BIGINT,
  full_name TEXT,
  role TEXT,
  access_code TEXT,
  is_locked BOOLEAN,
  last_login_at TIMESTAMP WITH TIME ZONE
) AS $$
DECLARE
  admin_data employees%ROWTYPE;
BEGIN
  -- Auth Check
  SELECT * INTO admin_data FROM employees WHERE employees.access_code = p_admin_code AND role IN ('superadmin', 'direksi') LIMIT 1;
  
  IF admin_data.id IS NULL THEN
    RAISE EXCEPTION 'Unauthorized';
  END IF;

  RETURN QUERY 
  SELECT e.id, e.full_name, e.role, e.access_code, e.is_locked, e.last_login_at 
  FROM employees e
  ORDER BY e.full_name ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
