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

#Need to run the script twice:
# First time with all locations that don't have the GAUL ID number
# Second time with all locations that needed manual correction
