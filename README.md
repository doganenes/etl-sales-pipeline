# ETL Sales Pipeline with Apache Airflow

## Overview

This project implements an **ETL pipeline using Apache Airflow** to automate the extraction, transformation, and loading of sales data. It:

- Extracts **e-commerce sales data from a PostgreSQL** database  
- Extracts **in-store sales data from a CSV** file  
- Aggregates **total sales per product**  
- Loads the transformed data into a **MySQL data warehouse** for analysis  

The pipeline uses **Airflow for orchestration** and **Docker for containerization**, ensuring scalability, maintainability, and platform compatibility.

---

## Project Structure

- **`dags/` Folder**: Contains Airflow DAG files, including the main ETL pipeline (`etl.py`) which manages all tasks.
- **`logs/` Folder**: Stores logs for monitoring and debugging DAG runs.
- **`docker-compose.yml`**: Defines services for PostgreSQL, MySQL, and Apache Airflow components.
- **`Dockerfile`**: Specifies the environment for Apache Airflow, including dependencies.
- **`requirements.txt`**: Lists Python dependencies for the Airflow pipeline.
- **`airflow.cfg`**: Contains Airflow configuration settings like executor type and database connections.

---

## Docker and Airflow Integration

This project uses Docker for containerization, providing **isolated and reproducible environments**.  
Docker Compose manages containers for:

- **PostgreSQL** (sales data)  
- **MySQL** (data warehouse)  
- **Apache Airflow** (ETL orchestration)  

This setup eliminates platform-specific issues, ensuring a **consistent and scalable environment** across all platforms that support Docker.

---

## DAG Design: `etl_sales_pipeline`

This DAG is designed to perform a **daily ETL (Extract, Transform, Load)** process for sales data.

### Tasks and Rationale

#### 1. Extract PostgreSQL Sales Data (`extract_postgresql`)

- **Operator**: `PythonOperator`  
- **Description**: Extracts sales data from the `online_sales` table in a PostgreSQL database for the previous day. Saves it as `online_sales_data.csv`.  
- **Tools**: `PostgresHook`, `get_pandas_df`  
- **Why?**: PythonOperator allows custom SQL logic, and PostgresHook is ideal for PostgreSQL connections.

---

#### 2. Extract CSV Sales Data (`extract_csv`)

- **Operator**: `PythonOperator`  
- **Description**: Reads from `in_store_sales.csv` and saves it as `in_store_sales_data.csv`.  
- **Why?**: PythonOperator offers flexibility for file reading/writing using Pandas.

---

#### 3. Transform Sales Data (`transform_data`)

- **Operator**: `PythonOperator`  
- **Description**: Combines online and in-store sales data, removes nulls, aggregates by `product_id`, and saves as `aggregated_sales_data.csv`.  
- **Why?**: Custom transformations are easier with Pandas and Python logic.

---

#### 4. Load Data into MySQL (`load_to_mysql`)

- **Operator**: `PythonOperator`  
- **Description**: Loads `aggregated_sales_data.csv` into `sales_aggregated` table in MySQL. Uses `ON DUPLICATE KEY UPDATE` to update existing records.  
- **Tools**: `MySqlHook`  
- **Why?**: Allows dynamic and custom SQL inserts.

---

### Operator Choice Rationale

- **PythonOperator** is used for all tasks:
  - It provides flexibility for:
    - Custom SQL querying
    - File manipulation
    - Data transformation
  - Perfect fit for integrating Pandas and Airflow hooks

---

## Overall Design Rationale

- The pipeline follows a **clear 4-stage ETL structure**: extract → transform → load  
- **Dependencies** between tasks ensure correct execution order  
- Python is used for all tasks to allow custom logic and handle multiple data sources  
- Scheduled to **run daily**  
- `catchup=False` ensures only future runs are processed (no backfilling)

---

## Challenges and Solutions

### 1. Platform and Software Compatibility Issues

- **Challenge**: Apache Airflow setup was difficult on WSL due to dependency mismatches  
- **Solution**: Docker containerization solved platform issues by standardizing the environment

---

### 2. Efficient Data Extraction and Transformation

- **Challenge**: Handling large datasets was slow and resource-intensive  
- **Solution**:  
  - Optimized SQL queries  
  - Used Airflow’s parallel processing capabilities

---

### 3. Debugging DAG Execution Failures

- **Challenge**: Debugging task failures with dependencies was complex  
- **Solution**: Airflow’s built-in logging made it easy to identify and resolve issues

---

## Conclusion

This project builds a **scalable and maintainable ETL pipeline** using:

- Apache Airflow  
- PostgreSQL  
- MySQL  
- Docker  

### Key Benefits:

- **Containerization** ensures consistent deployment  
- **Airflow orchestration** simplifies monitoring and error-handling  
- **Flexible and extensible design** allows for easy future enhancements, including:
  - Additional data sources  
  - Advanced data transformations  
  - Data quality validation

---

## Screenshots
![image](https://github.com/user-attachments/assets/7d86f37e-421d-43fd-86e8-f1e0c49086e4)
![image](https://github.com/user-attachments/assets/af91a6e0-caa0-4448-ba77-780ae02ac913)
![image](https://github.com/user-attachments/assets/68ac1d91-bef9-4b7a-ae7a-377e8961288c)
![image](https://github.com/user-attachments/assets/276c1a75-a06c-4f0a-93b5-d4ff68e408de)
![image](https://github.com/user-attachments/assets/0cb47581-d9e3-47f9-85fb-2955be177359)

