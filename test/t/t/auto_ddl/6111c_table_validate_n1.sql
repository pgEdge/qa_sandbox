SELECT pg_sleep(1);--to ensure all objects are replicated

-- 6111c - Validate tables on n1

SET ROLE appuser;

SET search_path TO s611, public;
-- Validate sub_tx_table0
-- Expected: table does not exist
\d sub_tx_table0
SELECT * FROM get_table_repset_info('sub_tx_table0');

-- Validate sub_tx_table2
-- Expected: table does not exist
\d sub_tx_table2
SELECT * FROM get_table_repset_info('sub_tx_table2');

-- Validate sub_tx_table3
-- Expected: table does not exist
\d sub_tx_table3
SELECT * FROM get_table_repset_info('sub_tx_table3');

-- Validate sub_tx_table5, sub_tx_table5a, sub_tx_table5c, sub_tx_table5b should not exist
-- Expected: tables do not exist
\d sub_tx_table5
SELECT * FROM get_table_repset_info('sub_tx_table5');
\d sub_tx_table5a
SELECT * FROM get_table_repset_info('sub_tx_table5a');
\d sub_tx_table5b
SELECT * FROM get_table_repset_info('sub_tx_table5b'); -- should not exist
\d sub_tx_table5c
SELECT * FROM get_table_repset_info('sub_tx_table5c');

-- Validate table_ctas1
-- Expected: table does not exist
\d table_ctas1
SELECT * FROM get_table_repset_info('table_ctas1');

-- Validate table_ctas2
-- Expected: table does not exist
\d table_ctas2
SELECT * FROM get_table_repset_info('table_ctas2');

-- Validate table_ctas3
-- Expected: table does not exist
\d table_ctas3
SELECT * FROM get_table_repset_info('table_ctas3');

-- Validate table_ctas4
-- Expected: table does not exist
\d table_ctas4
SELECT * FROM get_table_repset_info('table_ctas4');

-- Validate table_ctas5
-- Expected: table does not exist
\d table_ctas5
SELECT * FROM get_table_repset_info('table_ctas5');

-- Validate table_ctas6
-- Expected: table does not exist
\d table_ctas6
SELECT * FROM get_table_repset_info('table_ctas6');

-- Validate table_si1
-- Expected: table does not exist
\d table_si1
SELECT * FROM get_table_repset_info('table_si1');

-- Validate table_si2
-- Expected: table does not exist
\d table_si2
SELECT * FROM get_table_repset_info('table_si2');

-- Validate table_si3
-- Expected: table does not exist
\d table_si3
SELECT * FROM get_table_repset_info('table_si3');

-- Validate table_si4
-- Expected: table does not exist
\d table_si4
SELECT * FROM get_table_repset_info('table_si4');

-- Validate table_si5
-- Expected: table does not exist
\d table_si5
SELECT * FROM get_table_repset_info('table_si5');

-- Validate table_l1
-- Expected: table does not exist
\d table_l1
SELECT * FROM get_table_repset_info('table_l1');

-- Validate table_l2
-- Expected: table does not exist
\d table_l2
SELECT * FROM get_table_repset_info('table_l2');

-- Validate table_l3
-- Expected: table does not exist
\d table_l3
SELECT * FROM get_table_repset_info('table_l3');

-- Validate table_l4
-- Expected: table does not exist
\d table_l4
SELECT * FROM get_table_repset_info('table_l4');

-- Validate table_l5
-- Expected: table does not exist
\d table_l5
SELECT * FROM get_table_repset_info('table_l5');

RESET ROLE;
--dropping the schema
DROP SCHEMA s611 CASCADE;