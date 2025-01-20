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
    n=n+1
    
    ## Set spock.exception_behaviour:
    res=util_test.guc_set('spock.exception_behaviour', 'discard', f"{cluster_dir}/n{n}")
    print(f"Line 44 - res: {res.stdout}")
    ## Set spock.exception_logging:
    res=util_test.guc_set('spock.exception_logging', 'none', f"{cluster_dir}/n{n}")
    print(f"Line 47 - SHOW spock.exception_logging: {res.stdout}")
    ## Restart the service:
    command = "service restart pg{pgv}"
    res=util_test.run_cmd("Restart the service", (f"service restart pg{pgv}"), (f"{cluster_dir}/n{n}"))
    print(f"Line 51 - res: {res.stdout}")
    ## Check the GUC values:
    res = util_test.run_cmd("Run db guc-show command", "db guc-show spock.exception_behaviour",(f"{cluster_dir}/n{n}")) 
    print(f"Line 54 - SHOW spock.exception_behaviour: {res.stdout}")
    res = util_test.run_cmd("Run db guc-show command", "db guc-show spock.exception_logging",(f"{cluster_dir}/n{n}")) 
    print(f"Line 56 - SHOW spock.exception_logging: {res.stdout}")
    ## Check server status:
    res=util_test.run_cmd("Check the service status", (f"service status pg{pgv}"), (f"{cluster_dir}/n{n}"))
    print(f"Line 59 - res: {res.stdout}")

print("Setup starts")
## Setup - on each node:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Create a table:
    result = util_test.write_psql(f"CREATE TABLE case3 (bid integer PRIMARY KEY, bbalance integer, filler character(88))",host,dbname,port,pw,usr)
    ## Add a row:
    result = util_test.write_psql("INSERT INTO case3 VALUES (1, 11111, 'filler')",host,dbname,port,pw,usr)
    ## Add it to the default repset:
    result=util_test.run_cmd("comment", f"spock repset-add-table default case3 {dbname}", f"{cluster_dir}/n{n}")
    print(f"The repset-add-table command on n{n} returns: {result.stdout}")
    print("*"*100)
    ## Confirm with SELECT * FROM spock.tables.
    result = util_test.read_psql("SELECT relname FROM spock.tables;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.tables returns: {result}")
    print("*"*100)
    ## Check replication
    status=util_test.run_cmd("Checking spock sub-show-status", f"spock sub-show-status {sub} {dbname}", f"{cluster_dir}/n{n}")
    print(f"The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}")
    print("*"*100)
    port = port + 1

    if "replicating" not in status.stdout:
        util_test.EXIT_FAIL()

## Add one row that should be replicated from n1 to n2:

row = util_test.write_psql("INSERT INTO case3 VALUES(11, 11000, null)",host,dbname,port1,pw,usr)
print(f"TEST STEP: We inserted bid 11 on n1: {row}")
print("*"*100)

## Look for our row on n1 and n2 and check the replication state:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Confirm table content:
    result = util_test.read_psql("SELECT * FROM case3;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.tables on node n{n} returns: {result}")
    ## Confirm with spock sub-show-status
    status=util_test.run_cmd("Checking spock sub-show-status", (f"spock sub-show-status {sub} {dbname}"), f"{cluster_dir}/n{n}")
    print(f"The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}")
    port = port + 1
    
    if "replicating" not in status.stdout:
        util_test.EXIT_FAIL()

print(f"Node n1 and n2 should both contain bid 1/11")
print("*"*100)


## Create an anonymous block that puts the cluster in repair mode and does an insert statement that will
## add a row to n2 that will not be replicated to n1:

anon_block = """
DO $$
BEGIN
    PERFORM spock.repair_mode('True');
    INSERT INTO case3 VALUES (22, 22000, null);
END $$;
"""

print(anon_block)
row = util_test.write_psql(f"{anon_block}",host,dbname,port2,pw,usr)
print(row)

## Add a row to n1 that has the same bid as the row we added on n2; we're still in repair mode:

row = util_test.write_psql("INSERT INTO case3 VALUES(22, 99000, null)",host,dbname,port1,pw,usr)
print(f"TEST STEP: We just tried to insert bid 22 on n1 - this should fail, but it doesn't: {row}")
print("*"*100)

## Look for our row on n1 and n2 and check the replication state:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Confirm table content:
    result = util_test.read_psql("SELECT * FROM case3;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.tables on node n{n} returns: {result}")
    ## Confirm with spock sub-show-status
    status=util_test.run_cmd("Checking spock sub-show-status", (f"spock sub-show-status {sub} {dbname}"), f"{cluster_dir}/n{n}")
    print(f"The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}")
    port = port + 1
    
    if "replicating" not in status.stdout:
        util_test.EXIT_FAIL()

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
    result = util_test.read_psql("SELECT * FROM case3;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.tables on node n{n} returns: {result}")
    ## Confirm with spock sub-show-status
    status=util_test.run_cmd("Checking spock sub-show-status", (f"spock sub-show-status {sub} {dbname}"), f"{cluster_dir}/n{n}")
    print(f"The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}")
    port = port + 1
    
    if "replicating" not in status.stdout:
        util_test.EXIT_FAIL()

## Read from the spock.exception_log on n2 for our needle/haystack step:
row = util_test.read_psql("SELECT remote_new_tup FROM spock.exception_log WHERE table_name = 'case3';",host,dbname,port2,pw,usr)
print(f"TEST STEP: SELECT remote_new_tup FROM spock.exception_log on n2 returns: {row}")
print("*"*100)

if '"value": 22, "attname": "bid", "atttype": "int4"' in str(row):
    
    util_test.EXIT_PASS()
else:
    util_test.EXIT_FAIL()

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)


