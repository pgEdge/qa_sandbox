# This test case tells us how data can be filtered by column

import sys, os, util_test, subprocess, time

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()
#
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",2))
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
db=os.getenv("EDGE_DB","lcdb")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","pgedge")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")

port1 = port
port2 = port+1

## Create a table on n1:
res = util_test.write_psql("CREATE TABLE IF NOT EXISTS public.employee (emp_id smallint primary key, emp_govt_id varchar(15),emp_first_name varchar(40),emp_last_name varchar(40),emp_address varchar(50),emp_city_state varchar(15),emp_country varchar(2),emp_birth_date date,emp_division varchar(7),emp_date_added date)",host,dbname,port1,pw,usr)

if "0" not in str(res):
    util_test.EXIT_FAIL()

#Adding Table to the Repset and apply the column filter (that's the list that starts --columns). It replicates everything to n2 except emp_govt_id and emp_birth_date:
cmd = (f"spock repset-add-table default employee {db} --columns emp_id,emp_first_name,emp_last_name,emp_address,emp_city_state,emp_country,emp_division,emp_date_added")
res=util_test.run_cmd("running command", cmd, f"{cluster_dir}/n1")

print("*"*100)

if "Adding table" not in str(res.stdout):     
    util_test.EXIT_FAIL()

## Create a table on n2:
res = util_test.write_psql("CREATE TABLE IF NOT EXISTS public.employee (emp_id smallint primary key,emp_govt_id varchar(15),emp_first_name varchar(40),emp_last_name varchar(40),emp_address varchar(50),emp_city_state varchar(15),emp_country varchar(2),emp_birth_date date,emp_division varchar(7),emp_date_added date)",host,dbname,port2,pw,usr)
res=util_test.run_cmd("running command", cmd, f"{cluster_dir}/n2")

print("*"*100)

if "0" not in str(res) or res.returncode == 1:
    util_test.EXIT_FAIL()
 
#Adding table to repset on n2

cmd = f"spock repset-add-table default employee {db}"
res=util_test.run_cmd("running command", cmd, f"{cluster_dir}/n2")

print("*"*100)

if "Adding table" not in str(res.stdout) or res.returncode == 1:
    util_test.EXIT_FAIL()

## Insert data in table on n1:
res = util_test.write_psql("INSERT INTO public.employee VALUES ('8', '738963773', 'Alice', 'Adams', '18 Austin Blvd', 'Austin, TX', 'US', '1983-01-06', 'mgmt', '2021-04-15'),('20', '08031375B89', 'Benson', 'Brown', 'Rosensweig 58', 'Berlin', 'DE', '1975-03-13', 'sales', '2023-02-18'),('30', '839467228377', 'Charles', 'Clark', '4, Amrita Rd', 'Delhi', 'IN', '1963-07-18', 'sales', '2022-05-22'),('40', '560389338', 'Douglas', 'Davis', '3758 Hampton Street', 'Seattle, WA', 'US', '1973-08-09', 'sales', '2020-08-12'),('50', '0809246719', 'Elaine', 'Evans', 'Hauptstrasse 9375', 'Frankfurt', 'DE', '1967-09-24', 'mgmt', '2021-09-13'),('60', '294667291937', 'Frederick', 'Ford', 'Flat 80, Triveni Apartments', 'Pune', 'IN', '1971-02-21', 'sales', '2021-03-11'),('70', '833029112', 'Geoffrey', 'Graham', '84667 Blake Blvd', 'New York, NY', 'US', '1982-01-14', 'mgmt', '2022-08-19'),('80', '06030764H21', 'Helen', 'Harris', 'Dresden 3-9883', 'Munich', 'DE', '1964-03-07', 'sales', '2022-12-12'),('90', '8874 7793 8299', 'Isaac', 'Ingram', '4758 Miller Lane', 'Wan Chai', 'HK', '1968-04-19', 'sales', '2020-06-01')",host,dbname,port1,pw,usr)

if "0" not in str(res):
    util_test.EXIT_FAIL()

## Check the values on n1:
res = util_test.read_psql("SELECT * FROM employee",host,dbname,port1,pw,usr)
print(f"Line 70 - This is the result on n1: {res}") 

time.sleep(7)

## This is the end of the test - 
## Look for content replicated to n2; it shouldn't include a birthday or em_govt_id column:
res2 = util_test.read_psql("SELECT * FROM employee",host,dbname,port2,pw,usr)
print(f"Line 77 - This is the result on n2 - you should see some null values: {res2}")

if "8,     , Alice" in str(res2):
    util_test.EXIT_PASS()


## Cleanup - drop table on n1:
res = util_test.write_psql("DROP TABLE employee CASCADE",host,dbname,port1,pw,usr)
 

## Cleanup - drop table on n2:
res = util_test.write_psql("DROP TABLE employee CASCADE",host,dbname,port2,pw,usr)
 


