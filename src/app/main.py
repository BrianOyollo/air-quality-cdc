import requests
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv()

## create db
def create_db_and_collections(db_name:str, town_cods:dict):

    load_dotenv()

    # uri = "mongodb://admin:admin123@localhost:27017/" 
    # # if running inside docker, replace local with container name and vice versa

    # establish connection
    uri = os.getenv('MONGO_DB_URI')
    client = MongoClient(uri)

    # create db
    client.db_name

    # use the db
    db = client[db_name]

    # create collections
    for town in town_cods.keys():
        try:
            db.create_collection(town)
        except pymongo.errors.CollectionInvalid:
            print(f"Collection: {town} already exists")
    
    return db


# extract data
def extract(city:str, cods:tuple)->list:
    lat = cods[0]
    long = cods[1]

    base_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={long}&hourly=pm2_5,pm10,ozone,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,uv_index"
    response = requests.get(base_url)

    # extract
    town_data = {}
    data = response.json()
    hourly_data = data['hourly']
    town_data['time'] = hourly_data['time']
    town_data['pm2_5'] = hourly_data['pm2_5']
    town_data['pm10'] = hourly_data['pm10']
    town_data['ozone'] = hourly_data['ozone']
    town_data['carbon_monoxide'] = hourly_data['carbon_monoxide']
    town_data['nitrogen_dioxide'] = hourly_data['nitrogen_dioxide']
    town_data['sulphur_dioxide'] = hourly_data['sulphur_dioxide']
    town_data['uv_index'] = hourly_data['uv_index']

    # build the list
    mongo_data = []
    for index, time in enumerate(town_data['time']):
        mongo_data.append({
            "city":city,
            "time":time,
            "pm2_5":town_data['pm2_5'][index],
            "pm10":town_data['pm10'][index],
            "ozone":town_data['ozone'][index],
            "carbon_monoxide":town_data['carbon_monoxide'][index],
            "nitrogen_dioxide":town_data['nitrogen_dioxide'][index],
            "sulphur_dioxide":town_data['sulphur_dioxide'][index],
            "uv_index":town_data['uv_index'][index]
        })

    return mongo_data


# load data
def load_data(db, city:str, data:list):
    collection_obj = db[str(city)]
    collection_obj.insert_many(data)


if __name__ == '__main__':

    town_cods = {
        "nairobi": (1.286389,36.817223),
        "mombasa": (-4.043477,39.668206),


    }

    print("creating dbs and collections")
    db = create_db_and_collections('trials_db', town_cods)

    for city, cods in town_cods.items():
        try:
            print('extracting data')
            data = extract(city, cods)

            print('loading data...')
            load_data(db, city, data)

        except Exception as e:
            print(e)
            continue