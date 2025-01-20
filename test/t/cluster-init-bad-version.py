import sys, os, util_test, subprocess, json

# Print Script
print(f"Starting - {os.path.basename(__file__)}")

# Get Test Settings
util_test.set_env()
repo=os.getenv("EDGE_REPO")
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
spockver=os.getenv("EDGE_SPOCK_VER","4.0.1")
dbname=os.getenv("EDGE_DB","lcdb")

cwd=os.getcwd()
num_nodes=3

## Set pgv to an invalid version; we'll use 14 since it's deprecated.
pgv="14"

#print("*"*100)

print(f"home_dir = {home_dir}\n")
command = (f"cluster json-create {cluster_name} {num_nodes} {dbname} {usr} {pw} --pg_ver={pgv} --port={port} --force")
res=util_test.run_nc_cmd("This command should create a json file that defines a cluster", command, f"{home_dir}")
print(f"res = {res}\n")

if "Error: Invalid PostgreSQL version." in str(res.stdout) or res.returncode == 1:

    util_test.EXIT_PASS()
else:
    util_test.EXIT_FAIL()


