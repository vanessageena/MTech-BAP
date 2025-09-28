import pandas as pd
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import tree

# Merge original flattened file with clusters file-------------------

# Set the working directory
os.chdir('C:/Users/Daniel Loh/Documents/NUS-ISS_EBAC/BAP/BAP Practice Module Project/Final_Project_Data/Original')
df1 = pd.read_csv('yelp_food_business_flat_withoutcluster.csv')
df2 = pd.read_csv('final_business_clusters_12_clusteronly.csv')

print("File 1 columns:", df1.columns.tolist())
print("File 2 columns:", df2.columns.tolist())


print("File 1 types:\n", df1.dtypes)
print("File 2 types:\n", df2.dtypes)

merged_df = pd.merge(df1, df2, on='business_id', how='inner')

print("Merged File columns:", merged_df.columns.tolist())

merged_df = merged_df[merged_df['business_id'] != '#NAME?']

# Additionally merged flattened nested attributes-------------------

from functools import reduce

folder_path = 'Flattened Nested Attributes'

files_to_merge = [
    'ambience_df.csv',
    'bestnights_df.csv',
    'goodformeal_df.csv',
    'music_df.csv',
    'parking_df.csv'
]

# Load and clean each DataFrame
nested_dfs = []
for file in files_to_merge:
    df = pd.read_csv(os.path.join(folder_path, file))
    df = df[df['business_id'] != '#NAME?']  # Remove rows with '#NAME?' in business_id
    # Drop 'cluster' column if it exists
    if 'cluster' in df.columns:
        df = df.drop(columns=['cluster'])

    nested_dfs.append(df)

# Merge with your existing merged_df
merged = merged_df.copy()
for df in nested_dfs:
    merged = pd.merge(merged, df, on='business_id', how='left')


# # Merge them into one DataFrame
# nested_merged_df = reduce(lambda left, right: pd.merge(left, right, on='business_id', how='left'), nested_dfs)
final_df = merged
final_df = final_df.loc[:, ~final_df.columns.duplicated()]
print("Final File columns:", final_df.columns.tolist())



columns_to_drop = [
    'attributes_attr_HairSpecializesIn',
    'attributes_attr_DietaryRestrictions',
    'attributes_attr_RestaurantsCounterService',
    'attributes_attr_Open24Hours',
    'attributes_attr_AgesAllowed',
    'attributes_attr_AcceptsInsurance'
]

columns_to_drop = [col for col in columns_to_drop if col in final_df.columns]
final_df = final_df.drop(columns=columns_to_drop)


nested_prefixes = {
    'ambience_df.csv': 'attributes_attr_Ambience',
    'bestnights_df.csv': 'attributes_attr_BestNights',
    'goodformeal_df.csv': 'attributes_attr_GoodForMeal',
    'music_df.csv': 'attributes_attr_Music',
    'parking_df.csv': 'attributes_attr_BusinessParking'
}

columns_to_drop = []

for prefix in nested_prefixes.values():
    matching_cols = [col for col in final_df.columns if col.startswith(prefix)]
    columns_to_drop.extend(matching_cols)

# Drop them from the DataFrame
final_df = final_df.drop(columns=columns_to_drop)

print("Final File columns after cleaning:", final_df.columns.tolist())

attribute_cols = [col for col in final_df.columns if 'attributes' in col]
print("Number of attribute columns:", len(attribute_cols))

# Checking Is NA columns-------------------

missing_cols = final_df.isna().sum()
missing_cols = missing_cols[missing_cols > 0]

print("Columns with missing values:\n", missing_cols)

#plot out missing values
missing_cols = missing_cols.sort_values(ascending=False)
plt.style.use('seaborn-v0_8')  # Optional: for nicer aesthetics

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))
missing_cols.plot(kind='bar', ax=ax, color='skyblue')

# Customize the chart
ax.set_title('Missing Values per Column', fontsize=16)
ax.set_xlabel('Column Name', fontsize=12)
ax.set_ylabel('Number of Missing Values', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Show the plot
plt.show()

attribute_cols = [col for col in final_df.columns if 'attributes' in col]


missing_ratio = final_df[attribute_cols].isna().mean().sort_values(ascending=False)
print(missing_ratio)



# # Based on Missing Ratio, to determine which additional columns to drop, impute/flag or encode

# high_missing = missing_ratio[missing_ratio > 0.9].index.tolist()
# moderate_missing = missing_ratio[(missing_ratio > 0.5) & (missing_ratio <= 0.9)].index.tolist()
# low_missing = missing_ratio[missing_ratio <= 0.5].index.tolist()


# attribute_cols = [col for col in final_df.columns if 'attributes' in col]
# print("Number of attribute columns before drop:", len(attribute_cols))

# final_df = final_df.drop(columns=high_missing)

# attribute_cols = [col for col in final_df.columns if 'attributes' in col]
# print("Number of attribute columns after drop:", len(attribute_cols))


# Instead of dropping columns with High Missing Ratio, change NA to FALSE instead, as would be more contextually correct
final_df[attribute_cols] = final_df[attribute_cols].fillna(False)


# Check Remaining NA columns-------------------


missing_cols = final_df.isna().sum()
missing_cols = missing_cols[missing_cols > 0]

print("Columns with missing values:\n", missing_cols)

#plot out missing values
missing_cols = missing_cols.sort_values(ascending=False)
plt.style.use('seaborn-v0_8')  # Optional: for nicer aesthetics

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))
missing_cols.plot(kind='bar', ax=ax, color='skyblue')

# Customize the chart
ax.set_title('Missing Values per Column', fontsize=16)
ax.set_xlabel('Column Name', fontsize=12)
ax.set_ylabel('Number of Missing Values', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Show the plot
plt.show()






# -----------------------------------------------------------------------------------------------

# # Instead of Mode and Unknown, change NA to FALSE instead, as would be more contextually correct
# for col in moderate_missing:
#     final_df[col] = final_df[col].fillna("Unknown")


# for col in low_missing:
#     final_df[col] = final_df[col].fillna(final_df[col].mode()[0])

# for col in moderate_missing + low_missing:
#     final_df[col] = final_df[col].fillna(final_df[col].mode()[0])

# -----------------------------------------------------------------------------------------------




# -----------------------------------------------------------------------------------------------
# Checking Feature Importance using ANOVA F-test (but this is with LabelEncode, which assigns ordinal bias to the dataset)-------------------
# Good for pure predictive power, but not for interpretability

from sklearn.feature_selection import f_regression
from sklearn.preprocessing import LabelEncoder

# Select only attribute columns
attribute_cols = [col for col in final_df.columns if 'attributes' in col]
X = final_df[attribute_cols]
y = final_df['stars']

# Encode categorical features if needed
X_encoded = X.copy()
for col in X.columns:
    if X[col].dtype == 'object':
        X_encoded[col] = LabelEncoder().fit_transform(X[col].astype(str))


# Run F-test
f_scores, p_values = f_regression(X_encoded, y)

# Display results
feature_importance = pd.DataFrame({
    'Feature': attribute_cols,
    'F-Score': f_scores,
    'P-Value': p_values
}).sort_values(by='F-Score', ascending=False)

print(feature_importance.head(10))


top_features = feature_importance.head(20)


# plt.figure(figsize=(100,50))
# tree.plot_tree(model.estimators_[0], feature_names=None, filled=True)
# plt.show()


# Plot
plt.figure(figsize=(20, 10))
sns.barplot(x='F-Score',y='Feature', data=top_features, palette='viridis')
plt.title("F-Score Label Encoding")
plt.show()



# Filter for significant features
significant_features = feature_importance[feature_importance['P-Value'] < 0.05].sort_values(by='F-Score', ascending=False)

print("Significant features:\n", significant_features)
print("Number of significant features:", len(significant_features))


# Apply Multiple Testing Correction (Benjamini-Hochberg)-------------------

from statsmodels.stats.multitest import multipletests

# Adjust p-values using FDR
_, corrected_pvals, _, _ = multipletests(p_values, alpha=0.05, method='fdr_bh')

# Filter significant features after correction
significant_corrected = pd.DataFrame({
    'Feature': X_encoded.columns,
    'F-Score': f_scores,
    'Corrected P-Value': corrected_pvals
}).query('`Corrected P-Value` < 0.05').sort_values(by='F-Score', ascending=False)

print("Significant features after correction:\n", significant_corrected)
print("Number of significant features after correction:", len(significant_corrected))




# Rebuilt a model with significant features-------------------
top_features = significant_corrected['Feature'].tolist()
X_top = X_encoded[top_features]

from sklearn.model_selection import train_test_split

X_train_labelencode, X_test_labelencode, y_train_labelencode, y_test_labelencode = train_test_split(X_top, y, test_size=0.2, random_state=42)

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

model = RandomForestRegressor(random_state=42)
model.fit(X_train_labelencode, y_train_labelencode)



# Predict and evaluate
y_pred_labelencode = model.predict(X_test_labelencode)
mse_labelencode = mean_squared_error(y_test_labelencode, y_pred_labelencode)
rmse_labelencode = np.sqrt(mse_labelencode)

# print("R² Score for Label Encoder Random Forest Model:", r2_score(y_test_labelencode, y_pred_labelencode))
# print("RMSE for Label Encoder Random Forest Model:", rmse_labelencode)

# Output Test & Train R² as well-------------------

from sklearn.metrics import r2_score

r2_train = r2_score(y_train_labelencode, model.predict(X_train_labelencode))
r2_test = r2_score(y_test_labelencode, model.predict(X_test_labelencode))

print("RF Label Encode Train R²:", r2_train) #RF Label Encode Train R²: 0.7550586903050884
print("RF Label Encode Test R²:", r2_test) #RF Label Encode Test R²: 0.23113668668273724



# Trying XGBoost as well for Label Encoder-------------------
from xgboost import XGBRegressor
model = XGBRegressor(
    random_state=42,
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6,
    objective='reg:squarederror'
)
model.fit(X_train_labelencode, y_train_labelencode)

y_pred_labelencode = model.predict(X_test_labelencode)
mse_labelencode = mean_squared_error(y_test_labelencode, y_pred_labelencode)
rmse_labelencode = np.sqrt(mse_labelencode)
r2_labelencode = r2_score(y_test_labelencode, y_pred_labelencode)

print("R² Score for Label Encoded XGBoost Model:", r2_labelencode)
print("RMSE for Label Encoded XGBoost Model:", rmse_labelencode)


# Output Test & Train R² as well-------------------

from sklearn.metrics import r2_score

r2_train = r2_score(y_train_labelencode, model.predict(X_train_labelencode)) #R² Score for Label Encoded XGBoost Model: 0.30939236797126846
r2_test = r2_score(y_test_labelencode, model.predict(X_test_labelencode)) #RMSE for Label Encoded XGBoost Model: 0.6793779902009333

print("XGBoost Label Encode Train R²:", r2_train) #XGBoost Label Encode Train R²: 0.3646151274973991
print("XGBoost Label Encode Test R²:", r2_test) #XGBoost Label Encode Test R²: 0.30939236797126846




# # With cleaned Dataset, testing ANOVA -----------------------------------------------------------------------------------------------
# With One Hot Encoding instead of Label Encoding-------------------
import pandas as pd
import numpy as np
from sklearn.feature_selection import f_regression
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from statsmodels.stats.multitest import multipletests

# Step 1: Identify categorical attribute columns
attribute_cols = [col for col in final_df.columns if 'attributes' in col and final_df[col].dtype == 'object']

# Step 2: One-hot encode all categorical attributes
X_encoded = pd.get_dummies(final_df[attribute_cols], drop_first=True)

# Step 3: Define target variable
y = final_df['stars']

# Step 4: Run ANOVA F-test
f_scores, p_values = f_regression(X_encoded, y)

# Step 5: Create feature importance DataFrame
feature_importance = pd.DataFrame({
    'Feature': X_encoded.columns,
    'F-Score': f_scores,
    'P-Value': p_values
}).sort_values(by='F-Score', ascending=False)

print("Top features by F-score:\n", feature_importance.head(10))

top_features = feature_importance.head(20)


# plt.figure(figsize=(100,50))
# tree.plot_tree(model.estimators_[0], feature_names=None, filled=True)
# plt.show()


# Plot
plt.figure(figsize=(20, 10))
sns.barplot(x='F-Score', y='Feature', data=top_features, palette='viridis')
plt.title("Top 20 Features by F-Score (One-Hot Encoded)")
plt.xlabel("F-Score")
plt.ylabel("Feature")
plt.tight_layout()
plt.show()


# Step 6: Multiple testing correction
_, corrected_pvals, _, _ = multipletests(p_values, alpha=0.05, method='fdr_bh')

significant_corrected = pd.DataFrame({
    'Feature': X_encoded.columns,
    'F-Score': f_scores,
    'Corrected P-Value': corrected_pvals
}).query('`Corrected P-Value` < 0.05').sort_values(by='F-Score', ascending=False)




print("Significant features after correction:\n", significant_corrected)
print("Number of significant features:", len(significant_corrected))

# Step 7: Rebuild model using significant features
top_features = significant_corrected['Feature'].tolist()
X_top = X_encoded[top_features]

X_train_ohc, X_test_ohc, y_train_ohc, y_test_ohc = train_test_split(X_top, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(random_state=42)
model.fit(X_train_ohc, y_train_ohc)

# Step 8: Evaluate model
y_pred_ohc = model.predict(X_test_ohc)
mse_ohc = mean_squared_error(y_test_ohc, y_pred_ohc)
rmse_ohc = np.sqrt(mse_ohc)

# print("R² Score for One Hot Encoded Random Forest Model:", r2_score(y_test_ohc, y_pred_ohc))
# print("RMSE for One Hot Encoded Random Forest Model:", rmse_ohc)


# Testing with XGBoost instead of RandomForest-------------------

from xgboost import XGBRegressor
model = XGBRegressor(
    random_state=42,
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6,
    objective='reg:squarederror'
)
model.fit(X_train_labelencode, y_train_labelencode)

from xgboost import plot_importance

plt.figure(figsize=(12, 8))
plot_importance(model, max_num_features=20, importance_type='gain')
plt.title("XGBoost Feature Importance (Label Encoded)")
plt.tight_layout()
plt.show()

from xgboost import plot_importance
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 8))
plot_importance(model, max_num_features=20, importance_type='gain')
plt.title("XGBoost Feature Importance (Label Encoded)")
plt.tight_layout()
plt.show()





# # Trying Dimennsionality Reduction with PCA-------------------

# from sklearn.decomposition import PCA
# from sklearn.preprocessing import StandardScaler

# # Step 1: One-hot encode attributes
# attribute_cols = [col for col in final_df.columns if 'attributes' in col and final_df[col].dtype == 'object']
# X_encoded = pd.get_dummies(final_df[attribute_cols], drop_first=True)

# # Step 2: Standardize (important for PCA)
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X_encoded)

# # Step 3: Apply PCA
# pca = PCA(n_components=0.95)  # Retain 95% of variance
# X_pca = pca.fit_transform(X_scaled)

# print("Original feature count:", X_encoded.shape[1])
# print("Reduced feature count:", X_pca.shape[1])



# # Trying OHC again without feature selection-------------------

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Step 1: One-hot encode all categorical attribute columns
attribute_cols = [col for col in final_df.columns if 'attributes' in col and final_df[col].dtype == 'object']
X_encoded = pd.get_dummies(final_df[attribute_cols], drop_first=True)

# Step 2: Define target variable
y = final_df['stars']

# Step 3: Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

# Step 4: Train model
model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

# Step 5: Evaluate model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("R² Score:", r2)
print("RMSE:", rmse)

# Step 6: Feature importance
importances = pd.DataFrame({
    'Feature': X_encoded.columns,
    'Importance': model.feature_importances_
}).sort_values(by='Importance', ascending=False)

print("Top 10 important features:\n", importances.head(10))
top_features = importances.head(20)

# Output Test & Train R² as well-------------------

from sklearn.metrics import r2_score

r2_train = r2_score(y_train, model.predict(X_train))
r2_test = r2_score(y_test, model.predict(X_test))

print("RF OHC Train R²:", r2_train) # RF OHC Train R²: 0.1937388665523886
print("RF Test R²:", r2_test) #RF Test R²: 0.1125495323251503


# plt.figure(figsize=(100,50))
# tree.plot_tree(model.estimators_[0], feature_names=None, filled=True)
# plt.show()


# Plot
plt.figure(figsize=(20, 10))
sns.barplot(x='Importance',y='Feature', data=top_features)
plt.title("Feature Importance")
plt.show()




# Trying to tune Hyperparameters with GridSearchCV for RandomForest Decision Tree-------------------
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [100, 300, 500],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5],
    'max_features': ['sqrt', 'log2']
}

grid = GridSearchCV(RandomForestRegressor(random_state=42), param_grid, cv=3, scoring='r2')
grid.fit(X_train, y_train)

print("Best R²:", grid.best_score_)




print("R² Score for Label Encoder Random Forest Model:", r2_score(y_test_labelencode, y_pred_labelencode)) #R² Score for Label Encoder Random Forest Model: 0.23113668668273724
print("RMSE for Label Encoder Random Forest Model:", rmse_labelencode) #RMSE for Label Encoder Random Forest Model: 0.7168369042184569
print("R² Score with Feature Selection for One Hot Encoded Random Forest Model:", r2_score(y_test_ohc, y_pred_ohc)) #R² Score with Feature Selection for One Hot Encoded Random Forest Model: 0.11121576900199381
print("RMSE with Feature Selection for One Hot Encoded Random Forest Model:", rmse_ohc) #RMSE with Feature Selection for One Hot Encoded Random Forest Model: 0.7707152573264832
print("R² Score without Feature Selection for One Hot Encoded Random Forest Model:", r2) #R² Score without Feature Selection for One Hot Encoded Random Forest Model: 0.1125495323251503
print("RMSE without Feature Selection for One Hot Encoded Random Forest Model:", rmse) #RMSE without Feature Selection for One Hot Encoded Random Forest Model: 0.7701367492655742






# Try XGBoost as well-------------------
# Try incorporate other datasets as well-------------------
# Try top 10 features from each encoding method-------------------


from xgboost import XGBRegressor

# Step 7: Rebuild model using significant features
top_features = significant_corrected['Feature'].tolist()
X_top = X_encoded[top_features]

X_train_ohc, X_test_ohc, y_train_ohc, y_test_ohc = train_test_split(X_top, y, test_size=0.2, random_state=42)

# Replace with XGBoost
XGmodel = XGBRegressor(random_state=42, n_estimators=100, learning_rate=0.1)
XGmodel.fit(X_train_ohc, y_train_ohc)

# Step 8: Evaluate model
y_pred_ohcXG = XGmodel.predict(X_test_ohc)
mse_ohcXG = mean_squared_error(y_test_ohc, y_pred_ohcXG)
rmse_ohcXG = np.sqrt(mse_ohcXG)
r2_ohcXG = r2_score(y_test_ohc, y_pred_ohcXG)

print("R² Score for XGBoost Model:", r2_ohcXG) # R² Score for XGBoost Model: 0.1252386960226597
print("RMSE for XGBoost Model:", rmse_ohcXG) # RMSE for XGBoost Model: 0.764611046064029



from sklearn.metrics import r2_score

r2_train = r2_score(y_train_ohc, XGmodel.predict(X_train_ohc))
r2_test = r2_score(y_test_ohc, XGmodel.predict(X_test_ohc))

print("XGBoost OHC Train R²:", r2_train) # XGBoost OHC Train R²: 0.15002172245710632
print("XGBoost Test R²:", r2_test) # XGBoost Test R²: 0.1252386960226597

