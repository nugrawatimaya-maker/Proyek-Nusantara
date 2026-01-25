-- FIX MIGRATION: Allow Duplicate Block IDs for different Projects
-- Issue: 'D1' exists for Maros, preventing 'D1' for Pinrang.
-- Solution: Change Primary Key to Composite (id + kawasan).

-- 1. Update Legacy Data to ensure 'kawasan' is not NULL
UPDATE referensi_blok SET kawasan = 'Sunrise City Maros' WHERE kawasan IS NULL OR kawasan = '';

-- 2. Drop Data Integrity Constraint on 'id' (Primary Key)
-- We use a DO block to safely handle if the constraint name varies
DO $$
DECLARE
    r RECORD;
BEGIN
    -- Find and drop the primary key constraint on referensi_blok
    FOR r IN (
        SELECT conname 
        FROM pg_constraint 
        WHERE conrelid = 'referensi_blok'::regclass 
        AND contype = 'p'
    ) LOOP
        EXECUTE 'ALTER TABLE referensi_blok DROP CONSTRAINT ' || quote_ident(r.conname);
    END LOOP;
END $$;

-- 3. Create New Composite Primary Key (id + kawasan)
ALTER TABLE referensi_blok ADD PRIMARY KEY (id, kawasan);

-- 4. Re-Insert Missing Pinrang Blocks (B and D)
DO $$
DECLARE
    project_name TEXT := 'Sunrise City Pinrang';
BEGIN
    -- BLOK B
    INSERT INTO referensi_blok (id, kawasan) VALUES 
    ('B1', project_name), ('B2', project_name)
    ON CONFLICT (id, kawasan) DO NOTHING;

    -- BLOK D
    INSERT INTO referensi_blok (id, kawasan) VALUES 
    ('D1', project_name), ('D2', project_name), ('D3', project_name), ('D4', project_name), ('D5', project_name),
    ('D6', project_name), ('D7', project_name), ('D8', project_name), ('D9', project_name), ('D10', project_name),
    ('D11', project_name), ('D12', project_name), ('D13', project_name), ('D14', project_name), ('D15', project_name),
    ('D16', project_name), ('D17', project_name)
    ON CONFLICT (id, kawasan) DO NOTHING;
    
    -- Ensuring A and C are there too (Idempotent)
    -- ... (Omitting A/C as user confirmed they exist, but re-running is safe with ON CONFLICT)
END $$;
