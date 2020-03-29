# Imports
import pickle
import pandas as pd
import utils_covid as f
from logzero import logger


# Map informations
region_plotly = f.load_pickle('region_contours_geojson_plotly.p')
dept_plotly = f.load_pickle('dept_contours_geojson_plotly.p')


# Onglet hopitaux
df_h = f.load_pickle('df_sos_h.p')
df_f = f.load_pickle('df_sos_f.p')
df_t = f.load_pickle('df_sos_t.p')
age_conversion = f.load_pickle('age_transformation.p')


# Onglet Contamination
df_contamination_fr = f.load_pickle('df_contamination_fr.p')
options_region = f.load_pickle('radiobox_region.p')
dep_2_reg = f.load_pickle('dep_2_reg.p')
region_info = f.load_pickle('region_info_by_id.p')
fig_region_contamination = f.load_pickle('fig_fr_contamination_region.p')


# Onglet world
df_world = f.load_pickle('df_world.p')
df_world_fr = f.load_pickle('df_world_fr.p')

country_position = f.load_pickle('country_position.p')
region_info = f.load_pickle('region_info_by_id.p') # from contamination part
FIG_world = f.load_pickle('fig_world.p')
FIG_france = f.load_pickle('fig_france.p')
