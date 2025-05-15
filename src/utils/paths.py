import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATA_PATHS = {
    # emdat database
    "emdat_path": "/net/projects/xaida/raw_data/emdat_data/public_emdat_1990_2023.xlsx",
    # GAUL geolocation maps
    "gaul1_path": "/net/projects/xaida/raw_data/gaul_maps/gaul_admin1_clean.gpkg",
    "gaul2_path": "/net/projects/xaida/raw_data/gaul_maps/gaul_admin2_clean.gpkg",
    # Locations to identify with GeoNames
    "df_locations_path": "/net/projects/xaida/database_paper/intermediate_data/event_locations_to_geolocate.csv",
    # manually corrected locations
    "df_locations_corrected_path": "/net/projects/xaida/database_paper/intermediate_data/corrected_locations.csv",
    # folder containing identified locations
    "identified_locations_path": "/net/projects/xaida/database_paper/intermediate_data/identified_locations/",
    # folder containing manually corrected location names
    "corrected_locations_path": "/net/projects/xaida/database_paper/intermediate_data/corrected_locations/",
    # Geonames locations cleaned
    "geonames_locations_clean_path": "/net/projects/xaida/database_paper/intermediate_data/name_locations_identified_clean.csv",
    # geocoded locations no overlay
    "geocoded_locations_path": "/net/projects/xaida/database_paper/output_data/disaster_subnational_90_23.gpkg",
    # geocodded locations national overlay
    "geocoded_national_path": "/net/projects/xaida/database_paper/output_data/disaster_national_90_23.gpkg",
    # GDIS database
    "gdis_data_path": "/net/scratch/kteber/reproduce_studies/GDIS_paper_data/pend-gdis-1960-2018-disasterlocations.gpkg",
    # GDIS simplified
    "gdis_simplified_path": "/net/projects/xaida/database_paper/intermediate_data/simplified_gdis.gpkg",
    # Path to save intermediate data
    "intermediate_data_path": "/net/projects/xaida/database_paper/intermediate_data/",
    # Path to save clean data
    "clean_data_path": "/net/projects/xaida/database_paper/output_data/",
}


def get_path(name):
    """
    Retrieve the path for a given dataset name.
    Raises KeyError if the name is not found.
    """
    if name in DATA_PATHS:
        return DATA_PATHS[name]
    raise KeyError(f"No path found for dataset '{name}'")
