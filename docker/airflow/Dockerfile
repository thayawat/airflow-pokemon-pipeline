FROM ${AIRFLOW_IMAGE_NAME:-apache/airflow:2.2.0}

COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /requirements.txt

USER airflow