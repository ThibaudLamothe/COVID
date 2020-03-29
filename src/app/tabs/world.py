############################################################################################
########################################## IMPORTS #########################################
############################################################################################

# Classic libraries
import numpy as np
import pandas as pd
from logzero import logger

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
ind = df_world.groupby('date').sum().sort_index().iloc[-1]
total_confirmed = ind['confirmed']
total_deaths = ind['deaths']
total_recovered = ind['recovered']

cvd = f.load_pickle('df_covid_from_guy_100.p')
cvd_dead = f.load_pickle('df_covid_dead_from_guy_10.p')
cvd_recovered = f.load_pickle('df_covid_recovered_from_guy_10.p')

def world_from_100(df):
    
    x = df.index
    
    # Add traces
    data = []
    for col in df.columns:
        y =df[col]
        data.append(go.Scatter(x=x, y=y,
            mode='lines+markers',
            name = col,
        ))
    return {'data':data}

def world_evolution_update(df=df_world):

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
    layout = go.Layout(width=500)
    return {'data':data, 'layout':layout}

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
                        html.Div(
                            children = ['Nombre de cas confirmés', html.Br(), total_confirmed],
                            id='confirmed_world_total',
                            className='main_indicateur'),
                        html.Div(children = ['Nombre de victimes', html.Br(), total_deaths], id='deaths_world_total', className='main_indicateur'),
                        html.Div(children = ['Nombre de soignés', html.Br(), total_recovered], id='recovered_world_total', className='main_indicateur'),
                       
                    ]
                ),
                html.Br(),


                # Line 2 : MAP - WORLD
                html.Div(
                    id='world_line_2',
                    children = [
                        dcc.Graph(id='world_map', figure=FIG_world, config={'scrollZoom': False}),
                        dcc.Graph(id='france_map', figure=FIG_france, config={'scrollZoom': False}),
                        # html.P('test')
                        ]
                ),
                html.Br(),
                
                # Line 3 : MAP - France / curves
                html.Div(
                    id='world_line_3',
                    children = [
                        # dcc.Graph(id='france_map', figure=FIG_france, config={'scrollZoom': False}),
                        # dcc.Graph(id='world_evolution_curves', figure=world_evolution_update(df_world)),
                        html.Div(dcc.Graph(id='world_evolution_curves', figure=world_from_100(cvd)),className='curves_world_final'), 
                        html.Div(dcc.Graph(id='world_evolution_curves_dead', figure=world_from_100(cvd_dead)),className='curves_world_final'), 
                        html.Div(dcc.Graph(id='world_evolution_curves_recovered', figure=world_from_100(cvd_recovered)),className='curves_world_final'), 
                        html.Div(
                            className='curves_world_final',
                            id='country_comparison_w',
                            children=[

                            
                                dcc.Dropdown(
                                    id='country_dropdown_w',
                                    options=[{'label': col, 'value': col} for col in cvd.columns],
                                ),
                                dcc.Graph(id='country_selection_w'),
                            ],
                            
                        ), 
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


# @app.callback(
#     Output('world_evolution_curves', 'figure'),
#     [Input(component_id='test_statut', component_property='value')])



@app.callback(
    Output('country_selection_w', 'figure'),
    [Input(component_id='country_dropdown_w', component_property='value')])
def see_country_state(country, df=df_world):
    
    # logger.debug('1')
    if country is None:
        country ='France'

    tmp = df.xs(country, level=1)
    # logger.debug('2')
    
    # Define x axis
    x = tmp.index
    # logger.debug('3')
    
    # Add traces
    data = []
    for col in tmp.columns:
        logger.debug(col)
    
        y = tmp[col].values
        data.append(go.Scatter(x=x, y=y,
            mode='lines+markers',
            name = col,
        ))
    # layout = go.Layout(width=500)
    return {'data':data} #, 'layout':layout}

    

 