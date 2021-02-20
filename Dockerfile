FROM apache/airflow:1.10.11-python3.7

ENV AIRFLOW_CONN_OPEN_WEATHER_MAP "https://api.openweathermap.org"

RUN pip install --upgrade pip --user &&\
    pip install --no-cache-dir --user psycopg2-binary==2.8.5 supervisor==4.2.1

COPY --chown=airflow airflow.cfg supervisord.conf dependencies/wait-for-it.sh ./
COPY dags/ dags/

ENTRYPOINT []
CMD ["supervisord", "-c", "supervisord.conf"]
