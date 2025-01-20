-- This file runs on n1 again to see all the table and their partitions have been dropped on n1 (as a result of drop statements)
-- being auto replicated via 6144b

SELECT pg_sleep(1);--to ensure all objects are replicated

SET ROLE appuser;

SET search_path TO s614, public;
-- none of these tables should exist.
\d sales_hash_1
\d sales_hash_2
\d sales_hash_3
\d sales_hash_4
\d sales_hash
SELECT * FROM get_table_repset_info('sales_hash');

\d products_hash
\d products_hash_1
\d products_hash_2
\d products_hash_3
\d products_hash_4
SELECT * FROM get_table_repset_info('products_hash');

RESET ROLE;
--dropping the schema
DROP SCHEMA s614 CASCADE;