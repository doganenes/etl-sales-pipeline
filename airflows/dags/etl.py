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
    schedule="@daily",  # Executes daily
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
    df = hook.get_pandas_df(query)
    df.to_csv(
        "online_sales_data.csv", index=False
    )  
    return "online_sales_data.csv"


# Extract data from CSV
def extract_csv_sales():
    df = pd.read_csv("in_store_sales.csv")
    df.to_csv("in_store_sales_data.csv", index=False)
    return "in_store_sales_data.csv"


extract_postgresql = PythonOperator(
    task_id="extract_postgresql", python_callable=extract_postgresql_sales, dag=dag
)

extract_csv = PythonOperator(
    task_id="extract_csv", python_callable=extract_csv_sales, dag=dag
)


def transform_sales_data():
    online_df = pd.read_csv("online_sales_data.csv")
    in_store_df = pd.read_csv("in_store_sales_data.csv")

    combined_df = pd.concat(
        [
            online_df[["product_id", "quantity", "sale_amount"]],
            in_store_df[["product_id", "quantity", "sale_amount"]],
        ]
    )

    combined_df = combined_df.dropna()

    aggregated_df = (
        combined_df.groupby("product_id")
        .agg(
            total_quantity=("quantity", "sum"), total_sale_amount=("sale_amount", "sum")
        )
        .reset_index()
    )

    aggregated_df.to_csv("/tmp/aggregated_sales_data.csv", index=False)
    return "/tmp/aggregated_sales_data.csv"


transform_data = PythonOperator(
    task_id="transform_data", python_callable=transform_sales_data, dag=dag
)


def load_data_to_mysql():
    mysql_hook = MySqlHook(mysql_conn_id="mysql_conn")

    df = pd.read_csv("aggregated_sales_data.csv")

    for _, row in df.iterrows():
        query = """
        INSERT INTO sales_aggregated (product_id, total_quantity, total_sale_amount)
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


load_to_mysql = PythonOperator(
    task_id="load_to_mysql", python_callable=load_data_to_mysql, dag=dag
)

extract_postgresql >> extract_csv >> transform_data >> load_to_mysql
