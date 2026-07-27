# RetailX Sales Intelligence Platform

End-to-end Microsoft Fabric data engineering project combining batch ingestion,
medallion architecture, PySpark transformations, Warehouse views,
Power BI reporting, and real-time analytics using Eventstream and KQL.





# Business Scenario
RetailX is a fictional 50-store retail chain operating across multiple cities in India across 3 regions (North, South, West).



The project was built to solve four business problems:
1. Load daily Sales data incrementally sql server.
2. Refersh store and product reference data from CSV files.
3. Enrich  Sales with weather data from OpenWeatherMap API.
4. Provide a live real-time dashboard using Eventstream and KQL


-----


## Architecture

### Batch Flow

→ On-Premises SQL Server
→ On-Premise Data gateway 
→ Microsift Data fabric pipeline
→ Bzonze lakehouse 
→ Silver Pyspark Notebooks 
→ Gold Pyspark Notebooks
→ Fabric warehouse Viewes
→ Semantic Model 
→ Power BI Dashboard


### Real-Time Flow
POS event Generator 
→ Fabric Eventstream
→ Eventhouse / KQL Database 
→ KQL Queries 
→ Real - Time Dashboard

----

## Data Sources


### 1. On-Premises SQL Server

1. First import the Sales Transaction.csv file into the SSMS inside the RetailX_Orders database then Sales transaction data was extracted from a locally hosted SQL Server database.

2. The pipeline used the `LastModifiedDate` column as a watermark to load only
new or modified rows.


Fow:
→ Import Sales Transaction csv file to SSMS 
→ On-Premises Data Gateway
→ Fabric Copy Activity
→ Bronze Lakehouse

### 2. CSV Files  

Store and Product master dataset was loaded feom CSV files.

Because the datasets were small, a full-refresh overwrite pattern was used.



Files:
- stores.csv
- products.csv
- employees.csv
- sample_transactions.csv   (For incremrental load)
- Sales Transaction 



### 3. OpenWeatherMap API

Weather forecast data was extracted from the OpenWeatherMap API.


Main URL : https://api.openweathermap.org/

https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}


## Medallion Architecture

The project follows the Bronze, Silver, and Gold medallion architecture.

Source Systems
    ↓
Bronze Lakehouse
    ↓
Silver Lakehouse
    ↓
Gold Lakehouse
    ↓
Fabric Warehouse
    ↓
Semantic Model
    ↓
Power BI Dashboard




Main Bronze Lakehouse Tables:

bronze_salesTransaction
bronze_store
bronze_product
bronze_weather
quarantine_sales


Loading patterns:

Sales transactions are appended incrementally.
Store and product master data are overwritten during full refresh.
Weather data is refreshed daily.
Invalid sales records are stored in the quarantine table for investigation.
Silver Layer




##  Silver Layer

The Silver layer contains cleaned, validated, typed, and standardised data.

Main Silver tables:

Silver_SalesTransaction
Silver_store
Silver_product
Silver_weather




### Main Transformations:
Duplicate removal
Null-value validation
Data-type conversion
String standardisation
Derived Columns
Meta Columns
Data-quality validation
Weather JSON flattening



##  Gold Layer

The Gold layer contains aggreagated, business-ready datasets for reporting.


## Gold Layer Data Model


### gold_daily_sales


**Grain:** One row per store per day.

This tables combines sales, store & weather data.

Important columns:

GrossRevenue 
NetRevenue
TransactionCount 
ReturnCount
AvgBasketSize
DiscountRate
ReturnRate
temp_c
rain_mm
is_rainy
Partitioned by Year, Month 


### gold_store_performance

Grain: One row per store.

Important Columns:

- TotalRevenue
- TotalTransactions
- ProductsSold
- ActiveDays
- RegionRank
- OverallRank
- RevenuePerSqFt


### gold_product_rankings

Grain: one row per product

Important Columns:
- TotalRevenue
- UnitsSold
- TransactionCount
- StoresSoldIn
- EstimatedProfit
- CategoryRank
- OverallRank











