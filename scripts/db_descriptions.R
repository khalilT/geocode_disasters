library(tidyverse) # general utility functions
library(caret)#extract
library(here)
library(DALEX)
library(sf)#plot map
library(rnaturalearth)#plot map
library(rnaturalearthdata)#plot map
library(patchwork)

base_dir <- paste0(dirname(rstudioapi::getSourceEditorContext()$path),"/")
source(paste0(base_dir,"../src/utils/paths.R"))

disasters_df <- st_read(geocoded_national_path)

disasters_df <- disasters_df %>% as.data.frame() %>% select(-geom)
disasters_df


continent_plot <- disasters_df %>%
  ggplot(aes(x=year,fill=continent))+
  geom_bar()+
  scale_fill_viridis_d("Continent")+ylab("")+xlab("")+
  theme(text = element_text(size=16))



type_plot <- disasters_df %>%
  ggplot(aes(x=year,fill=disaster_type))+
  geom_bar()+
  scale_fill_viridis_d("Disaster Type",option = "A")+ylab("")+
  theme(text = element_text(size=16),
        legend.text = element_text(size=12))

continent_plot / type_plot


length(unique(disasters_df$country))


round((table(disasters_df$geocoding_q) / 8505) * 100,2)


disasters_df %>%
  ggplot(aes(geocoding_q))+
  geom_bar(stat = "count")+ylab("")+xlab("Quality flags")+
  stat_count(geom = "label", colour = "tomato", size = 7,
             aes(label = round(..count.. / 9217 * 100,2)),position=position_stack(vjust=1))+
  theme_minimal()+
  theme(text = element_text(size=28))



disasters_df %>% 
  ggplot(aes(area_km2))+
  geom_histogram(bins = 500)+
  geom_vline(xintercept = 30000, color="red")+
  annotate("text", x=30000, y=2000, angle=90,vjust=1,label="More text", size=9, color="red")+
  geom_vline(xintercept = 500000, color="red")+
  annotate("text", x=500000, y=2000, angle=90,vjust=1,label="More text", size=9, color="red")+
  geom_vline(xintercept = 1000000, color="red")+
  annotate("text", x=1000000, y=2000, angle=90,vjust=1,label="More text", size=9, color="red")
  