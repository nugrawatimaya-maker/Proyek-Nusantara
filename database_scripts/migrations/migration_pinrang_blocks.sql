-- Migration Script: Insert Block Data for Sunrise City Pinrang
-- TARGET TABLE: referensi_blok
-- COLUMNS: id (Block Name), kawasan (Project Location)

-- NOTE: This script assumes 'id' is NOT a unique Primary Key across the entire table, 
-- or that 'id' + 'kawasan' forms a composite key.
-- If 'A1' already exists for Maros and 'id' is a strict PK, this might fail.
-- In that case, you might need to suffix the ID, e.g., 'P-A1', or adjust the table schema.

DO $$
DECLARE
    project_name TEXT := 'Sunrise City Pinrang';
BEGIN
    -- BLOCK A (A1 - A18)
    INSERT INTO referensi_blok (id, kawasan) VALUES 
    ('A1', project_name), ('A2', project_name), ('A3', project_name), ('A4', project_name), ('A5', project_name),
    ('A6', project_name), ('A7', project_name), ('A8', project_name), ('A9', project_name), ('A10', project_name),
    ('A11', project_name), ('A12', project_name), ('A13', project_name), ('A14', project_name), ('A15', project_name),
    ('A16', project_name), ('A17', project_name), ('A18', project_name)
    ON CONFLICT DO NOTHING; 

    -- BLOCK B (B1 - B2)
    INSERT INTO referensi_blok (id, kawasan) VALUES 
    ('B1', project_name), ('B2', project_name)
    ON CONFLICT DO NOTHING;

    -- BLOCK C (C1 - C27)
    INSERT INTO referensi_blok (id, kawasan) VALUES 
    ('C1', project_name), ('C2', project_name), ('C3', project_name), ('C4', project_name), ('C5', project_name),
    ('C6', project_name), ('C7', project_name), ('C8', project_name), ('C9', project_name), ('C10', project_name),
    ('C11', project_name), ('C12', project_name), ('C13', project_name), ('C14', project_name), ('C15', project_name),
    ('C16', project_name), ('C17', project_name), ('C18', project_name), ('C19', project_name), ('C20', project_name),
    ('C21', project_name), ('C22', project_name), ('C23', project_name), ('C24', project_name), ('C25', project_name),
    ('C26', project_name), ('C27', project_name)
    ON CONFLICT DO NOTHING;

    -- BLOCK D (D1 - D17)
    INSERT INTO referensi_blok (id, kawasan) VALUES 
    ('D1', project_name), ('D2', project_name), ('D3', project_name), ('D4', project_name), ('D5', project_name),
    ('D6', project_name), ('D7', project_name), ('D8', project_name), ('D9', project_name), ('D10', project_name),
    ('D11', project_name), ('D12', project_name), ('D13', project_name), ('D14', project_name), ('D15', project_name),
    ('D16', project_name), ('D17', project_name)
    ON CONFLICT DO NOTHING;

END $$;
