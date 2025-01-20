SELECT pg_sleep(1);--to ensure all objects are replicated

--creating the necessary pre-reqs and then switching to the appuser role
CREATE SCHEMA IF NOT EXISTS s613;

GRANT ALL PRIVILEGES ON SCHEMA s613 TO appuser;

SET ROLE appuser;

SET search_path TO s613, public;

-----------------------------
-- List Partitioning
-----------------------------

-- Create a list partitioned table with primary key
CREATE TABLE sales_list (
    sale_id INT,
    sale_region TEXT,
    sale_amount DECIMAL,
    PRIMARY KEY (sale_id, sale_region)
) PARTITION BY LIST (sale_region);

-- Add partitions to the sales_list table
CREATE TABLE sales_list_east PARTITION OF sales_list
    FOR VALUES IN ('East');
CREATE TABLE sales_list_west PARTITION OF sales_list
    FOR VALUES IN ('West');

-- Insert data into the sales_list table
INSERT INTO sales_list (sale_id, sale_region, sale_amount) VALUES
(1, 'East', 100.0),
(2, 'West', 200.0),
(3, 'East', 150.0);

SELECT * FROM get_table_repset_info('sales_list'); -- Expect both parent and child tables in default repset
SELECT * FROM sales_list ORDER BY sale_id; -- Expect 3 rows

-- Alter the sales_list table to add a new partition
CREATE TABLE sales_list_north PARTITION OF sales_list
    FOR VALUES IN ('North');

-- Insert data into the new partition
INSERT INTO sales_list (sale_id, sale_region, sale_amount) VALUES
(4, 'North', 250.0);

-- Validate structure and data after adding new partition
\d+ sales_list_east
\d+ sales_list_west
\d+ sales_list_north
\d+ sales_list
SELECT * FROM get_table_repset_info('sales_list'); -- Expect the new partition to be listed
SELECT * FROM sales_list ORDER BY sale_id; -- Expect 4 rows
-- Create a list partitioned table without primary key
CREATE TABLE products_list (
    product_id INT,
    product_category TEXT,
    product_name TEXT
) PARTITION BY LIST (product_category);

-- Add partitions to the products_list table
CREATE TABLE products_list_electronics PARTITION OF products_list
    FOR VALUES IN ('Electronics');
CREATE TABLE products_list_clothing PARTITION OF products_list
    FOR VALUES IN ('Clothing');

-- Insert data into the products_list table
INSERT INTO products_list (product_id, product_category, product_name) VALUES
(1, 'Electronics', 'Laptop'),
(2, 'Clothing', 'Shirt'),
(3, 'Electronics', 'Smartphone');

-- Validate structure and data
\d+ products_list
SELECT * FROM get_table_repset_info('products_list'); -- Expect both parent and child tables in default_insert_only set
SELECT * FROM products_list ORDER BY product_id; -- Expect 3 rows

-- Alter the products_list table to add a primary key
ALTER TABLE products_list ADD PRIMARY KEY (product_id, product_category);

-- Validate structure and data after adding primary key
\d+ products_list
\d+ products_list_clothing
\d+ products_list_electronics
SELECT * FROM get_table_repset_info('products_list'); -- Expect the replication set to change to default
SELECT * FROM products_list ORDER BY product_id; -- Expect 3 rows

