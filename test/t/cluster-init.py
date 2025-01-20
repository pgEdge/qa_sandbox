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
repuser=os.getenv("EDGE_REPUSER","susan")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
spockver=os.getenv("EDGE_SPOCK_VER","4.0.1")
dbname=os.getenv("EDGE_DB","lcdb")

cwd=os.getcwd()
num_nodes=3
port=6432
port1=6433
port2=6434

#print("*"*100)

print(f"home_dir = {home_dir}\n")
command = (f"cluster json-create {cluster_name} {num_nodes} {dbname} {usr} {pw} --port={port} --pg_ver={pgv} --force")
res=util_test.run_nc_cmd("This command should create a json file that defines a cluster", command, f"{home_dir}")
print(f"res = {res}\n")

pg_ver = (f"{pgv}")
new_ver = (f"{spockver}")
port_0 = (f"{port}") 
port_1 = (f"{port1}")
port_2 = (f"{port2}")
print(f"Spock new version, pg version, port, port_01, port_02 is: {new_ver}, {pg_ver}, {port_0}, {port_1}, {port_2}")
new_path_0 = (f"{cwd}/{cluster_dir}/n1")
new_path_1 = (f"{cwd}/{cluster_dir}/n2")
new_path_2 = (f"{cwd}/{cluster_dir}/n3")

stanza = "demo_stanza"
repo_path = "/var/lib/pgbackrest"
repo_retention_full = 7
log_level_console = "info"
repo_cipher_type = "aes-256-cbc"
archive_mode = "on"

with open(f"{cluster_dir}/{cluster_name}.json", 'r') as file:
    data = json.load(file)
    #print(f"Line 49 - {data}")
    data["pgedge"]["pg_version"] = pg_ver
    data["pgedge"]["spock"]["spock_version"] = new_ver
    data["node_groups"][0]["port"] = port_0
    data["node_groups"][1]["port"] = port_1
    data["node_groups"][2]["port"] = port_2
    data["node_groups"][0]["path"] = new_path_0
    data["node_groups"][1]["path"] = new_path_1
    data["node_groups"][2]["path"] = new_path_2

newdata = json.dumps(data, indent=4)
with open(f"{cluster_dir}/{cluster_name}.json", 'w') as file:
    file.write(newdata)
    
print(newdata)

command = (f"cluster init {cluster_name}")
init=util_test.run_nc_cmd("This command should initialize a cluster based on the json file", command, f"{home_dir}")
print(f"init = {init.stdout}\n")
print("*"*100)

## 
## Check the replication state:
port = port
print(f"You're in the loop on line 94, and the port is: {port}")
subscriptions =["sub_n1n2","sub_n2n1","sub_n3n1"]
n = 0
for sub in subscriptions:
    n = n + 1
    ## Confirm with spock sub-show-status
    status=util_test.run_cmd("Checking spock sub-show-status", (f"spock sub-show-status {sub} {dbname}"), f"{cluster_dir}/n{n}")
    print(f"The spock sub-show-status {sub} {dbname} command on n{n} returns: {status.stdout}, {status.stderr}")
    port = port + 1

# Needle and Haystack
# Confirm the command worked by looking for:

if "\nSyntaxError" not in str(init.stdout) or init.returncode == 1:

    util_test.EXIT_PASS()
else:
    util_test.EXIT_FAIL()



