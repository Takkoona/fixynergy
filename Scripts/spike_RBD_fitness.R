library(jsonlite)


args <- commandArgs(trailingOnly=TRUE)

FITNESS_DATA_FILE <- "Data/SARS-CoV-2_spike/Spike_RBD_fitness.csv"
ESCAPE_DATA_FILE <- "Data/SARS-CoV-2_spike/Spike_RBD_escape.csv"

fitness_data <- read.csv(FITNESS_DATA_FILE)
RBD_sites <- unique(fitness_data$site_SARS2)

fit_sites <- split(fitness_data, fitness_data$site_SARS2)
fit_sites <- fit_sites[which(sapply(fit_sites, function(i) {
    any(i$bind_avg > 0 & i$expr_avg > 0)
}))]
fit_sites <- as.integer(names(fit_sites))


escape_data <- read.csv(ESCAPE_DATA_FILE)
escape_sites <- split(escape_data, escape_data$site)
escape_sites <- escape_sites[which(sapply(escape_sites, function(i) {
    any(i$site_max_escape > 0.1)
}))]
escape_sites <- unique(as.integer(names(escape_sites)))


