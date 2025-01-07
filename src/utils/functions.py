#module containing functions

#functions for cleaning location names to be used in script 1

import re

def split_and_clean_locations(location):
    # Define the pattern to identify "Level 1" and its surroundings
    pattern = re.compile(r'^(.*?)(Level 1\s*(.*))$', re.IGNORECASE)
    
    match = pattern.match(location)
    if match:
        before_level_1 = match.group(1).strip()
        after_level_1 = match.group(3).strip()
        # Format the output with "Level 1" part in brackets
        cleaned_entries = [f"{before_level_1} ({after_level_1})"]
    else:
        # Proceed with the original split logic if "Level 1" is not found
        entries = re.split(r';', location)
        cleaned_entries = []
        for entry in entries:
            if '(' in entry and ')' in entry:
                cleaned_entries.append(entry.strip())
            else:
                sub_entries = re.split(r',\s*(?![^()]*\))', entry)
                cleaned_entries.extend([sub_entry.strip() for sub_entry in sub_entries if sub_entry.strip()])
    
    return cleaned_entries
    
def split_text(text):
    if text.count('(') > 1:
        return re.split(r',\s*(?=\S)', re.sub(r'\),\s*(?=\S)', '),\n', text))
    return re.split(r'\),\s*(?=\S)', text)

def extract_locations(row):
    locations = []
    if '(' in row:
        parts = row.split('(')
        locs = parts[0].strip().split(',')
        regions = parts[1].replace(')', '').split(',')
        for loc in locs:
            for sub_loc in loc.strip().split('/'):
                for region in regions:
                    locations.append([sub_loc.strip(), region.strip()])
    elif ',' in row:
        for loc in row.split(','):
            locations.append([loc.strip(), None])
    else:
        for loc in row.strip().split('/'):
            locations.append([loc.strip(), None])
    return locations

# This function checks if the input is a string and if it ends with a comma.
# If so, it removes the trailing comma and returns the modified string.
# Otherwise, it returns the original string as is.|

def remove_str_if_last(s):
    if isinstance(s, str) and s.endswith(','):
        return s[:-1]
    return s