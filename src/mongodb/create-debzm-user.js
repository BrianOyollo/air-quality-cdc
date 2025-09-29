
db = db.getSiblingDB("admin");

// create a user for debezium
// this user will be able to read all databases as required by debezium
// can be customized to from a specific db

db.createUser({
  user: "debezium",
  pwd:  "debeziumPass123",
  roles: [
    { role: "readAnyDatabase", db: "admin" }, // allows the users to read all dbs
    { role: "clusterMonitor", db: "admin" }     // can read replica set & config info
  ]
});
