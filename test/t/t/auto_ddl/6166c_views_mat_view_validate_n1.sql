-- validations on n1 to ensure all DROP VIEW and DROP MATERIALIZED VIEW statements 
-- issued from n2 were replicated to n1. 

-- no object should exist
\d test_schema.view_test_1

\d test_schema.view_test_2

\d test_schema.view_recursive

\d test_schema.view_with_options

\d test_schema.view_with_check_option

\d test_schema.mv_test_view

\d test_schema.mv_test_view_nodata

\d test_schema.mv_test_view_colnames

\d test_schema.mv_test_view_method

\d test_schema.mv_test_view_storage

\d test_schema.mv_test_view_tablespace

\d s616.view_test_default

\d test_schema.view_depends_on_default

\d s616.mv_depends_on_test_schema

\d s616.view_depends_on_mv

\d s616.mv_depends_on_mv

RESET ROLE;
--dropping the schema
DROP SCHEMA s616 CASCADE;
-- Drop the schema
DROP SCHEMA test_schema CASCADE;