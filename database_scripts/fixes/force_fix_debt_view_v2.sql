-- FORCE FIX V2: Get Real GRN Date from Stok History
-- Masalah: Filter tanggal tidak akurat karena 'updated_at' sebelumnya hanya mengambil tanggal buat PO.
-- Solusi: Mengambil tanggal 'TERIMA GRN' dari tabel 'stok_history' melalui pencocokan Nomor PO.

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
    
    -- SUBQUERY untuk mengambil Tanggal GRN Asli dari Stok History
    -- Menggunakan COALESCE agar jika tidak ada history (data lama), tetap ambil created_at PO (fallback)
    COALESCE(
        (
            SELECT MAX(sh.created_at) 
            FROM stok_history sh 
            WHERE sh.jenis_transaksi = 'TERIMA GRN' 
            -- Mencocokkan Nomor PO di kolom keterangan history
            -- Format Keterangan biasanya: "ProjectName: NoPO"
            AND sh.keterangan LIKE '%' || po.nomor_po || '%' 
        ),
        MAX(po.created_at)
    ) as updated_at

FROM purchase_order po
WHERE po.status IN ('DITERIMA', 'SELESAI', 'LUNAS') 
GROUP BY po.nomor_po;

-- CHECK:
SELECT nomor_po, tanggal_po, updated_at FROM ap_monitoring_vw LIMIT 5;
