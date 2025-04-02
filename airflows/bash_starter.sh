#!/bin/bash

echo "Airflow veritabanı başlatılıyor..."
airflow db init

# 2. Airflow web server'ını başlatıyoruz
echo "Airflow Web UI başlatılıyor..."
airflow webserver --port 8080 &  # --port 8080, web UI'yi 8080 portunda başlatır.

# 3. Airflow zamanlayıcısını başlatıyoruz (scheduler)
echo "Airflow zamanlayıcısı başlatılıyor..."
airflow scheduler &

wait