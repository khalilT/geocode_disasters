### (c) Khalil Teber 2025 ###
### Code file for PAPER "Geocoding climate-related disaster events"

### In this script, we overlay the regions corresponding to each EM-DAT event within each country, to have the total reported area of the event
### we aggregate location data at the national level by dissolving administrative regions (ADM1 and ADM2) based on disaster event IDs (DisNo. from EM-DAT)

import numpy as np
import geopandas as gpd
import pandas as pd
import re
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from utils.paths import get_path  # Import the get_path function from paths.py
import utils.constants as constants
import utils.functions as functions

print("1 Load geolocated climate events data")
# 1 Load Geolocated Climate Events Data
###############################

climate_event_locations_90_23 = gpd.read_file(
    get_path("geocoded_locations_path"), driver="GPKG"
)

climate_event_locations_90_23 = climate_event_locations_90_23.set_index("DisNo.")
# Duplicate quality flags for each location
# This is done to ensure that the quality flags are preserved for each location
# and for the national overlay process
climate_event_locations_90_23["regional_flags"] = climate_event_locations_90_23[
    "geocoding_q"
]

print("2 Aggregate locations by event")
# 2 Aggregate Locations by event and save data
###############################

climate_event_locations_90_23_national_overlay = climate_event_locations_90_23.dissolve(
    by=["DisNo."],
    aggfunc={
        "ADM1_NAME": lambda x: " - ".join(np.unique((x).astype(str))),
        "ADM1_CODE": lambda x: " - ".join(np.unique((x).astype(str))),
        "ADM2_NAME": lambda x: " - ".join(np.unique((x).astype(str))),
        "ADM2_CODE": lambda x: " - ".join(np.unique((x).astype(str))),
        "Location": lambda x: " - ".join(np.unique((x).astype(str))),
        "geoNames": lambda x: " - ".join(np.unique((x).astype(str))),
        "ISO": lambda x: np.unique(x)[0],
        "admin_level": lambda x: " - ".join(np.unique((x).astype(str))),
        "geocoding_q": lambda x: np.max((x).astype(str)),
        "regional_flags": lambda x: " - ".join(np.unique(x.astype(str))),
    },
)

print("3 write data")
# 3 Write data
###############################
# write identified locations
climate_event_locations_90_23_national_overlay.to_file(
    get_path("intermediate_data_path")
    + "geolocated_climate_events_1990-2023_national_clean.gpkg",
    driver="GPKG",
)

print("National overlay of geolocated climate events saved to file")
