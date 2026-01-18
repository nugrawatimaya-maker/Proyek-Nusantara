-- FIX PERMISSION DRAFT PENGAJUAN --
-- Pastikan TABEL sudah ada (jalankan script sebelumnya jika belum).

-- 1. Disable RLS (Ensure it is off)
ALTER TABLE draft_pengajuan DISABLE ROW LEVEL SECURITY;

-- 2. GRANT PERMISSIONS
-- Ini PENTING karena walau RLS mati, role 'anon' (web client) butuh izin akses dasar.
GRANT ALL ON TABLE draft_pengajuan TO anon;
GRANT ALL ON TABLE draft_pengajuan TO authenticated;
GRANT ALL ON TABLE draft_pengajuan TO service_role;

-- 3. Cek sequence/uuid (biasanya aman, tapi just in case)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
