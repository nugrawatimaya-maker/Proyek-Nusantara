-- 1. Tambah Kolom Kawasan di Referensi Blok
ALTER TABLE referensi_blok ADD COLUMN IF NOT EXISTS kawasan TEXT;

-- 2. Update Data Lama menjadi 'Sunrise City Maros'
-- Semua blok yang ada saat ini diasumsikan milik Maros
UPDATE referensi_blok 
SET kawasan = 'Sunrise City Maros' 
WHERE kawasan IS NULL OR kawasan = '';
