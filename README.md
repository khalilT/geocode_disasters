# Geo-Disasters: Geocoding EM-DAT climate related disasters

This repository contains a series of Python scripts for processing and geolocating the climate-related disaster events from EM-DAT for the period 1990-2023. It uses geographic data from [GAUL administrative boundaries](https://data.apps.fao.org/map/catalog/srv/eng/catalog.search?id=12691#/metadata/9c35ba10-5649-41c8-bdfc-eb78e9e65654), and the [GeoNames API](https://www.geonames.org/).

## **Overview**

#### 1_clean_EmDAT_nogeocode.py

This script identifies the EM-DAT events for which no GAUL id was provided that need to be geocoded using Geonames API.

Inputs: EM-DAT data file (public_emdat_1990_2023.xlsx)
Outputs: Dataframe with events that need to be geocoded

#### 2_geolocation_geonames_script.py

This script is designed to geocode event locations using the GeoNames API.
Running might take a long time (3 to 4 days) as we have around 10k names to geolocate, with limits on the usage per hour and day, in addition to potential interruptions if there are too many requests on the API. The code is adapted to continue from were the operation was interrupted.
The script was run on two iterations. The first one on the list of events identified in the first script. The second one is on the events that were not identified in the first iteration (around 900 locations), after manually correcting the locations names / iso codes.

Inputs: Dataframe with locations that need to be geocoded
Outputs: Dataframe with geocoded locations: lat/lon and province names identified.

#### 3_clean_geonames_geolocation.py

This script processes the locations geocoded with Geonames and identified latitudes and longitudes in each case with GAUL administrative regions at both levels (ADM1 and ADM2). We assign geocoding quality flags to the geocoded regions.

Inputs: Dataframe with geocoded locations
Outputs: Dataframe with geocoded locations with identified corresponding GAUL admin level and code that enables matching with geographic data.

#### 4_geolocation_identified_gaul_ID.py

In this script, we identify the geometries corresponding to the locations where the GAUL id is provided with EM-DAT. we then concatenate all identified locations together (with the geonames identified locations) and apply quality flags for consistency

Inputs: Dataframe with geocoded locations with identified corresponding GAUL
Inputs: EM-DAT data file (public_emdat_1990_2023.xlsx)
Outputs: Geodaraframe with all identified locations and geographic data

#### 5_national_overlay.py

In this script, we overlay the regions corresponding to each EM-DAT event within each country, to have the total reported area of the event.

Inputs: Geodaraframe with all identified locations and geographic data
Outputs: Geodaraframe with overlayed extent per event

#### 6_prepare_data_4aggregation.py

In this script, we join essential event information from EM-DAT to the geocoded locations to prepare the aggregation of the climate variables.
Inputs: Geodaraframe with overlayed extent per event, EM-DAT database
Output: Geodaraframe with event locations, em-dat event and impact information, and needed time information for climate aggregation

### How to Run the Scripts

Ensure that the required input files (EM-DAT data, GAUL maps, location CSVs) are available in the specified directories.
Run each script in the appropriate order indicated in the names.

### Notes

The data output from these scripts is crucial for geographic analysis and visualization of climate-related disasters.
The scripts have built-in error handling for mismatched or missing locations, ensuring robust processing.
Manual corrections are necessary in many cases.
The GeoNames API script requires a valid username and should be run twice: once for locations without GAUL IDs and once for manually corrected locations.

## **Installation**

1. Clone the repository:
   ```bash
   git clone https://github.com/khalilT/geocode_disasters.git
   cd yourproject
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## **Session Info**

- **Python Version**: 3.8.19 | packaged by conda-forge | (default, Mar 20 2024, 12:47:35) 
[GCC 12.3.0]
- **Platform**: Linux-6.8.0-57-generic-x86_64-with-glibc2.10
- **OS**: Linux
- **Architecture**: 64bit
- **Processor**: x86_64
- **Generated On**: 2025-05-15 10:06:19
- **R Version**: R version 4.4.2 (2024-10-31) -- "Pile of Leaves"