-- 1. Create Counter Table
CREATE TABLE IF NOT EXISTS receipt_counters (
    project_name TEXT PRIMARY KEY,
    last_number INT DEFAULT 0
);

-- 2. Enable RLS
ALTER TABLE receipt_counters ENABLE ROW LEVEL SECURITY;

-- 3. Policy: Allow all (simplification for this use case, refine for prod)
CREATE POLICY "Enable all access" ON receipt_counters FOR ALL USING (true) WITH CHECK (true);

-- 4. RPC Function to Increment and Get Next Number atomically
CREATE OR REPLACE FUNCTION increment_receipt_counter(project_text TEXT)
RETURNS INT2
LANGUAGE plpgsql
AS $$
DECLARE
    next_val INT;
BEGIN
    -- Insert default if not exists, then update
    INSERT INTO receipt_counters (project_name, last_number)
    VALUES (project_text, 0)
    ON CONFLICT (project_name) DO NOTHING;

    -- Update and return new value
    UPDATE receipt_counters
    SET last_number = last_number + 1
    WHERE project_name = project_text
    RETURNING last_number INTO next_val;

    RETURN next_val;
END;
$$;
