# Database Scripts

This directory contains database-related scripts and tools, organized by category to keep the repository root clean.

## Structure

### `migrations/`
Contains scripts that alter the database schema, security policies, or initial setup.
- Examples: `create_expenses_table.sql`, `security_update.sql`, `migration_*.sql`

### `fixes/`
Contains ad-hoc scripts used to fix data issues, repair inconsistencies, or apply one-time patches.
- Examples: `fix_grn_call.sql`, `repair_stock.sql`, `force_fix_debt_view.sql`

### `debug/`
Contains diagnostic scripts and tools used to investigate issues or verify data.
- Examples: `debug_po_date.sql`, `check_pinrang_proyek.sql`

## Note
When running these scripts, ensure you are connected to the correct database (Production vs Development).
