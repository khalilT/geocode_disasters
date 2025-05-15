### (c) Khalil Teber 2025 ###
### Code file for PAPER "Geocoding climate-related disaster events"

# This script is designed to geocode event locations using the GeoNames API.
# It reads location data from a CSV file, converts ISO3 country codes to ISO2 format,
# and makes API requests to GeoNames to retrieve geographic coordinates (latitude and longitude)
# for each location. The results are saved in CSV files in chunks.

# Key features:
# - Implements rate limiting to comply with GeoNames' API limit of 900 requests per hour.
# - Handles API retries with exponential backoff in case of request failures.
# - Automatically retries failed geocoding requests for specific locations (e.g., South Sudan).
# - Processes data in chunks to efficiently handle large datasets and allows saving results incrementally.
# - Results are written to output files named according to their chunk number, allowing resumption from the last saved chunk.

# The script uses several key functions:
# 1. `get_country_alpha2_from_iso3`: Converts ISO3 country codes to ISO2 codes required by the GeoNames API.
# 2. `make_request_with_rate_limiting`: Manages API requests with rate limiting to ensure compliance with GeoNames' limits.
# 3. `get_place_coordinates_geonames`: Geocodes a location by querying the GeoNames API and handles errors and retries.
# 4. Processes data in chunks from the input CSV, geocodes each location, and saves results to CSV files in the output directory.

# Need to run the script twice:
# First time with all locations that don't have the GAUL ID number
# Second time with all locations that needed manual correction

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from utils.paths import get_path  # Import the get_path function from paths.py
import utils.constants as constants
import utils.functions as functions

import numpy as np
import pandas as pd
import requests
import pycountry
import time
import datetime


# geonames access
# (replace with valid GeoNames username)
username = "########"

# Read the CSV files with location names
# Retrieve path to locations to geolocate
df_locations_path = get_path("df_locations_path")
# df_locations_path = get_path("df_locations_corrected_path")
# Load EM-DAT using pandas
if os.path.exists(df_locations_path):
    df_locations = pd.read_csv(df_locations_path)
else:
    print(f"File not found at {df_locations_path}")

# Initialize an empty DataFrame to store the results
results_locations = pd.DataFrame()

# Set the chunk size
chunk_size = 150

# create output directory
intermediate_data_path = get_path("intermediate_data_path")
output_dir = intermediate_data_path + "identified_locations/"
# output_dir = intermediate_data_path + "corrected_locations/"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

existing_files = [
    f for f in os.listdir(output_dir) if f.startswith("EMDAT_golocations_coordinates_q")
]
existing_files.sort(key=lambda x: int(x.split("q")[-1].split(".")[0]))

# Determine the starting chunk number
if existing_files:
    last_file = existing_files[-1]
    last_chunk_number = int(last_file.split("q")[-1].split(".")[0])
    start_index = last_chunk_number * chunk_size
else:
    last_chunk_number = 0
    start_index = 0

# Loop through the DataFrame starting from the last chunk
for j in range(start_index, len(df_locations)):
    print(j, "/", len(df_locations))

    result = {}
    event = df_locations.iloc[j][["ISO", "Location", "DisNo."]]
    result.update(
        {
            event[1]: functions.get_place_coordinates_geonames(
                event[1].strip(), event[0], event[2], username
            )
        }
    )
    event_df = pd.DataFrame.from_dict(result, orient="index")
    event_df.columns = [
        "DisNo.",
        "EM-DAT-Location",
        "Longitude",
        "Latitude",
        "geoNames",
        "Province",
    ]

    # Append the result to the results DataFrame
    results_locations = pd.concat([results_locations, event_df])

    # Check if we've reached the chunk size or the end of the DataFrame
    if (j + 1) % chunk_size == 0 or (j + 1) == len(df_locations):
        # Reset the index of the results DataFrame
        results_locations = results_locations.reset_index(drop=True)

        # Determine the file number based on the current index
        file_number = (j + 1) // chunk_size

        # Write the results to a CSV file
        results_locations.to_csv(
            f"{output_dir}/EMDAT_golocations_coordinates_q{file_number}.csv",
            index=False,
        )

        # Clear the results DataFrame for the next chunk
        results_locations = pd.DataFrame()

# Handle any remaining results that didn't fill a full chunk
if not results_locations.empty:
    file_number += 1
    results_locations.to_csv(
        f"{output_dir}/EMDAT_golocations_coordinates_q{file_number}.csv", index=False
    )
