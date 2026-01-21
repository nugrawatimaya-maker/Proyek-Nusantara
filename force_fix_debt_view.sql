-- SECURITY DEFINER force fix
-- 1. Hapus View lama dengan paksa
DROP VIEW IF EXISTS ap_monitoring_vw;

-- 2. Buat Ulang View dengan Filter Ketat
CREATE OR REPLACE VIEW ap_monitoring_vw AS
SELECT 
    min(po.id) as id, 
    po.nomor_po,
    MAX(po.nama_vendor) as nama_vendor,
    MAX(po.nama_proyek) as nama_proyek,
    MAX(po.created_at) as tanggal_po, 
    MAX(po.jatuh_tempo) as jatuh_tempo,
    SUM(po.total_harga) as total_tagihan, 
    MAX(po.status) as status_po, 
    MAX(po.keterangan) as file_nota, -- Nota URL stored in keterangan
    NULL::text as file_po, 
    MAX(po.created_at) as updated_at 
FROM purchase_order po
WHERE po.status IN ('DITERIMA', 'SELESAI', 'LUNAS') -- FILTER UTAMA: Hanya yang sudah GRN/SELESAI
GROUP BY po.nomor_po;

-- 3. VERIFIKASI LANGSUNG
-- Jika query di bawah ini kosong, berarti perbaikan BERHASIL.
-- Jika masih muncul data PO 9739, berarti ada yang salah dengan status data aslinya.
SELECT * FROM ap_monitoring_vw WHERE nomor_po LIKE '%9739%';
