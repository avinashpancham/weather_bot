import datetime as dt

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.http_operator import SimpleHttpOperator

from helpers.general import get_secret_from_file
from helpers.helpers_weather_bot import parse_weather_response


default_args = {
    "owner": "me",
    "start_date": dt.datetime(2020, 7, 20, 0, 00, 00),
    "concurrency": 1,
    "retries": 0,
}

with DAG(
    "weather_bot",
    catchup=False,
    default_args=default_args,
    schedule_interval="0 7 * * 1-5",
) as dag:

    get_weather = SimpleHttpOperator(
        task_id="get_weather",
        method="POST",
        http_conn_id="weather",
        endpoint="data/2.5/onecall?lat=52.066669&lon=4.3&exclude=current,daily",
        headers={"x-api-key": get_secret_from_file("OPEN_WEATHER_API_KEY_FILE")},
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

    send_sms = SimpleHttpOperator(
        task_id="send_sms",
        method="POST",
        http_conn_id="sms",
        endpoint=f"2010-04-01/Accounts/{get_secret_from_file('ACCOUNT_SID_FILE')}/Messages.json",
        data={
            "To": get_secret_from_file("TO_PHONE_NUMBER_FILE"),
            "From": get_secret_from_file("FROM_PHONE_NUMBER_FILE"),
            "Body": "{{ task_instance.xcom_pull(task_ids='parse_response')}}",
        },
        response_check=lambda response: response.ok,
        dag=dag,
    )

get_weather >> parse_response >> send_sms
