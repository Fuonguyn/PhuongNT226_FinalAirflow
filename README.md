# PhuongNT226_FinalAirflow
## ETL Pipeline with local storage and PostgreSQL (Render + Dbeaver)
This project implements a local ETL pipeline that loads JSON log and song data into a PostgreSQL database hosted on Render. DBeaver is used for inspecting and verifying the loaded data.
### 1. Tech Stack
* Python for ETL scripts
* PostgreSQL (hosted on Render)
* DBeaver for database GUI
* Local JSON files as input
* Orchestrate by Airflow

### 2. Create a database Postgres by Render, then connect with DBeaver to verify data.
<img width="1161" height="623" alt="image" src="https://github.com/user-attachments/assets/e2618861-3a23-4136-be66-cdf5d81f9e84" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/57584a06-93ac-4124-831c-3420ab5c0a95" />

### 3. Environment Setup (Ubuntu via WSL)
* Install Python 3.11+ (Ubuntu/WSL)
`sudo apt update`
`sudo apt install python3.11 python3.11-venv python3.11-dev`
* Create virtual environment
* `python3.11 -m venv airflow_venv` 
`source airflow_venv/bin/activate`
* Install Apache Airflow with constraints
    `AIRFLOW_VERSION=2.8.1`
    
    `PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1,2)"`
    
    `CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"`
    
    `pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"`
    
    `pip install psycopg2-binary`
* Initialize Airflow
` airflow db init `
* Create user
`airflow users create `
 ` --username admin `
 ` --firstname Admin `
`  --lastname User `
`  --role Admin `
` --email phuongnt7803@gmail.com`
* Run Airflow
`airflow scheduler`
`airflow webserver --port 8080`

### 4. Run the ETL
* Place raw JSON files in `data/`
* Edit PostgreSQL connection in Airflow with info from Render
* Trigger DAG via Airflow UI (etl_local_postgres_dag.py)
* Use DBeaver to connect to Render DB and inspect loaded tables


