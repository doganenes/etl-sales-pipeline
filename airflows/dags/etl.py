from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mysql.hooks.mysql import MySqlHook
from datetime import datetime
import pandas as pd

# Define the DAG
dag = DAG(
    "etl_sales_pipeline",
    description="ETL pipeline for sales data from PostgreSQL and CSV",
    schedule_interval="@daily",  # Executes daily
    start_date=datetime(2025, 5, 5),
    catchup=False,
)


# Extract data from PostgreSQL
def extract_postgresql_sales():
    hook = PostgresHook(postgres_conn_id="postgres_conn")
    query = """
        SELECT product_id, quantity, sale_amount
        FROM online_sales
        WHERE sale_date >= current_date - interval '1 day';
    """
    # Run query to fetch the sales data
    df = hook.get_pandas_df(query)
    df.to_csv(
        "/tmp/online_sales_data.csv", index=False
    )  # Store the result to CSV for later use
    return "/tmp/online_sales_data.csv"


# Extract data from CSV
def extract_csv_sales():
    # Read the CSV file containing in-store sales
    df = pd.read_csv("/path/to/in_store_sales.csv")
    df.to_csv("/tmp/in_store_sales_data.csv", index=False)
    return "/tmp/in_store_sales_data.csv"


# Extract tasks
extract_postgresql = PythonOperator(
    task_id="extract_postgresql", python_callable=extract_postgresql_sales, dag=dag
)

extract_csv = PythonOperator(
    task_id="extract_csv", python_callable=extract_csv_sales, dag=dag
)


# Transform data
def transform_sales_data():
    # Load data from both files
    online_df = pd.read_csv("/tmp/online_sales_data.csv")
    in_store_df = pd.read_csv("/tmp/in_store_sales_data.csv")

    # Combine both datasets
    combined_df = pd.concat(
        [
            online_df[["product_id", "quantity", "sale_amount"]],
            in_store_df[["product_id", "quantity", "sale_amount"]],
        ]
    )

    # Cleanse the data (remove nulls)
    combined_df = combined_df.dropna()

    # Aggregate data by product_id
    aggregated_df = (
        combined_df.groupby("product_id")
        .agg(
            total_quantity=("quantity", "sum"), total_sale_amount=("sale_amount", "sum")
        )
        .reset_index()
    )

    # Store transformed data to CSV
    aggregated_df.to_csv("/tmp/aggregated_sales_data.csv", index=False)
    return "/tmp/aggregated_sales_data.csv"


# Transformation task
transform_data = PythonOperator(
    task_id="transform_data", python_callable=transform_sales_data, dag=dag
)


# Load data into MySQL
def load_data_to_mysql():
    # Connect to MySQL
    mysql_hook = MySqlHook(mysql_conn_id="mysql_conn")

    # Load the transformed data (from CSV)
    df = pd.read_csv("/tmp/aggregated_sales_data.csv")

    # Prepare the insert query
    for _, row in df.iterrows():
        query = """
        INSERT INTO product_sales_aggregated (product_id, total_quantity, total_sale_amount)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE total_quantity = VALUES(total_quantity), total_sale_amount = VALUES(total_sale_amount);
        """
        mysql_hook.run(
            query,
            parameters=(
                row["product_id"],
                row["total_quantity"],
                row["total_sale_amount"],
            ),
        )


# Loading task
load_to_mysql = PythonOperator(
    task_id="load_to_mysql", python_callable=load_data_to_mysql, dag=dag
)

# Set task dependencies
extract_postgresql >> extract_csv >> transform_data >> load_to_mysql
