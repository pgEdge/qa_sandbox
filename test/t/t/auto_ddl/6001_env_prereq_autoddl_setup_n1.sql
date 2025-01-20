-- This is a pre-req file that needs to executed prior to any of the autoDDL sql tests
-- This will create the necessary shared objects needed by the autoDDL tests

--creating a superuser
CREATE ROLE adminuser SUPERUSER LOGIN;

--creating a non superuser that will have access to the public schema as well as user schemas
-- the permission on the public schema will be granted here whereas the individual schema privileges
-- will be assigned in the individual tests.
CREATE ROLE appuser LOGIN;

GRANT ALL PRIVILEGES ON SCHEMA public TO appuser;

-- Creating a function with SECURITY DEFINER privileges so that a nonsuper
-- can query the spock.table catalog to check for tables' repset assignments
CREATE OR REPLACE FUNCTION public.get_table_repset_info(partial_name TEXT)
RETURNS TABLE (nspname TEXT, relname TEXT, set_name TEXT) 
LANGUAGE sql
SECURITY DEFINER AS
$$
SELECT nspname, relname, set_name 
FROM spock.tables 
WHERE relname LIKE '%' || partial_name || '%' 
ORDER BY relid;
$$;

-- Grant execution rights to the non-superuser
GRANT EXECUTE ON FUNCTION public.get_table_repset_info(TEXT) TO appuser;

