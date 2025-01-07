### (c) Khalil Teber 2025 ###
### Code file for PAPER "Geocoding climate-related disaster events"

#This script processes the locations geocoded with Geonames and identified latitudes and longitudes in each case with GAUL administrative regions at both levels (ADM1 and ADM2). We use a fuzzy string matching of the location and province names (Geonames) to identify the adequate administrative level.
#The script consolidates, cleans, and corrects location data, including manual adjustments and proximity-based matching to administrative units. 
#We assign geocoding quality flags to the geocoded regions.
#Quality flags:
### 1: highest quality: locations identified with GAUl ID provided by EM-DAT
### 2: high quality: location identified with Geonames that has a name match with GAUL region
### 3: low quality: location identified with match of province name from Geonames and GAUL region name
### 4: lowest quality: location identied with geonames only


import pandas as pd
import geopandas as gpd
import numpy as np
import re
import glob
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from utils.paths import get_path  # Import the get_path function from paths.py
import utils.constants as constants
import utils.functions as functions

# 1 Load and Merge Location Data
######################################
#add the paths to the folder containing the identified locations without and with manual correction
identified_locations_path = get_path("identified_locations_path")
corrected_locations_path = get_path("corrected_locations_path")

all_files = glob.glob(os.path.join(identified_locations_path + "*.csv"))
all_files.sort(key=lambda x: int(x.split('q')[-1].split('.')[0]))
df_locations = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=False)
df_locations_complete = df_locations[~np.isnan(df_locations.Longitude)]
df_locations_complete = df_locations_complete.drop_duplicates(keep='first')

all_files_corrected = glob.glob(os.path.join(corrected_locations_path+"*.csv"))
df_locations_corrected = pd.concat((pd.read_csv(f) for f in all_files_corrected), ignore_index=False).reset_index().drop(columns={"Unnamed: 0","index"})
df_locations_corrected_complete = df_locations_corrected[~np.isnan(df_locations_corrected.Longitude)]
df_locations_corrected_complete = df_locations_corrected_complete.drop_duplicates(keep='first')

df_locations_geonames = pd.concat([df_locations_complete, df_locations_corrected_complete])
df_locations_geonames = df_locations_geonames.rename(columns = {"EM-DAT-Location":"Location"})

#get iso codes
df_locations_path = get_path("df_locations_path")
df_corrected_path = get_path("df_locations_corrected_path")

df_locations = pd.read_csv(df_locations_path)
df_corrected = pd.read_csv(df_corrected_path)
df_locations_filtered = df_locations[~df_locations['DisNo.'].isin(df_corrected['DisNo.'])]
locations = pd.concat([df_locations_filtered, df_corrected]).reset_index().drop(columns={"Unnamed: 0","index"})

disaster_code_iso = locations.drop(columns="Location")
disaster_code_iso = disaster_code_iso.drop_duplicates(keep='first')

df_locations_geonames_iso = pd.merge(df_locations_geonames, disaster_code_iso, on=['DisNo.'], how='left', indicator=True)
df_locations_geonames_iso = df_locations_geonames_iso.drop_duplicates(keep='first')

#2 Manual Corrections for Specific Events
########################
#manual corrections

df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1991-0218-USA") & (df_locations_geonames_iso["Location"] == "rhode"),"Location"] = "Rhode Island"
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1991-0218-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Longitude"] = -71.49978
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1991-0218-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Latitude"] = 41.75038

df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1991-0543-USA") & (df_locations_geonames_iso["Location"] == "rhode"),"Location"] = "Rhode Island"
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1991-0543-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Longitude"] = -71.49978
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1991-0543-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Latitude"] = 41.75038

df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1992-0268-USA") & (df_locations_geonames_iso["Location"] == "rhode"),"Location"] = "Rhode Island"
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1992-0268-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Longitude"] = -71.49978
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1992-0268-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Latitude"] = 41.75038

df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1993-0424-USA") & (df_locations_geonames_iso["Location"] == "rhode"),"Location"] = "Rhode Island"
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1993-0424-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Longitude"] = -71.49978
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1993-0424-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Latitude"] = 41.75038

df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1996-0247-USA") & (df_locations_geonames_iso["Location"] == "rhode"),"Location"] = "Rhode Island"
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1996-0247-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Longitude"] = -71.49978
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1996-0247-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Latitude"] = 41.75038

df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1997-0040-USA") & (df_locations_geonames_iso["Location"] == "rhode"),"Location"] = "Rhode Island"
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1997-0040-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Longitude"] = -71.49978
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1997-0040-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Latitude"] = 41.75038

df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1999-0005-USA") & (df_locations_geonames_iso["Location"] == "rhode"),"Location"] = "Rhode Island"
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1999-0005-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Longitude"] = -71.49978
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1999-0005-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Latitude"] = 41.75038

df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1999-0327-USA") & (df_locations_geonames_iso["Location"] == "rhode"),"Location"] = "Rhode Island"
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1999-0327-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Longitude"] = -71.49978
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1999-0327-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Latitude"] = 41.75038

df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "2002-0858-USA") & (df_locations_geonames_iso["Location"] == "rhode"),"Location"] = "Rhode Island"
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "2002-0858-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Longitude"] = -71.49978
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "2002-0858-USA") & (df_locations_geonames_iso["Location"] == "Rhode Island"),"Latitude"] = 41.75038

df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1991-0492-USA") & (df_locations_geonames_iso["Location"] == "north"),"Location"] = "North Carolina"
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1991-0492-USA") & (df_locations_geonames_iso["Location"] == "North Carolina"),"Longitude"] = -80.00032
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1991-0492-USA") & (df_locations_geonames_iso["Location"] == "North Carolina"),"Latitude"] = 35.50069

df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1991-0502-USA") & (df_locations_geonames_iso["Location"] == "north"),"Location"] = "North Carolina"
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1991-0502-USA") & (df_locations_geonames_iso["Location"] == "North Carolina"),"Longitude"] = -80.00032
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1991-0502-USA") & (df_locations_geonames_iso["Location"] == "North Carolina"),"Latitude"] = 35.50069

df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1994-0023-USA") & (df_locations_geonames_iso["Location"] == "north"),"Location"] = "North Carolina"
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1994-0023-USA") & (df_locations_geonames_iso["Location"] == "North Carolina"),"Longitude"] = -80.00032
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1994-0023-USA") & (df_locations_geonames_iso["Location"] == "North Carolina"),"Latitude"] = 35.50069

df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1999-0005-USA") & (df_locations_geonames_iso["Location"] == "south"),"Location"] = "South Carolina"
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1999-0005-USA") & (df_locations_geonames_iso["Location"] == "South Carolina"),"Longitude"] = -81.00009
df_locations_geonames_iso.loc[(df_locations_geonames_iso["DisNo."] == "1999-0005-USA") & (df_locations_geonames_iso["Location"] == "South Carolina"),"Latitude"] = 34.00043

#### 3 Matching with gaul locations
########################

#load gaul data
gaul1 = gpd.read_file(get_path("gaul1_path"))
gaul2 = gpd.read_file(get_path("gaul2_path"))

#find intersections of geonames identified locations with
#gaul 1 and gaul2 geometries

result_gaul1 = []

for i in np.arange(len(df_locations_geonames_iso)):
    try:
        print(i)
        result_gaul1.append(functions.find_containing_geometry(gaul1, df_locations_geonames_iso.iloc[i].Longitude,
                                                    df_locations_geonames_iso.iloc[i].Latitude).ADM1_CODE.values[0])
    except Exception as e:
        print(f"Error at index {i}: {e}")
        result_gaul1.append("No match") 


result_gaul2 = []

for i in np.arange(len(df_locations_geonames_iso)):
    try:
        print(i)
        result_gaul2.append(functions.find_containing_geometry(gaul2, df_locations_geonames_iso.iloc[i].Longitude,
                                                    df_locations_geonames_iso.iloc[i].Latitude).ADM2_CODE.values[0])
    except Exception as e:
        print(f"Error at index {i}: {e}")
        result_gaul2.append("No match")

df_locations_geonames_iso["ADM1_CODE"] = result_gaul1
df_locations_geonames_iso["ADM2_CODE"] = result_gaul2

#extract corresponding region names and codes from GAUL 
df_locations_geonames_iso = df_locations_geonames_iso[~(df_locations_geonames_iso["ADM1_CODE"] == "No match")]

gaul1_codename = gaul1[["ADM1_CODE","ADM1_NAME"]]
gaul2_codename = gaul2[["ADM2_CODE","ADM2_NAME"]]


#match locations with gaul 1
df_locations_geonames_iso = df_locations_geonames_iso.set_index("ADM1_CODE")
gaul1_codename = gaul1_codename.set_index("ADM1_CODE")
df_locations_geonames_iso = df_locations_geonames_iso.join(gaul1_codename)
df_locations_geonames_iso = df_locations_geonames_iso.reset_index()

#match locations with gaul 2
df_locations_geonames_iso = df_locations_geonames_iso.set_index("ADM2_CODE")
gaul2_codename = gaul2_codename.set_index("ADM2_CODE")
df_locations_geonames_iso = df_locations_geonames_iso.join(gaul2_codename)
df_locations_geonames_iso = df_locations_geonames_iso.reset_index()

#remove duplicates
df_locations_geonames_iso = df_locations_geonames_iso.drop_duplicates(keep='first')

#Remove redundancies from Philippines region names

df_locations_geonames_iso.loc[df_locations_geonames_iso.ISO == "PHL"] = df_locations_geonames_iso.loc[df_locations_geonames_iso.ISO == "PHL"].replace(constants.replace_phl, regex=True)
df_locations_geonames_iso = df_locations_geonames_iso.sort_values("DisNo.")

#remove no matches entries
df_locations_geonames_iso = df_locations_geonames_iso[~(df_locations_geonames_iso.ADM2_CODE == "No match") | ~(df_locations_geonames_iso.ADM1_CODE == "No match")]

#### find names proximity to identify if locations are admin 1 or admin 2 level

# Apply the function to each row
df_locations_geonames_iso['similarity_ADM1'] = df_locations_geonames_iso.apply(functions.calculate_similarity_ADM1,axis=1)
# Apply the function to each row
df_locations_geonames_iso['similarity_ADM2'] = df_locations_geonames_iso.apply(functions.calculate_similarity_ADM2, axis=1)

#admin 1 regions
name_detected_adm1 = df_locations_geonames_iso[(df_locations_geonames_iso.similarity_ADM1 >= 50) & (df_locations_geonames_iso.similarity_ADM1 > df_locations_geonames_iso.similarity_ADM2)]

#admin 2 regions
name_detected_adm2 = df_locations_geonames_iso[(df_locations_geonames_iso.similarity_ADM2 >= 50) & (df_locations_geonames_iso.similarity_ADM2 > df_locations_geonames_iso.similarity_ADM1)]

#regions that can't be identified
no_match_names = df_locations_geonames_iso[(df_locations_geonames_iso.similarity_ADM1 <= 50) & (df_locations_geonames_iso.similarity_ADM2 <= 50)]

no_match_names_no_adm1 = no_match_names[(no_match_names["ADM1_NAME"] == "Administrative unit not available")]
no_match_names = no_match_names.drop(no_match_names_no_adm1.index)

# Apply the function to each row
no_match_names['similarity_geonames'] = no_match_names.apply(functions.calculate_similarity_geonames, axis=1)
admin2_geonames = no_match_names[(no_match_names["similarity_geonames"] >= 60) & (no_match_names["similarity_ADM1"] > 41)]
no_match_names = no_match_names.drop(admin2_geonames.index)

### identify locations in the right province / adm1
no_match_names.Province = no_match_names.Province.astype(str)
no_match_names = no_match_names.reset_index()

#find locations matching by provinces (ADM1)

no_match_province_df = no_match_names.apply(functions.find_match_province_adm1, axis=1)
dfprovince_list = []

for dfi in no_match_province_df:
    if not dfi.empty:
        dfprovince_list.append(dfi)

name_located_province = pd.concat(dfprovince_list)
no_match_names_matching_adm1 = no_match_names.set_index("index").loc[name_located_province["index"]]
no_match_names_matching_adm1 = no_match_names_matching_adm1.drop([416, 6869, 7666, 7199, 6873, 6935, 8038, 7667,7668,7669,417])

#remove identified adm1 locations
no_match_names_NOTmatching_adm1 = no_match_names.set_index("index").drop(no_match_names_matching_adm1.index).reset_index()

#find locations where the name is mentiond in the Admin name but can't be matched
regionnames_adm1_df = no_match_names_NOTmatching_adm1.apply(functions.find_regionname_adm1, axis=1)

regionnames_adm1_df_list = []

for dfi in regionnames_adm1_df:
    if not dfi.empty:
        regionnames_adm1_df_list.append(dfi)

regionnames_adm1_match_df = pd.concat(regionnames_adm1_df_list)
no_match_names_matching_adm1_b = no_match_names_NOTmatching_adm1.set_index("index").loc[regionnames_adm1_match_df["index"]].reset_index()

#remove selected regions
no_match_names_NOTmatching_adm1 = no_match_names_NOTmatching_adm1.set_index("index").drop(no_match_names_matching_adm1_b["index"]).reset_index()

#find name matches for regions level 1
admin1_name_matched_gaul = functions.find_retun_adm1_matches(no_match_names_NOTmatching_adm1)
admin2_name_matched_gaul = functions.find_retun_adm2_matches(no_match_names_NOTmatching_adm1)

admin1_name_matched_gaul = admin1_name_matched_gaul[admin1_name_matched_gaul["index"] != set(admin2_name_matched_gaul["index"]).intersection(admin1_name_matched_gaul["index"])]

no_match_names_NOTmatching_adm1 = no_match_names_NOTmatching_adm1.set_index("index").drop(admin1_name_matched_gaul["index"]).reset_index()
no_match_names_NOTmatching_adm1 = no_match_names_NOTmatching_adm1.set_index("index").drop(admin2_name_matched_gaul["index"]).reset_index()
