import datetime as dt
import os

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.http_operator import SimpleHttpOperator

from helpers.helpers_weather_bot import parse_weather_response


default_args = {
    "owner": "me",
    "start_date": dt.datetime(2020, 7, 20, 0, 00, 00),
    "concurrency": 1,
    "retries": 0,
}


with DAG(
    "weather_bot", catchup=False, default_args=default_args, schedule_interval="@daily",
) as dag:

    get_weather = SimpleHttpOperator(
        task_id="get_weather",
        method="POST",
        http_conn_id="weather",
        endpoint="data/2.5/onecall?lat=52.066669&lon=4.3&exclude=current,daily",
        headers={"x-api-key": os.environ["OPEN_WEATHER_API_KEY"]},
        xcom_push=True,
        response_check=lambda response: response.ok,
        dag=dag,
    )

    parse_response = PythonOperator(
        task_id="parse_response",
        python_callable=parse_weather_response,
        provide_context=True,
        do_xcom_push=True,
    )

get_weather >> parse_response