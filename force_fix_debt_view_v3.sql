-- FORCE FIX V3: Include "Hidden" GRN (Status APPROVED but History Exists)
-- Masalah: PO sudah ada GRN di Stok History, tapi Status PO masih 'APPROVED' (belum berubah jadi DITERIMA).
-- Akibatnya: Filter status sebelumnya menyembunyikan PO ini.
-- Solusi: 
-- 1. Perluas WHERE clause untuk memasukkan PO 'APPROVED' JIKA punya history GRN.
-- 2. Gunakan ILIKE untuk pencocokan string yang lebih fleksibel.

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
    MAX(po.keterangan) as file_nota,
    NULL::text as file_po, 
    
    -- Ambil Real GRN Date
    COALESCE(
        (
            SELECT MAX(sh.created_at) 
            FROM stok_history sh 
            WHERE sh.jenis_transaksi = 'TERIMA GRN' 
            AND sh.keterangan ILIKE '%' || po.nomor_po || '%' 
        ),
        MAX(po.created_at)
    ) as updated_at

FROM purchase_order po
WHERE 
    po.status IN ('DITERIMA', 'SELESAI', 'LUNAS') 
    OR 
    (
        po.status = 'APPROVED' 
        AND EXISTS (
             SELECT 1 FROM stok_history sh 
             WHERE sh.jenis_transaksi = 'TERIMA GRN' 
             AND sh.keterangan ILIKE '%' || po.nomor_po || '%'
        )
    )
GROUP BY po.nomor_po;

-- CHECK:
SELECT nomor_po, status_po, updated_at FROM ap_monitoring_vw WHERE nomor_po LIKE '%9739%';
