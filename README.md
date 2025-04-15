# ETL Sales Pipeline with Apache Airflow

## 🚀 Overview

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

![image](https://github.com/user-attachments/assets/7d86f37e-421d-43fd-86e8-f1e0c49086e4)  
![image](https://github.com/user-attachments/assets/af91a6e0-caa0-4448-ba77-780ae02ac913)  
![image](https://github.com/user-attachments/assets/68ac1d91-bef9-4b7a-ae7a-377e8961288c)  
![image](https://github.com/user-attachments/assets/276c1a75-a06c-4f0a-93b5-d4ff68e408de)  
![image](https://github.com/user-attachments/assets/0cb47581-d9e3-47f9-85fb-2955be177359)

---
