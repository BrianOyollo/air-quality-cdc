
**Real-Time Air Quality Data Pipeline**
This project implements a real-time data pipeline for air quality metrics using **Change Data Capture (CDC)** techniques. The pipeline pulls air quality data from the **Open-Meteo API**, stores the raw data in **MongoDB**, and uses CDC to stream updates to a **Cassandra** database for efficient querying and historical analysis.

Key components and technologies:
-   **Data Sources:** Open-Meteo API for air quality metrics.
-   **Databases:** MongoDB for raw data storage, Cassandra for historical/analytical queries.  
-   **Data Pipeline:** Apache Kafka to handle CDC events between MongoDB and Cassandra
-   **Programming Language:** Python for data ingestion, transformation
-   **Containerization:** Docker for environment consistency and easy deployment

...