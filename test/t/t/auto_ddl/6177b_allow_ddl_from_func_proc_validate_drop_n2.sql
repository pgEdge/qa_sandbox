SELECT pg_sleep(1);

-- Turn on the allow_ddl_from_functions GUC
ALTER SYSTEM SET spock.allow_ddl_from_functions = on;
SELECT pg_reload_conf();
SELECT pg_sleep(0.5);
SHOW spock.allow_ddl_from_functions;

SET search_path TO s617, public;

-- Validate replicated functions, procedures, tables
\df add_column*
\df remove_column*
\df employee_insert_trigger
\d+ tab1_proc_on
\d+ tab2_func_on
\d+ tab3_anon_on
\d+ tab4_proc_off
\d+ tab5_func_off
\d+ tab6_anon_off
\d+ tab7_anon_off
\d+ tab_emp
\dn john
\dn alice
\dn cena
\dn wonderland
SELECT * FROM get_table_repset_info('tab');

SET ROLE appuser2;

SET search_path TO s617, public;
-- Drop tables 
DO $$
BEGIN
  EXECUTE 'DROP TABLE tab1_proc_on';
  EXECUTE 'DROP TABLE tab2_func_on';
  EXECUTE 'DROP TABLE tab3_anon_on';
  EXECUTE 'DROP TABLE tab4_proc_off';
  EXECUTE 'DROP TABLE tab5_func_off';
  EXECUTE 'DROP TABLE tab6_anon_off';
  EXECUTE 'DROP TABLE tab_emp CASCADE';
  EXECUTE 'DROP PROCEDURE add_column_to_table_proc';
  EXECUTE 'DROP FUNCTION remove_column_from_table';
  EXECUTE 'DROP FUNCTION employee_insert_trigger';
END
$$;

DO $$
BEGIN
  EXECUTE 'DROP TABLE tab7_anon_off'; --should not exist
END
$$;

RESET ROLE;

DO $$
BEGIN
  EXECUTE 'DROP SCHEMA john';
  EXECUTE 'DROP SCHEMA cena';
END
$$;
--should error out as these shouldn't have been replicated to n2
DROP SCHEMA alice;
DROP SCHEMA wonderland;