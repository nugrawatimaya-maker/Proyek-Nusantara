-- Tabel Header RAB
CREATE TABLE public.sem_rab_header (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    nama_proyek TEXT NOT NULL,
    nama_klien TEXT,
    lokasi_proyek TEXT,
    tanggal_rab DATE DEFAULT CURRENT_DATE,
    total_biaya NUMERIC(15, 2) DEFAULT 0,
    status TEXT DEFAULT 'DRAFT', -- DRAFT, FINAL, APPROVED
    updated_by UUID -- Link to auth.users if needed
);

-- Tabel Detail Item RAB
CREATE TABLE public.sem_rab_detail (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    rab_id UUID REFERENCES public.sem_rab_header(id) ON DELETE CASCADE,
    kategori TEXT DEFAULT 'UMUM', -- I. PERSIAPAN, II. SIPIL, dll.
    uraian_pekerjaan TEXT NOT NULL,
    volume NUMERIC(10, 2) DEFAULT 0,
    satuan TEXT,
    harga_satuan NUMERIC(15, 2) DEFAULT 0,
    total_harga NUMERIC(15, 2) GENERATED ALWAYS AS (volume * harga_satuan) STORED,
    urutan INTEGER DEFAULT 0
);

-- RLS Policies (Optional: Enable if RLS is active)
ALTER TABLE public.sem_rab_header ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sem_rab_detail ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all access for authenticated users" ON public.sem_rab_header
FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all access for authenticated users" ON public.sem_rab_detail
FOR ALL USING (auth.role() = 'authenticated');
