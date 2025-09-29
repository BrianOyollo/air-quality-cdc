// this initializes replication
// uses the mongo service from the docker-compose.yml


rs.initiate({
  _id: "rs0",
  members: [{ _id: 0, host: "mongodb:27017" }]
});