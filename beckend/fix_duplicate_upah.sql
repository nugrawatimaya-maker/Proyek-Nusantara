-- FIX/DELETE DUPLICATES
-- Deletes from 'pengajuan_upah' if the item exists in 'transaksi_upah'

WITH normalized_transaksi AS (
    SELECT 
        kavling, 
        LOWER(SPLIT_PART(nama_pekerjaan, ' (', 1)) as clean_name
    FROM transaksi_upah
    GROUP BY kavling, clean_name
)

DELETE FROM pengajuan_upah
WHERE id IN (
    SELECT p.id
    FROM pengajuan_upah p
    JOIN normalized_transaksi t 
        ON p.kavling = t.kavling 
        AND LOWER(SPLIT_PART(p.nama_pekerjaan, ' (', 1)) = t.clean_name
    WHERE p.status = 'DIAJUKAN'
);
