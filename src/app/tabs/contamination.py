############################################################################################
########################################## IMPORTS #########################################
############################################################################################

# Classic libraries
import numpy as np
import pandas as pd
from logzero import logger

# Dash imports
import dash
import dash_daq as daq
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
from plotly.subplots import make_subplots
from plotly import graph_objs as go

# Load data
from app import app
import utils_covid as f
from load import df_contamination_fr as df
from load import region_plotly, options_region, region_info, dep_2_reg
from load import fig_region_contamination

JOUR = df.index.levels[0].max()
REGIONS = df.index.levels[1].tolist()
DF_TODAY = df.xs(JOUR).sum()


############################################################################################
####################################### TAB CONTENT ######################################
############################################################################################


# def create_global_kpis(texte, id_):
#     return  html.Div(
#         id=id_,
#         className='main_indicateur',
#         children = [
#             texte,
#             html.P(id_, id='{}_value'.format(id_) )
#             ],
#         )


region_radiobox = dcc.RadioItems(
    id='region_radiobox_contamination',
    options=options_region,
    value=None,
) 

# date_du_jour = create_global_kpis('Jour', 'jour_contamination')
# confirmes = create_global_kpis('Cas confirme', 'nb_confirme_c')
# hospitalises = create_global_kpis('Actuellement hospitalises', 'nb_actuellement_hospitalises_c')
# intensifs = create_global_kpis('Actuellement soins intensifs', 'nb_actuellement_en_soins_intensifs_c')
# soignes = create_global_kpis('Cas soignés', 'nb_soignes_c')
# decedes = create_global_kpis('Cas décédés', 'nb_deecdes_c')

date_du_jour = html.Div(children = ['Date du jour : ', html.Br(), JOUR], id='date_du_jour', className='main_indicateur')
confirmes = html.Div(children = ['Cas confirme', html.Br(),  DF_TODAY['cas_confirme']], id='jour_confirme', className='main_indicateur')
hospitalises = html.Div(children = ['Actuellement hospitalises', html.Br(),  DF_TODAY['nb_actuellement_hospitalises']], id='jour_rentre', className='main_indicateur')
intensifs = html.Div(children = ['Actuellement soins intensifs', html.Br(),  DF_TODAY['nb_actuellement_en_soins_intensifs']], id='jour_decede', className='main_indicateur')
soignes = html.Div(children = ['Cas soignés', html.Br(),  DF_TODAY['total_retour_a_domicile']], id='jour_hospitalise', className='main_indicateur')
decedes = html.Div(children = ['Cas décédés', html.Br(),  DF_TODAY['total_deces']], id='jour_intensif', className='main_indicateur')


button_superposition = daq.ToggleSwitch(
    id='toggle_cumul_curves',
    value=False,
    label=['', 'Par région'],
)

dropdown_day = dcc.Dropdown(
        id='day_dropdown_c',
        options=[{'label': i, 'value': i} for i in df.index.levels[0]],
        value=JOUR
    )

button_tte_fr = html.Button('Toute la France', id='button_toute_france')


############################################################################################
####################################### TAB STRUCTURE ######################################
############################################################################################


tab_fr = dcc.Tab(
    label="Cas de contaminations en France",
    value="contamination",
    id='contamination_tb',
    children=[

        # Jour actuel
        html.Div(className=JOUR, id='current_day_c'),


        # Indicateurs sur toute la France
        html.Div(
            id='france_indicateurs',
            children =[date_du_jour, confirmes, hospitalises, intensifs,  soignes, decedes]
        ),

        # Lignes de filtres
        html.Div(
            id='further_selection',
            children =[
                button_tte_fr,
                dropdown_day,
                button_superposition,
            ]
        ),

        # Partie de restitution
        html.Div(
            id='graph_contamination',
            children=[

                # Partie de Gauche
                html.Div(
                    id='left_part_c',
                    children=[

                        # Gauche Haut (Selection + Map)
                        html.Div(
                            id='upper_left',
                                children=[

                                html.Div(
                                    id='selection_part',
                                    children=[
                                        region_radiobox,
                                    ]
                                ),
                                html.Div(
                                    id='map_part',
                                    children=[
                                        dcc.Graph(id='map_contamination', figure=fig_region_contamination),
                                    ]
                                ),
                            ]
                        ),

                        # Gauche Bas (KPIS adaptés par région)
                        html.Div(
                            id='kpi_part',
                            children=[
                                html.Div(id='local_confirme', className='local_indicateur'), #+HF (pct)
                                html.Div(id='local_rentre', className='local_indicateur'), #+HF
                                html.Div(id='local_decede', className='local_indicateur'), #+HF
                                html.Div(id='local_hospitalise', className='local_indicateur'),
                                html.Div(id='local_intensif', className='local_indicateur'),
                            ]
                        ),
                    ]
                ),

                # Partie de droite
                html.Div(
                    id='right_part_c',
                    children=[
                        # Graphique
                        html.Div(
                            id = 'right_haut_c',
                            children=[dcc.Graph(id='cas_contamination_fr'),]
                        ),
                        
                        html.Div(
                            id = 'right_bas_c',
                            children=[
                                dcc.Graph(id='cas_contamination_fr_faible'),
                                dcc.Graph(id='cas_soins_fr'),
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)


############################################################################################
######################################  FUNCTIONS ##########################################
############################################################################################

def get_map_info_contamination(df, jour, col, region):
    if region is None:
        tmp = df.loc[jour][col].reset_index()
        tmp['code_region'] = tmp['code_region'].apply(str)
        # return tmp
    else:
        tmp = df.loc[jour].loc[region][col]
        tmp = pd.DataFrame({'code_region':[str(region)], col:[tmp]})
        # return tmp

    locations = np.array(tmp['code_region'].values)
    z = np.array(tmp[col].values)
    return locations, z

############################################################################################
######################################  CALLBACKS ##########################################
############################################################################################






# def caculate_kpis(df, region, jour):

#     if region is None:
#         tmp = df.xs(jour).sum()
#     else:
#         tmp = df.xs(jour).loc[region]#.sum()

#     # Calculate
#     confirme = tmp.loc['cas_confirme']
#     deces = tmp['total_deces']
#     domicile = tmp['total_retour_a_domicile']
#     intensifs = tmp['nb_actuellement_en_soins_intensifs']
#     hospit = tmp['nb_actuellement_hospitalises']


#     return confirme, domicile, deces, hospit, intensifs

###############################
# Update checkbox with no value
###############################
@app.callback(
    Output('region_radiobox_contamination', 'value'),  
    [Input(component_id='button_toute_france', component_property='n_clicks')],
    )
def update_checkbox(n_clicks, regions=REGIONS):
    return None


@app.callback(
    Output('current_day_c', 'className'),  
    [
    Input(component_id='day_dropdown_c', component_property='value')],
    )
def update_current_day(value, regions=REGIONS):
    return value


@app.callback(
    [
        Output('toggle_cumul_curves', 'disabled'),  
        Output('toggle_cumul_curves', 'value'),
        Output('toggle_cumul_curves', 'className'),  
    ],
    [Input(component_id='region_radiobox_contamination', component_property='value')],
    )
def update_toggle_visibility(value):
    if value is None:
        return False, False, 'toggle'
    return True, False, 'disabled'



###############################
# Local KPIs
###############################
@app.callback(
    [
        Output('local_confirme', 'children'),
        Output('local_rentre', 'children'),
        Output('local_decede', 'children'),
        Output('local_hospitalise', 'children'),
        Output('local_intensif', 'children'),
        
    ],
    [Input(component_id='region_radiobox_contamination', component_property='value'),
    Input(component_id='current_day_c', component_property='className')
    ],
    # [State(component_id='current_day', component_property='className')]
    )
def update_local_kpis(region, jour, df=df):
    if region is None:
        tmp = df.xs(jour).sum()
    else:
        tmp = df.xs(jour).loc[region]#.sum()

    # Calculate
    confirme = tmp.loc['cas_confirme']
    deces = tmp['total_deces']
    domicile = tmp['total_retour_a_domicile']
    intensifs = tmp['nb_actuellement_en_soins_intensifs']
    hospit = tmp['nb_actuellement_hospitalises']
    return confirme, domicile, deces, hospit, intensifs

###############################
# Map information
###############################
@app.callback(
    Output('map_contamination', 'figure'),
    [Input(component_id='region_radiobox_contamination', component_property='value'),
     Input(component_id='current_day_c', component_property='className')],
    [
        # State(component_id='current_day', component_property='value'),
    State(component_id='map_contamination', component_property='figure')],
    )

def update_map_contamination(region, jour, fig, col='cas_confirme', df=df):

    locations, z = get_map_info_contamination(df, jour, col, region)

    fig['data'][0]['locations'] = locations 
    fig['data'][0]['z'] = z 
    # fig['layout']['coloraxis']['cmax']

    return fig


def get_graph_1(df, size, sep=False):





    if sep:
        tmp = df.copy()
        data1 = []
        for i in tmp.reset_index()['code_region'].unique():
            x_ = tmp.xs(i, level=1).index
            y = tmp.xs(i, level=1)['cas_confirme'].values

            data1.append(
                go.Scatter(x=x_, y=y,  mode='lines+markers', marker=dict(size=size), name = region_info[i]['region']),
            )
        return data1

    x = df.index
    tmp = df.copy()
    data1 =[
        go.Scatter(x=x, y=tmp['cas_confirme'].values, mode='lines+markers', marker=dict(size=size), name = 'contamines'),
        go.Scatter(x=x, y=tmp['nb_actuellement_hospitalises'].values,  mode='lines+markers', marker=dict(size=size), name = 'hospit ajd'),
        go.Scatter(x=x, y=tmp['nb_actuellement_en_soins_intensifs'].values,  mode='lines+markers', marker=dict(size=size), name = 'soins intenses ajd'),  
    ]
    return data1

    
def get_graph_2(tmp, size):
    x = tmp.index
    data2 = [
        go.Scatter(x=x, y=tmp['total_retour_a_domicile'].values, mode='lines+markers', marker=dict(size=size), name = 'retour maison'),
        go.Scatter(x=x, y=tmp['total_deces'].values, mode='lines+markers', marker=dict(size=size),name = 'deces')
    ]

    data3 = [
        go.Scatter(x=x, y=tmp['service_covid'].values,mode='lines+markers', marker=dict(size=size), name = 'services ouverts'),
    ]

    return data2, data3

###############################
# Evolution contaminees/morts/soignes
###############################
@app.callback(
    [
        Output('cas_contamination_fr', 'figure'),
        Output('cas_contamination_fr_faible', 'figure'),
        Output('cas_soins_fr', 'figure'),
    ],
    [
        Input(component_id='region_radiobox_contamination', component_property='value'),
        Input(component_id='toggle_cumul_curves', component_property='value'),
        Input(component_id='current_day_c', component_property='className'),
    ])
def plot_cas_contamination(region, sep=False, jour=JOUR, df=df):  

    jours = df.index.levels[0].tolist()
    size = [20 if i== jour else 10 for i in jours]


    if region:
        sep=False
        tmp = df.xs(region, level=1)
        data1 = get_graph_1(tmp, size, sep)
        data2, data3 = get_graph_2(tmp, size)
    else:
        if sep:
            tmp = df.copy()
            data1 = get_graph_1(tmp, size, sep)
            tmp = df.groupby('date').sum()
            data2, data3 = get_graph_2(tmp, size)

        else:
            tmp = df.groupby('date').sum()
            data1 = get_graph_1(tmp, size, sep)
            data2, data3 = get_graph_2(tmp, size)
    
    



    layout = go.Layout(margin={"r":50,"t":25,"l":50,"b":25}, showlegend=True)
    return (
        {'data':data1, 'layout':layout},
        {'data':data2, 'layout':layout},
        {'data':data3, 'layout':layout}  #fig_urg , fig_sos
    )

