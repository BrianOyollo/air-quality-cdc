

    CREATE KEYSPACE IF NOT EXISTS weather WITH REPLICATION={
        'class':'SimpleStrategy',
        'replication_factor':1
    };

    USE weather;

    CREATE TABLE weather.air_quality (
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
