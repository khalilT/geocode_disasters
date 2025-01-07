import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATA_PATHS = {
    #emdat database
    "emdat_path":"/net/projects/xaida/raw_data/emdat_data/public_emdat_1990_2023.xlsx",
    #GAUL geolocation maps
    "gaul1_path" : "/net/projects/xaida/raw_data/gaul_maps/gaul_admin1_clean.gpkg",
    "gaul2_path" : "/net/projects/xaida/raw_data/gaul_maps/gaul_admin2_clean.gpkg",
    #Geonames identified locations
    "df_locations_path" : "../data/intermediate_data/event_locations_to_geolocate.csv",
    "df_locations_corrected_path" : "data/intermediate_data/corrected_locations/corrected_locations.csv",
    #Geonames locations cleaned
    "geonames_locations_clean_path" : "../data/intermediate_data/name_locations_identified_clean.csv",
    #Path to save intermediate data
    "intermediate_data_path":"/net/projects/xaida/database_paper/intermediate_data/",
}

def get_path(name):
    """
    Retrieve the path for a given dataset name.
    Raises KeyError if the name is not found.
    """
    if name in DATA_PATHS:
        return DATA_PATHS[name]
    raise KeyError(f"No path found for dataset '{name}'")
