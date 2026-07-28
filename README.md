# RetailX Sales Intelligence Platform

End-to-end Microsoft Fabric data engineering project combining batch ingestion,
medallion architecture, PySpark transformations, Warehouse views,
Power BI reporting, and real-time analytics using Eventstream and KQL.





# Business Scenario
RetailX is a fictional 50-store retail chain operating across multiple cities in India across 3 regions (North, South, West).



The project was built to solve four business problems:
1. Load daily Sales data incrementally sql server.
2. Refresh store and product reference data from CSV files.
3. Enrich  Sales with weather data from OpenWeatherMap API.
4. Provide a live real-time dashboard using Eventstream and KQL


-----


## Architecture

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/09fa5666-0424-4fbd-8f0e-80812564c209" />


### Batch Flow

- On-Premises SQL Server
-  On-Premise Data gateway 
- Microsift Data fabric pipeline
- Bronze lakehouse
-  Silver Pyspark Notebooks
- Gold Pyspark Notebooks
- Fabric warehouse Viwes
- Semantic Model
- Power BI Dashboard


### Real-Time Flow
POS event Generator 
- Fabric Eventstream
- Eventhouse / KQL Database
- KQL Queries
- Real - Time Dashboard

----

## Data Sources


### 1. On-Premises SQL Server

1. First import the Sales Transaction.csv file into the SSMS inside the RetailX_Orders database then Sales transaction data was extracted from a locally hosted SQL Server database.

2. The pipeline used the `LastModifiedDate` column as a watermark to load only
new or modified rows.


Flow:
- Import Sales Transaction csv file to SSMS
-  On-Premises Data Gateway
-   Fabric Copy Activity
-   Bronze Lakehouse

### 2. CSV Files  

Store and Product master dataset was loaded feom CSV files.

Because the datasets were small, a full-refresh overwrite pattern was used.



Files:
- stores.csv
- products.csv
- employees.csv
- sample_transactions.csv   (TO test incremental load)
- Sales Transaction 



### 3. OpenWeatherMap API (Ingest WeatherAPI (Daily))

Weather forecast data was extracted from the OpenWeatherMap API.


Main URL : https://api.openweathermap.org/

https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}

- Calls api.openweathermap.org/data/2.5/forecast for 9 cities.
- Fetches 5-day weather forecast (temperature, humidity, rainfall).
- Flattens JSON response into rows (one per forecast interval per city)
- Writes to bronze_weather (overwrite daily)



Sales teams want to correlate rainy days with in-store footfall drops.
Demonstrates: API auth handling, JSON flattening, rate limit awareness



## Medallion Architecture

The project follows the Bronze, Silver, and Gold medallion architecture.

```text
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
```




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

- Silver_SalesTransaction
- Silver_store
- Silver_product
- Silver_weather




### Main Transformations:
- Duplicate removal
- Null-value validation
- Data-type conversion
- String standardisation
- Derived Columns
- Meta Columns
- Data-quality validation
- Weather JSON flattening



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






---

## Batch Pipelines

The batch architecture contains three ingestion patterns:

1. Incremental SQL Server ingestion
2. Full-refresh CSV ingestion
3. Daily weather API ingestion

### 1. Incremental Sales Transaction Pipeline

The `Ingest_salesTransaction` pipeline extracts new or modified sales records
from the locally hosted SQL Server database.

The pipeline uses the `LastModifiedDate` column as a high-watermark.


SELECT *
FROM dbo.SalesTransaction
WHERE LastModifiedDate > @LastWatermark




Pipeline flow:


SQL Server SalesTransaction Table
        ↓
On-Premises Data Gateway
        ↓
Fabric Copy Activity
        ↓
Bronze Lakehouse
        ↓
Update Watermark



After a successful load, the watermark is updated to the maximum
LastModifiedDate received in the current batch.

This prevents the pipeline from reloading the complete historical table during
every run



2. CSV Full-Refresh Pipeline

Store, product, and employee reference datasets are relatively small.

Therefore, these datasets use a full-refresh overwrite pattern instead of
incremental loading.

Files loaded:

stores.csv
products.csv
employees.csv


CSV Files
    ↓
Fabric Pipeline / Notebook
    ↓
Bronze Lakehouse
    ↓
Overwrite Existing Reference Tables



3. Weather API Ingestion

The nb_ingest_api notebook calls the OpenWeatherMap forecast API for the
configured cities.

The JSON response is flattened into tabular format and written to the Bronze
Lakehouse.

Main weather fields:

City
Forecast timestamp
Temperature
Humidity
Weather condition
Rainfall
Wind speed

The weather dataset is refreshed daily.


## PySpark Notebooks

The project uses Fabric PySpark notebooks for ingestion, cleansing,
transformation, enrichment, and aggregation.



### Ingestion Notebooks

#### `nb_ingest_csv`

Loads store and product reference CSV files into the Bronze Lakehouse.

#### `nb_ingest_api`

Extracts weather forecast data from OpenWeatherMap, flattens the JSON response,
and writes the result to the Bronze Lakehouse.


#### `nb_silver_sales`

Main transformations:

- Removes duplicate transactions
- Keeps the latest record using `LastModifiedDate`
- Converts columns to correct data types
- Standardises payment methods and IDs
- Creates Year, Month, Quarter, and Week columns
- Identifies return transactions
- Calculates NetRevenue
- Sends invalid records to `quarantine_sales`

#### `nb_silver_store`

Main transformations:

- Removes duplicate stores
- Standardises city and region values
- Converts OpenDate to date
- Calculates StoreAgeYears
- Creates SizeBucket
- Identifies premium and flagship stores

#### `nb_silver_products`

Main transformations:

- Removes duplicate products
- Converts price columns to decimal
- Calculates GrossMarginPct
- Creates PriceBand
- Calculates DaysSinceLaunch
- Identifies new products

#### `nb_silver_weather`

Main transformations:

- Flattens weather JSON
- Converts forecast time to timestamp
- Creates forecast date
- Identifies rainy conditions
- Creates temperature and humidity categories




### Gold Aggregation Notebooks



Creates one row per store per day by joining:

- Silver sales
- Silver stores
- Silver weather



#### `nb_gold_store_perf`

Creates an all-time performance summary for each store.

#### `nb_gold_product_rank`

Creates an all-time sales and profitability summary for each product.





## Serving Layer



TheGOld Lakehouse tables are exposed thriugh the SQL viws in the `RetailX_DWH` Fabric Warehouse.

SQL Views

- `vw_daily_sales`
- `vw_store_performance`
- `vw_product_rankings`



Flow:


Gold Lakehouse
    ↓
Fabric Warehouse SQL Views
    ↓
Semantic Model
    ↓
Power BI Dashboard



# Then: Semantic Model


The `RetailX_Semantic_Model` was created using the warehouse viwes.


### Relationship


vw_store_performance (1)
        ↓
vw_daily_sales (Many)

join key   ---> StoreID


vw_product_rankings remains standalone because ProductID is not present in
the store-day grain of vw_daily_sales.



# Then: DAX Measures

## DAX Measures

Total Revenue =
SUM(vw_daily_sales[NetRevenue])


Total Transactions =
SUM(vw_daily_sales[TransactionCount])


Average Basket Size =
AVERAGE(vw_daily_sales[AvgBasketSize])



Return Rate % =
DIVIDE(
    SUM(vw_daily_sales[ReturnCount]),
    SUM(vw_daily_sales[TransactionCount]),
    0
) * 100



Top Store =
CALCULATE(
    MAX(vw_store_performance[StoreName]),
    TOPN(
        1,
        vw_store_performance,
        vw_store_performance[TotalRevenue],
        DESC
    )
)





<img width="2048" height="1115" alt="image" src="https://github.com/user-attachments/assets/0faf4fc8-cfe4-467f-9e96-390619be2672" />




## Real-Time Analytics Pipeline

The project includes a separate real-time analytics pipeline for observation live point_pf_scale transaction during store operating.

### Real-Time Architecture


POS Event Generator
Microsoft Fabric Eventstream
RetailX Eventhouse 
KQL Database 
KQL Queries and materialized Viwes 
Real - time Dashboard 


#### POS Event Generator

A Python notebook named POS was used to generate simulated retail transactions.

The generator produced approximately two events per second.


Each event contained:

event_id
store_id
product_id
quantity
unit_price
total_amount
payment_method
timestamp
is_return

The generated JSON events were sent to the Fabric Eventstream Custom App source.

The Eventstream connection string and SAS credentials are not included in this
public repository.


## Fabric Eventstream

Microsoft Fabric Eventstream was used as the managed real-time ingestion layer.

Event configurations:

source : Custom App
Input format:JSON 
Destinaion: RetailX Eventhouse 
Detination table : POSEvents 
status : Actuve during testing 


Eventstream receives the POS events, processes them continuously, and sends them
to the KQL database.

It provides managed streaming capabilities such as:

Continuous event ingestion
JSON event processing
Event routing
Checkpoint management
Event delivery to Eventhouse





## Eventhouse and KQL Database

The RetailX_Eventhouse stores and processes incoming POS events.

The main KQL table is:

Table columns:

event_id
store_id
product_id
quantity
unit_price
total_amount
payment_method
timestamp
is_return

The raw event table uses a 30-day retention period.



#### KQL Materialized Views

Materialized views were created to pre-aggregate streaming data and improve
dashboard performance.

#### HourlyStoreRevenue

Grain: One row per store per hour.

### Metrics:

HourlyRevenue
TransactionCount
UniqueProducts



#### DailyStoreRevenue

Grain: One row per store per day.

### Metrics:

DailyRevenue
TotalTransactions
AverageBasketSize
PaymentMethodSplit

Grain: One row per payment method per hour.

### Metrics:

TransactionCount
Revenue

Materialized views update incrementally when new events arrive, avoiding repeated
full-table scans.

## **Real-Time Dashboard

The RetailX_realtime_dashboard was connected to the KQL database.**

It contains five operational tiles:

1. Live Revenue

Displays total revenue generated during the last hour.

2. Store Leaderboard

Displays the top 10 stores by revenue during the last 15 minutes.

3. Revenue Trend

Displays revenue across the last six hours using 15-minute time intervals.

4. Payment Method Split

Displays the number of transactions and revenue by:

UPI
Card
Cash
Wallet

5. Return Rate

Displays the percentage of return transactions during the last two hours.


### Example KQL Query

The following query calculates the top 10 stores by revenue during the last
15 minutes:

POSEvents
| where timestamp > ago(15m)
| where is_return == false
| summarize
    Revenue = sum(total_amount),
    Transactions = count()
    by store_id
| order by Revenue desc
| take 10



### Real-Time Use Case


The batch pipeline is used for historical reporting and management analysis,
while the real-time pipeline is used for live operational observation.

The POS event generator produced simulated retail transcation at approximately two events per seconds.


the events were sent through Microsoft Fabric Eventstream and stored in the
`POSEvents` table inside the KQL database.

### KQL materialized viewa used to calculate:

- Hourly store revenue
- Daily store revenue
- Payment-method performance

The real-time pipeline helps the operations team observation:

Current store revenue
Top-performing stores
Sudden revenue drops
Payment-method behaviour
Return-rate spikes

The dashboard was configured to refresh every 30 seconds.



## Security

The repository does not contain any sensitive credentials.



The following values are replaced with placeholders:

- OpenWeatherMap API key
- SQL Server password
- Gateway credentials
- Eventstream connection string
- SAS token
- GitHub personal access token



## Tech Stack

- Microsoft Fabric
- Fabric Data Pipelines
- Fabric Lakehouse
- PySpark
- Delta Lake
- Fabric Warehouse
- Semantic Model
- Power BI
- Eventstream
- Eventhouse
- KQL
- SQL Server
- On-Premises Data Gateway
- OpenWeatherMap API



## Author

Himanshu

Microsoft Fabric Data Engineering Portfolio Project
