###  Loading the dataset ###
install.packages("jsonlite")
library(jsonlite)
file_path <- '~/Downloads/Yelp JSON/yelp_dataset/yelp_academic_dataset_restaurants.json'
df <- stream_in(file(file_path))
# Print the first 6 rows to get a quick look at the data
print("--- First 6 Businesses ---")
print(head(df))
# Print a concise summary of the data frame's structure
print("--- Data Summary ---")
str(df, max.level = 1)

### Filtering ###
install.packages("dplyr")
install.packages("stringr")
library(dplyr)
library(stringr)
# Filter for businesses that contain "Restaurants" in their categories
restaurants <- df %>%
  filter(
    !is.na(categories) &  #ensure category is not missing (NA)
      str_detect(categories, "Restaurants") # look for "restaurant"
  )

# 3. View the results
# You can view the names and categories of the filtered businesses
print("--- Businesses in the 'Restaurant' Category ---")
head(restaurants %>% select(name, categories))

dim(restaurants)
# 52268 businesses with "Restuarant" as a category
View(restaurants) #shows the table in R
