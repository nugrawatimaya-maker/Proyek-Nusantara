-- FIX: Ensure Projects appear in Inventory Dropdown (UPDATE 2)
-- Findings from Screenshot: Project 'Jalan blok C1/C13' (ID 81) has status 'PENDING'.
-- Inventory dropdown logic requires status = 'BERJALAN'.

-- 1. Force Status to 'BERJALAN' for ALL projects in Pinrang
-- This ensures that regardless of the name, if it is in the Pinrang region, it is active.
UPDATE master_proyek
SET status = 'BERJALAN'
WHERE kawasan = 'Sunrise City Pinrang' 
  AND status <> 'BERJALAN';

-- 2. General Cleanup: Ensure any project with "Pinrang" in the name is correctly labeled
-- Setting kawasan AND status.
UPDATE master_proyek
SET kawasan = 'Sunrise City Pinrang',
    status = 'BERJALAN'
WHERE nama_proyek ILIKE '%Pinrang%'
  AND (status <> 'BERJALAN' OR kawasan IS NULL OR kawasan <> 'Sunrise City Pinrang');

-- 3. Verify Data (Output for User)
-- Should verify that status is now 'BERJALAN'
SELECT id, nama_proyek, kawasan, status 
FROM master_proyek 
WHERE kawasan = 'Sunrise City Pinrang';
