#centroids 

   
#from pixel to um

measurements[, 8] <- measurements[, 8] * 0.85
measurements[, 9] <- measurements[, 9] * 0.85
measurements[, 10] <- measurements[, 10] * 0.85

distance_matrix_centroids <- dist(measurements[, c("Centroid X px", "Centroid Y px")])

set.seed(123) 

# Step 2: Convert to matrix if needed (optional)

distances_matrix <- as.matrix(distance_matrix_centroids)

# Load necessary library

library(geosphere)
library(dplyr)

# Step 3: Extract minimum distances
# Set diagonal to Inf to ignore distances to self
diag(distances_matrix) <- Inf

# Find minimum distance for each cell
min_distances <- apply(distances_matrix, 1, min)

# Step 4: Calculate average of the minimum distances
average_min_distance <- mean(min_distances)

# Output the result
cat("Average Minimum Distance between Cells:", average_min_distance, "\n")

#plot
boxplot(min_distances, 
        main = paste("Average minimum distance", threshold, " µm", sep = ""),
        ylab = "Distance (µm)", 
        col = "grey")


#calculate average nucleus area 

average_area_Pancreas <- mean(measurements[[10]], na.rm = TRUE)  

View(average_area)


boxplot(measurements$`Nucleus: Area`, 
        main = "Boxplot of Cells Nucleus Area Pancreas ", 
        ylab = "Cell Area", 
        col = "darkblue")

#plots together 

# Set up the plotting area to have 2 rows and 1 column
par(mfrow = c(2, 1))

# First boxplot
boxplot(min_distances, 
        main = paste("Cells minimum distance average", sep = ""),
        ylab = "Distance (µm)", 
        col = "lightblue")


# Second boxplot

boxplot(measurements$`Nucleus: Area`, 
        main = "Cells nucleus area average ", 
        ylab = "Cell Area", 
        col = "grey")


# Reset the plotting area to default (optional)
par(mfrow = c(1, 1))



