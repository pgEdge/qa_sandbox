SELECT pg_sleep(1);--to ensure all objects are replicated

--Drop the objects directly on n1 that weren't auto replicated (expected)
DROP DATABASE obj_database;
--The tablespace will have to be dropped in the _c file
DROP TABLESPACE obj_tablespace;
--drop subscription
DROP SUBSCRIPTION obj_subscription;

--Validate all objects on n1 do not exist 

-- Validate database
-- Validate database (due to catalog changes in pg17, we are not using \l meta command anymore)
SELECT
    datname AS name,
    pg_catalog.pg_get_userbyid(datdba) AS owner,
    pg_catalog.pg_encoding_to_char(encoding) AS encoding
FROM
    pg_database
WHERE
    datname = 'obj_database';

-- Validate extension
\dx "uuid-ossp"

-- Validate tablespace
SELECT count(*) FROM pg_tablespace WHERE spcname = 'obj_tablespace';

-- Validate role
\dg obj_role

-- Validate schema
\dn s1

-- Validate foreign data wrapper
\dew obj_fdw

-- Validate server
\des obj_server

-- Validate user mapping
\deu

-- Validate publication
\dRp obj_publication

-- Validate subscription
\dRs obj_subscription

-- Validate cast
\dC obj_type

-- Validate aggregate
\da obj_aggregate

-- Validate collation , using a query instead of meta command as there are catalog changes in pg17
SELECT
    n.nspname AS schema,
    c.collname AS name
FROM
    pg_collation c
JOIN
    pg_namespace n ON n.oid = c.collnamespace
WHERE
    c.collname = 'obj_collation';


-- Validate conversion
\dc obj_conversion

-- Validate domain
\dD obj_domain2

-- Validate event trigger
\dy obj_event_trigger

-- Validate foreign table
\det obj_foreign_table

-- Validate function
\df obj_function

-- Validate index
\di obj_index

-- Validate language
\dL plperl

-- Validate materialized view
\d+ obj_mview

-- Validate operator
\do s1.##

-- Validate operator class
\dAc btree integer

-- Validate operator family
SELECT count(*) FROM pg_opfamily WHERE opfname = 'obj_opfamily';

-- Validate procedure
\df obj_procedure

-- Validate text search configuration
\dF obj_tsconfig

-- Validate text search dictionary
\dFd obj_tsdict

-- Validate text search parser
\dFp obj_tsparser

-- Validate text search template
\dFt obj_tstemplate

-- Validate transform
SELECT  l.lanname, ty.typname
FROM pg_transform t
JOIN pg_language l ON t.trflang = l.oid
JOIN pg_type ty ON t.trftype = ty.oid
WHERE ty.typname = 'int4' AND l.lanname = 'sql';

-- Validate type
\dT+ obj_composite_type
\dT+ obj_enum
\dT+ obj_range

-- Validate view
\d+ obj_view

--validate table, triggers, rules
\d+ obj_table

-- Validate group
\dg obj_group

--role cleanup
DROP OWNED BY appuser3;
DROP ROLE appuser3;
