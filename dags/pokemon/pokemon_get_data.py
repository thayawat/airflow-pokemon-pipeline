import requests
import pandas as pd
from pokemon.config import DATA_FOLDER


def main_get_pokemon_name():
    """
    Get Pokemon name and save as csv
    """
    # Get pokemon quantity from API and save in variable
    api_response = requests.get("https://pokeapi.co/api/v2/pokemon")
    api_data = api_response.json()
    pokemon_quantity = api_data.get("count")

    # Send request to API
    result_df = pd.read_json(
        f"https://pokeapi.co/api/v2/pokemon?limit={pokemon_quantity}")
    # Get result
    result_list = result_df["results"].values.tolist()
    # Set formation
    pokemon_name_dict = list_dict_to_dict_list(result_list)
    # Create dataframe and filter only name
    pokemon_name_df = pd.DataFrame(pokemon_name_dict).filter(["name"])
    # Export to csv
    pokemon_name_df.to_csv(f"{DATA_FOLDER}pokemon_name.csv", index=False)


def main_get_pokemon_stats(segment_num, segment_total):
    """
    Get stats and save as csv
    """
    # Read Pokemon name from csv
    pokemon_name_df = pd.read_csv(f"{DATA_FOLDER}pokemon_name.csv")
    pokemon_name_len = len(pokemon_name_df)
    for i in range(segment_total+1):
        if i == segment_num:
            start = int((segment_num - 1) / segment_total * pokemon_name_len)
            stop = int(segment_num / segment_total * pokemon_name_len)
            pokemon_name_df_seg = pokemon_name_df[start:stop]
            break
    result = pokemon_name_df_seg["name"].apply(get_pokemon_data)

    pokemon_data_seg = pd.DataFrame(list_dict_to_dict_list(result))

    pokemon_data_seg.to_csv(
        f"{DATA_FOLDER}pokemon_data_{segment_num}.csv", index=False)


def main_concat_pokemon_stats(start_num, stop_num):
    frames = []
    for segment_num in range(start_num, stop_num+1):
        frames.append(pd.read_csv(
            f"{DATA_FOLDER}pokemon_data_{segment_num}.csv"))
    pokemon_data = pd.concat(frames)
    pokemon_data.to_csv(
        f"{DATA_FOLDER}pokemon_data.csv", index=False)


def get_pokemon_data(pokemon_name):
    pokemon_data_json = requests.get(
        f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}").json()
    pokemon_data = {}
    pokemon_data["id"] = pokemon_data_json.get("id")
    pokemon_data["name"] = pokemon_name
    pokemon_data["base_name"] = pokemon_data_json.get(
        "species").get("name")
    pokemon_data["height_meter"] = int(pokemon_data_json.get("height"))/10
    pokemon_data["weight_kg"] = int(pokemon_data_json.get("weight"))/10

    # Get stats base HP, ATK, DEF, SP_ATK, SP_DEF, Speed
    stats = pokemon_data_json.get("stats")
    for item in stats:
        base_stat = item.get("base_stat")
        stats_name = item.get("stat").get("name").replace("-", "_")
        pokemon_data[stats_name] = base_stat

    types = pokemon_data_json.get("types")
    pokemon_data["type_1"] = types[0].get("type").get("name")
    pokemon_data["type_2"] = types[1].get(
        "type").get("name") if len(types) == 2 else ""

    pokemon_species_json = requests.get(
        f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_data['base_name']}").json()
    pokemon_data["is_legendary"] = pokemon_species_json.get("is_legendary")
    pokemon_data["is_mythical"] = pokemon_species_json.get("is_mythical")

    return pokemon_data


def main_get_damage_relations():
    response_json = requests.get("https://pokeapi.co/api/v2/type").json()
    type_list = [i["name"] for i in response_json.get(
        "results") if not i["name"] in ["unknown", "shadow"]]
    damage_relations_list = []
    for type_name in type_list:
        response_json = requests.get(
            f"https://pokeapi.co/api/v2/type/{type_name}").json()
        damage_relations = response_json.get("damage_relations")
        damage_relations_ratio = {}
        damage_relations_ratio["defend_type"] = type_name
        damage_relations_ratio.update({key: 1 for key in type_list})
        for group, item in damage_relations.items():
            for value in item:
                if group == "double_damage_from":
                    damage_relations_ratio[value.get("name")] = 2
                elif group == "half_damage_from":
                    damage_relations_ratio[value.get("name")] = 0.5
                elif group == "no_damage_from":
                    damage_relations_ratio[value.get("name")] = 0
        damage_relations_list.append(damage_relations_ratio)
    damage_relations_table_df = pd.DataFrame(list_dict_to_dict_list(
        damage_relations_list))
    damage_relations_table_df.to_csv(
        f"{DATA_FOLDER}damage_relations_table.csv", index=False)


def list_dict_to_dict_list(list_dict):
    """
    Description:
    ------------
    Convert list of dict to dict of list.

    Example:
    --------
    [{A:1, B:4}, {A:2, B:5}, {A:3, B:6}] -> {A:[1, 2, 3], B:[4, 5, 6]}
    """
    result_dict = {}
    for item in list_dict:
        for key, value in item.items():
            if result_dict.get(key):
                result_dict[key].append(value)
            else:
                result_dict[key] = [value]
    return result_dict
