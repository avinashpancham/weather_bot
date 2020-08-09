import datetime as dt

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.http_operator import SimpleHttpOperator

from helpers.general import get_secret_from_file
from helpers.helpers_weather_bot import parse_weather_response, get_lat_lon

default_args = {
    "owner": "me",
    "start_date": dt.datetime(2020, 7, 20, 0, 00, 00),
    "concurrency": 1,
    "retries": 0,
}

location = get_lat_lon()

with DAG(
    "weather_bot",
    catchup=False,
    default_args=default_args,
    schedule_interval="0 7 * * 1-5",
) as dag:

    get_weather = SimpleHttpOperator(
        task_id="get_weather",
        method="POST",
        http_conn_id="open_weather_map",
        endpoint=f"data/2.5/onecall?lat={location.lat}&lon={location.lng}&exclude=current,daily&units=metric",
        headers={"x-api-key": get_secret_from_file("OPEN_WEATHER_MAP_API_KEY_FILE")},
        xcom_push=True,
        response_check=lambda response: response.ok,
        dag=dag,
    )

    parse_response = PythonOperator(
        task_id="parse_response",
        python_callable=parse_weather_response,
        op_kwargs={'city': location.city},
        provide_context=True,
        do_xcom_push=True,
    )

    send_sms = SimpleHttpOperator(
        task_id="send_sms",
        method="POST",
        http_conn_id="twilio",
        endpoint=f"2010-04-01/Accounts/{get_secret_from_file('TWILIO_ACCOUNT_SID_FILE')}/Messages.json",
        data={
            "To": get_secret_from_file("PERSONAL_PHONE_NUMBER_FILE"),
            "From": get_secret_from_file("TWILIO_PHONE_NUMBER_FILE"),
            "Body": "{{ task_instance.xcom_pull(task_ids='parse_response')}}",
        },
        response_check=lambda response: response.ok,
        dag=dag,
    )

get_weather >> parse_response >> send_sms
