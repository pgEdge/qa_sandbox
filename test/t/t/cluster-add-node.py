## This test case adds a node and tests a scenario reported by Cady where n4 to n1 replication is having trouble.

import sys, os, util_test, subprocess, json, shutil, pprint, time

# Print Script
print(f"Starting - {os.path.basename(__file__)}")

# Get Test Settings
util_test.set_env()
repo=os.getenv("EDGE_REPO")
pgv=os.getenv("EDGE_INST_VERSION")
num_nodes=int(os.getenv("EDGE_NODES",2))
home_dir=os.getenv("EDGE_HOME_DIR")
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
cluster_name=os.getenv("EDGE_CLUSTER","demo")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","susan")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")


## Get the current working directory
current_directory = os.getcwd()
print(f"Current Working Directory: {current_directory}")

## Meet prerequisite: add export PGBACKREST_REPO1_CIPHER_PASS=YourCipherPassHere to ~/.bashrc

# Check the ~/.bashrc file for the pgBackRest command and add it if it's missing:
export_pgbackrest = 'export PGBACKREST_REPO1_CIPHER_PASS=YourCipherPassHere'
bashrc_path = os.path.expanduser('~/.bashrc')

# Read the .bashrc file
with open(bashrc_path, 'r') as file:
    lines = file.readlines()

# Check if the line is already in the file and add it if it is not
if export_pgbackrest + '\n' not in lines:
    # If not, append it to the file
    with open(bashrc_path, 'a') as file:
        file.write(export_pgbackrest + '\n')
    print(f"pgBackRest export statement added to {bashrc_path}.")
else:
    print("The pgBackRest export statement is already in the .bashrc file.")


## Meet prerequisite: Delete any pgBackRest artifacts with: rm -rf /etc/pgbackrest

directory = '/etc/pgbackrest'
print(directory)

if os.path.exists(directory):
    shutil.rmtree(directory)
    print(f'Directory {directory} removed successfully.')
else:
    print(f'Directory {directory} does not exist.')

## Create the json file for n4:

data = {'json_version': 1.1, 'node_groups': [{'ssh': {'os_user': 'ec2-user', 'private_key': ''}, 'name': 'n4', 'is_active': 'on', 'public_ip': '127.0.0.1', 'private_ip': '127.0.0.1', 'port': '6435', 'path': '/home/ec2-user/work/platform_test/nc/pgedge/cluster/demo/n4', 'replicas': '0'}]}

file_name = 'n4.json'

## Write the node description to the JSON file
with open(file_name, 'w') as json_file:
    json.dump(data, json_file, indent=4)

## Move the n4.json file to home_dir:

source = (f"n4.json")
target = (f"{home_dir}/n4.json")
print(f"home_dir = {home_dir}\n")
print(f"We need to copy that file to: {home_dir}")
shutil.move(source, target)
print("*"*100)

port1 = port
## Create a table on n1:
res = util_test.write_psql("CREATE TABLE IF NOT EXISTS public.foo (one varchar(10) primary key,two varchar(10),three varchar(10),date date)",host,dbname,port1,pw,usr)
print(f"Line 83 res: {res}")
## Add the table to a repset on n1:
res=util_test.run_cmd("running command", f"spock repset-add-table default foo {dbname}", f"{cluster_dir}/n1")

## Then invoke cluster add-node:

data_source = "n1"
data_target = "n4"

command = (f"cluster add-node {cluster_name} {data_source} {data_target}")
init=util_test.run_nc_cmd("This command should initialize a cluster based on the json file", command, f"{home_dir}")
#print(f"init = {init.stdout}\n")
#print("*"*100)
print("line 96 - we just added a new node: {init.stdout}")

## Check for the existence of the new node:
if "sub_n4n2" not in init.stdout:
        util_test.EXIT_FAIL()
print("*"*100)

## Check the replication state - n3 should be missing from the result sets:
port = port
print(f"You're in the loop on line 98, and the port is: {port}")
subscriptions =["sub_n1n2","sub_n2n1","sub_n3_n1","sub_n4n2"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Confirm with spock sub-show-status
    status=util_test.run_cmd("Checking spock sub-show-status", (f"spock sub-show-status {sub} {dbname}"), f"{cluster_dir}/n{n}")
    print(f"The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}, {status.stderr}")
    print(f"This command will not show a node on n3 since we've removed it in an earlier test")
    port = port + 1

print("*"*100)

port1 = 6432
port4 = 6435

## Add some rows to the table on n1:
res = util_test.write_psql("INSERT INTO foo VALUES ('1', '1111111', 'Alice','2021-01-01'),('2', '2222222', 'Benson', '2022-02-02'),('3', '3333333', 'Charles', '2023-03-03')",host,dbname,port1,pw,usr)
print(f"Line 122 res: {res}")

## Check for the rows on n4:
res = util_test.read_psql("SELECT * FROM foo"
,host,dbname,port4,pw,usr)
print(f"Line 126 - This is the result from the query on n4: {res}")

## Look for the rows in the result set...
if "3333333" not in res:
        util_test.EXIT_FAIL()
print("*"*100)

## Add a row to the table on n4:
res = util_test.write_psql("INSERT INTO public.foo VALUES ('4', '4444444', 'Douglas','2024-04-04')",host,dbname,port4,pw,usr)
print(f"Line 135 res: {res}")

time.sleep(7)

## Check for the new row on n4:
res = util_test.read_psql("SELECT * FROM foo",host,dbname,port4,pw,usr)
print(f"Line 139 - This is the result from the query on n4: {res}")

## Check for the new row on n1:
res = util_test.read_psql("SELECT * FROM foo",host,dbname,port1,pw,usr)
print(f"Line 143 - This is the result from the query on n1: {res}")

## Look for the row added on n4 in the set on n1.....
if "4444444" not in res:
        util_test.EXIT_FAIL()
print("*"*100)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

