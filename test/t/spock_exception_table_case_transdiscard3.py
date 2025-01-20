import sys, os, util_test,subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()
#
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",2))
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port1=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","admin")
pw=os.getenv("EDGE_PASSWORD","password1")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","pgedge")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")
pgv=os.getenv("EDGE_INST_VERSION")

port2=port1+1
print(port2)

print("*"*100)
nc_dir=os.getenv("NC_DIR","nc")
print(nc_dir)
home_dir = os.getenv("EDGE_HOME_DIR")
print(home_dir)

# Check the information from cluster list-nodes.
#
res=util_test.run_nc_cmd("Exercise the list-nodes command", (f"cluster list-nodes demo"), f"{home_dir}")
print(f"The list-nodes command returns = {res}\n")
print("*"*100)

## Set the exception logging behaviors for the test:
for n in range(num_nodes):
    port = port1
    n=n+1
    ## Set parameter value
    # res = util_test.write_psql("SET spock.exception_behaviour TO transdiscard",host,dbname,port,pw,usr)
    print(f"spock.exception_behaviour - res: {res}")
    ## Set parameter value
    # res = util_test.write_psql("SET spock.exception_logging TO 'all'",host,dbname,port,pw,usr)
    print(f"spock.exception_logging - res: {res}")
    ## Restart the service:
    res=util_test.run_cmd("Restart the PG service", (f"service restart pg{pgv}"), (f"{cluster_dir}/n{n}"))
    print(f"service restart - res: {res.stdout}")
    ## Check the GUC values:
    res = util_test.read_psql("SHOW spock.exception_behaviour",host,dbname,port,pw,usr).strip("[]")
    print(f"SHOW spock.exception_behaviour: {res}")
    res = util_test.read_psql("SHOW spock.exception_logging",host,dbname,port,pw,usr).strip("[]")
    print(f"SHOW spock.exception_logging: {res}")
    ## Check server status:
    res=util_test.run_cmd("Check PG service status", (f"service status pg{pgv}"), (f"{cluster_dir}/n{n}"))
    print(f"Check the service status res: {res.stdout}")
    port=port+1

print("Setup starts")
## Setup - on each node:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Create a table:
    result = util_test.write_psql(f"CREATE TABLE case333 (bid integer PRIMARY KEY, bbalance integer, filler character(88))",host,dbname,port,pw,usr)
    ## Add a row:
    result = util_test.write_psql("INSERT INTO case333 VALUES (1, 11111, 'filler')",host,dbname,port,pw,usr)
    ## Add it to the default repset:
    result=util_test.run_cmd("comment", f"spock repset-add-table default case333 {dbname}", f"{cluster_dir}/n{n}")
    print(f"Line 74 - The repset-add-table command on n{n} returns: {result.stdout}")
    print("*"*100)
    ## Confirm with SELECT * FROM spock.tables.
    result = util_test.read_psql("SELECT relname FROM spock.tables;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.tables returns: {result}")
    print("*"*100)
    port=port+1

## Add one row that should be replicated from n1 to n2:

row = util_test.write_psql("INSERT INTO case333 VALUES(11, 11000, null)",host,dbname,port1,pw,usr)
print(f"Line 84 - TEST STEP: We inserted bid 11 on n1: {row}")
print("*"*100)

## Look for our row on n1 and n2 and check the replication state:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Confirm table content:
    result = util_test.read_psql("SELECT * FROM case333;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.tables on node n{n} returns: {result}")
    ## Confirm with spock sub-show-status
    status=util_test.run_cmd("Checking spock sub-show-status", (f"spock sub-show-status {sub} {dbname}"), f"{cluster_dir}/n{n}")
    print(f"The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}")
    port = port + 1
    
print(f"Node n1 and n2 should both contain bid 1/11")
print("*"*100)


## Create an anonymous block that puts the cluster in repair mode and does an insert statement that will
## add a row to n2 that will not be replicated to n1:

anon_block = """
DO $$
BEGIN
    PERFORM spock.repair_mode('True');
    INSERT INTO case333 VALUES (22, 22000, null);
END $$;
"""

print(anon_block)
row = util_test.write_psql(f"{anon_block}",host,dbname,port2,pw,usr)
print(row)

## Add a row to n1 that has the same bid as the row we added on n2; we're still in repair mode:

row = util_test.write_psql("INSERT INTO case333 VALUES(22, 99000, null)",host,dbname,port1,pw,usr)
print(f"TEST STEP: We just tried to insert bid 22 on n1 - this should fail, but it doesn't: {row}")
print("*"*100)

## Look for our row on n1 and n2 and check the replication state:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Confirm table content:
    result = util_test.read_psql("SELECT * FROM case333;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.tables on node n{n} returns: {result}")
    ## Confirm with spock sub-show-status
    status=util_test.run_cmd("Checking spock sub-show-status", (f"spock sub-show-status {sub} {dbname}"), f"{cluster_dir}/n{n}")
    print(f"The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}")
    port = port + 1
    

print(f"Node n1 should contain bid 1/11")
print(f"Node n2 should contain bid 1/11/22")

## Check the results from the statement above, and you can see the duplicate primary key error 
## is not being caught. Fix this when the patch is in.

## Read from the spock.exception_log on n1;
row = util_test.read_psql("SELECT remote_new_tup FROM spock.exception_log",host,dbname,port1,pw,usr).strip("[]")
print(f"SELECT remote_new_tup FROM spock.exception_log on n1 returns an empty result set: {row}")
print("*"*100)

## Read from the spock.exception_log on n2;
row = util_test.read_psql("SELECT remote_new_tup FROM spock.exception_log",host,dbname,port2,pw,usr).strip("[]")
print(f"SELECT remote_new_tup FROM spock.exception_log on n2 returns the replication error: {row}")
print("*"*100)

## Look for our row on n1 and n2 and check the replication state - specifically we don't want a death spiral here:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Confirm table content:
    result = util_test.read_psql("SELECT * FROM case333;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.tables on node n{n} returns: {result}")
    ## Confirm with spock sub-show-status
    status=util_test.run_cmd("Checking spock sub-show-status", (f"spock sub-show-status {sub} {dbname}"), f"{cluster_dir}/n{n}")
    print(f"The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}")
    port = port + 1

print(f"port2 = {port2}")
print(f"host = {host}")
print(f"dbname = {dbname}")
print(f"password = {pw}")
print(f"usr = {usr}")   


## We're using a SELECT COUNT statement because in this case, the result is a json, and isn't being 
## interpreted correctly by the test - we may need to pick it apart?
## At the psql CL, the result is correct if we use:
## lcdb=# SELECT remote_new_tup FROM spock.exception_log WHERE table_name = 'case333';
## but the if/in statement doesn't work...

row = util_test.read_psql("SELECT COUNT(*) FROM case333;",host,dbname,port2,pw,usr)
print(f"FINAL TEST: SELECT COUNT (*): {row}")
print("*"*100)

if "[2]" in str(row):
    
    util_test.EXIT_PASS()
else:
    util_test.EXIT_FAIL()

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)


