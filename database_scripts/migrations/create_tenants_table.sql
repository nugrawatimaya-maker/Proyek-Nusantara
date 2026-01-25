-- Create tenants table
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    project_name TEXT NOT NULL,
    room_number TEXT NOT NULL,
    
    nik TEXT,
    name TEXT NOT NULL,
    marital_status TEXT,
    phone TEXT,
    
    ktp_photo_url TEXT, -- Optional: Stores path/url if we upload storage
    status TEXT DEFAULT 'ACTIVE', -- ACTIVE, CHECKED_OUT
    
    check_in_date DATE DEFAULT CURRENT_DATE,
    duration INT, -- Durasi sewa dalam hari
    check_out_date DATE,
    
    rent_amount NUMERIC DEFAULT 0,
    payment_proof_url TEXT
);

-- RLS Policies
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all access for authenticated users" ON tenants
    FOR ALL USING (true) WITH CHECK (true);
