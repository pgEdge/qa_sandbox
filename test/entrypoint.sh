#!/bin/bash
set -e

cd /home/pgedge
. /home/pgedge/pgedge/pg16/pg16.env
echo 'export LD_LIBRARY_PATH=/home/pgedge/pgedge/pg16/lib/$LD_LIBRARY_PATH' >> /home/pgedge/.bashrc
echo 'export PATH=/home/test/pgedge/pg16/bin:$PATH' >> /home/pgedge/.bashrc
. /home/pgedge/.bashrc

echo "==========Recompiling Spock=========="
cd ~/spock-private
make clean && make -j16 && make install

echo "==========Installing Spockbench=========="
cd ~/spockbench
sudo python3 setup.py install

cd ~/pgedge
sed -i '/log_min_messages/s/^#//g' data/pg16/postgresql.conf
sed -i -e '/log_min_messages =/ s/= .*/= debug1/' data/pg16/postgresql.conf
./pgedge restart

while ! pg_isready -h /tmp; do
  echo "Waiting for PostgreSQL to become ready..."
  sleep 1
done

psql -h /tmp -U $DBUSER -d $DBNAME -c "drop extension spock;"
psql -h /tmp -U $DBUSER -d $DBNAME -c "drop schema public cascade;"
psql -h /tmp -U $DBUSER -d $DBNAME -c "create schema public;"
psql -h /tmp -U $DBUSER -d $DBNAME -c "create extension spock;"

./pgedge restart

while ! pg_isready -h /tmp; do
  echo "Waiting for PostgreSQL to become ready..."
  sleep 1
done

echo "==========Creating tables and repsets=========="
./pgedge spock node-create $HOSTNAME "host=$HOSTNAME user=pgedge dbname=demo" demo
./pgedge spock repset-create demo_replication_set demo

IFS=',' read -r -a peer_names <<< "$PEER_NAMES"

for PEER_HOSTNAME in "${peer_names[@]}";
do
  while :
    do
      mapfile -t node_array < <(psql -A -t demo -h $PEER_HOSTNAME -c "SELECT node_name FROM spock.node;")
      for element in "${node_array[@]}";
      do
        if [[ "$element" == "$PEER_HOSTNAME" ]]; then
            break 2
        fi
      done
      sleep 1
      echo "Waiting for $PEER_HOSTNAME..."
    done
done

# TODO: Re-introduce parallel slots at a later point when the apply worker restarts are handled correctly
# and transactions are not skipped on restart in parallel mode
./pgedge spock sub-create sub_${peer_names[0]}$HOSTNAME   "host=${peer_names[0]} port=5432 user=pgedge dbname=demo" demo
#./pgedge spock sub-create "sub_${peer_names[0]}$HOSTNAME"_1 "host=${peer_names[0]} port=5432 user=pgedge dbname=demo" demo
#./pgedge spock sub-create "sub_${peer_names[0]}$HOSTNAME"_2 "host=${peer_names[0]} port=5432 user=pgedge dbname=demo" demo
#./pgedge spock sub-create "sub_${peer_names[0]}$HOSTNAME"_3 "host=${peer_names[0]} port=5432 user=pgedge dbname=demo" demo
#./pgedge spock sub-create "sub_${peer_names[0]}$HOSTNAME"_4 "host=${peer_names[0]} port=5432 user=pgedge dbname=demo" demo

./pgedge spock sub-create sub_${peer_names[1]}$HOSTNAME   "host=${peer_names[1]} port=5432 user=pgedge dbname=demo" demo
#./pgedge spock sub-create "sub_${peer_names[1]}$HOSTNAME"_1 "host=${peer_names[1]} port=5432 user=pgedge dbname=demo" demo
#./pgedge spock sub-create "sub_${peer_names[1]}$HOSTNAME"_2 "host=${peer_names[1]} port=5432 user=pgedge dbname=demo" demo
#./pgedge spock sub-create "sub_${peer_names[1]}$HOSTNAME"_3 "host=${peer_names[1]} port=5432 user=pgedge dbname=demo" demo
#./pgedge spock sub-create "sub_${peer_names[1]}$HOSTNAME"_4 "host=${peer_names[1]} port=5432 user=pgedge dbname=demo" demo

psql -U admin -h /tmp -d demo -c "create table t1 (id serial primary key, data int8);"
psql -U admin -h /tmp -d demo -c "create table t2 (id serial primary key, data int8);"
psql -U admin -h /tmp -d demo -c "alter table t1 alter column data set (log_old_value=true, delta_apply_function=spock.delta_apply);"

./pgedge spock sub-add-repset sub_${peer_names[0]}$HOSTNAME demo_replication_set demo
#./pgedge spock sub-add-repset "sub_${peer_names[0]}$HOSTNAME"_1 demo_replication_set demo
#./pgedge spock sub-add-repset "sub_${peer_names[0]}$HOSTNAME"_2 demo_replication_set demo
#./pgedge spock sub-add-repset "sub_${peer_names[0]}$HOSTNAME"_3 demo_replication_set demo
#./pgedge spock sub-add-repset "sub_${peer_names[0]}$HOSTNAME"_4 demo_replication_set demo

./pgedge spock sub-add-repset sub_${peer_names[1]}$HOSTNAME demo_replication_set demo
#./pgedge spock sub-add-repset "sub_${peer_names[1]}$HOSTNAME"_1 demo_replication_set demo
#./pgedge spock sub-add-repset "sub_${peer_names[1]}$HOSTNAME"_2 demo_replication_set demo
#./pgedge spock sub-add-repset "sub_${peer_names[1]}$HOSTNAME"_3 demo_replication_set demo
#./pgedge spock sub-add-repset "sub_${peer_names[1]}$HOSTNAME"_4 demo_replication_set demo


cd /home/pgedge && ./run-tests.sh $peer_names
