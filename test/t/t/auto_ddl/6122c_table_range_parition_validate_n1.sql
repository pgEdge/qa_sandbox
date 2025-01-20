SELECT pg_sleep(1);--to ensure all objects are replicated

-- This file runs on n1 again to see all the table and their partitions have been dropped on n1 (as a result of drop statements)
-- being auto replicated via 6122b
SET ROLE appuser;

SET search_path TO s612, public;

-- none of these tables should exist.
\d+ sales_range
\d+ sales_range_2021
\d+ sales_range_2022
\d+ sales_range_2023
--spock.tables should be empty
SELECT * FROM get_table_repset_info('sales');

\d+ revenue_range
\d+ revenue_range_2021
\d+ revenue_range_2022
\d revenue_range
--spock.tables should be empty
SELECT * FROM get_table_repset_info('revenue');

\d+ orders_range
\d+ orders_range_2021
\d+ orders_range_2022
--spock.tables should be empty
SELECT * FROM get_table_repset_info('orders');

\d+ inventory_range
\d+ inventory_range_2021
\d+ inventory_range_default
\d+ inventory_standalone
--spock.tables should be empty
SELECT * FROM get_table_repset_info('inventory');

RESET ROLE;
--dropping the schema
DROP SCHEMA s612 CASCADE;