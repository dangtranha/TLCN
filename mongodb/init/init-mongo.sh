#!/bin/bash
set -e

# Start mongod in background
mongod --replSet rs0 --bind_ip_all --fork --logpath /var/log/mongodb.log

# Wait a few seconds for mongod to start
sleep 5

# Init replica set
mongosh --eval 'rs.initiate({_id: "rs0", members: [{ _id: 0, host: "localhost:27017" }]})'

# Create database, collections, user
mongosh <<EOF
db = db.getSiblingDB("pipeline");
db.createCollection("sales");
db.createCollection("products");
db.createUser({
  user: "debezium",
  pwd: "dbz",
  roles: [
    { role: "readWrite", db: "pipeline" },
  ]
});
EOF

# Keep mongod running in foreground
mongod --replSet rs0 --bind_ip_all