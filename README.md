

**Capstone Project: Real-Time Air Quality Data Pipeline**
This project implements a real-time data pipeline for air quality metrics using **Change Data Capture (CDC)** techniques. The pipeline pulls air quality data from the **Open-Meteo API**, stores the raw data in **MongoDB**, and uses CDC to stream updates to a **Cassandra** database for efficient querying and historical analysis.

Key components and technologies:
-   **Data Sources:** Open-Meteo API for air quality metrics.
-   **Databases:** MongoDB for raw data storage, Cassandra for historical/analytical queries.  
-   **Data Pipeline:** Apache Kafka to handle CDC events between MongoDB and Cassandra
-   **Programming Language:** Python for data ingestion, transformation
-   **Containerization:** Docker for environment consistency and easy deployment

# Running the Pipeline
1. Create a .env file inside the `src` folder with the following variables
```
# ================================
# MongoDB Configuration
# ================================

# Name of the MongoDB database where raw data will be stored
MONGO_DB=

# Name of the MongoDB collection to store air quality data
MONGO_COLLECTION=

# Root credentials for MongoDB (used for admin operations & replica set initialization)
# NOTE: Use these values when initiating the replica set
MONGO_ROOT_USERNAME=
MONGO_ROOT_PASSWORD=

# ================================
# Mongo Express (UI for MongoDB)
# ================================

# Credentials for accessing Mongo Express web UI
MONGO_EXPRESS_USERNAME=
MONGO_EXPRESS_PASSWORD=

# ================================
# Debezium MongoDB CDC User
# ================================

# User created specifically for Debezium to capture MongoDB change events
MONGO_DEBEZIUM_USER_NAME=
MONGO_DEBEZIUM_USER_PASSWORD=

# ================================
# Cassandra Configuration
# ================================

# Cassandra keyspace for storing CDC-propagated data
CASSANDRA_KEYSPACE=

# Cassandra table where air quality data will be stored
CASSANDRA_COLLECTION=
```

2. **Generate MongoDB key file**
```bash
bash src/mongo_keyfile.sh
```
3. **Initialize project files**

This will create the Cassandra schema (at `src/cassandra/init.cql`), Kafka source/sink connector configs (at `src/connectors/`) and the mongodb JS script for creating the debezium user (at `src/mongodb/create-debzm-user.js`)
```bash
uv run src/project_init.py
```
4. start containers
```bash
docker compose --env-file ./src/.env up --build -d
```
5. Initiate mongodb replica set

Replace `username` & `password` with your defined mongodb username and password
```bash
docker exec -i mongodb mongosh \
  --username admin --password admin123 \
  --authenticationDatabase admin \
  --eval 'rs.initiate({_id:"rs0", members:[{_id:0, host:"mongodb:27017"}]})'
```
6.  Create Cassandara keyspace and table
```bash
docker  exec  -i  cassandra  cqlsh < src/cassandra/init.cql
```
7. Register source and sink connectors
```bash
# register source connector
curl -i -X POST \
  -H "Accept:application/json" \
  -H "Content-Type:application/json" \
  http://localhost:8083/connectors/ \
  -d @src/connectors/mongo-connector.json

#register sink connector
curl -i -X POST \
  -H "Accept:application/json" \
  -H "Content-Type:application/json" \
  http://localhost:8083/connectors/ \
  -d @src/connectors/cassandra-sink.json
```
8. Run the ETL app
```bash
docker compose run --rm weather_etl uv run src/app/main.py
```
