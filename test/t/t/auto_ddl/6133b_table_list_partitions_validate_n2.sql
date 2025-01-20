SELECT pg_sleep(1);--to ensure all objects are replicated

--This file will run on n2 and validate all the replicated tables data, structure and replication sets they're in
SET ROLE appuser;

SET search_path TO s613, public;

\d+ sales_list_east
\d+ sales_list_west
\d+ sales_list_north
\d+ sales_list
SELECT * FROM get_table_repset_info('sales_list'); -- Expect the new partition to be listed
SELECT * FROM sales_list ORDER BY sale_id; -- Expect 4 rows
--exercise ddl on n2
DROP TABLE sales_list CASCADE;

\d+ products_list
\d+ products_list_clothing
\d+ products_list_electronics
SELECT * FROM get_table_repset_info('products_list'); -- Expect all to be in default repset
SELECT * FROM products_list ORDER BY product_id; -- Expect 3 rows
--exercise ddl on n2
DROP TABLE products_list CASCADE;

