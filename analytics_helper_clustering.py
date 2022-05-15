import numpy as np
import pandas as pd
import random
import requests

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from k_means_constrained import KMeansConstrained
from requests_html import HTMLSession
from requests_html import HTML
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler
from statistics import mean

from common import *

random.seed(3888)

def convert_interest_level_to_weighting(interested):
    interested_mapping = {
        True: 1000,
        False: 1
    }
    
    return interested_mapping[interested]

def convert_interests_to_col_weightings(interests):
    variable_groups = get_variable_groups()
    
    col_weightings = {}
    
    for interest in interests:
        cols = variable_groups[interest]
        weighting = convert_interest_level_to_weighting(interests[interest])
        for col in cols:
            col_weightings[col] = weighting
            
    return col_weightings

def combine_medians_w_qualitative_cols(data, medians):
    data_no_quant_cols = list(set(data.columns).difference(set(data.select_dtypes(include=[np.number]).columns)))
    data_no_quant_cols.remove("date")

    data_no_quant = data[data_no_quant_cols].drop_duplicates()

    combined = pd.merge(data_no_quant, medians, on="iso_code")

    combined = combined.set_index(combined["iso_code"]).drop(columns=["iso_code"])

    return combined

def compute_medians(data):
    medians = data.groupby(["iso_code"]).median()
    medians = medians.fillna(data.median())

    return medians

def prepare_data_for_clustering(data, regions, weightings):
    continents = convert_regions_to_continents(regions)

    # continents filtering
    continent_data = data[data["continent"].isin(continents)]

    medians = compute_medians(continent_data)

    iso_code = medians.index

    scaler = MinMaxScaler()

    medians_scaled = scaler.fit_transform(medians)
    medians_scaled = pd.DataFrame(medians_scaled, index=medians.index, columns=medians.columns)

    cols = list(data.columns)

    to_remove = ['iso_code', 'continent', 'location', 'date', 'advice', 'description']

    for col in to_remove:
        cols.remove(col)

    for col in medians_scaled.columns:
        medians_scaled[col] = medians_scaled[col].apply(lambda x: x * weightings[col])

    if len(medians_scaled.columns) > 2:
        pca = PCA(n_components=2)
        pc = pca.fit_transform(medians_scaled)
        medians_scaled_pca = pd.DataFrame(data = pc, columns = ['PC1', 'PC2'], index = medians_scaled.index)

    return medians_scaled_pca, medians_scaled

def generate_cluster_labels(data):
    variable_groups = get_variable_groups()

    clf = KMeansConstrained(
            n_clusters=data.shape[0]//10,
            size_min=10,
            size_max=12,
            random_state=3888
    )
    
    labels = clf.fit_predict(data)
    
    return labels

def compute_silhouette_score(data):
    labels = generate_cluster_labels(data)
    
    return silhouette_score(data, labels)

def generate_best_cluster(medians_scaled_pca, medians_scaled, interested):
    
    variable_groups = get_variable_groups()
    
    labels = generate_cluster_labels(medians_scaled_pca)
    
    clusters = {}
    iso_location = read_iso_loc_data()

    for i, label in enumerate(labels):
        if label in clusters:
            clusters[label].append(list(medians_scaled.index)[i])
        else:
            clusters[label] = [list(medians_scaled.index)[i]]
            
    col_weightings = convert_interests_to_col_weightings(interested)
        
    cols_of_interest = [col for col in col_weightings if col_weightings[col] == max(col_weightings.values())]
    
    cluster_rating = {}

    for cluster_label in clusters:
        all_ratings = []
        
        for col in cols_of_interest:
            cluster_col_vals = list(medians_scaled.loc[clusters[cluster_label]][col])
            for val in cluster_col_vals:
                if col in variable_groups["covid"]:
                    val = max(medians_scaled[col]) - val
                all_ratings.append(val)
        
        cluster_rating[cluster_label] = mean(all_ratings)
        
    best_cluster = sorted(cluster_rating, key=lambda x: cluster_rating[x], reverse = True)[0]    

    return clusters[best_cluster]