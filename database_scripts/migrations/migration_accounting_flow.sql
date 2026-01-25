-- MIGRASI DATA ACCOUNTING FLOW --
-- Tujuan: Memisahkan Antrian Pembayaran (Belum Bayar) dengan Verifikasi Kas Keluar (Sudah Bayar)

-- 1. Pindahkan data yang sudah punya 'bank_sumber' (berarti inputan dari Kas Keluar) 
--    dari 'APPROVED_BY_DIREKSI' ke 'TRANSFERED'.
UPDATE transaksi
SET jenis_transaksi = 'TRANSFERED'
WHERE jenis_transaksi = 'APPROVED_BY_DIREKSI'
  AND bank_sumber IS NOT NULL
  AND bank_sumber <> '';

-- 2. Pastikan data yang tidak punya 'bank_sumber' (Inputan Pengajuan Biaya) 
--    tetap di status 'APPROVED_BY_DIREKSI' (Masuk Antrian Pembayaran).
--    (Tidak perlu update apa-apa, ini defaultnya).

-- 3. Safety Check: Jika ada status 'APPROVED' yang punya bank_sumber, pindahkan juga?
--    Biasanya 'APPROVED' itu belum masuk Direksi Approval final jika flow lama, 
--    tapi di sistem baru 'APPROVED' juga masuk Queue.
--    Jika sudah ada bank_sumber, asumsikan sudah dibayar via Kas Keluar.
UPDATE transaksi
SET jenis_transaksi = 'TRANSFERED'
WHERE jenis_transaksi = 'APPROVED'
  AND bank_sumber IS NOT NULL
  AND bank_sumber <> '';

-- Note: transaksi_upah tidak disentuh karena user minta tetap di Antrian Pembayaran.
