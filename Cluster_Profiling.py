import pandas as pd
import os
import numpy as np



# Set the working directory
os.chdir('C:/Users/Daniel Loh/Documents/NUS-ISS_EBAC/BAP/BAP Practice Module Project/Final_Project_Data/Original')

# Confirm the change
print("Current working directory:", os.getcwd())


# Load the CSV file
df = pd.read_csv('final_business_clusters_13.csv')

# Preview the first few rows
print(df.head())

# Get all category columns
category_cols = [col for col in df.columns if col.startswith('categories_')]

# Group by cluster and sum category flags
cluster_profiles = df.groupby('cluster')[category_cols].sum()

# Find the top category per cluster
top_categories = cluster_profiles.idxmax(axis=1)
top_counts = cluster_profiles.max(axis=1)

# Combine into a summary DataFrame
summary = pd.DataFrame({
    'Top_Category': top_categories,
    'Top_Count': top_counts
})

print(summary)


# Calculate proportion of 1s per category per cluster
composition = df.groupby('cluster')[category_cols].mean()

# Optional: round for readability
composition = composition.round(3)

# View or export
composition.to_csv('cluster_category_composition.csv')

# -------------------------------------------------------------------------------------------

# Get all category columns
category_cols = [col for col in df.columns if col.startswith('categories_')]

# Sum category flags per cluster
cluster_profiles = df.groupby('cluster')[category_cols].sum()

# Get top category per cluster
top_categories = cluster_profiles.idxmax(axis=1)
top_counts = cluster_profiles.max(axis=1)

# Create summary DataFrame
summary = pd.DataFrame({
    'Cluster': cluster_profiles.index,
    'Top_Category': top_categories.values,
    'Count': top_counts.values
})


# import seaborn as sns
# import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))
# sns.barplot(data=summary, x='Cluster', y='Count', hue='Top_Category', dodge=False)
# plt.title("Top Category per Cluster")
# plt.xlabel("Cluster")
# plt.ylabel("Number of Businesses")
# plt.xticks(rotation=0)
# plt.legend(title='Top Category', bbox_to_anchor=(1.05, 1), loc='upper left')
# plt.tight_layout()
# plt.show()


import pandas as pd
import matplotlib.pyplot as plt

# Identify category columns
category_cols = [col for col in df.columns if col.startswith('categories_')]

# Group by cluster and sum category flags
cluster_profiles = df.groupby('cluster')[category_cols].sum()


# Set up the plot grid
fig, axes = plt.subplots(nrows=4, ncols=4, figsize=(18, 16))
axes = axes.flatten()

# Loop through each cluster
for i, ax in zip(cluster_profiles.index, axes):
    top10 = cluster_profiles.loc[i].sort_values(ascending=False).head(10)
    ax.barh(top10.index, top10.values, color='skyblue')
    ax.set_title(f'Cluster {i} - Top 10 Categories')
    ax.invert_yaxis()
    ax.set_xlabel('Business Count')

# Remove unused axes
for j in range(len(cluster_profiles), len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()



