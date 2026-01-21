-- =============================================
-- ROBUST GRN PROCESSING FUNCTION (V2)
-- Menangani case null dan locking dengan lebih baik
-- =============================================

CREATE OR REPLACE FUNCTION process_grn_item(
    p_po_id BIGINT,
    p_qty NUMERIC,
    p_price NUMERIC,
    p_nota_file TEXT,
    p_nota_url TEXT,
    p_history_desc TEXT
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_po RECORD;
    v_barang_id BIGINT;
    v_stok_lama NUMERIC;
    v_stok_baru NUMERIC;
BEGIN
    -- 1. Validasi Input
    IF p_qty <= 0 THEN
        RETURN json_build_object('success', false, 'message', 'QTY harus > 0');
    END IF;

    -- 2. Lock & Get PO Data
    SELECT * INTO v_po 
    FROM purchase_order 
    WHERE id = p_po_id 
    FOR UPDATE;

    IF NOT FOUND THEN
        RETURN json_build_object('success', false, 'message', 'PO tidak ditemukan');
    END IF;

    IF v_po.status = 'DITERIMA' THEN
        RETURN json_build_object('success', false, 'message', 'PO sudah diproses sebelumnya (Status DITERIMA).');
    END IF;

    IF v_po.status <> 'APPROVED' THEN
        RETURN json_build_object('success', false, 'message', 'PO belum di-approve direksi.');
    END IF;

    v_barang_id := v_po.barang_id;
    IF v_barang_id IS NULL THEN
         RETURN json_build_object('success', false, 'message', 'Barang ID Null di PO. Hubungi IT.');
    END IF;

    -- 3. Update Master Stok (Direct Update)
    -- Menggunakan UPDATE langsung tanpa read-modify-write variable untuk efisiensi
    -- COALESCE memastikan jika stok null dianggap 0
    UPDATE master_stok
    SET total_stok = COALESCE(total_stok, 0) + p_qty,
        harga_estimasi = p_price,
        harga_updated_ref = v_po.nomor_po,
        nama_proyek = COALESCE(nama_proyek, v_po.nama_proyek) -- Self-healing jika proyek kosong
    WHERE id = v_barang_id;

    IF NOT FOUND THEN
        RETURN json_build_object('success', false, 'message', 'Master Stok ID tidak ditemukan.');
    END IF;

    -- 4. Insert History
    INSERT INTO stok_history (barang_id, jenis_transaksi, jumlah, keterangan, created_at)
    VALUES (v_barang_id, 'TERIMA GRN', p_qty, p_history_desc, NOW());

    -- 5. Finalize PO
    UPDATE purchase_order
    SET status = 'DITERIMA',
        harga_satuan = p_price,
        file_nota = p_nota_file,
        keterangan = p_nota_url
    WHERE id = p_po_id;

    RETURN json_build_object('success', true, 'message', 'Stok berhasil ditambahkan.');

EXCEPTION WHEN OTHERS THEN
    RETURN json_build_object('success', false, 'message', 'SQL Error: ' || SQLERRM);
END;
$$;
