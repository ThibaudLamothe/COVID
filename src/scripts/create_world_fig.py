import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import sys
sys.path.append('../scripts/')
import utils_covid as f

import plotly.express as px
from plotly import graph_objs as go
from plotly.offline import init_notebook_mode, plot, iplot

mapbox_access_token = f.load_mapbox_token()

################################################################################################
################################################################################################
################################################################################################
################################################################################################




def create_world_fig():

    df = f.load_pickle('df_world.p')
    df_fr = f.load_pickle('df_world_fr.p')
    country_position = f.load_pickle('country_position.p')
    geo_world_ok = f.load_pickle('geo_world.p')
    region_info = f.load_pickle('region_info_by_id.p')

    startdate = '2020-03-01'

    tmp = df.reset_index()
    tmp = tmp[tmp['date'] > startdate]
    tmp['lat'] = tmp['subzone'].apply(lambda x:country_position[x]['lat']).apply(float)
    tmp['lon'] = tmp['subzone'].apply(lambda x:country_position[x]['lon']).apply(float)


    max_value = int(tmp['confirmed'].max())
    n_size = 100
    scales = np.array([i for i in range(0, max_value, int(max_value/n_size))])
    def transform_size(x):
        if x==0:
            return 0
        return np.argmin(np.abs(scales - x)) + 1
        
    x, y  = [], []
    for i in range(n_size+2):
        x.append(i)
        y.append(np.sqrt(i))
    tmp['size'] = tmp['confirmed'].apply(transform_size).apply(lambda v:y[v]*10)



    tmp = tmp.groupby(['date', 'subzone']).agg({'confirmed':'sum', 'deaths':'sum', 'recovered':'sum','lat':'last', 'lon':'last', 'size':'last'})
    tmp['confirmed'] = tmp['confirmed'].fillna(0)
    tmp['confirmed'] = tmp['confirmed'].fillna(0)
    tmp['confirmed'] = tmp['confirmed'].fillna(0)
    # tmp['size'] = (tmp['confirmed']/1000).apply(lambda x: 0 if x <=0 else x if x > 4 else 4)




    # tmp = tmp.loc[startdate:]

    jours = tmp.index.levels[0].tolist()
    jour = max(jours)

    # Initial display
    data = [go.Scattermapbox(
                lat=tmp.xs(jour)['lat'].values,
                lon=tmp.xs(jour)['lon'].values,
                mode='markers',
                marker=go.scattermapbox.Marker(size=(tmp.xs(jour)['size']).values),
                text=tmp.xs(jour)['confirmed'].values,
                )
            ]

    # Global Layout
    layout = go.Layout(
        # width=800,
        height=800,
        autosize=True,
        hovermode='closest',
        mapbox=dict(accesstoken=mapbox_access_token,
                    bearing=0,
                    center = {"lat": 37.86, "lon": 2.15},
                    pitch=0,
                    zoom=2.2,
                    style='light'
                    )
                )

    frames = [{
        'data':[{
                'type':'scattermapbox',
                'lat':tmp.xs(jour)['lat'].values,
                'lon':tmp.xs(jour)['lon'].values,
                'marker':go.scattermapbox.Marker(size=(tmp.xs(jour)['size']).values),
                'text':tmp.xs(jour)['confirmed'].values,
        }],
        'traces':[0],
        'name':'frame_{}'.format(jour)       
        } for jour  in  jours]           


    sliders = [{
        'steps':[
            {
                'method':'animate',
                'args':[
                    ['frame_{}'.format(k)],
                    {
                        'mode':'immediate',
                        'frame':{'duration':800, 'redraw': True},
                        'transition':{'duration':0}
                    }
                    ],
                'label':k
                } for k in jours
        ],
        'transition':{'duration': 0},
        'x':0.05,#slider starting position  
        'y':0, 
        'currentvalue':{'font':{'size':12}, 
                            'prefix':'Point: ', 
                            'visible':True, 
                            'xanchor':'center'},  
        'len':0.95
    }]


    layout.update(updatemenus=[dict(type='buttons', showactive=False,
                                    y=0,
                                    x=0.1,
                                    xanchor='right',
                                    yanchor='top',
                                    pad=dict(t=0, r=10),
                                    buttons=[dict(label='Play',
                                                method='animate',
                                                args=[None, 
                                                        dict(frame=dict(duration=100, 
                                                                        redraw=True),
                                                            transition=dict(duration=0),
                                                            fromcurrent=True,
                                                            mode='immediate'
                                                            )
                                                    ]
                                                )
                                            ]
                                )
                            ],
                    sliders=sliders,
                )
    FIG=go.Figure(data=data, layout=layout, frames=frames)
    FIG.update_layout(margin={"r":0,"t":0,"l":0,"b":50})

    f.save_pickle(FIG, 'fig_world.p')


################################################################################################
################################################################################################
################################################################################################
################################################################################################
#########################################################################################


def create_france_fig():

    df = f.load_pickle('df_world.p')
    df_fr = f.load_pickle('df_world_fr.p')
    country_position = f.load_pickle('country_position.p')
    geo_world_ok = f.load_pickle('geo_world.p')
    region_info = f.load_pickle('region_info_by_id.p')

    startdate = '2020-03-01'


    tmp = df_fr['confirmed'].reset_index()
    tmp['lat'] = tmp['code_region'].apply(lambda x: region_info[x]['lat'])
    tmp['lon'] = tmp['code_region'].apply(lambda x: region_info[x]['lon'])

    max_value = int(tmp['confirmed'].max())
    n_size = 100
    scales = np.array([i for i in range(0, max_value, int(max_value/n_size))])
        
    def transform_size(x):
        if x==0:
            return 0
        return np.argmin(np.abs(scales - x)) + 1

    x, y  = [], []
    for i in range(n_size+2):
        x.append(i)
        y.append(np.sqrt(i))
    tmp['size'] = tmp['confirmed'].apply(transform_size).apply(lambda v:y[v]*10)



    # tmp = tmp.groupby(['date', 'code_region']).agg({'confirmed':'sum', 'deaths':'sum', 'recovered':'sum','lat':'last', 'lon':'last'})
    tmp = tmp.groupby(['date', 'code_region']).agg({'confirmed':'sum','lat':'last', 'lon':'last', 'size':'last'})
    tmp['confirmed'] = tmp['confirmed'].fillna(0)
    #tmp['size'] = (tmp['confirmed']/100).apply(lambda x: 0 if x <=0 else x if x > 4 else 4)


    # tmp = tmp.loc[startdate:]
    jours = tmp.index.levels[0].tolist()
    jour = max(jours)

    # Initial display
    data = [go.Scattermapbox(
                lat=tmp.xs(jour)['lat'].values,
                lon=tmp.xs(jour)['lon'].values,
                mode='markers',
                marker=go.scattermapbox.Marker(size=(tmp.xs(jour)['size']).values),
                text=tmp.xs(jour)['confirmed'].values,
                )
            ]

    # Global Layout
    layout = go.Layout(
        # width=800,
        height=800,
        autosize=True,
        hovermode='closest',
        mapbox=dict(accesstoken=mapbox_access_token,
                    bearing=0,
                    center = {"lat": 47.86, "lon": 2.15},
                    pitch=0,
                    zoom=4.5,
                    style='light'
                    )
                )

    frames = [{
        'data':[{
                'type':'scattermapbox',
                'lat':tmp.xs(jour)['lat'].values,
                'lon':tmp.xs(jour)['lon'].values,
                'marker':go.scattermapbox.Marker(size=(tmp.xs(jour)['size']).values),
                'text':tmp.xs(jour)['confirmed'].values,
        }],
        'traces':[0],
        'name':'frame_{}'.format(jour)       
        } for jour  in  jours]           


    sliders = [{
        'steps':[
            {
                'method':'animate',
                'args':[
                    ['frame_{}'.format(k)],
                    {
                        'mode':'immediate',
                        'frame':{'duration':400, 'redraw': True},
                        'transition':{'duration':0}
                    }
                    ],
                'label':k
                } for k in jours
        ],
        'transition':{'duration': 0},
        'x':0.05,#slider starting position  
        'y':0, 
        'currentvalue':{'font':{'size':12}, 
                            'prefix':'Point: ', 
                            'visible':True, 
                            'xanchor':'center'},  
        'len':0.95
    }]


    layout.update(updatemenus=[dict(type='buttons', showactive=False,
                                    y=0,
                                    x=0.1,
                                    xanchor='right',
                                    yanchor='top',
                                    pad=dict(t=0, r=10),
                                    buttons=[dict(label='Play',
                                                method='animate',
                                                args=[None, 
                                                        dict(frame=dict(duration=100, 
                                                                        redraw=True),
                                                            transition=dict(duration=0),
                                                            fromcurrent=True,
                                                            mode='immediate'
                                                            )
                                                    ]
                                                )
                                            ]
                                )
                            ],
                    sliders=sliders,
                )
    FIG=go.Figure(data=data, layout=layout, frames=frames)
    FIG.update_layout(margin={"r":0,"t":0,"l":0,"b":50})

    f.save_pickle(FIG, 'fig_france.p')



################################################################################################
################################################################################################
################################################################################################
################################################################################################


def create_contamination_fig():
    # Carte des régions contaminées de France
    region_plotly = f.load_pickle('region_contours_geojson_plotly.p')
    tmp = f.load_pickle('df_contamination_fr.p')

    jour = tmp.index.levels[0].max()
    col = 'cas_confirme'

    tmp = tmp.loc[jour][col].reset_index()
    tmp['code_region'] = tmp['code_region'].apply(str)
        
    max_value = tmp[col].max()
    fig =  px.choropleth_mapbox(
        tmp,
        geojson=region_plotly,
        locations='code_region',
        color=col,
        # width=500,
        color_continuous_scale="oranges",
        range_color=(0, max_value),
        mapbox_style="carto-positron",
        zoom=4.5, center = {"lat": 47.86, "lon": 2.15},
        opacity=0.5,
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    f.save_pickle(fig, 'fig_fr_contamination_region.p')

################################################################################################
################################################################################################
################################################################################################
################################################################################################

if __name__ =="__main__":
    
    # create_contamination_fig()
    # create_france_fig()
    create_world_fig()