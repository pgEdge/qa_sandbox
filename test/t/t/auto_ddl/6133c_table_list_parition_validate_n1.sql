SELECT pg_sleep(1);--to ensure all objects are replicated

-- This file runs on n1 again to see all the table and their partitions have been dropped on n1 (as a result of drop statements)
-- being auto replicated via 6133b
SET ROLE appuser;

SET search_path TO s613, public;
--none of these should exist

\d sales_list_east
\d sales_list_west
\d sales_list_north
\d sales_list
SELECT * FROM get_table_repset_info('sales');

\d+ products_list
\d+ products_list_clothing
\d+ products_list_electronics
SELECT * FROM get_table_repset_info('products');

RESET ROLE;
--dropping the schema
DROP SCHEMA s613 CASCADE;