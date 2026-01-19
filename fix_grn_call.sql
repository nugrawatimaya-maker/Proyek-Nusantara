-- =============================================
-- ATOMIC GRN PROCESSING FUNCTION
-- Mencegah Stok Bertambah tapi Status PO Gagal Update
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
    -- 1. Lock & Get PO Data
    SELECT * INTO v_po 
    FROM purchase_order 
    WHERE id = p_po_id 
    FOR UPDATE; -- Lock baris ini agar tidak diproses ganda

    IF NOT FOUND THEN
        RETURN json_build_object('success', false, 'message', 'PO tidak ditemukan');
    END IF;

    -- 2. Validasi Status
    IF v_po.status <> 'APPROVED' THEN
        RETURN json_build_object('success', false, 'message', 'PO Status bukan APPROVED (Mungkin sudah diproses)');
    END IF;

    -- 3. Resolve Barang ID
    v_barang_id := v_po.barang_id;
    
    -- Fallback: Jika ID null, coba cari via nama (meski sebaiknya dihandle di frontend, ini safety net)
    -- Kita skip logic complex match name disini agar performa cepat, 
    -- asumsikan frontend sudah melakukan update barang_id jika null.
    IF v_barang_id IS NULL THEN
         RETURN json_build_object('success', false, 'message', 'Barang ID Null. Hubungi Admin.');
    END IF;

    -- 4. Update Stok Master
    SELECT total_stok INTO v_stok_lama 
    FROM master_stok 
    WHERE id = v_barang_id
    FOR UPDATE; -- Lock juga stoknya

    IF NOT FOUND THEN
        RETURN json_build_object('success', false, 'message', 'Master Stok Barang tidak ditemukan');
    END IF;

    v_stok_lama := COALESCE(v_stok_lama, 0);
    v_stok_baru := v_stok_lama + p_qty;

    UPDATE master_stok
    SET total_stok = v_stok_baru,
        harga_estimasi = p_price, -- Update harga terbaru
        harga_updated_ref = v_po.nomor_po
    WHERE id = v_barang_id;

    -- 5. Insert History
    INSERT INTO stok_history (barang_id, jenis_transaksi, jumlah, keterangan, created_at)
    VALUES (v_barang_id, 'TERIMA GRN', p_qty, p_history_desc, NOW());

    -- 6. Update PO Status (Finalize)
    UPDATE purchase_order
    SET status = 'DITERIMA',
        harga_satuan = p_price,
        file_nota = p_nota_file,
        keterangan = p_nota_url -- Simpan URL lengkap di keterangan agar mudah diakses
    WHERE id = p_po_id;

    RETURN json_build_object('success', true, 'message', 'Berhasil update stok dan status PO');

EXCEPTION WHEN OTHERS THEN
    -- Auto Rollback terjadi jika ada Error
    RETURN json_build_object('success', false, 'message', SQLERRM);
END;
$$;
