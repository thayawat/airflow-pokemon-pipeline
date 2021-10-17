from airflow import DAG
from airflow.utils import timezone
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator
from pokemon.pokemon_get_data import main_get_pokemon_name, main_get_pokemon_stats, main_concat_pokemon_stats, main_get_damage_relations
from pokemon.pokemon_combine_data import main_combine_data
from pokemon.config import DATA_FOLDER
import pandas as pd

default_args = {
    "owner": "Thayawat W.",
}


with DAG(
    "pokemon_pipeline",
    schedule_interval="@daily",
    default_args=default_args,
    start_date=timezone.datetime(2021, 10, 1),
    catchup=False,
) as dag:

    start = DummyOperator(task_id="start")

    create_data_folder = BashOperator(
        task_id="create_data_folder",
        bash_command=f"mkdir -p {DATA_FOLDER}"
    )

    get_pokemon_name = PythonOperator(
        task_id="get_pokemon_name",
        python_callable=main_get_pokemon_name,
    )

    segment_total = 20
    get_pokemon_stat = []
    for segment_num in range(1, segment_total+1):
        get_pokemon_stat.append(PythonOperator(
            task_id=f"get_pokemon_stat_{segment_num}",
            python_callable=main_get_pokemon_stats,
            op_kwargs={"segment_num": segment_num,
                       "segment_total": segment_total, },
        )
        )

    concat_pokemon_stats = PythonOperator(
        task_id="concat_pokemon_stats",
        python_callable=main_concat_pokemon_stats,
        op_kwargs={"start_num": 1,
                   "stop_num": segment_total, },
    )

    get_damage_relation = PythonOperator(
        task_id="get_damage_relations",
        python_callable=main_get_damage_relations,
    )

    combine_data = PythonOperator(
        task_id="combine_data",
        python_callable=main_combine_data,
    )

    create_pokemon_stat_table = MySqlOperator(
        task_id="create_pokemon_stat_table",
        mysql_conn_id="mysql_conn",
        sql=f"""
            CREATE TABLE IF NOT EXISTS pokemon_stats (
                id                  INT PRIMARY KEY,
                name                VARCHAR(64) NOT NULL,
                base_name           VARCHAR(64) NOT NULL,
                height_meter        DOUBLE(6, 2),
                weight_kg           DOUBLE(6, 2),
                hp                  INT,
                attack              INT,
                defense             INT,
                special_attack      INT,
                special_defense     INT,
                speed               INT,
                type_1              VARCHAR(64),
                type_2              VARCHAR(64),
                is_legendary        BOOLEAN,
                is_mythical         BOOLEAN,
                normal              DOUBLE(6, 2),
                fighting            DOUBLE(6, 2),
                flying              DOUBLE(6, 2),
                poison              DOUBLE(6, 2),
                ground              DOUBLE(6, 2),
                rock                DOUBLE(6, 2),
                bug                 DOUBLE(6, 2),
                ghost               DOUBLE(6, 2),
                steel               DOUBLE(6, 2),
                fire                DOUBLE(6, 2),
                water               DOUBLE(6, 2),
                grass               DOUBLE(6, 2),
                electric            DOUBLE(6, 2),
                psychic             DOUBLE(6, 2),
                ice                 DOUBLE(6, 2),
                dragon              DOUBLE(6, 2),
                dark                DOUBLE(6, 2),
                fairy               DOUBLE(6, 2)
            );
        """
    )

    with open(f"{DATA_FOLDER}pokemon_data_combine.csv") as file:
        txt = file.read()
        txt = txt.replace(",", "', '")
        txt = txt.strip()
        txt_sp = txt.split("\n")
        txt_sp = txt_sp[1:]
        sql = ""
        for row in txt_sp:
            sql += f"('{row}'),"
        sql = sql[:-1]

    update_pokemon_stats_db = MySqlOperator(
        task_id="update_pokemon_stats_db",
        mysql_conn_id="mysql_conn",
        sql=f"""
            INSERT IGNORE INTO pokemon_stats (id, name, base_name, height_meter, weight_kg, hp, attack, defense, special_attack, special_defense, speed, type_1, type_2, is_legendary, is_mythical, normal, fighting, flying, poison, ground, rock, bug, ghost, steel, fire, water, grass, electric, psychic, ice, dragon, dark, fairy)
            VALUES
            {sql}
            ;
        """
    )

    end = DummyOperator(task_id="end")

    start >> create_data_folder >> get_pokemon_name >> get_pokemon_stat >> concat_pokemon_stats >> get_damage_relation >> combine_data >> create_pokemon_stat_table >> update_pokemon_stats_db >> end
