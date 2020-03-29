############################################################################################
########################################## IMPORTS #########################################
############################################################################################

# Classic libraries
import numpy as np
import pandas as pd


# Dash imports
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
from plotly import graph_objs as go


# Load data
from app import app
import utils_covid as f
from load import df_world, df_world_fr
from load import FIG_france, FIG_world
from load import country_position, region_info

############################################################################################
####################################### TAB COMPONENT ######################################
############################################################################################


############################################################################################
####################################### TAB STRUCTURE ######################################
############################################################################################

tab_w = dcc.Tab(
    label="Cas de contaminations dans le monde",
    value="world",

    children=[
        html.Div(
            id='world_content',
            children=[


                # Line 1 : KPIS - World
                html.Div(
                    id='world_line_1',
                    children = [ 
                        html.Div(children = ['Cas confirme', 10000], id='jour_confirme_', className='main_indicateur'),
                        html.Div(children = ['Cas confirme', 10000], id='jour_confirme__', className='main_indicateur'),
                        # html.Div(children = ['Cas confirme', df_today['cas_confirme']], id='jour_confirme_', className='main_indicateur'),
                        # html.Div(children = ['Guérisons', df_today['nb_actuellement_hospitalises']], id='jour_rentre_', className='main_indicateur'),
                        # html.Div(children = ['Deces', df_today['nb_actuellement_en_soins_intensifs']], id='jour_decede_', className='main_indicateur'),
                        
                    ]
                ),
                html.Br(),

                # Line 2 : MAP - WORLD
                html.Div(
                    id='world_line_2',
                    children = [ dcc.Graph(id='world_map', figure=FIG_world, config={'scrollZoom': False}),]
                ),
                html.Br(),
                
                # Line 3 : MAP - France / curves
                html.Div(
                    id='world_line_3',
                    children = [
                        dcc.Graph(id='france_map', figure=FIG_france, config={'scrollZoom': False}),
                        dcc.Graph(id='world_evolution_curves'),
                    ]
                ),
            ]
        )
    ]
)

############################################################################################
######################################  FUNCTIONS ##########################################
############################################################################################



############################################################################################
######################################  CALLBACKS ##########################################
############################################################################################



@app.callback(
    Output('world_evolution_curves', 'figure'),
    [Input(component_id='test_statut', component_property='value')])

def world_evolution_update(radio, df=df_world):

    jour = df.index.levels[0].max()
    max_countries = df.xs(jour)['confirmed'].sort_values(ascending=False).index[:10].tolist()
    tmp = df.reset_index()[df.reset_index()['subzone'].isin(max_countries)].groupby(['subzone', 'date']).sum()

    # Define x axis
    x = tmp.index.levels[1].tolist()
    
    # Add traces
    data = []
    for i in max_countries:
        y = tmp.xs(i)['confirmed'].values
        data.append(go.Scatter(x=x, y=y,
            mode='lines+markers',
            name = i,
        ))
    return {'data':data}

