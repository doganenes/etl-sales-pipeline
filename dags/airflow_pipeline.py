from datetime import datetime, timedelta
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mysql.hooks.mysql import MySqlHook

import logging

# Default arguments for the DAG
default_args = {
    "owner": "retail_analytics",
    "depends_on_past": False,
    "start_date": datetime(2025, 4, 2),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "retail_sales_etl",
    default_args=default_args,
    description="ETL pipeline for retail sales data",
    schedule_interval="@daily",
    catchup=False,
)


# Function to extract online sales data from PostgreSQL
def extract_online_sales(**kwargs):
    logging.info("Extracting online sales data from PostgreSQL")
    pg_hook = PostgresHook(postgres_conn_id="postgres_retail")
    execution_date = kwargs["ds"]

    extract_sql = f"""
    SELECT product_id, quantity, sale_amount, sale_date 
    FROM online_sales 
    WHERE sale_date = '{execution_date}';
    """
    online_sales_df = pd.DataFrame(pg_hook.get_records(sql=extract_sql))
    online_sales_df.columns = ["product_id", "quantity", "sale_amount", "sale_date"]
    kwargs["ti"].xcom_push(
        key="online_sales_data", value=online_sales_df.to_dict(orient="records")
    )
    logging.info(f"Extracted {len(online_sales_df)} records from PostgreSQL")


# Function to extract in-store sales data from CSV file
def extract_instore_sales(**kwargs):
    logging.info("Extracting in-store sales data from CSV")
    execution_date = kwargs["ds"]
    csv_path = f"/path/to/instore_sales/instore_sales_{execution_date}.csv"
    try:
        df = pd.read_csv(csv_path)
        df["sale_date"] = pd.to_datetime(df["sale_date"])
        df = df[df["sale_date"] == execution_date]
        df = df[["product_id", "quantity", "sale_amount", "sale_date"]]
        kwargs["ti"].xcom_push(
            key="instore_sales_data", value=df.to_dict(orient="records")
        )
        logging.info(f"Extracted {len(df)} records from CSV")
    except Exception as e:
        logging.error(f"Error extracting in-store data: {e}")
        raise


# Function to combine and transform sales data
def transform_sales_data(**kwargs):
    ti = kwargs["ti"]
    execution_date = kwargs["ds"]
    logging.info("Transforming sales data")

    # Get online sales data
    online_sales_data = ti.xcom_pull(
        task_ids="extract_online_sales", key="online_sales_data"
    )
    online_sales_df = pd.DataFrame(online_sales_data)

    # Get in-store sales data
    instore_sales_data = ti.xcom_pull(
        task_ids="extract_instore_sales", key="instore_sales_data"
    )
    instore_sales_df = pd.DataFrame(instore_sales_data)

    # Combine both sales data
    combined_df = pd.concat([online_sales_df, instore_sales_df], ignore_index=True)

    # Data cleansing
    combined_df = combined_df.dropna(subset=["product_id", "quantity", "sale_amount"])
    combined_df = combined_df[combined_df["quantity"] > 0]
    combined_df = combined_df[combined_df["sale_amount"] > 0]
    combined_df["product_id"] = combined_df["product_id"].astype(int)

    # Aggregate data by product_id
    aggregated_df = (
        combined_df.groupby("product_id")
        .agg({"quantity": "sum", "sale_amount": "sum"})
        .reset_index()
    )

    aggregated_df.columns = ["product_id", "total_quantity", "total_sale_amount"]
    ti.xcom_push(key="aggregated_sales", value=aggregated_df.to_dict(orient="records"))
    logging.info(f"Data transformed successfully with {len(aggregated_df)} records")


# Function to load data into MySQL
def load_sales_to_mysql(**kwargs):
    ti = kwargs["ti"]
    aggregated_sales = ti.xcom_pull(
        task_ids="transform_sales_data", key="aggregated_sales"
    )
    aggregated_df = pd.DataFrame(aggregated_sales)

    mysql_hook = MySqlHook(mysql_conn_id="mysql_retail")
    conn = mysql_hook.get_conn()
    cursor = conn.cursor()

    for _, row in aggregated_df.iterrows():
        insert_sql = """
        INSERT INTO aggregated_sales (product_id, total_quantity, total_sale_amount) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        total_quantity = total_quantity + VALUES(total_quantity),
        total_sale_amount = total_sale_amount + VALUES(total_sale_amount);
        """
        cursor.execute(
            insert_sql,
            (row["product_id"], row["total_quantity"], row["total_sale_amount"]),
        )

    conn.commit()
    cursor.close()
    conn.close()
    logging.info(f"Loaded {len(aggregated_df)} records into MySQL")


# Define tasks
extract_online_sales_task = PythonOperator(
    task_id="extract_online_sales",
    python_callable=extract_online_sales,
    provide_context=True,
    dag=dag,
)

extract_instore_sales_task = PythonOperator(
    task_id="extract_instore_sales",
    python_callable=extract_instore_sales,
    provide_context=True,
    dag=dag,
)

transform_sales_task = PythonOperator(
    task_id="transform_sales_data",
    python_callable=transform_sales_data,
    provide_context=True,
    dag=dag,
)

load_sales_task = PythonOperator(
    task_id="load_sales_to_mysql",
    python_callable=load_sales_to_mysql,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
extract_online_sales_task >> transform_sales_task
extract_instore_sales_task >> transform_sales_task
transform_sales_task >> load_sales_task
