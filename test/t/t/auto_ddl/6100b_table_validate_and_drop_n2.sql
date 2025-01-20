SELECT pg_sleep(1);--to ensure all objects are replicated

-- AutoDDL validation on n2 to ensure all the DDL/DML performed in the 6100a files on n1 
-- was auto replicated to n2.
-- In the end, the same objects are dropped.

SET ROLE appuser;

SET search_path TO s610, public;
-- Final validation of all tables along with querying the spock.tables
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

-- Validating data in all tables
SELECT * FROM employees ORDER BY emp_id;
SELECT * FROM departments ORDER BY dept_id;
SELECT * FROM projects ORDER BY project_id;
SELECT * FROM employee_projects ORDER BY emp_id, project_id;
SELECT * FROM products ORDER BY product_id;
SELECT * FROM "CaseSensitiveTable" ORDER BY "ID";
SELECT * FROM test_tab1 ORDER BY id;
SELECT * FROM test_tab2 ORDER BY id;
SELECT * FROM test_tab3 ORDER BY id;
SELECT * FROM test_tab4 ORDER BY id;
SELECT * FROM test_tab5 ORDER BY 1;

-- Execute drop statements on n2 to exercise DROP TABLE, ensuring it gets replicated.
-- This also helps with the cleanup
drop table employees cascade;
drop table departments cascade;
drop table projects cascade;
drop table employee_projects cascade;
drop table products cascade;
drop table "CaseSensitiveTable";
drop table test_tab1;
drop table test_tab2;
drop table test_tab3;
drop table test_tab4;
drop table test_tab5;
