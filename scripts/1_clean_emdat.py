### (c) Khalil Teber 2025 ###
### Code file for PAPER "Geocoding climate-related disaster events"

# In this script, we identify the events where the locations do not have the GAUL ID provided,
# and where the geocoding will be done based on the regions' name.
# This is the case for events from 1990 to 2000, and some events from 2000 to 2023


import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from utils.paths import get_path  # Import the get_path function from paths.py
import utils.constants as constants
import utils.functions as functions

import pandas as pd
import geopandas as gpd
import numpy as np
import re


def main():

    # 1 Read and Apply Location Corrections
    ######################################
    # Read data and apply corrections

    emdat_data_path = get_path("emdat_path")
    print(f"EM-DAT Data Path: {emdat_data_path}")

    # Load EM-DAT using pandas
    if os.path.exists(emdat_data_path):
        emdat = pd.read_excel(emdat_data_path)
        print(emdat.head())
    else:
        print(f"File not found at {emdat_data_path}")

    emdat["Location"] = emdat["Location"].str.lower()

    emdat.loc[emdat.ISO == "PHL", "Location"] = emdat.loc[
        emdat.ISO == "PHL", "Location"
    ].replace(constants.rep_philippines, regex=True)
    emdat.loc[emdat.ISO == "BFA", "Location"] = emdat.loc[
        emdat.ISO == "BFA", "Location"
    ].replace(constants.rep_burkina, regex=True)
    emdat.loc[emdat.ISO == "HTI", "Location"] = emdat.loc[
        emdat.ISO == "HTI", "Location"
    ].replace(constants.rep_haiti, regex=True)
    emdat.loc[emdat.ISO == "TCD", "Location"] = emdat.loc[
        emdat.ISO == "TCD", "Location"
    ].replace(constants.rep_chad, regex=True)

    Emdata = emdat.copy()

    # 2 Standardize and Clean Location Data
    ######################################
    # select locations that do not have admin units, but only admin names, and only for natural events

    Emdata_loconly = Emdata[
        (Emdata["Admin Units"].isna())
        & (Emdata["Location"].notna())
        & (Emdata["Disaster Group"] == "Natural")
    ]

    # This script processes and cleans EM-DAT locations. The goal is to standardize and separate the location information.
    # The script performs the following key tasks:

    # String Replacement: Replaces words like 'and', 'Between', '&', etc., with commas to standardize the separation between multiple locations.
    # Location Splitting: Uses a function `split_and_clean_locations` to split location strings based on commas, semicolons, and parentheses,
    # while handling special cases such as entries containing "Level 1".
    # Location Name Cleanup: removes certain common terms related to geographic divisions (like 'Province', 'District', 'Region', etc.).
    # Further Location Splitting: Uses a function `split_text` to break down entries that contain multiple parenthetical groups or locations
    # into individual components for easier parsing.
    # Location Extraction: The `extract_locations` function is used to parse locations that contain brackets or geographic references.
    # New Data Creation:A new DataFrame is created with four main columns: 'DisNo.' (event ID), 'Individual_Location', 'Location_Before'
    # (location before parentheses), and 'Bracketed' (location inside parentheses). It combines the cleaned-up
    #'Location_Before' and 'Bracketed' columns to create a final 'Appended' location field, which merges both parts where applicable.

    # The final DataFrame presents a standardized and cleaned version of the original location data, making it suitable for further analysis or geocoding operations.

    Emdata_loconly.loc[:, "Location"] = Emdata_loconly["Location"].str.replace(
        r"\) and\b", "),", regex=True
    )

    Emdata_loconly.loc[:, "Location"] = Emdata_loconly["Location"].str.replace(
        r"\b(and|Between|&|\+)\b", ",", regex=True
    )

    # 3 Split and Parse Location Strings
    ######################################

    expanded_rows = [
        [row["DisNo."], row["Location"], loc]
        for _, row in Emdata_loconly.iterrows()
        for loc in functions.split_and_clean_locations(row["Location"])
    ]

    expanded_df = pd.DataFrame(
        expanded_rows, columns=["DisNo.", "Full_Location_List", "Individual_Location"]
    )

    for term in constants.replace_terms:
        expanded_df["Individual_Location"] = expanded_df[
            "Individual_Location"
        ].str.replace(term, " ", case=False, regex=False)

    expanded_df["Individual_Location"] = expanded_df["Individual_Location"].apply(
        functions.split_text
    )
    expanded_df = expanded_df.explode("Individual_Location", ignore_index=True)
    expanded_df["Individual_Location"] = expanded_df["Individual_Location"].str.replace(
        r"\b(and| & |Between| \+ | \) and)\b", ",", regex=True
    )

    new_data = [
        [row["DisNo."], row["Individual_Location"], loc[0], loc[1]]
        for _, row in expanded_df.iterrows()
        for loc in functions.extract_locations(row["Individual_Location"])
    ]

    new_df = pd.DataFrame(
        new_data,
        columns=["DisNo.", "Individual_Location", "Location_Before", "Bracketed"],
    )
    new_df["Appended"] = (
        new_df["Location_Before"]
        + ","
        + new_df["Bracketed"].apply(lambda x: f" {x}" if x else "")
    )

    print(new_df)

    new_df["Appended"] = new_df["Appended"].apply(functions.remove_str_if_last)

    # remove locations that are only numbers or digits

    numeric_rows = (
        new_df[["Location_Before"]]
        .applymap(lambda x: isinstance(x, str) and x.isdigit())
        .any(axis=1)
    )
    new_df = new_df[~numeric_rows]

    # Find locations where the number of characters is 2
    one_char_rows = new_df[["Individual_Location"]].applymap(
        lambda x: isinstance(x, str) and len(x) == 2
    )
    usa_rep_rows = new_df[one_char_rows.Individual_Location][
        (new_df[one_char_rows.Individual_Location]["DisNo."].str.contains("USA"))
    ]

    # apply the correction to the locations in the USA
    new_df.loc[usa_rep_rows.index] = new_df.loc[usa_rep_rows.index].replace(
        constants.rep_us_states, regex=True
    )

    # extract the ISO column from the disaster number
    new_df["ISO"] = new_df["DisNo."].str[-3:]

    # search for and remove uncorrect ISO codes.
    # For some events, older ISO codes or iso codes other than iso 3 are used by EM-DAT
    # ISO to correct: original iso and replacement
    # AZO by PRT
    # DFR by DEU
    # 1346 by MNE
    # SCG by SRB
    new_df["ISO"].replace("AZO", "PRT", inplace=True)
    new_df["ISO"].replace("DFR", "DEU", inplace=True)
    new_df["ISO"].replace("SCG", "SRB", inplace=True)

    # event in montenegro that belonged to serbia in the past
    new_df.loc[(new_df.ISO == "SRB") & (new_df.Bracketed == "montenegro"), "ISO"] = (
        "MNE"
    )

    # events to delete, as they happened in countries that no longer exist (e.g. Youguslavia), at the scale of entire countries today (e.g. Slovenia)
    #'ANT'
    #'SUN'
    #'YUG'
    new_df = new_df[~(new_df.ISO == "YUG")]
    new_df = new_df[~(new_df.ISO == "SUN")]
    new_df = new_df[~(new_df.ISO == "ANT")]

    # 4 Apply Final Corrections and Export
    ######################################
    # select USA events
    new_df_usa = new_df[new_df.ISO == "USA"]
    new_df_usa = new_df_usa[["DisNo.", "ISO", "Appended"]].rename(
        columns={"Appended": "Location"}
    )

    # select rest of the world events
    new_df_restwolrd = new_df[~(new_df.ISO == "USA")]
    new_df_restwolrd = new_df_restwolrd[["DisNo.", "ISO", "Appended"]].rename(
        columns={"Appended": "Location"}
    )

    # concat togethr
    df_locations = pd.concat([new_df_usa, new_df_restwolrd])

    df_locations = df_locations[~(df_locations["Location"] == "nan")]

    df_locations = df_locations.reset_index().drop(columns="index")

    intermediate_data_path = get_path("intermediate_data_path")

    df_locations.to_csv(intermediate_data_path + "event_locations_to_geolocate.csv")


if __name__ == "__main__":
    main()
