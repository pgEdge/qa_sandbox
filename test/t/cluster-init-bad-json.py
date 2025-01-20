import sys, os, util_test, subprocess, json

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
repuser=os.getenv("EDGE_REPUSER","repuser")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")


print(f"cluster_dir contains: {cluster_dir}")
tmpcluster = "holdings"
new_cluster_dir = (f"nc/pgedge/cluster/{tmpcluster}")
file_name = (f"{tmpcluster}.json")
cwd=os.getcwd()

#
# Use cluster json-template to create a template file:
# 
print(f"home_dir = {home_dir}\n")
command = (f"cluster json-create {tmpcluster} {num_nodes} {dbname} {usr} {pw} --port={port} --pg_ver={pgv} --force")
res=util_test.run_nc_cmd("This command should create a json file that defines a cluster", command, f"{home_dir}")
print(f"res = {res}\n")

port_0 = (f"{port}") 
port_1 = (f"{port}")
print(f"The pg version, port, port_01 is: {pgv}, {port_0}, {port_1}")
new_path_0 = (f"{cwd}/{new_cluster_dir}/{tmpcluster}/n1")
new_path_1 = (f"{cwd}/{new_cluster_dir}/{tmpcluster}/n2")

print(f"The path to n1 is: {new_path_0}")
print(f"The path to n2 is: {new_path_1}")

stanza = "demo_stanza"
repo_path = "/var/lib/pgbackrest"
repo_retention_full = 7
log_level_console = "info"
repo_cipher_type = "aes-256-cbc"
archive_mode = "on"

with open(f"{new_cluster_dir}/{tmpcluster}.json", 'r') as file:
    data = json.load(file)
    #print(f"Line 49 - {data}")
    data["node_groups"][0]["port"] = port_0
    data["node_groups"][1]["port"] = port_1
    data["node_groups"][0]["path"] = new_path_0
    data["node_groups"][1]["path"] = new_path_1

newdata = json.dumps(data, indent=4)
with open(f"{new_cluster_dir}/{tmpcluster}.json", 'w') as file:
    file.write(newdata)

# Use cluster init to initialize the cluster defined in the template file.
# This will throw an error because both ports in the json file are the same.
# 
command = (f"cluster init {tmpcluster}")
res1=util_test.run_nc_cmd("This command initializes the cluster", command, f"{home_dir}")
print(f"res1.returncode contains = {res1.returncode}\n")
print(f"res1.stdout contains = {res1.stdout}\n")
print("*"*100)

print("This test should return a pass if the error 'Port 6432 is unavailable' is in the output!")

if "Port 6432 is unavailable" in str(res1.stdout):

    util_test.EXIT_PASS()
else:
    util_test.EXIT_FAIL()

