import requests
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv()


## create db
def create_db_and_collection(db_uri:str, mongo_db:str,mongo_collection:str):
    # establish connection
    client = MongoClient(db_uri)

    # create db
    client.mongo_db_name

    # create collection
    db = client[mongo_db]
    db.create_collection(mongo_collection)

    return db


# extract data
def extract(location:str, cods:tuple)->list:
    lat = cods[0]
    long = cods[1]
    loc_data = []

    base_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={long}&hourly=pm2_5,pm10,ozone,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,uv_index"
    response = requests.get(base_url)
    retrieval_time = datetime.now(timezone.utc).isoformat(timespec='minutes')
    data = response.json()
    hourly_data = data['hourly']
    for time, pm2_5, pm10, ozone, carbon_monoxide, nitrogen_dioxide, sulphur_dioxide, uv_index in zip(
        hourly_data['time'],
        hourly_data['pm2_5'],
        hourly_data['pm10'],
        hourly_data['ozone'],
        hourly_data['carbon_monoxide'],
        hourly_data['nitrogen_dioxide'],
        hourly_data['sulphur_dioxide'],
        hourly_data['uv_index']
    ):
        loc_data.append(
            {   
                "location":location,
                "retrieval_time": retrieval_time,
                "forecast_time":time,
                "pm2_5":pm2_5,
                "pm10":pm10,
                "ozone":ozone,
                "carbon_monoxide":carbon_monoxide,
                "nitrogen_dioxide":nitrogen_dioxide,
                "sulphur_dioxide":sulphur_dioxide,
                "uv_index":uv_index
            }
        )
    return loc_data


# load data
def load_data(db, mongo_collection:str, data:list[dict]):
    collection = db[str(mongo_collection)]
    collection.insert_many(data)



if __name__ == '__main__':

    db_uri = os.getenv('DB_URI')

    mongo_db = os.getenv('MONGO_DB')
    mongo_collection = os.getenv('MONGO_COLLECTION')
    mongo_user = os.getenv('MONGO_USER')
    mongo_password = os.getenv('MONGO_PASSWORD')

    # load_data
    town_cods = {
        "nairobi": (1.286389,36.817223),
        "mombasa": (-4.043477,39.668206),

    }

    # create db
    print("creating dbs and collection")
    mongodb_uri = f"mongodb://{mongo_user}:{mongo_password}@mongodb:27017/?replicaSet=rs0&authSource=admin"
    db = create_db_and_collection(mongodb_uri, mongo_db, mongo_collection)

    # extract data
    mongo_data = []
    for location, cods in town_cods.items():
        try:
            print('extracting data')
            data = extract(location, cods)
            mongo_data.extend(data)
        except Exception as e:
            print(e)
            continue

    # load data
    print("Loading data into mongodb...")
    load_data(db, mongo_collection, mongo_data)