# airflow-pokemon-pipeline

Run airflow with Docker

```sh
docker-compose -f .\docker-compose.yaml up -d
```

Run airflow and set airflow-worker quantity

```sh
docker-compose -f .\docker-compose.yaml up --scale airflow-worker=3 -d
```

Remove airflow from docker process 

```sh
docker-compose -f .\docker-compose.yaml down
```

Airflow URL

```
http://localhost:8080/
```

Flower URL

```
http://localhost:5555/
```
