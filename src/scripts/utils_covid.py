# Import packages
import os as __os
import numpy as __np
import json as __json
import pandas as __pd
import pickle as __pickle
import datetime as __datetime
from sklearn.cluster import KMeans as __KMeans
 
DATA_PATH = '/Users/thibaud/Documents/Python_scripts/02_Projects/COVID/data/'
PICKLE_PATH = DATA_PATH + 'pickle/'
RAW_FR_PATH = DATA_PATH + 'raw_france/'
RAW_WRD_PATH = DATA_PATH + 'raw_monde/'
OPENDATA_PATH = DATA_PATH + 'open_data_soft/' + '20200629/'

def load_pickle(file_name):
    file_path = PICKLE_PATH + file_name
    with open(file_path, 'rb') as pfile:
        my_pickle = __pickle.load(pfile)
    return my_pickle


def save_pickle(object_, file_name):
    file_path = PICKLE_PATH + file_name
    with open(file_path, 'wb') as pfile:
        __pickle.dump(object_, pfile, protocol=__pickle.HIGHEST_PROTOCOL)


def list_pickle():
    file_list = __os.listdir(PICKLE_PATH)
    pickle_list = [i for i in file_list if '.p' in i]
    print(pickle_list)

def load_mapbox_token():
    file_path = DATA_PATH + 'mapbox.token'
    with open(file_path, 'r') as pfile:
        token = pfile.read()
    return token
