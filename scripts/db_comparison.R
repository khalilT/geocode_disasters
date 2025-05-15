library(tidyverse) # general utility functions
library(ggbreak)
library(sf) # plot map
sf_use_s2(FALSE)
library(rnaturalearth) # plot map
library(rnaturalearthdata) # plot map
library(patchwork)
library(here)
library(glue)

base_dir <- paste0(dirname(rstudioapi::getSourceEditorContext()$path), "/")
source(paste0(base_dir, "../src/utils/paths.R"))



# Read data ---------------------------------------------------------------

compare_df <- read_csv("/net/projects/xaida/database_paper/output_data/geodat_gdis_comaprison_qflags.csv")
disasters_subnat_st <- st_read(geocoded_location_path)
gdis_data <- st_read("/net/projects/xaida/database_paper/intermediate_data/simplified_gdis.gpkg")

disasterno <- gdis_data %>% unite("Dis.No", disasterno, iso3, sep = "-")
gdis_data <- gdis_data %>% mutate(year = as.integer(substr(disasterno, 1, 4)))
gdis_data$DisNo. <- disasterno$Dis.No
gdis_data_9018 <- gdis_data %>% filter(year > 1989 & year < 2019)
length(unique(gdis_data_9018$DisNo.))
# 8115
gdis_data_9018_climate <- gdis_data_9018 %>%
    filter(disastertype %in% c(
        "flood", "storm", "extreme temperature ",
        "landslide", "drought", "mass movement (dry)"
    ))
length(unique(gdis_data_9018_climate$DisNo.))
# 7218

disasters_subnat_st <- disasters_subnat_st %>% mutate(year = as.integer(substr(DisNo., 1, 4)))
disasters_subnat_st_9018 <- disasters_subnat_st %>% filter(year > 1989 & year < 2019)
length(unique(disasters_subnat_st_9018$DisNo.))
# 7546

gdis_disno <- unique(gdis_data_9018$DisNo.)
geoclim_disno <- unique(disasters_subnat_st_9018$DisNo.)

common_events <- intersect(gdis_disno, geoclim_disno)
different_events <- setdiff(gdis_disno, geoclim_disno)

unfindable_events <- gdis_data_9018 %>%
    filter(DisNo. %in% different_events) %>%
    as.data.frame() %>%
    select(c(DisNo., disastertype, iso3, country)) %>%
    distinct() %>%
    filter(disastertype %in% c(
        "flood", "storm", "extreme temperature ",
        "landslide", "drought", "mass movement (dry)"
    ))

unfindable_events %>%
    filter(is.na(iso3)) %>%
    nrow() # 76 events
unfindable_events %>%
    select(c(country, iso3)) %>%
    distinct() %>%
    arrange(country) %>%
    group_by(country) %>%
    filter(n() > 1) %>%
    summarize(iso3_codes = paste(iso3, collapse = ", ")) %>%
    mutate(row_text = glue("Country: {country}, Iso code: {iso3_codes}")) %>%
    pull(row_text) %>%
    paste(collapse = " | ")

# 52 countries have 2 different iso3 codes


# comparison of mismatch --------------------------------------------------

compare_df %>%
    filter(DisNo. %in% common_events) %>%
    group_by(`Mismatch > 10%`) %>%
    tally()

# Mismatch > 10%`     n
# 1 FALSE             2785
# 2 TRUE              2835


compare_df %>%
    filter(DisNo. %in% common_events & geoD_geocoding_q == "[1]" & `Mismatch > 10%` == TRUE)
# 2,166 events
compare_df %>%
    filter(DisNo. %in% common_events & geoD_geocoding_q == "[1]" & `Mismatch > 10%` == FALSE)
# 2,198 events

compare_df %>%
    filter(DisNo. %in% common_events & geoD_geocoding_q == "[1]" & `Mismatch > 10%` == TRUE) %>%
    summarise(mean_mismatch = mean(`Mismatch Percentage`))


compare_df %>%
    filter(DisNo. %in% common_events & geoD_geocoding_q == "[1]" & `Mismatch > 10%` == TRUE &
        gdis_admin_level %in% c("['3']")) %>%
    summarise(mean_mismatch = mean(`Mismatch Percentage`))

index_distype <- gdis_data_9018 %>%
    as.data.frame() %>%
    select(c(DisNo., disastertype))

compare_disaster <- left_join(compare_df, index_distype)

compare_disaster %>%
    group_by(disastertype) %>%
    summarise(mean_mismatch = mean(`Mismatch Percentage`))

compare_disaster %>%
    group_by(disastertype) %>%
    summarise(median_mismatch = median(`Mismatch Percentage`))

compare_df %>%
    filter(`Mismatch > 10%` == TRUE) %>%
    ggplot(aes(x = `Total Area GeoD`, y = `Total Area GDIS`, color = `Mismatch Percentage`)) +
    geom_point() +
    xlab("geo-clim-data") +
    ylab("GDIS")

hist(compare_df$`Mismatch Percentage`, breaks = 100)


# compare plots -----------------------------------------------------------

sample_mismatch <- compare_df %>%
    filter(`Mismatch > 10%` == TRUE & geoD_geocoding_q == "[1]") %>%
    pull(DisNo.) %>%
    sample(8)


geoDisasters_sample <- disasters_subnat_st %>%
    filter(DisNo. %in% sample_mismatch) %>%
    select(c(DisNo., geom)) %>%
    mutate(database = "GeoDisasters")
gdis_sample <- gdis_data %>%
    filter(DisNo. %in% sample_mismatch) %>%
    select(c(DisNo., geom)) %>%
    mutate(database = "GDIS")

events_sample <- rbind(geoDisasters_sample, gdis_sample)

# library(tmap)
event_sample_plots <- events_sample %>%
    tm_shape() +
    tm_polygons(
        fill = "database", fill_alpha = 0.5, lwd = 0,
        title = "Database",
        textNA = ""
    ) +
    tm_facets("DisNo.")


event_sample_plots

tmap_save(
    event_sample_plots,
    filename = "figures/fig_5_event_sample_plots.png",
    width = 14, height = 8, dpi = 300, units = "in"
)


disasters_st %>%
    as.data.frame() %>%
    select(-(geom)) %>%
    filter(admin_level == "1 - 2")

disaster_centroids %>%
    as.data.frame() %>%
    select(-(geom)) %>%
    group_by(`Disaster Type`, admin_level) %>%
    # filter(admin_level == "1 - 2") %>%
    tally()
