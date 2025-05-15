# module containing functions

# functions for cleaning location names to be used in script 1
from .paths import get_path
import re


def split_and_clean_locations(location):
    # Define the pattern to identify "Level 1" and its surroundings
    pattern = re.compile(r"^(.*?)(Level 1\s*(.*))$", re.IGNORECASE)

    match = pattern.match(location)
    if match:
        before_level_1 = match.group(1).strip()
        after_level_1 = match.group(3).strip()
        # Format the output with "Level 1" part in brackets
        cleaned_entries = [f"{before_level_1} ({after_level_1})"]
    else:
        # Proceed with the original split logic if "Level 1" is not found
        entries = re.split(r";", location)
        cleaned_entries = []
        for entry in entries:
            if "(" in entry and ")" in entry:
                cleaned_entries.append(entry.strip())
            else:
                sub_entries = re.split(r",\s*(?![^()]*\))", entry)
                cleaned_entries.extend(
                    [
                        sub_entry.strip()
                        for sub_entry in sub_entries
                        if sub_entry.strip()
                    ]
                )

    return cleaned_entries


def split_text(text):
    if text.count("(") > 1:
        return re.split(r",\s*(?=\S)", re.sub(r"\),\s*(?=\S)", "),\n", text))
    return re.split(r"\),\s*(?=\S)", text)


def extract_locations(row):
    locations = []
    if "(" in row:
        parts = row.split("(")
        locs = parts[0].strip().split(",")
        regions = parts[1].replace(")", "").split(",")
        for loc in locs:
            for sub_loc in loc.strip().split("/"):
                for region in regions:
                    locations.append([sub_loc.strip(), region.strip()])
    elif "," in row:
        for loc in row.split(","):
            locations.append([loc.strip(), None])
    else:
        for loc in row.strip().split("/"):
            locations.append([loc.strip(), None])
    return locations


# This function checks if the input is a string and if it ends with a comma.
# If so, it removes the trailing comma and returns the modified string.
# Otherwise, it returns the original string as is.|


def remove_str_if_last(s):
    if isinstance(s, str) and s.endswith(","):
        return s[:-1]
    return s


# functions for geolocating event regions used in script 2

import numpy as np
import pandas as pd
import requests
import pycountry
import datetime
import time

# Geolocation function parameters
MAX_REQUESTS_PER_HOUR = 900
SECONDS_IN_AN_HOUR = 3600
delay_between_requests = SECONDS_IN_AN_HOUR / MAX_REQUESTS_PER_HOUR  # 4 seconds

request_count = 0
start_time = datetime.datetime.now()


def get_country_alpha2_from_iso3(iso3_code):
    try:
        country = pycountry.countries.get(alpha_3=iso3_code)
        return country.alpha_2
    except AttributeError:
        print(f"Invalid ISO3 code: '{iso3_code}'")
        return None


def make_request_with_rate_limiting(params):
    global request_count, start_time

    # Check if an hour has passed and reset the counter if so
    elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
    if elapsed_time >= SECONDS_IN_AN_HOUR:
        request_count = 0
        start_time = datetime.datetime.now()

    # Check if we've hit the request limit
    if request_count >= MAX_REQUESTS_PER_HOUR:
        wait_time = SECONDS_IN_AN_HOUR - elapsed_time
        print(f"Rate limit reached. Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
        request_count = 0
        start_time = datetime.datetime.now()

    # Make the request
    response = requests.get("http://api.geonames.org/searchJSON", params=params)
    request_count += 1
    time.sleep(delay_between_requests)  # Ensure delay between requests
    return response


def get_place_coordinates_geonames(
    place_name, iso3_code, event_id, username, retries=1, delay=1, fuzzy=0.7
):
    country_code = get_country_alpha2_from_iso3(iso3_code)

    if not country_code:
        print(f"Invalid ISO3 code '{iso3_code}'. Unable to find country code.")
        return ""

    for attempt in range(retries):
        try:
            params = {
                "q": place_name,
                "country": country_code,
                "maxRows": 1,
                "username": username,
                "fuzzy": 0.7,
            }
            response = make_request_with_rate_limiting(params)
            response.raise_for_status()
            data = response.json()

            if data["geonames"]:
                lng = data["geonames"][0]["lng"]
                lat = data["geonames"][0]["lat"]
                name = data["geonames"][0]["name"]
                adm1 = data["geonames"][0]["adminName1"]
                # country = data['geonames'][0]['countryName']
                output = (
                    event_id,
                    place_name,
                    float(lng),
                    float(lat),
                    name,
                    adm1,
                )  # , country
                return output
            else:
                print(
                    f"Place named '{place_name}' not found in country with ISO3 code '{iso3_code}'. Retrying..."
                )

                # Special condition: If SDN fails, try SSD
                if iso3_code == "SDN":
                    print("Trying with South Sudan (SSD)...")
                    return get_place_coordinates_geonames(
                        place_name, "SSD", event_id, username, retries, delay, fuzzy
                    )

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"Geocoding failed after {retries} attempts.")
                output_na = event_id, place_name, np.nan, np.nan, np.nan, np.nan
                return output_na

    print(
        f"Place named '{place_name}' not found in country with ISO3 code '{iso3_code}'."
    )
    output_na = event_id, place_name, np.nan, np.nan, np.nan, np.nan  # , np.nan
    return output_na


# functions for geolocating event regions used in script 3

from shapely.geometry import Point


def find_containing_geometry(gdf, Longitude, Latitude):
    """
    Find the geometry in the GeoDataFrame that contains the given coordinates.

    Parameters:
    gdf (GeoDataFrame): The GeoDataFrame with geometries.
    coordinates (tuple): The coordinates (longitude, latitude).

    Returns:
    GeoSeries or None: The row(s) in the GeoDataFrame that contain the coordinates.
    """
    point = Point(Longitude, Latitude)

    # Check if the point is within any of the geometries in the GeoDataFrame
    containing_geometry = gdf[gdf.contains(point)]

    if containing_geometry.empty:
        return "None found"
    else:
        return containing_geometry


from fuzzywuzzy import fuzz


def calculate_similarity_ADM1(row):
    location = str(row["Location"]) if pd.notna(row["Location"]) else ""
    ADM1_NAME = str(row["ADM1_NAME"]) if pd.notna(row["ADM1_NAME"]) else ""
    return fuzz.ratio(location.lower(), ADM1_NAME.lower())


# Function to calculate the similarity score between two strings
def calculate_similarity_ADM2(row):
    location = str(row["Location"]) if pd.notna(row["Location"]) else ""
    ADM2_NAME = str(row["ADM2_NAME"]) if pd.notna(row["ADM2_NAME"]) else ""
    return fuzz.ratio(location.lower(), ADM2_NAME.lower())


# Function to calculate the similarity score between two strings
def calculate_similarity_geonames(row):
    location = str(row["Location"]) if pd.notna(row["Location"]) else ""
    geoname = str(row["geoNames"]) if pd.notna(row["geoNames"]) else ""
    return fuzz.ratio(location.lower(), geoname.lower())


# function to find matching regions at admin level 1
def find_matching_region_adm1(row, gaul1, threshold=80):
    # Extract ISO code and location from the row
    iso_code = row["ISO"]
    regionoi = row["Location"]

    # Filter the GAUL1 DataFrame for matching ISO codes
    gaul1_iso = gaul1[gaul1.iso3 == iso_code]

    # Initialize variables to store the best match
    best_match = None
    best_score = threshold

    # Iterate through GAUL1 regions and calculate fuzzy matching score
    for i in np.arange(len(gaul1_iso)):
        match_score = fuzz.ratio(
            row["Location"].lower(), gaul1_iso.iloc[i]["ADM1_NAME"].lower()
        )
        if match_score > best_score:
            best_match = gaul1_iso.iloc[i]["ADM1_NAME"]
            best_score = match_score

    # If a best match was found above the threshold, return it as a DataFrame
    if best_match:
        adm1code = gaul1_iso[gaul1_iso.ADM1_NAME == best_match]["ADM1_CODE"].values[0]
        result_df = pd.DataFrame(
            {
                "ADM1_NAME": [best_match],
                "ADM1_CODE": [adm1code],
                "Score": [best_score],
                "DisNo.": [row["DisNo."]],
                "Location": [row["Location"]],
                "index": [row["index"]],
                "geoNames": [row["geoNames"]],
                "Province": [row["Province"]],
                "ISO": [row["ISO"]],
            }
        )
        return result_df

    # If no match is found above the threshold, return an empty DataFrame
    return pd.DataFrame(
        columns=[
            "ADM1_NAME",
            "ADM1_CODE",
            "Score",
            "DisNo.",
            "Location",
            "index",
            "geoNames",
            "Province",
            "ISO",
        ]
    )


# function to find matching regions at admin level 2
def find_matching_region_adm2(row, gaul2, threshold=80):
    # Extract ISO code and location from the row
    iso_code = row["ISO"]
    regionoi = row["Location"]
    adm1_name = row["ADM1_NAME"]
    adm1_code = row["ADM1_CODE"]

    # Filter the GAUL2 DataFrame for matching ISO codes
    gaul2_iso = gaul2[(gaul2.iso3 == iso_code) & (gaul2.ADM1_CODE == adm1_code)]

    # Initialize variables to store the best match
    best_match = None
    best_score = threshold

    # Iterate through GAUL1 regions and calculate fuzzy matching score
    for i in np.arange(len(gaul2_iso)):
        match_score = fuzz.ratio(
            row["Location"].lower(), gaul2_iso.iloc[i]["ADM2_NAME"].lower()
        )
        if match_score > best_score:
            best_match = gaul2_iso.iloc[i]["ADM2_NAME"]
            best_score = match_score

    # If a best match was found above the threshold, return it as a DataFrame
    if best_match:
        adm2code = gaul2_iso[gaul2_iso.ADM2_NAME == best_match]["ADM2_CODE"].values[0]
        result_df = pd.DataFrame(
            {
                "ADM1_NAME": [adm1_name],
                "ADM1_CODE": [adm1_code],
                "ADM2_NAME": [best_match],
                "ADM2_CODE": [adm2code],
                "Score": [best_score],
                "DisNo.": [row["DisNo."]],
                "Location": [row["Location"]],
                "index": [row["index"]],
                "geoNames": [row["geoNames"]],
                "Province": [row["Province"]],
                "ISO": [row["ISO"]],
            }
        )
        return result_df

    # If no match is found above the threshold, return an empty DataFrame
    return pd.DataFrame(
        columns=[
            "ADM1_NAME",
            "ADM1_CODE",
            "ADM2_NAME",
            "ADM2_CODE",
            "Score",
            "DisNo.",
            "Location",
            "index",
            "geoNames",
            "Province",
            "ISO",
        ]
    )


# function to find matching regions at admin level 1 with province identified with Geonames
def find_match_province_adm1(row, gaul1, threshold=80):
    # Extract ISO code and location from the row
    iso_code = row["ISO"]
    regionoi = row["Province"]

    # Filter the GAUL1 DataFrame for matching ISO codes
    gaul1_iso = gaul1[gaul1.iso3 == iso_code]

    # Initialize variables to store the best match
    best_match = None
    best_score = threshold

    # Iterate through GAUL1 regions and calculate fuzzy matching score
    for i in np.arange(len(gaul1_iso)):
        match_score = fuzz.ratio(
            row["Province"].lower(), gaul1_iso.iloc[i]["ADM1_NAME"].lower()
        )
        if match_score > best_score:
            best_match = gaul1_iso.iloc[i]["ADM1_NAME"]
            best_score = match_score

    # If a best match was found above the threshold, return it as a DataFrame
    if best_match:
        adm1code = gaul1_iso[gaul1_iso.ADM1_NAME == best_match]["ADM1_CODE"].values[0]
        result_df = pd.DataFrame(
            {
                "ADM1_NAME": [best_match],
                "ADM1_CODE": [adm1code],
                "Score": [best_score],
                "DisNo.": [row["DisNo."]],
                "Province": [row["Province"]],
                "index": [row["index"]],
                "geoNames": [row["geoNames"]],
                "ISO": [row["ISO"]],
            }
        )
        return result_df
    # If no match is found above the threshold, return an empty DataFrame
    return pd.DataFrame(
        columns=[
            "ADM1_NAME",
            "ADM1_CODE",
            "Score",
            "DisNo.",
            "Province",
            "index",
            "geoNames",
            "ISO",
        ]
    )


def find_retun_adm1_matches(df, gaul1):
    no_match_adm1_df = df.apply(
        lambda row: find_matching_region_adm1(row, gaul1), axis=1
    )
    df1_list = []
    for dfi in no_match_adm1_df:
        if not dfi.empty:
            df1_list.append(dfi)
    name_located_adm1 = pd.concat(df1_list)
    return name_located_adm1


def find_retun_adm2_matches(df, gaul2):
    no_match_adm2_df = df.apply(
        lambda row: find_matching_region_adm2(row, gaul2), axis=1
    )
    df2_list = []
    for dfi in no_match_adm2_df:
        if not dfi.empty:
            df2_list.append(dfi)
    name_located_adm2 = pd.concat(df2_list)
    return name_located_adm2


def is_substring_in_string(substring, main_string):
    return substring.lower() in main_string.lower()


def find_regionname_adm1(row):
    regionname = row["Location"]
    adm1name = row["ADM1_NAME"]
    adm1code = row["ADM1_CODE"]

    if is_substring_in_string(regionname, adm1name):
        result_df = pd.DataFrame(
            {
                "ADM1_NAME": [adm1name],
                "ADM1_CODE": [adm1code],
                "Location": [regionname],
                "DisNo.": [row["DisNo."]],
                "Province": [row["Province"]],
                "index": [row["index"]],
            }
        )
        return result_df
    return pd.DataFrame(
        columns=["ADM1_NAME", "ADM1_CODE", "Score", "DisNo.", "Province", "index"]
    )


def find_regionname_adm2(row):
    regionname = row["Location"]
    adm1name = row["ADM1_NAME"]
    adm1code = row["ADM1_CODE"]
    adm2name = row["ADM2_NAME"]
    adm2code = row["ADM2_CODE"]

    if is_substring_in_string(regionname, adm2name):
        result_df = pd.DataFrame(
            {
                "ADM1_NAME": [adm1name],
                "ADM1_CODE": [adm1code],
                "ADM2_NAME": [adm2name],
                "ADM2_CODE": [adm2code],
                "Location": [regionname],
                "DisNo.": [row["DisNo."]],
                "Province": [row["Province"]],
                "index": [row["index"]],
            }
        )
        return result_df
    return pd.DataFrame(
        columns=[
            "ADM1_NAME",
            "ADM1_CODE",
            "ADM2_NAME",
            "ADM2_CODE",
            "Score",
            "DisNo.",
            "Province",
            "index",
        ]
    )


# Function to calculate the similarity score between two strings
def calculate_similarity_location_province(row):
    location = str(row["Location"]) if pd.notna(row["Location"]) else ""
    province = str(row["Province"]) if pd.notna(row["Province"]) else ""
    return fuzz.ratio(location.lower(), province.lower())


# Functions used in script 4


# Process 'Admin Units' column to get Admin1 Code, Admin2 Code, and Geo Locations
def process_admin_units(units):
    if pd.isna(units):
        return pd.Series([None, None, None])

    admin1_units = []
    admin2_units = []

    # Extract Admin1 and Admin2 information
    for unit in eval(units):
        if "adm1_code" in unit:
            admin1_units.append((unit["adm1_code"], unit["adm1_name"]))
        if "adm2_code" in unit:
            admin2_units.append((unit["adm2_code"], unit["adm2_name"]))

    # Sort admin units alphabetically
    admin1_units.sort(key=lambda x: x[1])  # Sort by adm1_name
    admin2_units.sort(key=lambda x: x[1])  # Sort by adm2_name

    admin1_codes = [str(unit[0]) for unit in admin1_units]
    admin1_names_list = [unit[1] for unit in admin1_units]

    admin2_codes = [str(unit[0]) for unit in admin2_units]
    admin2_names_list = [unit[1] for unit in admin2_units]

    # Construct Geo Locations string
    geo_location_str = ", ".join(admin1_names_list) + (
        " (Adm1)." if admin1_names_list else ""
    )
    if admin2_names_list:
        geo_location_str += " " + ", ".join(admin2_names_list) + " (Adm2)."

    return pd.Series([";".join(admin1_codes), ";".join(admin2_codes), geo_location_str])


# fix invalid geometries
def fix_invalid_geometry(geometry):
    """
    Fix invalid geometries by buffering with a value of 0.
    Parameters:
        geometry (shapely.geometry): A geometry object to check and fix.
    Returns:
        shapely.geometry: Fixed geometry if invalid, otherwise the original geometry.
    """
    if not geometry.is_valid:
        return geometry.buffer(0)  # Fix invalid geometry
    return geometry


def check_bounding_box_containment(gdf):
    # Get the bounding boxes for each geometry
    bounding_boxes = gdf.bounds

    for i in range(len(gdf)):
        for j in range(len(gdf)):
            if i != j:  # Avoid comparing a geometry with itself
                # Get bounding boxes for geometry i and geometry j
                bbox_i = bounding_boxes.iloc[i]
                bbox_j = bounding_boxes.iloc[j]

                # Check if bbox_i is contained within bbox_j
                contained = (
                    bbox_i["minx"] >= bbox_j["minx"]
                    and bbox_i["miny"] >= bbox_j["miny"]
                    and bbox_i["maxx"] <= bbox_j["maxx"]
                    and bbox_i["maxy"] <= bbox_j["maxy"]
                )

                if contained:
                    return np.unique(
                        gdf["DisNo."].values[0]
                    )  # Return True as soon as containment is detected

    return None  # Return False if no containment is found


import geopandas as gpd
import pandas as pd
import numpy as np


def compare_single_event_by_area(event_id, gdf1, gdf2, index_col, threshold=0.1):
    """
    Compare a single event's affected area between two GeoDataFrames and estimate the mismatch percentage.

    Parameters:
    - event_id (str/int): The index of the event to compare.
    - gdf1 (GeoDataFrame): First GeoDataFrame.
    - gdf2 (GeoDataFrame): Second GeoDataFrame.
    - index_col (str): The column name used as a common index for events.
    - threshold (float): The area mismatch ratio threshold (default = 0.1 or 10%).

    Returns:
    - A dictionary with the event ID, areas, absolute and percentage differences, and mismatch flag.
    """

    # Ensure the index is set correctly
    gdf1 = gdf1.set_index(index_col)
    gdf2 = gdf2.set_index(index_col)

    # Check if event_id exists in both datasets
    if event_id not in gdf1.index or event_id not in gdf2.index:
        return {"Event": event_id, "Status": "Missing in one dataset"}

    # Extract event geometries
    g1 = gdf1.loc[event_id].geometry
    g2 = gdf2.loc[event_id].geometry

    # Ensure valid geometries (handle multiple regions)
    total_area_g1 = g1.unary_union.area if isinstance(g1, gpd.GeoSeries) else g1.area
    total_area_g2 = g2.unary_union.area if isinstance(g2, gpd.GeoSeries) else g2.area

    # Check if geometries are missing or empty
    if np.isnan(total_area_g1) or total_area_g1 == 0:
        total_area_g1 = 0
    if np.isnan(total_area_g2) or total_area_g2 == 0:
        total_area_g2 = 0

    # Compute absolute and relative differences
    area_difference = abs(total_area_g1 - total_area_g2)
    max_area = max(total_area_g1, total_area_g2)
    mismatch_ratio = area_difference / max_area if max_area > 0 else 0

    # Calculate mismatch percentage
    mismatch_percentage = mismatch_ratio * 100  # Convert ratio to percentage

    # Check if difference exceeds threshold
    mismatch_flag = mismatch_ratio > threshold

    # Return comparison results
    return {
        "Event": event_id,
        "Total Area GeoD": np.round(total_area_g1, decimals=3),
        "Total Area GDIS": np.round(total_area_g2, decimals=3),
        "Area Difference": np.round(area_difference, decimals=3),
        "Mismatch Ratio": (
            np.round(mismatch_ratio, decimals=3) if not np.isnan(mismatch_ratio) else 0
        ),
        "Mismatch Percentage": (
            round(mismatch_percentage, 2) if not np.isnan(mismatch_percentage) else 0
        ),
        "Mismatch > 10%": mismatch_flag,
    }


import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import geopandas as gpd
from shapely.ops import unary_union
import matplotlib.patches as mpatches  # ✅ Import for custom legend


def plot_multiple_events_to_pdf(
    event_ids,
    gdf1,
    gdf2,
    index_col,
    comparison_df=None,
    output_pdf="../figures/" + "event_plots.pdf",
    plots_per_page=4,
):
    """
    Plots multiple events and saves them as a multi-page PDF with page numbers.

    Parameters:
    - event_ids (list): List of event IDs to plot.
    - gdf1 (GeoDataFrame): First dataset.
    - gdf2 (GeoDataFrame): Second dataset.
    - index_col (str): Column name used as a common index for events.
    - comparison_df (DataFrame, optional): DataFrame containing additional information to annotate.
    - output_pdf (str): Name of the output PDF file.
    - plots_per_page (int): Number of plots per page (default: 4).
    """

    grid_size = int(plots_per_page**0.5)  # Square layout (e.g., 2x2 for 4 per page)
    if grid_size * grid_size < plots_per_page:
        grid_size += 1

    fig_size = (12, 12)  # Fixed page size
    total_pages = (
        len(event_ids) + plots_per_page - 1
    ) // plots_per_page  # Calculate total pages

    with PdfPages(output_pdf) as pdf:
        for page_num, i in enumerate(range(0, len(event_ids), plots_per_page), start=1):
            batch_ids = event_ids[i : i + plots_per_page]
            fig, axes = plt.subplots(grid_size, grid_size, figsize=fig_size)
            axes = axes.flatten()

            for j, event_id in enumerate(batch_ids):
                print(f"📌 Plotting event: {event_id}")
                plot_single_event_debug(
                    event_id,
                    gdf1,
                    gdf2,
                    index_col,
                    comparison_df=comparison_df,
                    ax=axes[j],
                )

            # Hide unused subplots
            for k in range(len(batch_ids), len(axes)):
                axes[k].axis("off")

            # ✅ Add page number to the bottom right corner
            fig.text(
                0.9,
                0.02,
                f"Page {page_num} of {total_pages}",
                fontsize=10,
                color="gray",
            )

            # Save the figure into the PDF
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    print(f"✅ PDF saved as {output_pdf}")


def plot_single_event_debug(
    event_id, gdf1, gdf2, index_col, comparison_df=None, ax=None
):
    """
    Plots a single event from two GeoDataFrames with annotations and legend.

    Parameters:
    - event_id (str/int): The event to plot.
    - gdf1 (GeoDataFrame): First dataset.
    - gdf2 (GeoDataFrame): Second dataset.
    - index_col (str): The column name used as a common index.
    - comparison_df (DataFrame, optional): DataFrame for annotations.
    - ax (matplotlib.axes.Axes, optional): Axis to plot on.
    """

    # Ensure index is set
    gdf1 = gdf1.set_index(index_col)
    gdf2 = gdf2.set_index(index_col)

    # Check if event exists
    exists_in_gdf1 = event_id in gdf1.index
    exists_in_gdf2 = event_id in gdf2.index

    if not exists_in_gdf1 and not exists_in_gdf2:
        print(f"⚠️ Event {event_id} not found in either dataset.")
        return

    # Extract event geometries (handling multiple rows)
    g1 = gdf1.loc[event_id, "geometry"] if exists_in_gdf1 else None
    g2 = gdf2.loc[event_id, "geometry"] if exists_in_gdf2 else None

    # Merge multiple geometries into a single MultiPolygon
    if exists_in_gdf1 and isinstance(g1, gpd.GeoSeries):
        g1 = unary_union(g1)
    if exists_in_gdf2 and isinstance(g2, gpd.GeoSeries):
        g2 = unary_union(g2)

    # Fix invalid geometries
    if g1 is not None and not g1.is_valid:
        g1 = g1.buffer(0)
    if g2 is not None and not g2.is_valid:
        g2 = g2.buffer(0)

    # Ensure CRS consistency
    if g1 is not None and g2 is not None and gdf1.crs != gdf2.crs:
        g2 = g2.to_crs(gdf1.crs)

    # Use the provided axis (`ax`) instead of creating a new figure
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    # Plot gdf1 (Blue)
    has_g1 = g1 is not None and not g1.is_empty
    if has_g1:
        gpd.GeoSeries([g1]).plot(
            ax=ax, color="none", alpha=0.5, linewidth=4, edgecolor="blue"
        )

    # Plot gdf2 (Red)
    has_g2 = g2 is not None and not g2.is_empty
    if has_g2:
        gpd.GeoSeries([g2]).plot(
            ax=ax, color="none", alpha=0.5, linewidth=4, edgecolor="red"
        )

    # Set title
    ax.set_title(f"Event {event_id}")

    # ✅ Manually create a legend
    legend_handles = []
    if has_g1:
        legend_handles.append(
            mpatches.Patch(color="blue", alpha=0.5, label="Geo-Disasters")
        )
    if has_g2:
        legend_handles.append(mpatches.Patch(color="red", alpha=0.5, label="GDIS"))

    if legend_handles:
        ax.legend(handles=legend_handles, loc="upper right")

    # ✅ Add annotation from `comparison_df`
    if comparison_df is not None and event_id in comparison_df.index:
        event_info = comparison_df.loc[event_id]
        if isinstance(event_info, pd.DataFrame):
            event_info = event_info.iloc[0]

        annotation_text = "\n".join(
            [f"{col}: {event_info[col]}" for col in comparison_df.columns]
        )
        ax.annotate(
            annotation_text,
            xy=(0.65, -0.1),
            xycoords="axes fraction",
            fontsize=8,
            bbox=dict(
                boxstyle="round,pad=0.3", edgecolor="black", facecolor="lightyellow"
            ),
        )

    # Ensure aspect ratio
    ax.set_aspect("equal", adjustable="datalim")

    # If this is a standalone plot, show it
    if ax is None:
        plt.show()
