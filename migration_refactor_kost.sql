-- Migration Script for Refactoring Dashboard Kost (FIXED)
-- Fix: tenant_id changed to UUID to match Supabase tenants table type

-- 1. Create Projects Table for Dynamic Configuration
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    total_rooms INTEGER DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed Initial Projects
INSERT INTO projects (name, total_rooms)
VALUES 
    ('Kos Sunrise Banta-Bantaeng', 9),
    ('Kost Faisal', 10)
ON CONFLICT (name) DO UPDATE SET total_rooms = EXCLUDED.total_rooms;

-- 2. Create Payment Transactions Table (for History)
CREATE TABLE IF NOT EXISTS payment_transactions (
    id SERIAL PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id), -- CHANGED TO UUID
    project_name TEXT NOT NULL,
    room_number TEXT,
    tenant_name TEXT, -- Snapshot of name in case tenant is deleted/changed
    amount NUMERIC NOT NULL,
    payment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT,
    category TEXT DEFAULT 'RENT', -- 'RENT', 'DEPOSIT', 'OTHER'
    proof_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Update Tenants Table Status Constraint (if strictly enforced previously)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tenant_status') THEN
        -- If enum doesn't exist, it might be raw text, or we create it
        -- For now, assuming text column, we just ensure no check constraint blocks it
        NULL; 
    END IF;
END $$;

-- 4. Enable RLS for new tables (Standard Security)
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_transactions ENABLE ROW LEVEL SECURITY;

-- 5. Policies (Public/Auth Access - Adjust as per current 'tenants' policy)
DROP POLICY IF EXISTS "Enable read access for all users" ON projects;
CREATE POLICY "Enable read access for all users" ON projects FOR SELECT USING (true);

DROP POLICY IF EXISTS "Enable read access for all users" ON payment_transactions;
CREATE POLICY "Enable read access for all users" ON payment_transactions FOR SELECT USING (true);

DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON payment_transactions;
CREATE POLICY "Enable insert for authenticated users only" ON payment_transactions FOR INSERT WITH CHECK (auth.role() = 'authenticated');
