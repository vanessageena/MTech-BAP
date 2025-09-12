
import pandas as pd
import matplotlib.pyplot as plt
import ast
import os
os.chdir('C:/Users/Daniel Loh/Documents/NUS-ISS_EBAC/BAP/BAP Practice Module Project/Final_Project_Data/Original')


# Load your CSV file
df = pd.read_csv('yelp_food_business_flat.csv')
df = df[df['cluster'] != '#NAME?']
df = df[df['cluster'] != '#VALUE!']


# Ensure output directory exists
output_dir = 'attribute_charts'
os.makedirs(output_dir, exist_ok=True)

# Identify attribute columns
attribute_cols = [col for col in df.columns if col.startswith('attribute')]
# attribute_cols = [col for col in df.columns if col.startswith('temp_attributes')]


# Expand nested dictionaries into separate columns
expanded_cols = {}
for col in attribute_cols:
    if df[col].apply(lambda x: isinstance(x, dict)).any():
        # Expand nested dicts
        nested_df = df[col].apply(pd.Series)
        for sub_col in nested_df.columns:
            new_col_name = f"{col}_{sub_col}"
            df[new_col_name] = nested_df[sub_col]
            expanded_cols[new_col_name] = col
    else:
        expanded_cols[col] = None  # Not nested

# Get cluster column
cluster_col = 'cluster'  # Change if your cluster column has a different name

# Plot each attribute column
for attr_col in expanded_cols:
    # Group by attribute value and cluster
    count_df = df.groupby([attr_col, cluster_col]).size().unstack(fill_value=0)

    # Plot stacked bar chart
    count_df.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='tab20')
    plt.title(f'Cluster Composition by {attr_col}')
    plt.xlabel(f'{attr_col} Values')
    plt.ylabel('Number of Businesses')
    plt.legend(title='Cluster', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    # Save chart
    filename = f"{output_dir}/AttributeByCluster_{attr_col}.png"
    plt.savefig(filename)
    plt.close()

print("Attribute charts saved.")