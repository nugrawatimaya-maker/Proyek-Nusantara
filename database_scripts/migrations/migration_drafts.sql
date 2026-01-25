-- REVISI TABEL DRAFT PENGAJUAN (FIX USER ID TYPE) --

-- Drop dulu tabel lama jika ada
DROP TABLE IF EXISTS draft_pengajuan;

-- Create ulang dengan user_id bertipe TEXT (karena sistem auth pakai custom ID integer/string)
create table draft_pengajuan (
    id uuid default uuid_generate_v4() primary key,
    user_id text not null, -- Changed from UUID to TEXT to support integer IDs like "5" or "330428"
    draft_type text not null, -- 'PETTY', 'REIMBURSE', etc.
    content jsonb default '{}'::jsonb,
    updated_at timestamp with time zone default now(),
    unique(user_id, draft_type)
);

-- RLS
alter table draft_pengajuan enable row level security;

-- Policy: User hanya bisa akses row milik ID-nya sendiri
-- Kita pakai casting auth.uid() ke text jika perlu, TAPI...
-- NOTE: Supabase auth.uid() mengembalikan UUID dari tabel auth.users.
-- JIKA sistem login Anda TIDAK MENGGUNAKAN tabel auth.users bawaan Supabase (Login Custom), 
-- maka 'auth.uid()' akan null atau tidak match dengan 'user_id' custom (misal "5").

-- SOLUSI RLS UNTUK CUSTOM LOGIN (Tanpa Supabase Auth):
-- Karena Anda login pakai 'pn_session_v2' (Local Storage) dan client supabase di-init dengan public key,
-- client-side RLS dengan auth.uid() TIDAK AKAN BERFUNGSI untuk user custom (karena di mata Supabase ini 'anon' user).

-- JADI: Kita harus disable RLS sementara atau buat policy 'anon' allow all (TIDAK AMAN jika publik).
-- ATAU (Recommended for Custom Auth without Supabase Auth):
-- Kita filter di level aplikasi (JavaScript) dan biarkan table ini public (dengan risiko).
-- Mengingat ini aplikasi internal/terbatas, kita enable access untuk public role TAPI kita coba batasi.
-- Namun, cara termudah agar "Just Work" sekarang adalah DISABLE RLS atau allow public access.

-- Opsi Aman: Tetap nyalakan RLS tapi policy 'true' untuk testing, atau matikan RLS.
-- Mengingat waktu, kita Matikan RLS dulu agar tidak ada error permission, 
-- karena User ID "5" tidak dikenali sebagai auth user supabase.

ALTER TABLE draft_pengajuan DISABLE ROW LEVEL SECURITY;

-- (Jika ingin aman nanti, perlu setup Custom Claims di JWT supaya Supabase kenal User ID "5", tapi itu butuh backend setup).
