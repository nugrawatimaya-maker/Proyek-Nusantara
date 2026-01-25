-- FIND DUPLICATES: Items that are in 'pengajuan_upah' (DIAJUKAN) but ALREADY in 'transaksi_upah'
-- Matches based on: kavling, nama_pekerjaan (normalized)

WITH normalized_transaksi AS (
    SELECT 
        kavling, 
        LOWER(SPLIT_PART(nama_pekerjaan, ' (', 1)) as clean_name
    FROM transaksi_upah
    GROUP BY kavling, clean_name
)

SELECT 
    p.id, 
    p.kavling, 
    p.nama_pekerjaan, 
    p.nilai,
    p.status as status_pengajuan
FROM pengajuan_upah p
JOIN normalized_transaksi t 
    ON p.kavling = t.kavling 
    AND LOWER(SPLIT_PART(p.nama_pekerjaan, ' (', 1)) = t.clean_name
WHERE p.status = 'DIAJUKAN';
