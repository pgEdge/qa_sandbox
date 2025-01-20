-- This is a autoddl cleanup file cleaning up all objects created via 6001 setup script

DROP OWNED BY adminuser;

DROP OWNED BY appuser;

DROP FUNCTION IF EXISTS public.get_table_repset_info(TEXT);

DROP ROLE IF EXISTS appuser;

DROP ROLE adminuser;
