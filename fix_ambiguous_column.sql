-- FIX: Ambiguous column reference in admin_list_employees
-- Masalah: Kolom 'access_code' ambigu antara parameter output dan kolom tabel.
-- Solusi: Menggunakan 'employees.access_code' secara eksplisit.

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
  -- Auth Check (Fixed: qualified employees.access_code)
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
