# script4 snakemake

args <- commandArgs(trailingOnly = TRUE)
input_csv <- args[1]
output_min_distance <- args[2]
output_nuclear_expansion <- args[3]
output_nuclei_diameter <- args[4]

library(geosphere)
library(dplyr)
library(readr)
library(yaml)

# Load config
config <- yaml.load_file("config.yaml")

# Get sample size from config
desired_sample_size <- config$sample_size

# Load from Snakemake-passed CSV path
data <- read_delim(input_csv, delim = "\t", escape_double = FALSE, trim_ws = TRUE)

# Check structure
if (ncol(data) < 11) {
  stop("Expected at least 11 columns in input CSV")
}

# Calculate average nucleus area (column 11)
average_area <- mean(data[[11]], na.rm = TRUE)
average_diameter <- average_area / 3.14
nucleus_ray <- sqrt(average_diameter) 

# Sample 15000 nuclei or fewer if total rows < 15000
#set.seed(123)
#sample_size <- min(15000, nrow(data))
#sampled_data <- data[sample(nrow(data), sample_size), ]

# Sample 15000 nuclei or fewer if total rows < 15000 (or other value from config)
set.seed(123)
sample_size <- min(desired_sample_size, nrow(data))
sampled_data <- data[sample(nrow(data), sample_size), ]

# Compute distance matrix between centroids (columns 8 and 9)
distance_matrix <- dist(sampled_data[, c(8, 9)])
distances_matrix <- as.matrix(distance_matrix)
diag(distances_matrix) <- Inf
min_distances <- apply(distances_matrix, 1, min)
average_min_distance <- mean(min_distances)

# Compute average nuclear expansion
nuclei_rays <- nucleus_ray * 2
average_nuclear_expansion <- (average_min_distance - nuclei_rays)/2

# Round to 2 decimals
average_min_distance_df <- data.frame(Average_Min_Distance = round(average_min_distance, 2))
average_nuclear_expansion_df <- data.frame(Average_Nuclear_Expansion = round(average_nuclear_expansion, 2))
average_diameter_df<- data.frame(Average_Diameter=round(average_diameter,2))

# Write outputs to separate CSV files passed from Snakemake
write.csv(average_min_distance_df, file = output_min_distance, row.names = FALSE)
write.csv(average_nuclear_expansion_df, file = output_nuclear_expansion, row.names = FALSE)
write.csv(average_diameter_df, file = output_nuclei_diameter, row.names = FALSE)


# Optional console output
cat("Average Minimum Distance:", round(average_min_distance, 2), "\n")
cat("Average Nuclear Expansion:", round(average_nuclear_expansion, 2), "\n")
cat("Average Nuclei Diameter:", round(average_diameter, 2), "\n")
