
# To clear the environment and variables
rm(list = ls())

# install.packages("jsonlite")  # don't think these are needed unless fromJSON
library(jsonlite)

setwd("C:/Users/Daniel Loh/Documents/NUS-ISS_EBAC/BAP/BAP Practice Module Project/Final_Project_Data")

# yelp_business <- fromJSON("yelp_academic_dataset_business.json")
yelp_business <- stream_in(file("yelp_academic_dataset_business.json"))

# Error when trying to stream user json file directly, due to last row error, so need to drop last line
#yelp_user <- stream_in(file("yelp_academic_dataset_user.json"))
yelp_user_raw <- readLines("yelp_academic_dataset_user.json", warn = FALSE)
yelp_user_valid_lines <- yelp_user_raw[1:(length(yelp_user_raw)-1)]  # Drop last line
yelp_user <- lapply(yelp_user_valid_lines, fromJSON)
yelp_user <- do.call(rbind, yelp_user)

yelp_tip <- stream_in(file("yelp_academic_dataset_tip.json"))

# Error when trying to stream review json file directly, due to last row error, so need to drop last line
# yelp_review <- stream_in(file("yelp_academic_dataset_review.json"))
yelp_review_raw <- readLines("yelp_academic_dataset_review.json", warn = FALSE)
writeLines(yelp_review_raw[-length(yelp_review_raw)], "yelp_academic_dataset_review_fixed.json")
yelp_review <- stream_in(file("yelp_academic_dataset_review_fixed.json"))


yelp_checkin <- stream_in(file("yelp_academic_dataset_checkin.json"))


summary(yelp_business)
summary(yelp_user)
summary(yelp_tip)
summary(yelp_review)
yelp_review$date <- as.POSIXct(yelp_review$date, format = "%Y-%m-%d %H:%M:%S")
summary(yelp_checkin)

head(yelp_business, n = 10L)
head(yelp_user, n = 10L)
head(yelp_tip, n = 10L)
head(yelp_review, n = 10L)
head(yelp_checkin, n = 10L)


# To find out the business concentration in the states---------------------------
library(dplyr)

state_counts <- yelp_business%>%
  count(state, name = "business_count")

state_coords <- data.frame(state = state.abb,
                           lat = state.center$y,
                           lon = state.center$x)

# Merge with business counts

library(ggplot2)
library(maps)


us_map <- map_data("state")

state_plot_data <- yelp_business %>%
  group_by(state) %>%
  summarise(business_count = n()) %>%
  left_join(state_coords, by = "state")

ggplot() + geom_map(data = us_map, map = us_map, 
                    aes(x = long, y = lat, map_id = region), 
                    fill = "white", color = "gray70", size = 0.3) +
  geom_point(data = state_plot_data, 
             aes(x = lon, y = lat, size = business_count), 
             color = "dodgerblue", alpha = 0.6) +
  scale_size(range = c(2, 12)) +
  labs(title = "Business Concentration by State", size = "Number of Businesses") +
  theme_minimal()

# Distribution of Star Ratings -----------------------
ggplot(yelp_business, aes(x = stars)) + geom_histogram(colour="black", fill="white")


# Trying to find out if any correlation count between Number of Reviews vs Final Star Rating of Business, but none
ggplot(yelp_business, aes(x = review_count, y = stars)) +
  geom_point(alpha = 0.3) +
  labs(title = "Review Count vs. Star Rating", x = "Review Count", y = "Stars")


cor(yelp_business$review_count, yelp_business$stars, use = "complete.obs")

# Finding out the average business rating by city ---------------------------
city_avg <- yelp_business %>%
  group_by(city) %>%
  summarise(avg_rating = mean(stars, na.rm = TRUE),
            n_businesses = n()) %>%
  arrange(desc(avg_rating))



ggplot(city_avg, aes(x = reorder(city, avg_rating), y = avg_rating)) +
  geom_col(fill = "steelblue") +
  coord_flip() +
  labs(title = "Average Business Rating by City", x = "City", y = "Average Stars")


# Finding out the average business rating by state ---------------------------

state_avg <- yelp_business %>%
  group_by(state) %>%
  summarise(avg_rating = mean(stars, na.rm = TRUE),
            n_businesses = n()) %>%
  arrange(desc(avg_rating))

ggplot(state_avg, aes(x = reorder(state, avg_rating), y = avg_rating)) +
  geom_col(fill = "steelblue") +
  coord_flip() +
  labs(title = "Average Business Rating by State", x = "State", y = "Average Stars")


# Finding out the categories with the top average ratings----------------------------

library(tidyr)
library(dplyr)

# Split the categories column into individual categories
category_expanded <- yelp_business %>%
  filter(!is.na(categories)) %>%
  separate_rows(categories, sep = ",\\s*")

# Calculate average rating and count per category
category_ratings <- category_expanded %>%
  group_by(categories) %>%
  summarise(avg_rating = mean(stars, na.rm = TRUE),
            n_businesses = n()) %>%
  arrange(desc(avg_rating))



# Split and unnest categories
bottom_cats <- category_ratings %>%
  filter(n_businesses >= 50) %>%
  slice_min(avg_rating, n = 100)

ggplot(bottom_cats, aes(x = reorder(categories, avg_rating), y = avg_rating)) +
  geom_col(fill = "firebrick") +
  coord_flip() +
  labs(title = "Bottom Categories by Average Rating", x = "Category", y = "Avg Stars")

# Trying to find out the boxplot distribution of the ratings by state---------

ggplot(yelp_business, aes(x = state, y = stars)) +
  geom_boxplot() + labs(title = "Star Rating by State", x = "State", y = "Stars")



ggplot(yelp_tip, aes(x = compliment_count)) +
  geom_histogram() + labs(title = "Compliment Count", x = "Number of Compliments", y = "Amount")




merged_yelp_business_review <- merge(x = yelp_business, y = yelp_review, by = "business_id")
summary(merged_yelp_business_review)

mean(merged_yelp_business_review$stars.y)
median(merged_yelp_business_review$stars.y)




# Count number of businesses per category
top_categories <- category_expanded %>%
  group_by(categories) %>%
  summarise(n_businesses = n()) %>%
  arrange(desc(n_businesses))

# View top categories
head(top_categories, 10)


ggplot(top_categories %>% slice_max(n_businesses, n = 20), 
       aes(x = reorder(categories, n_businesses), y = n_businesses)) +
  geom_col(fill = "darkgreen") +
  coord_flip() +
  labs(title = "Top 20 Categories by Business Count", x = "Category", y = "Number of Businesses")



library(dplyr)
library(stringr)

# Filter businesses where 'categories' contains the word "Restaurants"
yelp_restaurants <- yelp_business %>%
  filter(!is.na(categories)) %>%
  filter(str_detect(categories, regex("Restaurants", ignore_case = TRUE)))


library(jsonlite)

# Save yelp_restaurants as line-delimited JSON
stream_out(yelp_restaurants, file("yelp_academic_dataset_restaurants.json"))
readLines("yelp_academic_dataset_restaurants.json", n = 5)

# Quick check
glimpse(yelp_restaurants)

name_expanded_restaurant <- yelp_restaurants %>%
  filter(!is.na(name)) %>%
  separate_rows(name, sep = ",\\s*")

top_name_restaurant <- name_expanded_restaurant %>%
  group_by(name) %>%
  summarise(n_restaurants = n()) %>%
  arrange(desc(n_restaurants))

# View top restaurants-----------
head(top_name_restaurant, 10)


yelp_McDonalds <- yelp_restaurants %>%
  filter(!is.na(name)) %>%
  filter(str_detect(name, regex("McDonald's", ignore_case = TRUE)))


state_plot_data <- yelp_restaurants %>%
  group_by(state) %>%
  summarise(business_count = n()) %>%
  left_join(state_coords, by = "state")  # state_coords should have lon/lat for each state

ggplot() +
  geom_polygon(data = us_map, aes(x = long, y = lat, group = group), 
               fill = "white", color = "gray70", size = 0.3) +
  geom_point(data = state_plot_data, 
             aes(x = lon, y = lat, size = business_count), 
             color = "dodgerblue", alpha = 0.6) +
  scale_size(range = c(2, 12)) +
  labs(title = "Restaurant Concentration by State", size = "Number of Restaurants") +
  theme_minimal()




# Distribution of Star Ratings -----------------------
ggplot(yelp_restaurants, aes(x = stars)) + geom_histogram(colour="black", fill="white")

ggplot(yelp_McDonalds, aes(x = stars)) + geom_histogram(colour="black", fill="white")


merged_yelp_restaurant_review <- merge(x = yelp_restaurants, y = yelp_review, by = "business_id")
summary(merged_yelp_restaurant_review)


# Subway -------------

yelp_subway <- yelp_restaurants %>%
  filter(!is.na(name)) %>%
  filter(str_detect(name, regex("Subway", ignore_case = TRUE)))


state_plot_data <- yelp_restaurants %>%
  group_by(state) %>%
  summarise(business_count = n()) %>%
  left_join(state_coords, by = "state")  # state_coords should have lon/lat for each state

ggplot() +
  geom_polygon(data = us_map, aes(x = long, y = lat, group = group), 
               fill = "white", color = "gray70", size = 0.3) +
  geom_point(data = state_plot_data, 
             aes(x = lon, y = lat, size = business_count), 
             color = "dodgerblue", alpha = 0.6) +
  scale_size(range = c(2, 12)) +
  labs(title = "Restaurant Concentration by State", size = "Number of Restaurants") +
  theme_minimal()




# Distribution of Star Ratings -----------------------
ggplot(yelp_restaurants, aes(x = stars)) + geom_histogram(colour="black", fill="white")

ggplot(yelp_McDonalds, aes(x = stars)) + geom_histogram(colour="black", fill="white")


ggplot(yelp_subway, aes(x = stars)) + geom_histogram(colour="black", fill="white")

# # Testing Sentiment Analysis and Predictive Analysis -----------------
# install.packages("tidytext")
# library(tidytext)
# reviews_sentiment <- yelp_review %>%
#   unnest_tokens(word, text) %>%
#   inner_join(get_sentiments("bing")) %>%
#   count(review_id, sentiment) %>%
#   spread(sentiment, n, fill = 0) %>%
#   mutate(sentiment_score = positive - negative)
# 
# 
# 
# library(rpart)
# model <- rpart(stars ~ review_count + sentiment_score + checkin_count, data = merged_data)



# Split the categories by comma
all_categories <- unlist(strsplit(yelp_business$categories, ","))

# Trim whitespace
all_categories <- trimws(all_categories)

# Get unique values
unique_categories <- unique(all_categories)

# View result
print(unique_categories)


# Ensure date column is in Date format
yelp_review$date <- as.Date(yelp_review$date)
summary(yelp_review)

nrow(yelp_review)

library(dplyr)
library(lubridate)

reviews_by_year <- yelp_review %>%
  mutate(year = year(date)) %>%  # Extract year from date
  count(year, name = "review_count")    # Count reviews per year

print(reviews_by_year)

# Filter for dates between 2017-01-01 and 2022-12-31
filtered_reviews <- subset(yelp_review, date >= as.Date("2017-01-01") & date <= as.Date("2022-12-31"))

# Count number of rows
num_reviews <- nrow(filtered_reviews)

# View result
print(num_reviews)


# Ensure date column is in Date format
yelp_review$date <- as.Date(yelp_review$date)

# Filter reviews between 2017 and 2022
filtered_reviews <- subset(yelp_review, date >= as.Date("2017-01-01") & date <= as.Date("2022-12-31"))

# Export to CSV
write.csv(filtered_reviews, "filtered_yelp_reviews_2017_2022.csv", row.names = FALSE)


data <- read.csv("./business_output.csv")


# Define food-related keywords
food_keywords <- c(
  "Restaurants", "Fast Food", "Diners", "Cafes", "Coffee & Tea", "Bakeries", "Bubble Tea",
  "Ice Cream & Frozen Yogurt", "Pizza", "Sandwiches", "Delis", "Barbeque", "Chicken Wings",
  "Hot Dogs", "Seafood", "Sushi Bars", "Steakhouses", "Burgers", "Salad", "Soup", "Bagels",
  "Donuts", "Breakfast & Brunch", "Comfort Food", "Noodles", "Wraps", "Acai Bowls", "Vegan",
  "Vegetarian", "Cajun/Creole", "Mediterranean", "Mexican", "Thai", "Japanese", "Chinese",
  "Korean", "Indian", "Vietnamese", "Caribbean", "Filipino", "Italian", "Greek",
  "American (Traditional)", "American (New)", "Turkish", "Moroccan", "French", "Ethiopian",
  "Latin American", "Persian/Iranian", "Malaysian", "Burmese", "Trinidadian", "Lebanese",
  "Food Trucks", "Food Stands", "Specialty Food", "Grocery", "Convenience Stores",
  "Farmers Market", "Imported Food", "Ethnic Food", "Organic Stores", "Health Markets",
  "Candy Stores", "Chocolatiers & Shops", "Juice Bars & Smoothies", "Beer, Wine & Spirits",
  "Wine Bars", "Brewpubs", "Breweries", "Beer Bar", "Tea Rooms", "Patisserie/Cake Shop",
  "Do-It-Yourself Food", "Meat Shops", "Fruits & Veggies", "Caterers", "Asian Fusion", 
  "Indian", "Desserts", "Bagels", "Donuts", "Pretzels", "Shaved Ice", "Cupcakes", 
  "Pasta Shops", "Coffee Roasteries", "Falafel", "Tacos", "Cheesesteaks", "Gluten-Free", 
  "Hawaiian", "Empanadas", "Sardinian", "Creperies", "Fish & Chips", "Food Court", 
  "Food Delivery Services", "Halal", "Breakfast & Brunch"
)

# Categorize each business
yelp_business_food <- yelp_business %>%
  mutate(
    category_type = ifelse(
      str_detect(categories, paste(food_keywords, collapse = "|")),
      "Food",
      "Others"
    )
  )

# Check result
table(yelp_business_food$category_type)



library(dplyr)
library(stringr)
library(openxlsx)

# Split comma-separated categories into individual entries
others_categories <- yelp_business %>%
  filter(category_type == "Others") %>%
  pull(categories) %>%
  str_split(",\\s*") %>%
  unlist() %>%
  unique() %>%
  sort()

# Convert to data frame for export
others_df <- data.frame(Category = others_categories)

# Save to Excel file
write.xlsx(others_df, "others_categories.xlsx", rowNames = FALSE)



# Split comma-separated categories into individual entries
food_categories <- yelp_business %>%
  filter(category_type == "Food") %>%
  pull(categories) %>%
  str_split(",\\s*") %>%
  unlist() %>%
  unique() %>%
  sort()


foods_df <- data.frame(Category = food_categories)

write.xlsx(foods_df, "food_categories.xlsx", rowNames = FALSE)


# Filter for Food businesses
food_businesses <- yelp_business %>%
  filter(category_type == "Food")

# Export to CSV
write.csv(food_businesses, "yelp_food_businesses.csv", row.names = FALSE)


# Load required package
library(jsonlite)

# Filter for Food businesses
food_businesses <- yelp_business %>%
  filter(category_type == "Food")

# Export to JSON
write_json(food_businesses, "yelp_food_businesses.json", pretty = TRUE)


library(dplyr)
library(stringr)

# Filter businesses that include "Convenience Stores" in their categories
convenience_stores <- yelp_business %>%
  filter(str_detect(categories, "Convenience Stores"))

# View the first few rows
head(convenience_stores)

# Count how many businesses match
nrow(convenience_stores)


convenience_names <- unique(convenience_stores$name)
head(convenience_names)
length(convenience_names)
convenience_names



summary(yelp_business_food)

# EDA for Food Businesses------------------------------------

library(dplyr)
yelp_business_food <- stream_in(file("yelp_academic_dataset_restaurants.json"))

yelp_business_food_clean <- yelp_business_food %>%
  filter(category_type == "Food")

library(dplyr)

yelp_business_food_clean <- yelp_business_food_clean %>%
  mutate(across(
    starts_with("attributes."),
    ~ case_when(
      . %in% c("True", "true")  ~ TRUE,
      . %in% c("False", "false") ~ FALSE,
      . %in% c("None", "", NA)   ~ NA,
      TRUE ~ NA  # catch-all for unexpected values
    )
  ))

library(tidyr)

head(yelp_business_food)


#flatten nested attribute column:
library(tidyr)

yelp_business_flat <- yelp_business_food %>%
  unnest_wider(attributes, names_sep = "_attr_")
head(yelp_business_flat)


#further find out those which have inner nested columns
nested_candidates <- yelp_business_flat %>%
  select(starts_with("attributes_attr_")) %>%
  summarise(across(everything(), ~ any(grepl("\\{.*\\}", ., perl = TRUE)))) %>%
  pivot_longer(everything(), names_to = "column", values_to = "is_nested") %>%
  filter(is_nested)

nested_cols <- nested_candidates$column
nested_cols



# defining the barchart plotting for the columns specified

library(ggplot2)

plot_attribute_distribution <- function(df, col_name) {
  df %>%
    count(.data[[col_name]], sort = TRUE) %>%
    ggplot(aes(x = reorder(.data[[col_name]], n), y = n)) +
    geom_bar(stat = "identity", fill = "#2c7fb8") +
    coord_flip() +
    labs(title = paste("Distribution of", col_name), x = "Value", y = "Count") +
    theme_minimal(base_size = 12) +
    theme(
      plot.background = element_rect(fill = "white", color = NA),
      panel.background = element_rect(fill = "white", color = NA)
    )
}

plot_attribute_distribution(yelp_business_flat, "attributes_attr_WiFi")



# Output saved plot files and loop through all the columns that start with attribute

attribute_cols <- grep("^attributes_attr_", names(yelp_business_flat), value = TRUE)


for (col in attribute_cols) {
  g <- plot_attribute_distribution(yelp_business_flat, col)
  ggsave(
    filename = paste0("plot_", col, ".png"),
    plot = g,
    width = 8,
    height = 5,
    bg = "white"
  )
}


#Function to flatten JSON columns:
library(jsonlite)
library(tidyr)
library(dplyr)
library(purrr)

#clean python json to true json
clean_json <- function(x) {
  x <- gsub("'", "\"", x)
  x <- gsub("None", "null", x)
  x <- gsub("True", "true", x)
  x <- gsub("False", "false", x)
  return(x)
}

#flatten true json to columns in R
# flatten_nested_column <- function(df, col_name, prefix = NULL) {
#   prefix <- prefix %||% col_name
#   nested_df <- df %>%
#     mutate(temp = map(.data[[col_name]], ~ tryCatch(fromJSON(.x), error = function(e) NULL))) %>%
#     select(business_id, temp) %>%
#     unnest_wider(temp, names_sep = paste0("_", prefix, "_"))
#   
#   return(nested_df)
# }


flatten_nested_column <- function(df, col_name, prefix = NULL) {
  prefix <- prefix %||% col_name
  
  nested_df <- df %>%
    mutate(temp = map(.data[[col_name]], function(x) {
      if (is.character(x)) {
        x_clean <- clean_json(x)
        tryCatch(fromJSON(x_clean), error = function(e) NULL)
      } else {
        NULL
      }
    })) %>%
    select(business_id, temp) %>%
    unnest_wider(temp, names_sep = paste0("_", prefix, "_"))
  
  return(nested_df)
}

# summary(yelp_business_flat)
# yelp_business_flat$attributes_attr_BusinessParking[1:5]
parking_df <- flatten_nested_column(yelp_business_flat, "attributes_attr_BusinessParking")
ambience_df <- flatten_nested_column(yelp_business_flat, "attributes_attr_Ambience")
goodformeal_df <- flatten_nested_column(yelp_business_flat, "attributes_attr_GoodForMeal")
music_df <- flatten_nested_column(yelp_business_flat, "attributes_attr_Music")
bestnights_df <- flatten_nested_column(yelp_business_flat, "attributes_attr_BestNights")
dietrestrictions_df <- flatten_nested_column(yelp_business_flat, "attributes_attr_DietaryRestrictions")
hairspecialize_df <- flatten_nested_column(yelp_business_flat, "attributes_attr_HairSpecializesIn")

summary(parking_df)


# List of flattened dataframes
flattened_dfs <- list(
  parking_df,
  ambience_df,
  goodformeal_df,
  music_df,
  bestnights_df,
  dietrestrictions_df,
  hairspecialize_df
)

# Optional: names for file prefixes
df_names <- c(
  "BusinessParking",
  "Ambience",
  "GoodForMeal",
  "Music",
  "BestNights",
  "DietaryRestrictions",
  "HairSpecializesIn"
)

# Loop through each dataframe and each column
for (i in seq_along(flattened_dfs)) {
  df <- flattened_dfs[[i]]
  df_name <- df_names[i]
  
  # Skip business_id column
  cols_to_plot <- setdiff(names(df), "business_id")
  
  for (col in cols_to_plot) {
    g <- plot_attribute_distribution(df, col)
    
    ggsave(
      filename = paste0("plot_", df_name, "_", col, ".png"),
      plot = g,
      width = 8,
      height = 5,
      bg = "white"
    )
  }
}


# Output as CSV & JSON:

dataframes <- list(
  yelp_business_flat = yelp_business_flat,
  parking_df = parking_df,
  ambience_df = ambience_df,
  goodformeal_df = goodformeal_df,
  music_df = music_df,
  bestnights_df = bestnights_df,
  dietrestrictions_df = dietrestrictions_df,
  hairspecialize_df = hairspecialize_df
)


library(jsonlite)

for (name in names(dataframes)) {
  df <- dataframes[[name]]
  
  # Save as CSV
  write.csv(df, file = paste0(name, ".csv"), row.names = FALSE)
  
  # Save as JSON
  write_json(df, path = paste0(name, ".json"), pretty = TRUE, auto_unbox = TRUE)
}



# Replot as Percentage and
yelp_business_flat <- fromJSON("yelp_food_business_flat.json")
library(tidyr)
library(dplyr)
library(ggplot2)
yelp_long <- yelp_business_flat %>%
  separate_rows(categories, sep = ",\\s*") %>%
  mutate(categories = trimws(categories))

head(yelp_long)

attribute_cols <- grep("^attributes_attr_", names(yelp_business_flat), value = TRUE)

library(ggplot2)
library(dplyr)
library(tidyr)


# Group by Category and check non-NA % for each category in attributes

# plot_attribute_coverage <- function(df, attribute_col) {
#   df_long <- df %>%
#     separate_rows(categories, sep = ",\\s*") %>%
#     mutate(categories = trimws(categories))
#   
#   coverage <- df_long %>%
#     group_by(categories) %>%
#     summarise(
#       total = n(),
#       non_na = sum(!is.na(.data[[attribute_col]])),
#       percent_non_na = round(100 * non_na / total, 1),
#       .groups = "drop"
#     ) %>%
#     filter(total > 10) %>%  # Optional: filter out sparse categories
#     arrange(desc(percent_non_na))
#   
#   ggplot(coverage, aes(x = reorder(categories, percent_non_na), y = percent_non_na)) +
#     geom_bar(stat = "identity", fill = "#2c7fb8") +
#     geom_text(aes(label = paste0(percent_non_na, "%")), hjust = -0.1, size = 3.5) +
#     coord_flip() +
#     labs(title = paste("Coverage of", attribute_col, "by Category"),
#          x = "Category",
#          y = "Non-NA Coverage (%)") +
#     theme_minimal(base_size = 12) +
#     theme(
#       plot.background = element_rect(fill = "white", color = NA),
#       panel.background = element_rect(fill = "white", color = NA)
#     )
# }
# 
# for (col in attribute_cols) {
#   g <- plot_attribute_coverage(yelp_business_flat, col)
#   ggsave(
#     filename = paste0("coverage_by_category_", col, ".png"),
#     plot = g,
#     width = 10,
#     height = 6,
#     bg = "white"
#   )
# }
# 
# 



# Separately plot by each category and its attribute composition

library(dplyr)
library(tidyr)
library(ggplot2)

plot_attribute_composition_by_category <- function(df, attribute_col) {
  df_long <- df %>%
    separate_rows(categories, sep = ",\\s*") %>%
    mutate(categories = trimws(categories))
  
  comp <- df_long %>%
    group_by(categories, .data[[attribute_col]]) %>%
    summarise(count = n(), .groups = "drop") %>%
    group_by(categories) %>%
    mutate(percent = round(100 * count / sum(count), 1)) %>%
    ungroup()
  
  # Create one plot per category
  categories_list <- unique(comp$categories)
  
  for (cat in categories_list) {
    comp_cat <- comp %>% filter(categories == cat)
    
    p <- ggplot(comp_cat, aes(x = .data[[attribute_col]], y = percent, fill = .data[[attribute_col]])) +
      geom_bar(stat = "identity") +
      geom_text(aes(label = paste0(percent, "%")), vjust = -0.5, size = 3.5) +
      labs(title = paste("Composition of", attribute_col, "in", cat),
           x = "Attribute Value",
           y = "Percentage") +
      theme_minimal(base_size = 12) +
      theme(
        plot.background = element_rect(fill = "white", color = NA),
        panel.background = element_rect(fill = "white", color = NA),
        legend.position = "none"
      )
    
    ggsave(
      filename = paste0("composition_", attribute_col, "_", gsub("[^A-Za-z0-9]", "_", cat), ".png"),
      plot = p,
      width = 7,
      height = 5,
      bg = "white"
    )
  }
}


