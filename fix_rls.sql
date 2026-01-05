-- 1. Cek Policy yang sudah ada (Optional, hanya untuk info)
-- SELECT * FROM pg_policies WHERE tablename = 'activity_logs';

-- 2. Hapus policy lama jika ada (untuk menghindari duplikat/konflik)
-- Ganti 'Enable insert for authenticated users only' dengan nama policy Anda jika berbeda
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON "public"."activity_logs";
DROP POLICY IF EXISTS "Izinkan Insert Semua User" ON "public"."activity_logs";

-- 3. Buat Policy Baru yang Mengizinkan Insert dari PUBLIC (Anonim)
CREATE POLICY "Izinkan Insert Semua User"
ON "public"."activity_logs"
FOR INSERT
TO public
WITH CHECK (true);

-- 4. Enable RLS (Pastikan RLS aktif, meskipun policy sudah dibuat)
ALTER TABLE "public"."activity_logs" ENABLE ROW LEVEL SECURITY;

-- 5. (Opsional) Policy untuk SELECT/READ (Biar bisa dilihat di halaman Log)
-- Biasanya public tidak boleh baca sembarangan, tapi untuk admin panel internal bisa di-set:
-- CREATE POLICY "Izinkan Read Authenticated" ON "public"."activity_logs" FOR SELECT TO authenticated USING (true);
