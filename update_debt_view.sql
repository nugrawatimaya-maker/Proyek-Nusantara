-- View: ap_monitoring_vw
-- Purpose: Aggregate Purchase Order Items into a single Debt Record per PO.
-- Logic:
-- 1. DROP VIEW first to allow column structural changes.
-- 2. Filter items where status is 'DITERIMA', 'SELESAI', or 'LUNAS'.
-- 3. Group by nomor_po.
-- 4. Sum total_harga.
-- 5. Map 'keterangan' to 'file_nota'.

DROP VIEW IF EXISTS ap_monitoring_vw;

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
    NULL::text as file_po, -- Placeholder/Fallback
    MAX(po.created_at) as updated_at -- Fallback to created_at
FROM purchase_order po
WHERE po.status IN ('DITERIMA', 'SELESAI', 'LUNAS') 
GROUP BY po.nomor_po;
