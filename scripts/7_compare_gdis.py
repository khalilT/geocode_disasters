### (c) Khalil Teber 2025 ###
### Code file for PAPER "Geocoding climate-related disaster events"

### In this script, we compare our geocoded events to GDIS database.

import numpy as np
import geopandas as gpd
import pandas as pd
import re
import sys
import os

import dask
from dask import delayed, compute

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from utils.paths import get_path  # Import the get_path function from paths.py
import utils.constants as constants
import utils.functions as functions

# 1 Load Events Data
###############################

print("#####################")
print("Read data")
print("#####################")

disaster_locations_90_23 = gpd.read_file(
    get_path("geocoded_locations_path"), driver="GPKG"
)

gdis_locations = gpd.read_file(get_path("gdis_data_path"), driver="GPKG")
# gdis_locations = gpd.read_file(get_path("gdis_simplified_path"), driver="GPKG")

# 2 Find locations about events common to both databases
###############################

print("#####################")
print("Find common event")
print("#####################")

gdis_locations[["disasterno", "iso3"]] = gdis_locations[["disasterno", "iso3"]].astype(
    str
)
gdis_locations["DisNo."] = gdis_locations[["disasterno", "iso3"]].agg("-".join, axis=1)

locations_geodat = np.unique(disaster_locations_90_23[["DisNo."]])
locations_gdis = np.unique(gdis_locations[["DisNo."]])

common_locations = list(set(locations_geodat).intersection(set(locations_gdis)))

locations_common = disaster_locations_90_23.set_index("DisNo.").loc[common_locations]
gdis_locations_common = gdis_locations.set_index("DisNo.").loc[common_locations]


# 3 run test to compare events
###############################

print("#####################")
print("Compare events and save results")
print("#####################")


# result = []

# for idx in common_locations:
#     print(idx)
#     result.append(
#         pd.DataFrame(
#             {
#                 idx: functions.compare_single_event_by_area(
#                     idx,
#                     locations_common.reset_index(),
#                     gdis_locations_common.reset_index(),
#                     "DisNo.",
#                 )
#             }
#         ).T
#     )

# Avoid pickling huge objects every time by binding them up front
# comparison_df = pd.concat(result)

locs = locations_common.reset_index()
g_locs = gdis_locations_common.reset_index()


def _single(idx, locs, g_locs):
    """Returns a 1-row DataFrame for one location."""
    return pd.DataFrame(
        {idx: functions.compare_single_event_by_area(idx, locs, g_locs, "DisNo.")}
    ).T


tasks = [delayed(_single)(idx, locs, g_locs) for idx in common_locations]

comparison_df = pd.concat(compute(*tasks))
comparison_df = comparison_df.reset_index().rename(columns={"index": "DisNo."})

# comparison_df.to_csv(get_path("clean_data_path")+"geodat_gdis_comaprison.csv")


# 4 plot differences
##############################

# get quality flags and admin level of geo-clim-data
quality_flags = locations_common[["geocoding_q", "admin_level"]]
quality_flags = quality_flags.add_prefix("geoD_")
quality_flags_grouped = quality_flags.groupby(level=0).agg(lambda x: list(set(x)))
quality_flags_grouped[["geoD_geocoding_q", "geoD_admin_level"]] = quality_flags_grouped[
    ["geoD_geocoding_q", "geoD_admin_level"]
].astype(str)

# get admin level of GDIS
admin_level = gdis_locations_common[["level"]]
admin_level = admin_level.add_prefix("gdis_admin_")
admin_level_grouped = admin_level.groupby(level=0).agg(lambda x: list(set(x)))
admin_level_grouped[["gdis_admin_level"]] = admin_level_grouped[
    ["gdis_admin_level"]
].astype(str)

# join to comparison dataframe
comparison_df = (
    comparison_df.set_index("DisNo.")
    .join(quality_flags_grouped)
    .join(admin_level_grouped)
)
comparison_df = comparison_df[
    [
        "Event",
        "Mismatch > 10%",
        "Mismatch Percentage",
        "Total Area GDIS",
        "Total Area GeoD",
        "gdis_admin_level",
        "geoD_admin_level",
        "geoD_geocoding_q",
    ]
]
comparison_df.to_csv(get_path("clean_data_path") + "geodat_gdis_comaprison_qflags.csv")

# plot the events
# determine the events with high overlap mismatch and highest quality flag in geo-clim-dat
diff_highest_q = comparison_df[
    (comparison_df["Mismatch > 10%"] == True)
    & (comparison_df["geoD_geocoding_q"] == "[1]")
]
events_to_test = diff_highest_q["Event"].values
events_to_test.sort()

functions.plot_multiple_events_to_pdf(
    events_to_test,
    locations_common.reset_index(),
    gdis_locations_common.reset_index(),
    "DisNo.",
    comparison_df,
)
