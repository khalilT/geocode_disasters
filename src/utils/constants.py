#module containing constants

#Constants to be used to correct location & region names in script 1

#Cleaning region names in specific countries
#manual corrections needs to be applied to the names of the regions as reported in EM-DAT in 5 countries:
# 1) Burkina Faso, 2) Haiti, 3) Chad, 4) The philippines, and 5) The United States of America

rep_burkina = {
'west central': 'centre-ouest',
'north central': 'centre-nord',
'north loroum': 'loroum',
'west tuy': 'tuy',
'sector 12': 'ouagadougou',
'sect 30': 'ouagadougou',
'arr. 10': 'ouagadougou',
'arr. 4': 'ouagadougou',
'arr. 7': 'ouagadougou',
'arr.8': 'ouagadougou',
'arr.3': 'ouagadougou',
'centrall': 'centre',
'north': 'nord',
'west': 'centre-ouest',
'east': 'est'
}

rep_haiti = {
'north east': 'nord est',
'north-east': 'nord est',
'north west': 'nord ouest',
'north-west': 'nord ouest',
'northwest': 'nord ouest',
'north':'nord',
'south west': 'sud ouest',
'south-west': 'sud ouest',
'south east': 'sud est',
'south': 'sud'}

rep_chad = {
"n'djamena region": 'ndjamena',
"near n'djamena": 'ndjamena',
"n'djam centre": 'ndjamena',
"n'djam est": 'ndjamena',
"n'djam sud": 'ndjamena',
"n'djamena": 'ndjamena',
}

rep_philippines = {
'Region XIII': 'Caraga',
'Region XII': 'Soccsksargen',
'Region XI': 'Davao Region',
'Region X': 'Northern Mindanao',
'Region IX': 'Zamboanga Peninsula',
'Region VIII': 'Eastern Visayas',
'Region VII': 'Central Visayas',
'Region VI': 'Western Visayas',
'Region V': 'Bicol region',
'Region IV-A': 'Calabarzon',
'Region IV': 'Southern Tagalog',
'Region III': 'Central Luzon',
'Region II': 'Cagayan Valley',
'Region I': 'Ilocos region',

'XIII': 'Caraga',
'XII': 'Soccsksargen',
'XI': 'Davao Region',
'X': 'Northern Mindanao',
'IX': 'Zamboanga Peninsula',
'VIII': 'Eastern Visayas',
'VII': 'Central Visayas',
'VI': 'Western Visayas',
'V': 'Bicol region',
'IV-A': 'Calabarzon',
'IV': 'Southern Tagalog',
'III': 'Central Luzon',
'II': 'Cagayan Valley',
'I': 'Ilocos region',

'12': 'Soccsksargen',
'11': 'Davao Region',
'10': 'Northern Mindanao',
'9': 'Zamboanga Peninsula',
'8': 'Eastern Visayas',
'7': 'Central Visayas',
'6': 'Western Visayas',
'5': 'Bicol region',
'4': 'Southern Tagalog',
'3': 'Central Luzon',
'2': 'Cagayan Valley',
'1': 'Ilocos region'
}

rep_us_states = {
    "al": "alabama",  "ak": "alaska",   "az": "arizona",   "ar": "arkansas",   "ca": "california",    "co": "colorado",   "ct": "connecticut",
    "de": "delaware",    "fl": "florida",    "ga": "georgia",    "hi": "hawaii",    "id": "idaho",    "il": "illinois",    "in": "indiana",
    "ia": "iowa",    "ks": "kansas",    "ky": "kentucky",    "la": "louisiana",    "me": "maine",    "md": "maryland",    "ma": "massachusetts",
    "mi": "michigan",    "mn": "minnesota",    "ms": "mississippi",    "mo": "missouri",    "mt": "montana",    "ne": "nebraska",    "nv": "nevada",
    "nh": "new hampshire",    "nj": "new jersey",    "nm": "new mexico",    "ny": "new york",    "nc": "north carolina",    "nd": "north dakota",
    "oh": "ohio",    "ok": "oklahoma",    "or": "oregon",    "pa": "pennsylvania",    "ri": "rhode island",    "sc": "south carolina",    "sd": "south dakota",
    "tn": "tennessee",    "tx": "texas",    "ut": "utah",    "vt": "vermont",    "va": "virginia",    "wa": "washington",    "wv": "west virginia",
    "wi": "wisconsin",    "wy": "wyoming"
}

replace_terms = ["Near", "Between","Provinces", "Province","Prov.","Districts","District","Dis.","Div.","Regions" ,"Region", "states","state",
                 "(cities)","(City)","cities","City", "Regency", "districts", "county","Departments", "Department","municipalities", "Municipality",
                 "=","Level 2","-","N.A. on the source", "islands", "island", "of the"," isl.(archip.)"," isl.", "area", " in"]


#Constants to be used to correct location & region names in script 2
replace_phl = {'Region XIII': '',
'Region XII': '',
'Region XI': '',
'Region X': '',
'Region IX': '',
'Region VIII': '',
'Region VII': '',
'Region VI': '',
'Region V': '',
'Region IV-A': '',
'Region IV': '',
'Region III': '',
'Region II': '',
'Region I': '',
'\(':'',
'\)':''}