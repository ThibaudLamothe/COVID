############################################################################################
########################################## IMPORTS #########################################
############################################################################################

# Classic libraries
import pandas as pd
import numpy as nppip 
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

from load import region_plotly, age_conversion
from load import df_h, df_f, df_t


############################################################################################
####################################### TAB CONTENT ########################################
############################################################################################


radio_h_f = dcc.RadioItems(
            options=[
                {'label': 'Tous', 'value': 'All'},
                {'label': 'Homme', 'value': 'H'},
                {'label': 'Femme', 'value': 'F'}
            ],
            value='All',
            id='radio_sex'
        )
        
radio_type_1 = dcc.RadioItems(
            options=[
                {'label': 'SOS - Actes', 'value': 'sos_tot'},
                {'label': 'SOS - Actes Corona', 'value': 'sos_susp'},
                {'label': 'Urgences - Total', 'value': 'urg_tot'},
                {'label': 'Urgences - Corona', 'value': 'urg_susp'},
                {'label': 'Urgences - Corona Hospitalisation', 'value': 'urg_hosp'}
            ],
            value='urg_susp',
            id='radio_type',
            labelStyle={'display': 'inline-block'},
        )

############################################################################################
####################################### TAB STRUCTURE ######################################
############################################################################################



tab_h = dcc.Tab(
    label="Saturation des hopitaux Français",
    value="hopitaux",
    id='global_tab',
    children=[

        html.Div(className='All', id='current_sex'),
        html.Div(className='2020-03-20', id='current_day'),
        html.Div(className='test', id='test'),
        
        # Radio H/F/TOUS
        radio_h_f,

        html.Div(
            id='content_tab',
            children=[

                # Content
                html.Div(
                    id='left_part',
                    children=[
                        # Radio selection carte
                        radio_type_1,
                        # radio_type_2,
                        
                        # Carte Region
                        dcc.Graph(id='map', config={'scrollZoom': False}),

                        # Updatable variables
                        html.Div(
                            id='updatable',
                            children=[

                                # Histo Age
                                dcc.Graph(id='age_malade'),

                                # Pie Chart H/G
                                dcc.Graph(id='sexe_malade'),
                            ]
                        )
                    ]
                ),
                html.Div(
                    id='right_part',
                    children=[
                        # SOS medecin
                        dcc.Graph(id='sos_medecin'),

                        # Hopitaux
                        dcc.Graph(id='hopitaux'),
                    ]
                )
            ]
        )
    ]
)

############################################################################################
######################################  Functions ##########################################
############################################################################################



def get_sexe_df(sexe, df_t=df_t, df_h=df_h, df_f=df_f):
    if sexe=='H':
        return df_h
    if sexe=='F':
        return df_f
    return df_t

  
def get_age_region(df, jour='2020-03-21', region=11, col='urg_susp', age_conversion=age_conversion):
    if region is None:
        tmp = df.xs(jour).groupby('age')[col].sum()
    else:
        tmp = df.xs(jour).xs(region)[col]
    
    tmp = tmp.loc[['__15', '15_44', '45_64', '65_74', '74__', 'all']]
    ages = tmp.index.tolist()
    labels = [age_conversion['value_2_label'][age] for age in ages]
    values = tmp.values
    return labels, values

def get_sexe_region(jour='2020-03-21', region=11, col='urg_susp', df_f=df_f, df_h=df_h):
    if region is None:
        h = df_h.xs(jour).xs('all', level=1)[col].sum()
        f = df_f.xs(jour).xs('all', level=1)[col].sum()
    else:
        h = df_h.xs(jour).xs(region).xs('all')[col]
        f = df_f.xs(jour).xs(region).xs('all')[col]
    
    x = [h, f]
    y = ['Hommes', 'Femmes']
    return x, y

def get_map_info(df, jour, col):
    tmp = df.xs(jour).xs('all', level=1)[[col, 'lat','lon']]
    tmp = tmp.reset_index()
    return tmp


def get_infra_info(df, sexe):
    tmp = df.xs('all', level=2).groupby('date').sum()
    
    urg_col = ['urg_tot', 'urg_susp', 'urg_hosp']
    urg = tmp[urg_col]

    sos_col = ['sos_tot', 'sos_susp']
    sos = tmp[sos_col]
    return urg, sos

############################################################################################
######################################  Callbacks ##########################################
############################################################################################

# Knowing current sex information
@app.callback(
    Output('current_sex', 'className'),
    [Input(component_id='radio_sex', component_property='value')])
def change_sexe(sex):
    logger.info('Changement de sexe : {}'.format(sex))
    return sex


# Map information
@app.callback(
    Output('map', 'figure'),
    [Input(component_id='radio_type', component_property='value')],
    [State(component_id='current_sex', component_property='className'),
    State(component_id='current_day', component_property='className')]
    )

def update_map(col, sexe, jour, region_plotly=region_plotly):
    # logger.debug('update map')
    df = get_sexe_df(sexe)
    df = get_map_info(df, jour, col)
    df['code_region'] = df['code_region'].apply(str)
    # logger.debug(df.head())
    f.save_pickle(df, 'df_debug.p')

    max_value = df[col].max()

    fig = px.choropleth_mapbox(
        df, geojson=region_plotly,
        locations='code_region',
        color=col,
        color_continuous_scale="oranges",
        range_color=(0, max_value),
        mapbox_style="carto-positron",
        zoom=4.5, center = {"lat": 47.86, "lon": 2.15},
        opacity=0.5,
        #labels={'unemp':'unemployment rate'}
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
    # clickmode='event+select'
    )
    return fig


# Sexe information
@app.callback(
    Output('sexe_malade', 'figure'),
    [Input(component_id='radio_type', component_property='value'),
    Input('map', 'hoverData')],
    [State(component_id='current_day', component_property='className')],
    )
def count_sexe(col, clickData, jour, df_f=df_f, df_h=df_h):
    
    region = None
    if clickData:
        region = clickData['points'][0]['location']
        logger.debug(region)
        region = int(region)

    x, y = get_sexe_region(jour, region=region, col=col, df_f=df_f, df_h=df_h)

    data=[go.Pie(
        labels=y,
        values=x,
        # width=100,
        hoverinfo='value',
        textinfo='percent+label',
        textfont_size=10,
        showlegend=False,
        #hole=.5
        #marker=dict(colors=colors, line=dict(color='#000000', width=2))
    )]

    layout =  go.Layout(
        width=200,
        height=200,
        margin={"r":30,"t":30,"l":30,"b":30}
        )
    return {'data':data, 'layout':layout}



# Age information
@app.callback(
    Output('age_malade', 'figure'),
    [Input(component_id='radio_type', component_property='value'),
        Input('map', 'hoverData')],
    [State(component_id='current_day', component_property='className'),
    State(component_id='current_sex', component_property='className')],
    )
def count_age(col, clickData, jour, sexe):

    region = None
    if clickData:
        region = clickData['points'][0]['location']
        logger.debug(region)
        region = int(region)

    df = get_sexe_df(sexe)
    labels, values = get_age_region(df, jour=jour, region=region, col=col, age_conversion=age_conversion)
    
    data=[go.Bar(
        x=labels,
        y=values,
    
        #textinfo='percent+label',
        #textfont_size=10,
        #showlegend=False,
        #hole=.5
        #marker=dict(colors=colors, line=dict(color='#000000', width=2))
    )]



    layout =  go.Layout(
        width=200,
        height=200,
        margin={"r":30,"t":30,"l":30,"b":30}
        )
    return {'data':data, 'layout':layout}



# Occupation in sos and hospitals
@app.callback(
    [
    Output('hopitaux', 'figure'),
    Output('sos_medecin', 'figure')
    ],
    [Input(component_id='current_sex', component_property='className')],
    )
def plot_occup(sexe):
    
    df = get_sexe_df(sexe)
    urg, sos = get_infra_info(df, sexe)

    x = urg.index
    data =[]
    for i in urg.columns:
        y = urg[i]
        data.append(go.Scatter(x=x, y=y, name=i))
    fig_urg = {'data':data}

    x = sos.index
    data =[]
    for i in sos.columns:
        y = sos[i]
        data.append(go.Scatter(x=x, y=y, name=i))
    # layout = go.Layout(clickmode='event+select')
    fig_sos = {'data':data, 'layout':{'clickmode': 'event+select'}}
    # fig_sos.update_layout(clickmode='event+select')

    return fig_urg , fig_sos



@app.callback(
    Output('test', 'className'),
    [
        # Input('sos_medecin', 'clickData'),
    Input('map', 'clickData')
    ])
def display_click_data(hover):
    logger.error(hover)
    # logger.error(clickData)
    return 'json.dumps(clickData, indent=2)'
