import os
import json
import pandas as pd
import numpy as np
import kmodes



# Set the working directory
os.chdir('C:/Users/Daniel Loh/Documents/NUS-ISS_EBAC/BAP/BAP Practice Module Project/Final_Project_Data/Original')

# Confirm the change
print("Current working directory:", os.getcwd())


# Open and load the JSON file
with open('yelp_food_business_flat.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Now 'data' is a Python dictionary (or list, depending on the JSON structure)
# print(data)


# Convert to DataFrame and drop all columns except 'business_id', 'name', and 'categories'
df = pd.DataFrame(data)
print(df.head(10))
print(df.columns)
df = df[['business_id', 'categories']]
print(df.columns)

# Flattening the categories column------------------------------------

# Split the 'categories' string into lists
df['categories'] = df['categories'].fillna('').apply(lambda x: [cat.strip() for cat in x.split(',') if cat.strip()])


# Use MultiLabelBinarizer to one-hot encode
from sklearn.preprocessing import MultiLabelBinarizer


mlb = MultiLabelBinarizer()
categories_encoded = pd.DataFrame(mlb.fit_transform(df['categories']), columns=[f"categories_{c}" for c in mlb.classes_])



# Combine with original DataFrame
df = pd.concat([df.drop(columns=['categories']), categories_encoded], axis=1)

# Or specify how many rows you want
print(df.head(10))

print("done")



# Checking for rare categories ------------------------------------



# Select only category columns (assuming they start with 'categories_')
category_cols = [col for col in df.columns if col.startswith('categories_')]


category_counts = df[category_cols].sum().sort_values()


# Display the least common categories first
print(category_counts)


# Filter for rare categories (less than 10 businesses)
rare_categories = category_counts[category_counts < 10]

# Display the result
print(f"Number of rare categories: {len(rare_categories)}")
print(rare_categories.sort_values())


# # Find columns where the sum is 0 (i.e., all values are 0)
# zero_columns = [col for col in category_cols if df[col].sum() == 0]



# # View or print the result
# print(f"Number of unused category columns: {len(zero_columns)}")
# print

# df.drop(columns=zero_columns, inplace=True)


# # Clustering ------------------------------------

category_cols = [col for col in df.columns if col.startswith('categories_')]
X = df[category_cols]



from kmodes.kmodes import KModes
km = KModes(n_clusters=9, init='Huang', n_init=5, verbose=1)
clusters = km.fit_predict(X)
df['cluster'] = clusters


print(df['cluster'].value_counts())
print(df.head(10))


df.to_csv('final_business_clusters_9.csv', index=False)
df.to_json('final_business_clusters_9.json', orient='records', lines=True)
print('done clustering')


# # Check clustering performanc with Jaccard Similarity ------------------------------------

# from sklearn.metrics import pairwise_distances


# def jaccard_similarity(set1, set2):
#     intersection = len(set1.intersection(set2))
#     union = len(set1.union(set2))
#     return intersection / union

# # Only use binary columns (e.g., categories)
# category_cols = [col for col in df.columns if col.startswith('categories_')]
# binary_matrix = df[category_cols].to_numpy()

# # Compute pairwise Jaccard similarity
# jaccard_sim = 1 - pairwise_distances(binary_matrix, metric='jaccard')


# # Trying to check performance using Dunn Index ------------------------------------

# def dunn_index(X, labels):
#     unique_clusters = np.unique(labels)
#     inter_dists = []
#     intra_dists = []

#     for i in unique_clusters:
#         cluster_i = X[labels == i]
#         intra = pairwise_distances(cluster_i)
#         intra_dists.append(np.max(intra))  # max intra-cluster distance

#         for j in unique_clusters:
#             if i >= j:
#                 continue
#             cluster_j = X[labels == j]
#             inter = pairwise_distances(cluster_i, cluster_j)
#             inter_dists.append(np.min(inter))  # min inter-cluster distance

#     return np.min(inter_dists) / np.max


# # Visualizing KModes Clusters Effectiveness ------------------------------------

# import umap
# import matplotlib.pyplot as plt

# reducer = umap.UMAP(metric='jaccard', random_state=42)
# embedding = reducer.fit_transform(df[category_cols])

# plt.figure(figsize=(10, 6))
# plt.scatter(embedding[:, 0], embedding[:, 1], c=df['cluster'], cmap='tab10', s=10)
# plt.title("UMAP Projection of K-Modes Clusters")
# plt.xlabel("UMAP 1")
# plt.ylabel("UMAP 2")
# plt.colorbar(label='Cluster')
# plt.show()

# # Visualizing Category Presence by Cluster ------------------------------------

# import seaborn as sns

# cluster_profiles = df.groupby('cluster')[category_cols].mean()
# plt.figure(figsize=(15, 8))
# sns.heatmap(cluster_profiles.T, cmap='YlGnBu', linewidths=0.5)
# plt.title("Category Presence by Cluster")
# plt.xlabel("Cluster")
# plt.ylabel("Category")
# plt.show()




# # Checking the cluster centroids ------------------------------------
# for i, mode in enumerate(km.cluster_centroids_):
#     print(f"\nCluster {i} Mode Categories:")
#     print([col for col, val in zip(category_cols, mode) if val == 1])



# # Check Elbow Method for Optimal K ------------------------------------

# from kmodes.kmodes import KModes
# import matplotlib.pyplot as plt
# import numpy as np

# # Step 1: Select only category columns
# category_cols = [col for col in df.columns if col.startswith('categories_')]
# X = df[category_cols]

# # Step 2: Run Elbow Method
# costs = []
# for k in range(2, 15):
#     km = KModes(n_clusters=k, init='Huang', n_init=5, verbose=0)
#     km.fit(X)  # Use only category features
#     costs.append(km.cost_)

# # Step 3: Plot the Elbow
# plt.plot(range(2, 15), costs, marker='o')
# plt.xlabel('Number of Clusters (k)')
# plt.ylabel('Cost')
# plt.title('Elbow Method for K-Modes')
# plt.savefig("elbow_plot.png", dpi=300, bbox_inches='tight')
# plt.show()

# print("Elbow Plot done")

# # Check Silhouette Score ------------------------------------

# from sklearn.metrics import silhouette_score, pairwise_distances

# silhouette_scores = []
# for k in range(2, 15):
#     km = KModes(n_clusters=k, init='Huang', n_init=5, verbose=0)
#     labels = km.fit_predict(df)
#     dist_matrix = pairwise_distances(df[category_cols], metric='jaccard')
#     score = silhouette_score(dist_matrix, labels, metric='precomputed')
#     silhouette_scores.append(score)


# print("silhouette_scores done")