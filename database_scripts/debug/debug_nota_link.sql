-- Check if the View has the Link for the specific PO
SELECT nomor_po, file_nota
FROM ap_monitoring_vw
WHERE nomor_po ILIKE '%9727%';

-- Also check stok_history just in case
SELECT no_po, file_nota, keterangan
FROM stok_history
WHERE no_po ILIKE '%9727%';
