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
command = (f"cluster list-nodes demo")
res=util_test.run_nc_cmd("Exercise the list-nodes command", command, f"{home_dir}")
print(f"Command: {command}")
print(f"The list-nodes command returns = {res}\n")
print("*"*100)

## Set the exception logging behaviors for the test:
for n in range(num_nodes):
    n=n+1
    
    ## Set spock.exception_behaviour:
    res=util_test.guc_set('spock.exception_behaviour', 'sub_disable', f"{cluster_dir}/n{n}")
    print(f"Line 47 - res: {res.stdout}")
    ## Set spock.exception_logging:
    res=util_test.guc_set('spock.exception_logging', 'none', f"{cluster_dir}/n{n}")
    print(f"Line 50 - SHOW spock.exception_logging: {res.stdout}")
    ## Restart the service:
    command = "service restart pg{pgv}"
    res=util_test.run_cmd("Restart the service", (f"service restart pg{pgv}"), (f"{cluster_dir}/n{n}"))
    print(f"Line 54 - res: {res.stdout}")
    ## Check the GUC values:
    res = util_test.run_cmd("Run db guc-show command", "db guc-show spock.exception_behaviour",(f"{cluster_dir}/n{n}")) 
    print(f"Line 57 - SHOW spock.exception_behaviour: {res.stdout}")
    res = util_test.run_cmd("Run db guc-show command", "db guc-show spock.exception_logging",(f"{cluster_dir}/n{n}")) 
    print(f"Line 59 - SHOW spock.exception_logging: {res.stdout}")
    ## Check server status:
    res=util_test.run_cmd("Check the service status", (f"service status pg{pgv}"), (f"{cluster_dir}/n{n}"))
    print(f"Line 62 - res: {res.stdout}")

print("Setup starts")
## Setup - on each node:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Create a table:
    result = util_test.write_psql(f"CREATE TABLE case22 (bid integer PRIMARY KEY, bbalance integer, filler character(88))",host,dbname,port,pw,usr)
    ## Add a row:
    result = util_test.write_psql("INSERT INTO case22 VALUES (1, 11111, 'filler')",host,dbname,port,pw,usr)
    ## Add it to the default repset:
    result=util_test.run_cmd("comment", f"spock repset-add-table default case22 {dbname}", f"{cluster_dir}/n{n}")
    print(f"The repset-add-table command on n{n} returns: {result.stdout}")
    ## Confirm with SELECT * FROM spock.tables.
    result = util_test.read_psql("SELECT relname FROM spock.tables;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.tables returns: {result}")
    ## Check replication
    print(f"{n} is the value in n")
    status=util_test.run_cmd("Checking spock sub-show-status", f"spock sub-show-status {sub} {dbname}", f"{cluster_dir}/n{n}")
    print(f"Line 72 - The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}")
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
    ## Confirm with spock sub-show-status
    status=util_test.run_cmd("Checking spock sub-show-status", (f"spock sub-show-status {sub} {dbname}"), f"{cluster_dir}/n{n}")
    print(f"The spock sub-show-status {sub} {dbname} command on n1 returns: {status.stdout}")
    print("*"*100)
    port = port + 1
        
    if "replicating" not in status.stdout:
        util_test.EXIT_FAIL()


## Add two rows that should be replicated from n1 to n2:

row = util_test.write_psql("INSERT INTO case22 VALUES(11, 11000, null)",host,dbname,port1,pw,usr)
print(f"TEST STEP: We inserted bid 11 on n1: {row}")
print("*"*100)

row = util_test.write_psql("INSERT INTO case22 VALUES(22, 22000, null)",host,dbname,port1,pw,usr)
print(f"TEST STEP: We inserted bid 22 on n1: {row}")
print("*"*100)


## Look for our row on n1 and n2 and check the replication state:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Confirm table content:
    result = util_test.read_psql("SELECT * FROM case22;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.tables on node n{n} returns: {result}")
    ## Confirm with spock sub-show-status
    status=util_test.run_cmd("Checking spock sub-show-status", (f"spock sub-show-status {sub} {dbname}"), f"{cluster_dir}/n{n}")
    print(f"Line 124 - The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}")
    print("*"*100)
    port = port + 1
    
    if "replicating" not in status.stdout:
        util_test.EXIT_FAIL()

## Create an anonymous block that puts the cluster in repair mode and does an insert statement that will
## add a row to n2 that will not be replicated to n1:

anon_block = """
DO $$
BEGIN
    PERFORM spock.repair_mode('True');
    INSERT INTO case22 VALUES (33, 33000, null);
END $$;
"""

print(anon_block)
row = util_test.write_psql(f"{anon_block}",host,dbname,port2,pw,usr)
print(row)

## Check the rows on n1 and n2:

## Look for our row on n1 and n2 and check the replication state:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Confirm table content:
    result = util_test.read_psql("SELECT * FROM case22;",host,dbname,port,pw,usr)
    print(f"SELECT * from spock.tables on node n{n} returns: {result}")
    ## Confirm with spock sub-show-status
    status=util_test.run_cmd("Checking spock sub-show-status", (f"spock sub-show-status {sub} {dbname}"), f"{cluster_dir}/n{n}")
    print(f"The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}")
    print("*"*100)
    port = port + 1
    
    if "replicating" not in status.stdout:
        util_test.EXIT_FAIL()

print(f"TEST STEP: We're in repair mode - the table on n1 should contain 1/11/22, and n2 should contain 1/11/22/33")

## Node n2 has three rows; bid 33 is not replicated to n1, so an update should end up in the exception log table:
row = util_test.write_psql("UPDATE case22 SET filler = 'trouble' WHERE bid = 33",host,dbname,port2,pw,usr)
print(f"TEST STEP: We're in repair mode - the update to bid 33 on n2 returns: {row}")
print("*"*100)

## Demonstrate that replication continues
row = util_test.write_psql("UPDATE case22 SET filler = 'replication check' WHERE bid = 11",host,dbname,port2,pw,usr)
print(f"TEST STEP: The update to bid 11 on n1 returns: {row}")
print("*"*100)

## Show that the row update made it to n2 without causing a death spiral:
row = util_test.read_psql("SELECT * FROM case22",host,dbname,port2,pw,usr).strip("[]")
print(f"TEST STEP: bid 11 should be updated on n2, case22 contains: {row}")
print("*"*100)

## Check the replication state:
port = port1
subscriptions =["sub_n1n2","sub_n2n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Confirm with spock sub-show-status
    status=util_test.run_cmd("Checking spock sub-show-status", (f"spock sub-show-status {sub} {dbname}"), f"{cluster_dir}/n{n}")
    print(f"Line 191 - The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}")
    port = port + 1
    print("*"*100)
    if "replicating" not in status.stdout:
        util_test.EXIT_FAIL()


## Read from the spock.exception_log on n1 (the update of bid3 should be here);
row = util_test.read_psql("SELECT remote_new_tup FROM spock.exception_log WHERE table_name = 'case22';",host,dbname,port1,pw,usr)
print(f"SELECT * FROM spock.exception_log on n1 returns: {row}")
print("*"*100)

if '"value": 33, "attname": "bid", "atttype": "int4"' in str(row):
    
    util_test.EXIT_PASS()
else:
    util_test.EXIT_FAIL()

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

