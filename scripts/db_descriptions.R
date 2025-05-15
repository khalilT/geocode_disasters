library(tidyverse) # general utility functions
library(ggbreak)
library(sf) # plot map
sf_use_s2(FALSE)
library(rnaturalearth) # plot map
library(rnaturalearthdata) # plot map
library(patchwork)
library(here)

base_dir <- paste0(dirname(rstudioapi::getSourceEditorContext()$path), "/")
source(paste0(base_dir, "../src/utils/paths.R"))


disasters_national_st <- st_read(geocoded_national_path)


disasters_subnat_st <- st_read(geocoded_location_path)
emdat_df <- readxl::read_excel(emdat_path)

# disaster information nat. overlay
disasters_df <- disasters_national_st %>%
  as.data.frame() %>%
  select(-geom)
disasters_df <- left_join(disasters_df, emdat_df, by = "DisNo.")

# disaster information subnational
disasters_subnat_df <- disasters_subnat_st %>%
  as.data.frame() %>%
  select(-c(geom))
disasters_subnat_df <- left_join(disasters_subnat_df, emdat_df, by = "DisNo.")

# Event evolution distribution --------------------------------------------


continent_plot <- disasters_df %>%
  ggplot(aes(x = `Start Year`, fill = Region)) +
  geom_bar() +
  scale_fill_viridis_d("Continent") +
  ylab("Event count") +
  xlab("") +
  theme(text = element_text(size = 16))


type_plot <- disasters_df %>%
  ggplot(aes(x = `Start Year`, fill = `Disaster Type`)) +
  geom_bar() +
  scale_fill_viridis_d("Disaster Type", option = "A") +
  ylab("Event count") +
  xlab("Year") +
  theme(
    text = element_text(size = 16),
    legend.text = element_text(size = 12)
  )

event_distribution <- (continent_plot / type_plot)
ggsave(
  "figures/fig_2_event_distribution.png",
  event_distribution,
  width = 16, height = 10, dpi = 300, units = "in"
)


length(unique(disasters_df$Country))


round((table(disasters_df$geocoding_q) / 9217) * 100, 2)

# Quality flags plot ------------------------------------------------------

# disaster scale
quality_df <- disasters_df %>%
  count(geocoding_q, name = "events") %>% # events per flag
  mutate(pct = (events / sum(events)) * 100) # share of total

quality_df <- quality_df %>%
  mutate(geocoding_q = case_when(
    geocoding_q == "1" ~ "1 - Highest",
    geocoding_q == "2" ~ "2 - High",
    geocoding_q == "3" ~ "3 - Medium",
    geocoding_q == "4" ~ "4 - Low"
  ))

quality_plot <- ggplot(
  quality_df,
  aes(x = factor(geocoding_q), y = pct)
) +
  geom_col(fill = "#595959") + # dark-grey bars
  geom_text(aes(label = round(pct, 2)),
    vjust = -0.3, colour = "tomato", size = 6
  ) +
  geom_text(aes(label = events), y = 1, colour = "white", size = 5) +
  scale_y_break(c(25, 70),
    ticklabels = c(0, 10, 20, 70, 80, 90, 100),
    scales = "free"
  ) +
  ylim(0, 100) +
  labs(x = "Quality flag", y = "Share of events(%)") +
  theme_minimal(base_size = 16) +
  theme(
    plot.margin = margin(5.5, 12, 5.5, 5.5),
    axis.title.y.right = element_blank(),
    axis.text.y.right = element_blank(),
    axis.ticks.y.right = element_blank()
  )

ggsave(
  "figures/fig_3_qualityflags.png",
  quality_plot,
  width = 14, height = 8, dpi = 300, units = "in"
)
# location scale
quality_location_df <- disasters_subnat_df %>%
  count(geocoding_q, name = "events") %>% # events per flag
  mutate(pct = (events / sum(events)) * 100) # share of total

quality_location_df <- quality_location_df %>%
  mutate(geocoding_q = case_when(
    geocoding_q == "1" ~ "1 - Highest",
    geocoding_q == "2" ~ "2 - High",
    geocoding_q == "3" ~ "3 - Medium",
    geocoding_q == "4" ~ "4 - Low"
  ))


quality_location_plot <- ggplot(
  quality_location_df,
  aes(x = factor(geocoding_q), y = pct)
) +
  geom_col(fill = "#595959") + # dark-grey bars
  geom_text(aes(label = round(pct, 2)),
    vjust = -0.3, colour = "tomato", size = 6
  ) +
  geom_text(aes(label = events), y = 0.5, colour = "white", size = 5) +
  scale_y_break(c(15, 75),
    ticklabels = c(0, 10, 20, 70, 80, 90, 100),
    scales = "free"
  ) +
  ylim(0, 100) +
  labs(x = "Quality flag", y = "Share of events(%)") +
  theme_minimal(base_size = 16) +
  theme(
    plot.margin = margin(5.5, 12, 5.5, 5.5),
    axis.title.y.right = element_blank(),
    axis.text.y.right = element_blank(),
    axis.ticks.y.right = element_blank()
  )


ggsave(
  "figures/fig_S1_quality_location_flags.png",
  quality_location_plot,
  width = 14, height = 8, dpi = 300, units = "in"
)


# plot disaster distribution map ------------------------------------------

# map distribution
disaster_centroids <- st_centroid(disasters_national_st)
coordinates <- disaster_centroids %>% st_coordinates()
disaster_centroids$lon <- coordinates[, 1]
disaster_centroids$lat <- coordinates[, 2]

disaster_centroids <- left_join(disaster_centroids, emdat_df, by = "DisNo.")

disaster_centroids <- disaster_centroids %>% mutate(`Disaster Type` = case_when(
  `Disaster Type` == "Mass movement (wet)" ~ "Mass movement",
  `Disaster Type` == "Mass movement (dry)" ~ "Mass movement",
  `Disaster Type` != "Mass movement" ~ `Disaster Type`
))
disaster_centroids <- disaster_centroids %>% mutate(`Disaster Type` = factor(`Disaster Type`,
  levels = c(
    "Flood", "Storm", "Mass movement",
    "Extreme temperature", "Wildfire", "Drought"
  )
))

count_labels <- disaster_centroids %>%
  group_by(`Disaster Type`) %>%
  st_set_geometry(NULL) %>%
  count(`Disaster Type`) %>%
  mutate(label = paste0(`Disaster Type`, " (n = ", n, ")")) %>%
  with(setNames(label, `Disaster Type`))

# load geographic details for maps
coastlines <- ne_coastline(scale = "medium", returnclass = "sf")
shp_countries <- ne_countries(scale = "medium", returnclass = "sf")

disaster_distribution <- disaster_centroids %>%
  ggplot() +
  ggplot2::geom_sf(data = shp_countries, lwd = 0.2, color = "grey90", fill = "grey97") +
  ggplot2::geom_sf(data = coastlines, lwd = 0.1, color = "grey10") +
  geom_sf(
    data = disaster_centroids, aes(color = `Disaster Type`),
    color = "darkred", pch = 19, size = 0.2, show.legend = FALSE
  ) +
  facet_wrap(~`Disaster Type`, ncol = 2, labeller = as_labeller(count_labels)) +
  labs(y = NULL, x = NULL) +
  coord_sf(crs = st_crs("ESRI:54034")) +
  cowplot::theme_minimal_grid() +
  theme(
    strip.text = element_text(size = 14, hjust = 0, face = "bold"),
    panel.spacing = unit(0, "lines")
  )

disaster_distribution

ggsave(
  "figures/fig_1_disaster_distribution.png",
  disaster_distribution,
  width = 14, height = 8, dpi = 300, units = "in"
)


# hurricane IRMA ----------------------------------------------------------

# gdis_data <- st_read("/net/projects/xaida/project_data/gdis/gdis_1990_2020.gpkg")
gdis_data <- st_read(gdis_path)
disasterno <- gdis_data %>% unite("Dis.No", disasterno, iso3, sep = "-")
gdis_data <- gdis_data %>% mutate(year = as.integer(substr(disasterno, 1, 4)))
gdis_data$DisNo. <- disasterno$Dis.No


library(basemapR)

event <- valid_disasters %>% filter(`DisNo.` == "2017-0381-USA")
bbox <- expand_bbox(st_bbox(event), X = 0, Y = 150000)

irma_impacts <- ggplot() +
  base_map(bbox, increase_zoom = 5, basemap = "google-terrain") +
  geom_sf(data = event, fill = "tomato") +
  scale_x_continuous(breaks = c(-80, -81, -82))

event_gdis <- gdis_data %>% filter(DisNo. == "2017-0381-USA")
bbox_gdis <- expand_bbox(st_bbox(event_gdis), X = 0, Y = 150000)

irma_impacts_gdis <- ggplot() +
  base_map(bbox_gdis, increase_zoom = 5, basemap = "google-terrain") +
  geom_sf(data = event_gdis, fill = "tomato")


hurricane_irma <- (irma_impacts_gdis | irma_impacts) + plot_annotation(tag_levels = "a")

ggsave(
  "figures/fig_5_hurricane_irma.png",
  hurricane_irma,
  width = 14, height = 8, dpi = 300, units = "in"
)


# Admin level counts ------------------------------------------------------


proportion_admin_level <- disasters_subnat_df %>%
  mutate(admin_level = factor(admin_level, levels = c("1", "2"))) %>%
  ggplot(aes(x = `Start Year`)) +
  geom_bar(position = "fill", aes(fill = admin_level)) +
  scale_fill_brewer("Administrative Level", palette = "Set1") +
  facet_wrap(~Region, ncol = 1) +
  labs(x = "", y = "") +
  theme_minimal() +
  theme(
    legend.position = "bottom",
    text = element_text(size = 18)
  )

ggsave(
  "figures/fig_S2_proportion_admin_level.png",
  proportion_admin_level,
  width = 14, height = 8, dpi = 300, units = "in"
)


# Boxplot area ------------------------------------------------------------


library(dplyr)
library(ggplot2)
library(scales)

year_region <- disasters_df %>% select(c(`DisNo.`, `Start Year`, Region))

disasters_subnat_info <- left_join(disasters_subnat_st, year_region)

disasters_subnat_info["area"] <- st_area(disasters_subnat_info)
disasters_subnat_info <- disasters_subnat_info %>%
  mutate(
    area_km2 = as.numeric(area / 1e6),
    area = as.numeric(area)
  ) %>%
  select(-c(geom)) %>%
  as.data.frame()


df <- disasters_subnat_info %>%
  mutate(admin_level = factor(admin_level, levels = c("1", "2")))

# global medians by admin_level
global_meds <- df %>%
  group_by(admin_level) %>%
  summarize(med = median(area_km2), .groups = "drop")

subnation_regions_plot <- ggplot(df, aes(x = admin_level, y = area_km2, fill = admin_level)) +
  geom_violin(alpha = 0.4, width = 0.8, show.legend = FALSE) +
  geom_boxplot(width = 0.2, outlier.shape = NA, colour = "black", show.legend = TRUE) +
  geom_jitter(width = 0.05, size = 0.25, alpha = 0.1, colour = "grey30", show.legend = FALSE) +

  # ← here’s the trick: draw a dashed line at each global median
  geom_hline(
    data = global_meds,
    aes(yintercept = med, colour = admin_level),
    linetype = "dashed",
    size = 0.7,
    show.legend = FALSE
  ) +
  scale_y_log10(labels = comma, limits = c(1, 4e6)) +
  facet_wrap(~Region, scales = "free_y", ncol = 5) +
  scale_fill_brewer(
    palette = "Set1", name = "Admin level",
    labels = c("1" = "Level 1", "2" = "Level 2")
  ) +
  scale_colour_brewer(palette = "Set1") +
  guides(colour = "none") +
  theme_minimal() +
  theme(
    legend.position = "right",
    text = element_text(size = 18)
  ) +
  labs(
    title = "Area distribution by admin level (with global medians)",
    x = "Admin level",
    y = "Area (km², log scale)"
  )


ggsave(
  "figures/fig_S3_subnation_regions_plot.png",
  subnation_regions_plot,
  width = 14, height = 8, dpi = 300, units = "in"
)


# DB - information --------------------------------------------------------

# number of countries and territories
disasters_df %>%
  pull(Country) %>%
  unique() %>%
  length()

disasters_df %>%
  group_by(ISO.x, `Disaster Type`) %>%
  mutate(
    `Disaster Type` = case_when(
      `Disaster Type` == "Mass movement (wet)" ~ "Mass movement",
      `Disaster Type` == "Mass movement (dry)" ~ "Mass movement",
      `Disaster Type` != "Mass movement" ~ `Disaster Type`
    ),
    `Disaster Type` = factor(`Disaster Type`,
      levels = c(
        "Flood", "Storm", "Mass movement",
        "Extreme temperature", "Wildfire", "Drought"
      )
    )
  ) %>%
  tally() %>%
  pivot_wider(names_from = `Disaster Type`, values_from = n, values_fill = 0) %>%
  mutate(total = sum(c_across(Flood:Wildfire))) %>%
  rename(
    Mass_movement = `Mass movement`,
    Extreme_temperature = `Extreme temperature`,
    ISO = ISO.x
  ) %>%
  filter(!is.na(ISO)) %>%
  xtable::xtable()

disasters_df %>%
  filter(is.na(ISO.x)) %>%
  pull(Country)
