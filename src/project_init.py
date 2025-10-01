import os
import json
import re
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# some regex pattern to clean user provided values
# guided by ChatGPT

VALID_NAME = re.compile(r'^[A-Za-z][A-Za-z0-9_]*[A-Za-z0-9]$')

def sanitize_env_var(name, value):
    if not value:
        raise ValueError(f"Missing required env var: {name}")
    if not VALID_NAME.match(value):
        raise ValueError(f"Invalid value for {name}: '{value}'.\n"
                         ">> Only letters, numbers, and underscores are allowed.\n"
                         ">> Provided value must start and end with a letter.\n" \
                         ">> Spaces are not allowed")
    return value


MONGO_DB = sanitize_env_var("MONGO_DB", os.getenv("MONGO_DB"))
MONGO_COLLECTION = sanitize_env_var("MONGO_COLLECTION", os.getenv("MONGO_COLLECTION"))

MONGO_ROOT_USERNAME = sanitize_env_var("MONGO_ROOT_USERNAME", os.getenv("MONGO_ROOT_USERNAME"))
MONGO_ROOT_PASSWORD = sanitize_env_var("MONGO_ROOT_PASSWORD", os.getenv("MONGO_ROOT_PASSWORD"))

MONGO_EXPRESS_USERNAME = sanitize_env_var("MONGO_EXPRESS_USERNAME", os.getenv("MONGO_EXPRESS_USERNAME"))
MONGO_EXPRESS_PASSWORD = sanitize_env_var("MONGO_EXPRESS_PASSWORD", os.getenv("MONGO_EXPRESS_PASSWORD"))

MONGO_DEBEZIUM_USER_NAME = sanitize_env_var("MONGO_DEBEZIUM_USER_NAME", os.getenv("MONGO_DEBEZIUM_USER_NAME"))
MONGO_DEBEZIUM_USER_PASSWORD = sanitize_env_var("MONGO_DEBEZIUM_USER_PASSWORD", os.getenv("MONGO_DEBEZIUM_USER_PASSWORD"))

CASSANDRA_KEYSPACE = sanitize_env_var("CASSANDRA_KEYSPACE", os.getenv("CASSANDRA_KEYSPACE"))
CASSANDRA_COLLECTION = sanitize_env_var("CASSANDRA_COLLECTION", os.getenv("CASSANDRA_COLLECTION"))


# ---------- Source Connector ----------
source_config = {
    "name": "mongo-connector",
    "config": {
        "connector.class": "io.debezium.connector.mongodb.MongoDbConnector",
        "tasks.max": "1",
        "mongodb.connection.string": f"mongodb://{MONGO_DEBEZIUM_USER_NAME}:{MONGO_DEBEZIUM_USER_PASSWORD}@mongodb:27017/?replicaSet=rs0",
        "mongodb.user": f"{MONGO_ROOT_USERNAME}",
        "mongodb.password": f"{MONGO_ROOT_PASSWORD}",
        "mongodb.authsource": "admin",
        "topic.prefix": f"{MONGO_DB}",
        "capture.scope": "deployment",
        "snapshot.mode": "initial",
        "transforms": "unwrap",
        "transforms.unwrap.type": "io.debezium.connector.mongodb.transforms.ExtractNewDocumentState",
        "transforms.unwrap.delete.tombstone.handling.mode": "drop",
        "transforms.unwrap.add.headers": "op"
    }
}

# ---------- Sink Connector ----------
sink_config = {
    "name": "cassandra-sink-connector",
    "config": {
        "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
        "tasks.max": "1",
        "topics": f"{MONGO_DB}.{MONGO_DB}.{MONGO_COLLECTION}",
        "contactPoints": "cassandra",
        "loadBalancing.localDc": "datacenter1",
        "port": 9042,
        "auth.provider": "None",
        "ssl.provider": "None",
        f"topic.{MONGO_DB}.{MONGO_DB}.{MONGO_COLLECTION}.{CASSANDRA_KEYSPACE}.{CASSANDRA_COLLECTION}.mapping": (
            "forecast_time=value.forecast_time,"
            "retrieval_time=value.retrieval_time,"
            "carbon_monoxide=value.carbon_monoxide,"
            "nitrogen_dioxide=value.nitrogen_dioxide,"
            "ozone=value.ozone,"
            "pm10=value.pm10,"
            "pm2_5=value.pm2_5,"
            "sulphur_dioxide=value.sulphur_dioxide,"
            "uv_index=value.uv_index,"
            "location=value.location"
        )
    }
}

cassandra_schema = f"""

    CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE} WITH REPLICATION={{
        'class':'SimpleStrategy',
        'replication_factor':1
    }};

    USE {CASSANDRA_KEYSPACE};

    CREATE TABLE {CASSANDRA_KEYSPACE}.{CASSANDRA_COLLECTION} (
        forecast_time timestamp,
        retrieval_time timestamp,
        location text,
        pm2_5 double,
        pm10 double,
        ozone double,
        carbon_monoxide double,
        nitrogen_dioxide double,
        sulphur_dioxide double,
        uv_index double,
        PRIMARY KEY (location, forecast_time)
    );
"""

mongodb_debezium_user = f"""

    db = db.getSiblingDB("admin");

    // create a user for debezium
    // this user will be able to read all databases as required by debezium
    // can be customized to from a specific db

    db.createUser({{
    user: "{MONGO_DEBEZIUM_USER_NAME}",
    pwd:  "{MONGO_DEBEZIUM_USER_PASSWORD}",
    roles: [
        {{ role: "readAnyDatabase", db: "admin" }}, // allows the users to read all dbs
        {{ role: "clusterMonitor", db: "admin" }}     // can read replica set & config info
    ]
    }});

"""

if __name__ == "__main__":
    # write connector files
    with open("src/connectors/mongo-connector.json", "w") as source_json:
        json.dump(source_config, source_json, indent=2)

    with open("src/connectors/cassandra-sink.json", "w") as sink_json:
        json.dump(sink_config, sink_json, indent=2)

    # write cassandra schema file
    with open("src/cassandra/init.cql", "w") as cass_init:
        cass_init.write(cassandra_schema)

    # write js file for creating mongodb debezium user
    with open("src/mongodb/create-debzm-user.js", "w") as dbzm_user:
        dbzm_user.write(mongodb_debezium_user)


