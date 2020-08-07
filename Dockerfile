FROM apache/airflow:1.10.11-python3.7

RUN pip install --upgrade pip --user &&\
    pip install --no-cache-dir --user psycopg2-binary==2.8.5

ENV AIRFLOW_CONN_OPEN_WEATHER_MAP "https://api.openweathermap.org"

COPY dags/ dags/
COPY airflow.cfg airflow.cfg

COPY --chown=airflow:root wait-for-it.sh wait-for-it.sh
RUN chmod +x wait-for-it.sh

ENTRYPOINT []
CMD ["sh", "-c", "airflow upgradedb \
     && airflow connections --add --conn_id 'twilio' --conn_uri $(cat $TWILIO_ENDPOINT_FILE) \
     && airflow scheduler"]