-- DATA REPAIR SCRIPT
-- Tujuan: Memperbaiki item di Master Stok yang proyeknya tidak sesuai dengan PO yang masuk.
-- Masalah: User GRN di 'Sunrise City Maros', tapi Stok tercatat di 'Gudang Utama' atau NULL.

-- 1. IDENTIFIKASI & FIX (Satu per satu kasus umum)

-- Kasus A: Barang ID linked ke PO 'Sunrise City Maros', tapi di Master Stok proyeknya NULL atau Beda.
-- Kita update Master Stok agar ikut Proyek PO-nya (Asumsi: Barang ini memang milik proyek tsb).

UPDATE master_stok ms
SET nama_proyek = po.nama_proyek
FROM purchase_order po
WHERE ms.id = po.barang_id
  AND po.status IN ('APPROVED', 'DITERIMA')
  AND po.nama_proyek IS NOT NULL
  AND (ms.nama_proyek IS NULL OR ms.nama_proyek <> po.nama_proyek);

-- 2. Cek Hasil (Optional, untuk log)
-- Harusnya return kosong jika semua sudah fix.
SELECT count(*) as sisa_masalah 
FROM master_stok ms
JOIN purchase_order po ON ms.id = po.barang_id
WHERE po.status IN ('APPROVED', 'DITERIMA')
AND ms.nama_proyek <> po.nama_proyek;
