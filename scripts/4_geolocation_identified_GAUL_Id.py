### (c) Khalil Teber 2025 ###
### Code file for PAPER "Geocoding climate-related disaster events"

### In this script, we identify the geometries corresponding to the locations where the GAUL id is provided with EM-DAT.
### we then concatenate all identified locations together and apply quality flags for consistency

import numpy as np
import geopandas as gpd
import pandas as pd
import dask_geopandas as dgpd
import re

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from utils.paths import get_path  # Import the get_path function from paths.py
import utils.constants as constants
import utils.functions as functions

print("# 1 Read and clean Location Data")
# 1 Read and clean Location Data
########################
# read data and set 'DisNo.' as index
emdat_data_path = get_path("emdat_path")
if os.path.exists(emdat_data_path):
    emdat = pd.read_excel(emdat_data_path)
else:
    print(f"File not found at {emdat_data_path}")
emdat = emdat.set_index("DisNo.")

# Select only 'Location' and 'Admin Units' columns and drop rows where both are NaN
emdat = emdat[["Location", "Admin Units"]].dropna(how="all")

# Sort 'Location' column alphabetically
emdat["Location"] = emdat["Location"].apply(
    lambda x: ", ".join(sorted(str(x).split(", ")))
)


print("# 2 Process and Extract Administrative regions with corresponding id")
# 2 Process and Extract Administrative regions with corresponding id
########################

# Apply the process_admin_units function to 'Admin Units' column and assign the result to Emdata
Emdata = emdat["Admin Units"].apply(functions.process_admin_units)
Emdata.columns = ["Admin1 Code", "Admin2 Code", "Geo Locations"]

# Merge 'Location' column from emdat into Emdata DataFrame
Emdata["Location"] = emdat["Location"]

common_nans = emdat[emdat["Location"].notna() & emdat["Admin Units"].isna()]

# get the entires that only have location name indiction (not the geolocation name and code)
Emdata_loconly = Emdata[Emdata["Admin1 Code"].isna() & Emdata["Admin2 Code"].isna()]
# get the geocoded entries
Emdata_geocode = Emdata.drop(Emdata_loconly.index)

print("# 3 Match Events with Geolocations (Admin1 and Admin2 Levels)")
# 3 Match Events with Geolocations (Admin1 and Admin2 Levels)
########################

# load gaul data
gaul1 = gpd.read_file(get_path("gaul1_path"))
gaul2 = gpd.read_file(get_path("gaul2_path"))

# Match events with geolocations (from 2021 onwards)
# geometries at Admin 1 level

####Administrative level 1 geometries
# Extract Adm1 locations
emdat_geocode_adm1 = Emdata_geocode.loc[
    Emdata_geocode["Geo Locations"].str.contains("(Adm1)")
]
emdat_geocode_adm1["Geo Locations"] = emdat_geocode_adm1["Geo Locations"].str.split(
    " \(Adm1", expand=True
)[0]
# Shape Adm1 locations: 1 row = 1 geolocation
emdat_geocode_adm1_stacked = pd.DataFrame(
    emdat_geocode_adm1["Admin1 Code"].str.split(";", expand=True).stack()
).rename(columns={0: "ADM1_CODE"})
emdat_geocode_adm1_stacked["location"] = pd.DataFrame(
    emdat_geocode_adm1["Location"].str.split(",", expand=True).stack()
)
emdat_geocode_adm1_stacked["geolocation"] = pd.DataFrame(
    emdat_geocode_adm1["Geo Locations"].str.split(",", expand=True).stack()
)
emdat_geocode_adm1_identified = emdat_geocode_adm1_stacked.reset_index().drop(
    columns={"level_1"}
)

# geometries at Admin 2 level

####Administrative level 2 geometries
# Extract Adm2 locations
emdat_geocode_adm2 = Emdata_geocode[
    Emdata_geocode["Geo Locations"].str.contains("(Adm2)")
]
# In the Geo Locations column, some rows still have admin1 geometry locations that need to be removed
# clean Adm1 mention for the admin2 locations
emdat_geocode_adm2_cadm1 = emdat_geocode_adm2[
    emdat_geocode_adm2["Geo Locations"].str.contains("(Adm1)")
]  # location 2 with location 1 mentions still
# emdat_geocode_adm2_cadm1 = emdat_geocode_adm2_cadm1.reset_index().iloc[:,1::]
emdat_geocode_adm2_cadm1["Geo Locations"] = (
    emdat_geocode_adm2_cadm1["Geo Locations"]
    .str.split(" \(Adm1\).", expand=True)[1]
    .str.replace(" \(Adm2\).", "")
)
emdat_geocode_adm2_wtadm1 = emdat_geocode_adm2[
    ~emdat_geocode_adm2["Geo Locations"].str.contains("(Adm1)")
]
emdat_geocode_adm2_wtadm1["Geo Locations"] = emdat_geocode_adm2_wtadm1[
    "Geo Locations"
].str.replace(" \(Adm2\).", "")
emdat_geocode_adm2 = pd.concat([emdat_geocode_adm2_cadm1, emdat_geocode_adm2_wtadm1])

# Shape Adm1 locations: 1 row = 1 geolocation
emdat_geocode_adm2_stacked = pd.DataFrame(
    emdat_geocode_adm2["Admin2 Code"].str.split(";", expand=True).stack()
).rename(columns={0: "ADM2_CODE"})
emdat_geocode_adm2_stacked["location"] = pd.DataFrame(
    emdat_geocode_adm2["Location"].str.split(",", expand=True).stack()
)
emdat_geocode_adm2_stacked["geolocation"] = pd.DataFrame(
    emdat_geocode_adm2["Geo Locations"].str.split(",", expand=True).stack()
)
emdat_geocode_adm2_identified = emdat_geocode_adm2_stacked.reset_index()

# get the admin1 geolocated events geometries #emdat_geocode_adm1_identified
emdat_geocode_adm1_identified["ADM1_CODE"] = emdat_geocode_adm1_identified[
    "ADM1_CODE"
].astype(int)
events_adm1 = emdat_geocode_adm1_identified.merge(gaul1, on="ADM1_CODE", how="left")

# get the admin2 geolocated events geometries #emdat_geocode_adm2_identified
emdat_geocode_adm2_identified["ADM2_CODE"] = emdat_geocode_adm2_identified[
    "ADM2_CODE"
].astype(int)
events_adm2 = emdat_geocode_adm2_identified.merge(gaul2, on="ADM2_CODE", how="left")

print("# 4 Collect locations together and assign quality flags")
# 4 collect locations together
# and assign quality flags
##########################

# locations geocoded with Geonames
geonames_locations = pd.read_csv(get_path("geonames_locations_clean_path")).drop(
    columns={"Unnamed: 0"}
)

# admin 1
events_adm1.loc[:, "ADM2_NAME"] = np.NaN
events_adm1.loc[:, "ADM2_CODE"] = np.NaN
events_adm1.loc[:, "geoNames"] = np.NaN
events_adm1.loc[:, "Province"] = np.NaN
events_adm1.loc[:, "admin_level"] = 1
events_adm1.loc[:, "geocoding_q"] = 1
events_adm1

events_adm1 = events_adm1.rename(columns={"iso3": "ISO", "location": "Location"})
events_adm1 = events_adm1[
    [
        "ADM1_NAME",
        "ADM1_CODE",
        "ADM2_NAME",
        "ADM2_CODE",
        "DisNo.",
        "Location",
        "geoNames",
        "Province",
        "ISO",
        "admin_level",
        "geocoding_q",
    ]
]

# admin 2
events_adm2.loc[:, "geoNames"] = np.NaN
events_adm2.loc[:, "Province"] = np.NaN
events_adm2.loc[:, "admin_level"] = 2
events_adm2.loc[:, "geocoding_q"] = 1

events_adm2 = events_adm2.rename(columns={"iso3": "ISO", "location": "Location"})
events_adm2 = events_adm2[
    [
        "ADM1_NAME",
        "ADM1_CODE",
        "ADM2_NAME",
        "ADM2_CODE",
        "DisNo.",
        "Location",
        "geoNames",
        "Province",
        "ISO",
        "admin_level",
        "geocoding_q",
    ]
]

located_events = pd.concat([events_adm1, events_adm2, geonames_locations])
located_events = located_events.sort_values("DisNo.")

emdat = pd.read_excel(emdat_data_path)

# select only climate events

natural_events = emdat[emdat["Disaster Group"] == "Natural"]
disaster_types = natural_events[["DisNo.", "Disaster Type", "Disaster Subtype"]]
selected_disasters = disaster_types[
    (disaster_types["Disaster Type"] == "Drought")
    | (disaster_types["Disaster Type"] == "Extreme temperature")
    | (disaster_types["Disaster Type"] == "Flood")
    | (disaster_types["Disaster Type"] == "Storm")
    | (disaster_types["Disaster Type"] == "Wildfire")
    | (disaster_types["Disaster Type"] == "Mass movement (wet)")
    | (disaster_types["Disaster Type"] == "Mass movement (dry)")
]

selected_disasters = selected_disasters.rename(
    columns={"Disaster Type": "disaster_type"}
).drop(columns={"Disaster Subtype"})


selected_disasters = selected_disasters.set_index("DisNo.")
located_events = located_events.set_index("DisNo.")

located_events_disasters = located_events.join(selected_disasters)
located_events_disasters = located_events_disasters.dropna(subset="disaster_type")

print("# 5 Merge identified locations with GAUL geodata")
# 5 Merge identified locations with GAUL geodata
##########################
admin1_locations = located_events_disasters[located_events_disasters.admin_level == 1]
admin2_locations = located_events_disasters[located_events_disasters.admin_level == 2]


admin1_locations = admin1_locations.reset_index()
admin2_locations = admin2_locations.reset_index()

admin1_locations["ADM1_CODE"] = admin1_locations["ADM1_CODE"].astype(int)
admin2_locations["ADM2_CODE"] = admin2_locations["ADM2_CODE"].astype(int)

gaul1_tomerge = gaul1[["ADM1_CODE", "geometry"]]
gaul2_tomerge = gaul2[["ADM2_CODE", "geometry"]]

# get the admin1 geolocated events geometries #emdat_geocode_adm1_identified
admin1_locations = admin1_locations.merge(gaul1_tomerge, on="ADM1_CODE", how="left")
# get the admin2 geolocated events geometries #emdat_geocode_adm2_identified
admin2_locations = admin2_locations.merge(gaul2_tomerge, on="ADM2_CODE", how="left")


climate_event_locations_90_23 = (
    pd.concat([admin1_locations, admin2_locations])
    .reset_index()
    .drop(columns={"disaster_type", "index"})
)
climate_event_locations_90_23 = gpd.GeoDataFrame(climate_event_locations_90_23)

# simplify geometries of the geodataframe (to optimize object size)

simplified_geometries = climate_event_locations_90_23.simplify(0.005)
climate_event_locations_90_23["geometry"] = simplified_geometries
climate_event_locations_90_23 = gpd.GeoDataFrame(
    climate_event_locations_90_23, crs="EPSG:4326"
)

### Last correction
# remove redundancies: admin1 level region on top of identified admin 2 layers
# if the regions identified by geonames on 2 different administrative levels overlap completely, keep the admin 2 region only
# remove events that were associated to the wrong geometries

climate_event_locations_90_23.geometry = climate_event_locations_90_23.geometry.apply(
    lambda geometry: functions.fix_invalid_geometry(geometry)
)
# correction of geometries in parallel

# # Convert to Dask GeoDataFrame
# dask_gdf = dgpd.from_geopandas(climate_event_locations_90_23, npartitions=100)

# dask_gdf["geometry"] = dask_gdf["geometry"].map(functions.fix_invalid_geometry, meta=("geometry", "object"))
# result_gdf = dask_gdf.compute()

# climate_event_locations_90_23 = gpd.GeoDataFrame(result_gdf, crs="EPSG:4326")

collect_results = []

for even in np.unique(climate_event_locations_90_23["DisNo."]):
    location_gdf = climate_event_locations_90_23[
        climate_event_locations_90_23["DisNo."] == even
    ]
    collect_results.append(functions.check_bounding_box_containment(location_gdf))

# concatenate the results
cleaned_results = [x for x in collect_results if x is not None]

indices_to_remove = []

for i in np.arange(len(cleaned_results)):
    df = climate_event_locations_90_23[
        climate_event_locations_90_23["DisNo."] == cleaned_results[i][0]
    ].drop(columns="geometry")
    duplicated_df = df[
        ((df["ADM1_CODE"].duplicated(keep=False)) & (df["admin_level"] == 1))
    ]
    if duplicated_df.empty:
        pass
    else:
        indices_to_remove.append(duplicated_df.index)

flattened_list = [item for sublist in indices_to_remove for item in sublist]
climate_event_locations_90_23 = climate_event_locations_90_23.drop(flattened_list)
climate_event_locations_90_23 = climate_event_locations_90_23.reset_index().drop(
    columns={"index"}
)

print("# 6 Save identified locations to file")
output_path = (
    get_path("intermediate_data_path")
    + "geolocated_climate_events_1990-2023_simplified_clean.gpkg"
)
if os.path.exists(output_path):
    os.remove(output_path)
# write identified locations
climate_event_locations_90_23.to_file(output_path, driver="GPKG")

print("Geolocated climate events saved to file")
