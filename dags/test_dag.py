import datetime as dt
import os

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.http_operator import SimpleHttpOperator


default_args = {
    'owner': 'me',
    'start_date': dt.datetime(2020, 7, 20, 0, 00, 00),
    'concurrency': 1,
    'retries': 0
}


def hello_world():
    print("Hello world")

def parse_response(**context):
    response = context['task_instance'].xcom_pull(task_ids='get_weather')
    return


with DAG('hello_world_dag',
         catchup=False,
         default_args=default_args,
         schedule_interval='@hourly',
         ) as dag:

    get_weather = SimpleHttpOperator(
        task_id='get_weather',
        method='POST',
        http_conn_id='weather',
        endpoint='data/2.5/onecall?lat=52.066669&lon=4.3&exclude=current,daily',
        headers={"x-api-key": os.environ["OPEN_WEATHER_API_KEY"]},
        xcom_push=True,
        response_check=lambda response: response.ok,
        dag=dag
    )

    process_response = PythonOperator(task_id='process_response',
                                python_callable=parse_response,
                                provide_context=True)

get_weather >> process_response

