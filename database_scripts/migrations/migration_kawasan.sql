-- 1. Tambah Kolom Kawasan di Master Proyek (Jika belum ada)
ALTER TABLE master_proyek ADD COLUMN IF NOT EXISTS kawasan TEXT;

-- 2. Update Data Lama menjadi 'Sunrise City Maros'
-- Asumsi: Semua data yang ada saat ini adalah data Maros
UPDATE master_proyek 
SET kawasan = 'Sunrise City Maros' 
WHERE kawasan IS NULL OR kawasan = '';

-- 3. Opsional: Pastikan index agar searching cepat
CREATE INDEX IF NOT EXISTS idx_master_proyek_kawasan ON master_proyek(kawasan);
