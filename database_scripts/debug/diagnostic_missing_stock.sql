-- DIAGNOSTIC SCRIPT
-- Tujuan: Mengecek kemana perginya data GRN user.

-- 1. Cek 10 PO Terakhir yang statusnya 'DITERIMA'
-- Perhatikan kolom 'nama_proyek'. Apakah sesuai dengan proyek Anda?
SELECT 
    id, nomor_po, nama_proyek, status, created_at
FROM purchase_order
WHERE status = 'DITERIMA'
ORDER BY created_at DESC
LIMIT 10;

-- 2. Cek Stok History terakhir
-- Apakah ada history yang barang_id nya mungkin tidak nyambung?
SELECT 
    sh.id, 
    sh.created_at, 
    sh.jenis_transaksi, 
    sh.jumlah, 
    ms.nama_barang, 
    ms.nama_proyek as proyek_di_master_stok
FROM stok_history sh
LEFT JOIN master_stok ms ON sh.barang_id = ms.id
ORDER BY sh.created_at DESC
LIMIT 10;
