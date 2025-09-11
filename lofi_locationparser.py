import pandas as pd
import reverse_geocoder as rg

def run_geocoding():
    print("Loading data...")
    try:
        df = pd.read_json('data/yelp_academic_dataset_restaurants.json', lines=True)
        df_cleaned = df.dropna(subset=['latitude', 'longitude']).copy()
        print(f"Data loaded. Processing all {len(df_cleaned)} businesses offline.")

        # Prepare coordinates in the format the library needs
        coords = list(zip(df_cleaned['latitude'], df_cleaned['longitude']))

        print("Performing offline reverse geocoding...")
        # This is the main function that uses multiprocessing
        results = rg.search(coords)
        print("Processing complete.")

        # Convert the list of dictionary results into a DataFrame
        df_results = pd.DataFrame(results)
        df_results = df_results.drop('name', axis=1)

        # Add the results back to your original DataFrame
        df_cleaned.reset_index(drop=True, inplace=True)
        df_final = pd.concat([df_cleaned, df_results], axis=1)
        
        # --- Display the Result ---
        print("\n--- Offline Geocoding Complete ---")
        print(df_final[[
            'name',
            'city', # From the geocoder
            'state', # From the geocoder
            'lat', # From the geocoder
            'lon'  # From the geocoder
        ]].head())
        
        # save the result
        output_filename = 'geocoded_restaurants_offline_all.json'
        df_final.to_json(output_filename, orient='records', lines=True)
        print(f"\nSuccessfully saved the data to '{output_filename}'")

    except FileNotFoundError:
        print("Error: 'yelp_academic_dataset_restaurants.json' not found.")
        

if __name__ == '__main__':
    run_geocoding()