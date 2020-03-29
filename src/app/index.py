############################################################################################
########################################## IMPORTS #########################################
############################################################################################

# Import dash library and related ones
import os
import dash
import dash_core_components as dcc
import dash_html_components as html

# Import use case tabs
from app import app
from tabs.contamination import tab_fr
from tabs.hopitaux import tab_h
from tabs.world import tab_w
from tabs.sentiment import tab_sentiment

# Logging information
import logging
import logzero
from logzero import logger

############################################################################################
######################################## PARAMETERS ########################################
############################################################################################

# Initiating logger
logzero.loglevel(logging.DEBUG)

# Deployment inforamtion
DEPLOYED = 'DEPLOYED' in os.environ
PORT = 8050


############################################################################################
######################################### LAYOUT ###########################################
############################################################################################


app.layout = html.Div(
    # className="app__container",
    children=[
        html.Div(
            className="app__header",
            children=[
                # html.Img(src="assets/carrefour.png", className="app__logo", style={'height':100, 'margin-bottom':'15px'}),
                html.H2("COVID 19 - Analyse des cas en France et dans le monde", className="header__text"),

            ],
        ),
        html.Div(
            className="tabs__container",
            children=[
                dcc.Tabs(
                    id="tabs",
                    value="contamination",
                    children=[
                        tab_fr,         # contamination
                        tab_w,          # world
                        tab_sentiment,  # sentiment
                        tab_h,          # hopitaux
                    ],
                ),
            ],
        ),
    ],
)

############################################################################################
######################################### RUNNING ##########################################
############################################################################################

if __name__ == "__main__":
    
    # Display app start
    logger.error('*' * 80)
    logger.error('Initialisation de l\'Application')
    logger.error('*' * 80)

    # Run application
    if DEPLOYED:
        app.run_server(host='0.0.0.0',debug=False, port=PORT)
    else:
        app.run_server(debug=True, port=PORT)
    




    