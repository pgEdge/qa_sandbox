SELECT pg_sleep(1);--to ensure all objects are replicated

-- Final AutoDDL validation for the 6100 series on n1 to ensure all the DROP TABLE performed in the 6100b files on n2 
-- was auto replicated to n1.
-- None of the Tables should exist and spock.tables should not contain any entries for these tables

SET ROLE appuser;

SET search_path TO s610, public;

-- Final validation of all tables along with querying the spock.tables
-- validating all tables dropped on n1
\d+ employees
SELECT * FROM get_table_repset_info('employees');

\d+ departments
SELECT * FROM get_table_repset_info('departments');

\d+ projects
SELECT * FROM get_table_repset_info('projects');

\d+ employee_projects
SELECT * FROM get_table_repset_info('employee_projects');

\d+ products
SELECT * FROM get_table_repset_info('products');

\d+ "CaseSensitiveTable"
SELECT * FROM get_table_repset_info('CaseSensitiveTable');

\d+ test_tab1
SELECT * FROM get_table_repset_info('test_tab1');

\d+ test_tab2
SELECT * FROM get_table_repset_info('test_tab2');

\d+ test_tab3
SELECT * FROM get_table_repset_info('test_tab3');

\d+ test_tab4
SELECT * FROM get_table_repset_info('test_tab4');

\d+ test_tab5
SELECT * FROM get_table_repset_info('test_tab5');

RESET ROLE;
--dropping the schema
DROP SCHEMA s610 CASCADE;