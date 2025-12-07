## 🚀 Overview

<img width="805" height="193" alt="Screenshot_6" src="https://github.com/user-attachments/assets/9ac8bee3-3dbd-434a-a820-3668dc8b17fd" />

This project builds a **scalable and maintainable ETL (Extract, Transform, Load) pipeline** using:

- **Apache Airflow** for orchestration  
- **Docker** for containerization and environment consistency
- **PostgreSQL** as the online sales data source  
- **MySQL** as the target data warehouse  


The pipeline automates the end-to-end data flow—**extracting sales data**, **transforming and aggregating it by product**, and **loading it into a data warehouse** for analysis.

---

## 📁 Project Structure

- `dags/`: Contains Airflow DAGs including the main ETL workflow (`etl.py`)
- `logs/`: Stores DAG run logs for monitoring and debugging
- `docker-compose.yml`: Defines Docker services (Airflow, PostgreSQL, MySQL)
- `Dockerfile`: Custom Airflow image setup with dependencies
- `requirements.txt`: Lists Python dependencies for the Airflow pipeline
- `airflow.cfg`: Airflow configuration (executor, connections, etc.)

---

## Docker & Airflow Integration

Docker ensures an **isolated, reproducible, and platform-independent environment**.  
Docker Compose runs containers for:

- **PostgreSQL** (online sales data)  
- **MySQL** (data warehouse)  
- **Apache Airflow** (ETL scheduler and orchestrator)  

This architecture supports seamless deployment across any system with Docker installed.

---

## ⏳ DAG Design: `etl_sales_pipeline`

This Airflow DAG runs **daily** and follows a classic **ETL workflow**:

### 🔹 Task Breakdown

#### 1. `extract_postgresql` – Extract Online Sales

- **Operator**: `PythonOperator`  
- **Description**: Fetches data from the `online_sales` table (PostgreSQL) for the previous day and saves it as `online_sales_data.csv`.  
- **Tools**: `PostgresHook`, `get_pandas_df()`  

#### 2. `extract_csv` – Extract In-Store Sales

- **Operator**: `PythonOperator`  
- **Description**: Reads `in_store_sales.csv` and writes it as `in_store_sales_data.csv` for transformation.

#### 3. `transform_data` – Transform Sales Data

- **Operator**: `PythonOperator`  
- **Description**: Combines online and in-store data, removes nulls, aggregates sales by `product_id`, and outputs `aggregated_sales_data.csv`.

#### 4. `load_to_mysql` – Load Aggregated Data

- **Operator**: `PythonOperator`  
- **Description**: Loads `aggregated_sales_data.csv` into the `sales_aggregated` table in MySQL.  
- **Tools**: `MySqlHook`, with `ON DUPLICATE KEY UPDATE` to handle updates gracefully.

---

## 💡 Key Benefits

- **Containerized environment** ensures consistent behavior across systems  
- **Airflow orchestration** provides robust scheduling, monitoring, and error handling  
- **Extensible design** allows easy integration of:
  - New data sources  
  - Advanced transformation logic  
  - Data quality checks and alerts

---

## 📸 Screenshots

<img width="1173" height="397" alt="Screenshot_7" src="https://github.com/user-attachments/assets/a8e08ccf-6763-494a-8113-d3ba2c61af57" />
<img width="782" height="433" alt="Screenshot_2" src="https://github.com/user-attachments/assets/3dec022c-c30c-4567-9611-b88d89ddb36b" />
<img width="781" height="230" alt="Screenshot_1" src="https://github.com/user-attachments/assets/6f5eaa80-f16f-46fc-86a7-1b61d375dc16" />
<img width="767" height="378" alt="Screenshot_3" src="https://github.com/user-attachments/assets/23bb0174-6b13-4183-aa21-d859bce690e9" />
<img width="1164" height="591" alt="Screenshot_8" src="https://github.com/user-attachments/assets/23670041-009f-4083-8975-d89613f34707" />





---
