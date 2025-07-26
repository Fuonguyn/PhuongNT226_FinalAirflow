from datetime import datetime, timedelta
from airflow import DAG
import os
import glob
import json
from airflow.operators.python_operator import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import sql_queries 

# Data path
LOCAL_DATA_PATH = os.path.expanduser("~/airflow/data")

# Execute SQL
def execute_sql(sql_statement: str, conn_id: str = "postgres_id"):
    hook = PostgresHook(postgres_conn_id = conn_id)
    result = hook.run(sql_statement)
    print(f"Executed SQL: {sql_statement[:50]}... -> Result: {result}")

#Get all JSON files
def get_all_files(filepath):
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, '*.json'))
        for f in files:
            all_files.append(os.path.abspath(f))
    return all_files

# Process avoid duplicated files
def process_input_files(data_dir, file_ext, is_valid_record, insert_fn):
    hook = PostgresHook(postgres_conn_id="postgres_id")
    conn = hook.get_conn()
    files = get_all_files(data_dir)

    print(f"Found {len(files)} files in {data_dir}")
    with conn.cursor() as cur:
        for file_path in files:
            cur.execute("SELECT 1 FROM loaded_files WHERE file_name = %s", (file_path,))
            if cur.fetchone():
                print(f"Skipped (already processed): {file_path}")
                continue

            with open(file_path, 'r') as f:
                content = f if file_ext == 'json' else f.readlines()
                for line in content:
                    data = json.loads(line) if isinstance(content, list) else json.load(f)
                    if not is_valid_record(data): continue
                    insert_fn(cur, data)
            
            cur.execute("INSERT INTO loaded_files (file_name) VALUES (%s)", (file_path,))
        conn.commit()

# Load data song into staging_songs
def stage_songs_to_postgres():
    def is_valid_song(_): return True
    def insert_song(cur, data):
        cur.execute("""
            INSERT INTO staging_songs (num_songs, artist_id, artist_latitude, artist_longitude,
                                       artist_location, artist_name, song_id, title, duration, year)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('num_songs'), data.get('artist_id'),
            data.get('artist_latitude'), data.get('artist_longitude'),
            data.get('artist_location'), data.get('artist_name'),
            data.get('song_id'), data.get('title'),
            data.get('duration'), data.get('year')
        ))

    process_input_files(os.path.join(LOCAL_DATA_PATH, 'song_data'), 'json', is_valid_song, insert_song)
    print("Finished stage_songs_to_postgres")

# Load data event into staging_events
def stage_events_to_postgres():
    def is_valid_event(data): return data.get('page') == 'NextSong'
    def insert_event(cur, data):
        cur.execute("""
            INSERT INTO staging_events (artist, auth, firstName, gender, itemInSession, lastName,
                                        length, level, location, method, page, registration,
                                        sessionId, song, status, ts, userAgent, userId)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('artist'), data.get('auth'),
            data.get('firstName'), data.get('gender'),
            data.get('itemInSession'), data.get('lastName'),
            data.get('length'), data.get('level'),
            data.get('location'), data.get('method'),
            data.get('page'), data.get('registration'),
            data.get('sessionId'), data.get('song'),
            data.get('status'), data.get('ts'),
            data.get('userAgent'), data.get('userId')
        ))

    process_input_files(os.path.join(LOCAL_DATA_PATH, 'log_data'), 'log', is_valid_event, insert_event)
    print("Finished stage_events_to_postgres")

# fact & dim tables
def load_songplays_table():
    execute_sql(sql_queries.SqlQueries.songplay_table_insert)
def load_songs_table():
    execute_sql(sql_queries.SqlQueries.song_table_insert)
def load_users_table():
    execute_sql(sql_queries.SqlQueries.user_table_insert)
def load_artists_table():
    execute_sql(sql_queries.SqlQueries.artist_table_insert)
def load_time_table():
    execute_sql(sql_queries.SqlQueries.time_table_insert)

# check quality for data
def data_quality_check():
    hook = PostgresHook(postgres_conn_id="postgres_id")
    conn = hook.get_conn()

    with conn.cursor() as cur:
        tables = ['songplays', 'users', 'songs', 'artists', 'time']
        for table in tables:
            print(f"Checking data quality for table: {table}")
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            result = cur.fetchone()
            if result is None or result[0] < 1:
                raise ValueError(f"Data quality check failed for {table}. Table is empty!")
            print(f"Table {table} passed with {result[0]} records.")
    print("Finished data quality checks.")

#defaut argurments
default_args = {
    'owner': 'phuongnt226',
    'depends_on_past': False,
    'start_date': datetime(2025, 7, 20),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'email_on_retry': False,
}

# Initialize DAG
dag = DAG(
    'etl_local_postgres_pipeline',
    default_args=default_args,
    description='ETL pipeline for TuneStream',
    schedule_interval='@hourly',
)

# Tasks
start_task = EmptyOperator(task_id='begin_execution', dag=dag)

stage_songs_task = PythonOperator(
    task_id='stage_songs',
    python_callable=stage_songs_to_postgres,
    dag=dag
)

stage_events_task = PythonOperator(
    task_id='stage_events',
    python_callable=stage_events_to_postgres,
    dag=dag
)

load_songplays_task = PythonOperator(
    task_id='load_songplays_fact_table',
    python_callable=load_songplays_table,
    dag=dag
)

load_songs_task = PythonOperator(
    task_id='load_song_dim_table',
    python_callable=load_songs_table,
    dag=dag
)

load_users_task = PythonOperator(
    task_id='load_user_dim_table',
    python_callable=load_users_table,
    dag=dag
)

load_artists_task = PythonOperator(
    task_id='load_artist_dim_table',
    python_callable=load_artists_table,
    dag=dag
)

load_time_task = PythonOperator(
    task_id='load_time_dim_table',
    python_callable=load_time_table,
    dag=dag
)

check_quality_task = PythonOperator(
    task_id='run_data_quality_check',
    python_callable=data_quality_check,
    dag=dag
)

end_task = EmptyOperator(task_id='end_execution', dag=dag)

# Dependencies
start_task >> [stage_songs_task, stage_events_task]
[stage_songs_task, stage_events_task] >> load_songplays_task
load_songplays_task >> [load_songs_task, load_users_task, load_artists_task, load_time_task]
[load_songs_task, load_users_task, load_artists_task, load_time_task] >> check_quality_task
check_quality_task >> end_task
