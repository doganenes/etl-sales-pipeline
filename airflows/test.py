import psycopg2

DB_NAME = "sales"
DB_USER = "airflow"
DB_PASSWORD = "airflow"
DB_HOST = "localhost"  
DB_PORT = "5432"

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        client_encoding="UTF8",
    )
    print("Bağlantı başarılı!")

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales_aggreated;")

    rows = cursor.fetchall()
    for row in rows:
        print(row)

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Hata oluştu: {e}")
