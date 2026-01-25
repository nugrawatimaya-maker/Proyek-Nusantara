-- Update constraint untuk tabel employees agar menerima role 'kos-kosan'

ALTER TABLE employees DROP CONSTRAINT IF EXISTS employees_role_check;

ALTER TABLE employees 
ADD CONSTRAINT employees_role_check 
CHECK (role IN ('operasional', 'finance', 'marketing', 'hr', 'direksi', 'superadmin', 'kos-kosan'));
