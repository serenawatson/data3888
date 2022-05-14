import numpy as np
import pandas as pd
import random
import requests

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from requests_html import HTMLSession
from requests_html import HTML
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

from common import *

random.seed(3888)

def convert_interests_to_cols(interests):
    cols = []

    variable_groups = get_variable_groups()

    for interest in interests:
        for col in variable_groups[interest]:
            cols.append(col)

    return cols

def generate_feature_weightings_dict(cols_of_interest):
    variable_groups = get_variable_groups()

    all_features = get_all_features()

    feature_weightings = {}

    for feature in all_features:
        if feature in cols_of_interest:
            feature_weightings[feature] = 100
        else:
            feature_weightings[feature] = 1

    return feature_weightings

def prepare_data_for_nn(data, country, continents, weightings):
    # continents filtering
    data = data[(data["continent"].isin(continents)) | (data["location"] == country)]

    data_no_quant = list(set(data.columns).difference(set(data.select_dtypes(include=[np.number]).columns)))
    data_no_quant.remove("date")

    medians = data.groupby(["iso_code"]).median()
    medians = medians.fillna(data.median())

    if medians.shape[0] == 0:
        return medians, medians, data[data_no_quant]

    iso_code = medians.index

    scaler = MinMaxScaler()

    medians_scaled = scaler.fit_transform(medians)

    cols = list(data.columns)

    to_remove = ['iso_code', 'continent', 'location', 'date', 'advice', 'description']

    for col in to_remove:
        cols.remove(col)
        
    medians_scaled = pd.DataFrame(medians_scaled, 
                                columns = cols, 
                                index = iso_code)

    for col in medians_scaled.columns:
        medians_scaled[col] = medians_scaled[col].apply(lambda x: x * weightings[col])

    if len(medians_scaled.columns) > 2:
        pca = PCA(n_components=2)
        pc = pca.fit_transform(medians_scaled)
        medians_scaled = pd.DataFrame(data = pc, columns = ['PC1', 'PC2'], index = medians_scaled.index)

    return medians_scaled, medians, data[data_no_quant]

def find_top_neighbours(country, location_neighbours_df, num_neighbours=5):
    d = {}
    lists = location_neighbours_df.loc[country].tolist()
    for ls in lists:
        for c in ls:
            if c in d:
                d[c] += 1
            else:
                d[c] = 1
    top = []

    for k,v in sorted(d.items(), key=lambda p:p[1], reverse=True)[:num_neighbours]:
        top.append(k)
    return top

def generate_final_df_w_nn(country, medians_scaled, medians, data_no_quant, num_neighbours = 5):
    iso_location = read_iso_loc_data()

    dist_metrics = ['euclidean', 'manhattan', 'chebyshev', 'cosine', 'cityblock', 'braycurtis', 'canberra',
               'correlation', 'minkowski']

    location_neighbours = {}

    for metric in dist_metrics:
        nbrs = NearestNeighbors(metric = metric, 
                                n_neighbors = num_neighbours + 1, 
                                algorithm='auto').fit(medians_scaled)
        
        nbr_indices = list(list(x) for x in nbrs.kneighbors(medians_scaled)[1])

        for i in range(len(nbr_indices)):
            current_iso_code = list(medians_scaled.index)[i]
            current_location = iso_code_to_loc(current_iso_code, iso_location)

            if current_location != country:
                continue

            neighbours = []
            for j in range(1, num_neighbours + 1):
                iso_code = medians_scaled.index[nbr_indices[i][j]]
                neighbours.append(iso_code_to_loc(iso_code, iso_location))

            if not current_location in location_neighbours:
                location_neighbours[current_location] = {metric: neighbours}
            else:
                location_neighbours[current_location][metric] = neighbours

    location_neighbours_df = pd.DataFrame(location_neighbours).transpose()

    top_neighbours = {}

    top_neighbours[country] = find_top_neighbours(country, location_neighbours_df)

    final_df = pd.merge(medians, data_no_quant, on="iso_code").drop_duplicates()
    final_df = final_df.set_index(final_df["iso_code"]).drop(columns=["iso_code"])
    final_df = final_df[final_df["location"] == country]

    final_df['5NN'] = [top_neighbours[iso_code_to_loc(iso_code, iso_location)] for iso_code in final_df.index]

    return final_df