# ETL Pipeline with local storage and PostgreSQL (Render + Dbeaver)
> This project implements a local ETL pipeline that loads JSON log and song data into a PostgreSQL database hosted on Render. DBeaver is used for inspecting and verifying the loaded data.

## Workflow & folder structure:
1. Load all unique JSON files from `data/` into pre-defined dim & fact tables from `PostgresSQL` 
2. Check quality for loaded files (emtpy or not)

    <img width="800" height="300" alt="image" src="https://github.com/user-attachments/assets/8a81c87e-cb49-4551-87bd-8df5b013fb96" />
    <img width="800" height="200" alt="image" src="https://github.com/user-attachments/assets/e3517070-b5c1-4544-916f-f5fa07c584de" />
    <img width="800" height="200" alt="image" src="https://github.com/user-attachments/assets/f159e2f4-afeb-4a73-8d56-e944ad37e1d1" />

### 1. Tech Stack
* Python for ETL scripts
* PostgreSQL (hosted on **Render** platform - free web services and datastores)
* DBeaver for database GUI
* Local JSON files as input
* Orchestrate by Airflow

### 2. Create a database Postgres by Render, then connect with DBeaver to verify data.
<img width="800" height="500" alt="image" src="https://github.com/user-attachments/assets/e2618861-3a23-4136-be66-cdf5d81f9e84" />
<img width="800" height="500" alt="image" src="https://github.com/user-attachments/assets/57584a06-93ac-4124-831c-3420ab5c0a95" />

### 3. Environment Setup (Ubuntu via WSL)
* Install Python 3.11+ (Ubuntu/WSL)
`sudo apt update`
`sudo apt install python3.12 python3.12-venv python3.12-dev`
* Create virtual environment
  `python3.12 -m venv airflow_venv`
  `source airflow_venv/bin/activate`
* Install Apache Airflow with constraints
  ```
    AIRFLOW_VERSION=2.9.1
    PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1,2)"
    CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
    pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
    pip install psycopg2-binary
  ```
> Check version:
  <img width="400" height="100" alt="image" src="https://github.com/user-attachments/assets/80329f09-bbcc-4333-a68a-f7d3d50232f8" />

* Initialize Airflow
` airflow db init `
* Create user
`airflow users create `
 ` --username admin `
 ` --firstname Admin `
`  --lastname User `
`  --role Admin `
`  --password admin `
` --email phuongnt7803@gmail.com`

### 4. Prepare for running the ETL
* Place raw JSON files in `data/`, ETL.py and sql_queries in `dags/`
* Edit PostgreSQL connection in Airflow with info from Render
* Use DBeaver to connect to Render DB and inspect loaded tables
    #### Needed libraries:
* from datetime import datetime, timedelta
* from airflow import DAG
* import os
* import glob
* import json
* from airflow.operators.python_operator import PythonOperator
* from airflow.operators.empty import EmptyOperator
* from airflow.providers.postgres.hooks.postgres import PostgresHook
* import sql_queries

### 5. Run ETL & Check logs
1. Run Airflow
`airflow scheduler`
`airflow webserver --port 8080`
2. Trigger DAG via Airflow UI (etl_local_postgres_dag.py)

