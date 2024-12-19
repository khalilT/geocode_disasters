import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from utils.paths import get_path  # Import the get_path function from paths.py
from utils.functions import a
from utils.functions import print_smthg



import pandas as pd

def main():

    print(a)
    print_smthg()

    # Retrieve the paths to data
    emdat_data_path = get_path("emdat_path")
    print(f"EM-DAT Data Path: {emdat_data_path}")

    # Example: Load data using pandas
    if os.path.exists(emdat_data_path):
        df = pd.read_excel(emdat_data_path)
        print(df.head())
    else:
        print(f"File not found at {disaster_data_path}")

if __name__ == "__main__":
    main()
