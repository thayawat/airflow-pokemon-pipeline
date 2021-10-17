# airflow-pokemon-pipeline

Run airflow with Docker

```sh
docker-compose -f .\docker-compose.yaml up -d
```

Run airflow with with scale airflow-worker

```sh
docker-compose -f .\docker-compose.yaml up --scale airflow-worker=3 -d
```

Remove airflow from docker process 

```sh
docker-compose -f .\docker-compose.yaml up down
```

Airflow URL

```
http://localhost:8080/
```

Flower URL

```
http://localhost:5555/
```
