-- Add missing column 'file_nota' to purchase_order table
-- This fixes the error: column "file_nota" of relation "purchase_order" does not exist

ALTER TABLE purchase_order 
ADD COLUMN IF NOT EXISTS file_nota TEXT;

-- Verify
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'purchase_order' AND column_name = 'file_nota';
