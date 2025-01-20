import sys, os, util_test, subprocess, time

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
home_dir=os.getenv("EDGE_HOME_DIR")
port2=port1+1
nc_dir=os.getenv("NC_DIR","nc")
home_dir = os.getenv("EDGE_HOME_DIR")


## Check the information from cluster list-nodes.
res=util_test.run_nc_cmd("Check the cluster with the list-nodes command", (f"cluster list-nodes demo"), f"{home_dir}")
print(f"The list-nodes command returns = {res}\n")
print("*"*100)

## Set the exception logging behaviors for the test:
for n in range(num_nodes):
    n=n+1
    
    ## Set spock.exception_behaviour:
    res=util_test.guc_set('spock.exception_behaviour', 'discard', f"{cluster_dir}/n{n}")
    print(f"Line 39 - res: {res.stdout}")
    ## Set spock.exception_logging:
    res=util_test.guc_set('spock.exception_logging', 'none', f"{cluster_dir}/n{n}")
    print(f"Line 42 - SHOW spock.exception_logging: {res.stdout}")
    ## Restart the service:
    command = "service restart pg{pgv}"
    res=util_test.run_cmd("Restart the service", (f"service restart pg{pgv}"), (f"{cluster_dir}/n{n}"))
    print(f"Line 46 - res: {res.stdout}")
    ## Check the GUC values:
    res = util_test.run_cmd("Run db guc-show command", "db guc-show spock.exception_behaviour",(f"{cluster_dir}/n{n}")) 
    print(f"Line 49 - SHOW spock.exception_behaviour: {res.stdout}")
    res = util_test.run_cmd("Run db guc-show command", "db guc-show spock.exception_logging",(f"{cluster_dir}/n{n}")) 
    print(f"Line 51 - SHOW spock.exception_logging: {res.stdout}")
    ## Check server status:
    res=util_test.run_cmd("Check the service status", (f"service status pg{pgv}"), (f"{cluster_dir}/n{n}"))
    print(f"Line 54 - res: {res.stdout}")

print("Setup starts")
## Setup - on each node:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
        
    ## Create a table:
    result = util_test.write_psql(f"CREATE TABLE case1 (bid integer PRIMARY KEY, bbalance integer, filler character(88))",host,dbname,port,pw,usr)
    ## Add a row:
    result = util_test.write_psql("INSERT INTO case1 VALUES (1, 11111, 'filler')",host,dbname,port,pw,usr)
    ## Add it to the default repset:
    result=util_test.run_cmd("comment", f"spock repset-add-table default case1 {dbname}", f"{cluster_dir}/n{n}")
    print(f"The repset-add-table command on n{n} returns: {result.stdout}")
    ## Confirm with SELECT * FROM spock.tables.
    result = util_test.read_psql("SELECT relname FROM spock.tables;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.tables returns: {result}")
    ## Check replication
    print(f"We're on node n{n} now:")
    status=util_test.run_cmd("Checking spock sub-show-status", f"spock sub-show-status {sub} {dbname}", f"{cluster_dir}/n{n}")
    print(f"The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}")
    print("*"*100)
    port = port + 1

    if "replicating" not in status.stdout:
        util_test.EXIT_FAIL()

print("Confirming the configuration")
## Confirm the configuration:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Confirm with SELECT * FROM spock.tables.
    result = util_test.read_psql("SELECT relname FROM spock.tables;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.tables returns: {result}")
    ## Confirm with SELECT * FROM spock.subscription.
    result = util_test.read_psql("SELECT * FROM spock.subscription;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.subscriptions returns: {result}")
    print("*"*100)
    ## Confirm with spock sub-show-status
    status=util_test.run_cmd("Checking spock sub-show-status", (f"spock sub-show-status {sub} {dbname}"), f"{cluster_dir}/n{n}")
    print(f"The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}")
    port = port + 1

    if "replicating" not in status.stdout:
        util_test.EXIT_FAIL()

## Test Steps
## Create an anonymous block that puts the cluster in repair mode and does an insert statement that will
## add a row to n1 that will not be replicated to n2 

anon_block = """
DO $$
BEGIN
    PERFORM spock.repair_mode('True');
    INSERT INTO case1 VALUES (2, 70000, null);
END $$;
"""

print(f"Executing the anonymous block: anon_block")
row = util_test.write_psql(f"{anon_block}",host,dbname,port1,pw,usr)
print(row)

## Look for our row on n1 and n2:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Confirm with SELECT * FROM spock.tables.
    result = util_test.read_psql("SELECT * FROM case1;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.tables on node n{n} returns: {result}")
    port = port+1
    print("*"*100)    

    if "replicating" not in status.stdout:
        util_test.EXIT_FAIL()


## More test steps:
## Update the record that is out of sync, forcing a record into the exception table...
row = util_test.write_psql("UPDATE case1 SET filler = 'hi' WHERE bid = 2",host,dbname,port1,pw,usr)
print(f"TEST STEP: The update to bid 2 returns: {row}")
print("*"*100)

## Demonstrate that replication continues on n1:
row = util_test.write_psql("UPDATE case1 SET filler = 'bye' WHERE bid = 1",host,dbname,port1,pw,usr)
print(f"TEST STEP: The update to bid 1 on n1 returns: {row}")
print("*"*100)

## Look for our row on n1 and n2 and check the replication state:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Check our table contents:
    result = util_test.read_psql("SELECT * FROM case1;",host,dbname,port,pw,usr)
    print(f"SELECT * from case1 on node n{n} returns: {result}")
    ## Confirm with spock sub-show-status
    status=util_test.run_cmd("Checking spock sub-show-status", (f"spock sub-show-status {sub} {dbname}"), f"{cluster_dir}/n{n}")
    print(f"The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}")
    port = port + 1
    
    if "replicating" not in status.stdout:
        util_test.EXIT_FAIL()

## Query the spock.exception_log; adding this command to cover error in 4.0.4 where a query on the wrong node caused a server crash.
row1 = util_test.read_psql("SELECT remote_new_tup FROM spock.exception_log WHERE table_name = 'case1';",host,dbname,port1,pw,usr)
print(f"This command is the query that used to cause a server crash! The result s/b []: {row1}")
print("*"*100)

if '[]' not in str(row1):
    util_test.EXIT_FAIL()

## Confirm the test results from the spock.exception_log:
row = util_test.read_psql("SELECT remote_new_tup FROM spock.exception_log WHERE table_name = 'case1';",host,dbname,port2,pw,usr)
print(f"TEST CONFIRMATION: SELECT * FROM spock.exception_log on n2 returns: {row}")
print("*"*100)

if '"value": 2, "attname": "bid", "atttype": "int4"' in str(row):
    util_test.EXIT_PASS()
else:
    util_test.EXIT_FAIL()

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)


