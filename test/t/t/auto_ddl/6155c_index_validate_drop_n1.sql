-- This file runs on n1 again to see all the table and their partitions have been dropped on n1 (as a result of drop statements)
-- being auto replicated via 6155b
SELECT pg_sleep(1);--to ensure all objects are replicated

SET ROLE appuser;

SET search_path TO s615, public;

-- Validate indexes on product_catalog, should not exist
\di *product_catalog_*
\d product_catalog

-- Validate indexes on employee_directory, should not exist
\di *_emp_*
\d employee_directory

-- Validate indexes on sales_data, should not exist
\di *sales*
\d sales_data

-- Validate concurrently created indexes on concurrent_idx_tbl, should not exist
\di *concurrent*
\d concurrent_idx_tbl

RESET ROLE;
--dropping the schema
DROP SCHEMA s615 CASCADE;