import pandas as pd
from geopy.geocoders import Nominatim
from tqdm import tqdm
import time

# --- Part 1: Load and Prepare the Data ---
print("Loading data...")
try:
    df = pd.read_json('data/yelp_academic_dataset_restaurants.json', lines=True)
    df_cleaned = df.dropna(subset=['latitude', 'longitude']).copy()

    print(f"Data loaded. Processing all {len(df_cleaned)} businesses.")

except FileNotFoundError:
    print("Error: 'yelp_academic_dataset_restaurants.json' not found.")
    df_cleaned = None

# --- Part 2: Define the Reverse Geocoding Function ---
def get_address_from_coords(lat, lon, geolocator):
    try:
        location = geolocator.reverse(f"{lat}, {lon}", exactly_one=True, timeout=10)
        time.sleep(1) # Pause for 1 second to respect usage policy
        
        if location:
            raw_address = location.raw.get('address', {})
            house_number = raw_address.get('house_number', '')
            road = raw_address.get('road', '')
            city = raw_address.get('city', raw_address.get('town', ''))
            state = raw_address.get('state', '')
            zip_code = raw_address.get('postcode', '')
            street_address = f"{house_number} {road}".strip()
            return street_address, city, state, zip_code
    except Exception as e:
        return '', '', '', ''
    return '', '', '', ''

# --- Part 3: Apply the Function and Create New Columns ---
if df_cleaned is not None:
    geolocator = Nominatim(user_agent="yelp_address_parser_full")
    tqdm.pandas(desc="Reverse Geocoding Addresses")
    
    parsed_addresses = df_cleaned.progress_apply(
        lambda row: get_address_from_coords(row['latitude'], row['longitude'], geolocator),
        axis=1
    )

    df_cleaned[[
        'Building number and street address',
        'City',
        'State',
        'ZIP Code'
    ]] = pd.DataFrame(parsed_addresses.tolist(), index=df_cleaned.index)

    # --- Part 4: Save the Final Result to a JSON file ---
    output_filename = 'geocoded_restaurants_all.json'
    df_cleaned.to_json(output_filename, orient='records', lines=True)
    print(f"\n--- Geocoding Complete ---")
    print(f"Successfully saved all geocoded data to '{output_filename}'")
