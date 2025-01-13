### (c) Khalil Teber 2025 ###
### Code file for PAPER "Geocoding climate-related disaster events"

### In this script, we manually filter events by available impact information and geocoding accuracy.

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

#1 Load Geolocated Climate Events Data
###############################
disasters_90_23 = gpd.read_file(get_path("geocoded_national_path"), driver="GPKG")
disaster_locations_90_23 = gpd.read_file(get_path("geocoded_locations_path"), driver="GPKG")
emdat = pd.read_excel(get_path("emdat_path"))

#select only geocoded event information
event_indices = disasters_90_23["DisNo."]
geocoded_emdat = emdat.set_index("DisNo.").loc[event_indices]

#2 Select only events with impact information
###############################

### drop events with no available impact records
columns_to_check = ['Total Deaths', 'Total Affected', 'Total Damage (\'000 US$)']
geocoded_emdat = geocoded_emdat.dropna(how='all', subset=columns_to_check)
selected_events = list(geocoded_emdat.index)

### reorder columns, calculate area in Km2
disasters_90_23['area_km2'] = np.round(disasters_90_23.to_crs(6933).area / 1e6,2)

#3 Manual corrections
################################

disasters_90_23 = disasters_90_23.set_index("DisNo.")
#keep only events with available impact information
disasters_90_23 = disasters_90_23.loc[selected_events]
#drop inaccurately geocoded events
disasters_90_23 = disasters_90_23.drop(["1993-0585-IRN", "1999-0298-USA", "2022-0863-USA"]).sort_values("DisNo.")
#Filter locations only for events we keep
events_to_keep = list(disasters_90_23.index)
disaster_locations_90_23 = disaster_locations_90_23.set_index("DisNo.").loc[events_to_keep]

#4 Write cleaned data
################################

disasters_90_23 = disasters_90_23.reset_index()
disaster_locations_90_23 = disaster_locations_90_23.reset_index()

#write identified locations
disasters_90_23.to_file(get_path("clean_data_path")+"disaster_national_90_23.gpkg", driver="GPKG")
disaster_locations_90_23.to_file(get_path("clean_data_path")+"disaster_subnational_90_23.gpkg", driver="GPKG")

print("Clean data saved to file")