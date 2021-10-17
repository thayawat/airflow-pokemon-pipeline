import pandas as pd
from pokemon.config import DATA_FOLDER


def get_dataframe_value(data, index, column, error_value=1):
    """
    Read value in dataframe with specific index name and column name.
    If error will return 1 as default.
    """
    try:
        return float(data.loc[index, column])
    except:
        return error_value


def main_combine_data():
    """
    Combine pokemon_data and damage_relations_table and calculate pokemon damage relations for pokemon that have multi-type.
    """
    # Read pokemon_data
    pokemon_data = pd.read_csv(f"{DATA_FOLDER}pokemon_data.csv")

    # Read damage relations table and set first column as index
    damage_relations_table_df = pd.read_csv(
        f"{DATA_FOLDER}damage_relations_table.csv", index_col=[0])

    # Join pokemon_data type_1 with damage reletion table
    pokemon_data_combine = pokemon_data.merge(
        damage_relations_table_df, left_on="type_1", right_on="defend_type")

    # Multiply type_1 damage relation value with type_2 damage relation value
    for i in damage_relations_table_df.columns:
        pokemon_data_combine[i] = pokemon_data_combine.apply(
            lambda x: x[i] * get_dataframe_value(damage_relations_table_df, x.type_2, i), axis=1)

    # Save file as csv to data folder
    pokemon_data_combine = pokemon_data_combine.sort_values(by=['id'])
    pokemon_data_combine.to_csv(
        f"{DATA_FOLDER}pokemon_data_combine.csv", index=False)
