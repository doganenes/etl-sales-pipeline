#!/bin/bash

echo "Airflow veritabanı başlatılıyor..."
airflow db init

echo "Airflow Web UI başlatılıyor..."
airflow webserver --port 8080 &

echo "Airflow zamanlayıcısı başlatılıyor..."
airflow scheduler &

wait
