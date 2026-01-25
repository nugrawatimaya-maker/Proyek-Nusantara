-- DIAGNOSTIC SCRIPT
-- Ganti '9739' atau '9722' dengan nomor PO yang bermasalah jika perlu.
-- Script ini akan mengecek:
-- 1. Apakah data PO ada?
-- 2. Apakah data History ada?
-- 3. Apakah Logic View berhasil menggabungkannya?

WITH target_po AS (
    SELECT '9739' as search_term -- Coba cari yang mengandung angka ini
)
SELECT 
    '1. Data PO' as check_type,
    po.nomor_po, 
    po.created_at as tgl_po_asli, 
    po.status
FROM purchase_order po, target_po
WHERE po.nomor_po LIKE '%' || target_po.search_term || '%'

UNION ALL

SELECT 
    '2. Data History' as check_type,
    sh.keterangan as history_desc, 
    sh.created_at as tgl_grn,
    sh.jenis_transaksi
FROM stok_history sh, target_po
WHERE sh.keterangan LIKE '%' || target_po.search_term || '%'

UNION ALL

SELECT 
    '3. Test View Logic' as check_type,
    (SELECT MAX(created_at) FROM stok_history WHERE keterangan LIKE '%' || po.nomor_po || '%') as computed_grn_date,
    NULL as col3,
    NULL as col4
FROM purchase_order po, target_po
WHERE po.nomor_po LIKE '%' || target_po.search_term || '%';
