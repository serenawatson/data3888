import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from requests_html import HTML
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
import random

random.seed(3888)


def get_variable_groups():
    variable_groups = {}
    variable_groups["covid"] = ['new_cases_smoothed_per_million', 'stringency_index', 'positive_rate', 'new_vaccinations_smoothed_per_million']
    variable_groups["infrastructure quality_and_availability"] = ['tourist_service', 'air_transport', 'ground_port']
    variable_groups["health_and_safety"] = ['safety_security', 'health_hygiene']
    variable_groups["cost"] = ['price_competitiveness']
    variable_groups["food"] = ['food', 'restaurant', 'cafe']
    variable_groups["places_of_worship"] = ['church', 'mosque', 'place_of_worship', 'hindu_temple', 'synagogue']
    variable_groups["indoor_attractions"] = ['art_gallery', 'museum', 'aquarium']
    variable_groups["outdoor_attractions"] = ['amusement_park', 'zoo']
    variable_groups["nature"] = ['park', 'natural_cultural_resources', 'natural_feature']
    variable_groups["nightlife"] = ['casino', 'bar', 'night_club']
    variable_groups["shopping"] = ['shopping_mall', 'clothing_store', 'department_store']
    variable_groups["relaxation"] = ['spa']

    return variable_groups

def convert_interests_to_cols(interests):
    cols = []

    variable_groups = get_variable_groups()

    for interest in interests:
        for col in variable_groups[interest]:
            cols.append(col)

    return cols

def get_all_features():
    variable_groups = get_variable_groups()

    all_features = []
    for group in variable_groups.values():
        for col in group:
            all_features.append(col)

    return all_features

def get_all_cols():
    cols = get_all_features()
    cols.append("iso_code")
    cols.append("location")
    cols.append("advice")
    cols.append("description")
    cols.append("continent")
    cols.append("date")

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

def read_original_data():
    df = pd.read_csv("data/data.txt")
    df = df.drop(columns='Unnamed: 0')

    df = df.rename(columns = {'tourist_service_index': 'tourist_service'})

    df_without_covid = df.drop(columns=['new_cases_per_million', 
                                    'new_cases_smoothed_per_million', 
                                    'stringency_index', 
                                    'positive_rate', 
                                    'human_development_index', 
                                    'international_travel_controls',
                                    'cost_living_index',
                                    'date',
                                    'location',
                                    'continent'])

    df_without_covid = df_without_covid.drop_duplicates()
    df_without_covid = df_without_covid.reset_index()
    df_without_covid = df_without_covid.drop(columns=['index'])

    return df_without_covid

def read_tourism_data():
    full_tourism = pd.read_csv("data/full_tourism.csv")
    full_tourism = full_tourism[full_tourism["Country ISO3"] != "AUS"]

    indicators = {
                    'WEF Infrastructure subindex, 1-7 (best)': 'infrastructure', 
                    'WEF Natural and cultural resources subindex, 1-7 (best)': 'natural_cultural_resources',
                    'WEF Safety and security pillar, 1-7 (best)': 'safety_security',
                    'WEF Health and hygiene, 1-7 (best)': 'health_hygiene',
                    'WEF Price competitiveness in the Travel and Tourism Industry pillar, 1-7 (best)': 'price_competitiveness',
                    'WEF Air transport infrastructure, 1-7 (best)': 'air_transport',
                    'WEF Ground and port infrastructure, 1-7 (best)': 'ground_port'
    }

    full_tourism_req_indicators = full_tourism[full_tourism["Indicator"].isin(indicators)]
    full_tourism_req_indicators = full_tourism_req_indicators[['Country ISO3', 'Indicator', 'Subindicator Type', '2019']]
    full_tourism_req_indicators = full_tourism_req_indicators[full_tourism["Subindicator Type"] == "Value"]
    full_tourism_req_indicators = full_tourism_req_indicators.drop(columns = ['Subindicator Type'])
    full_tourism_req_indicators = full_tourism_req_indicators.rename(columns = {'Country ISO3': 'iso_code'})
    full_tourism_req_indicators = full_tourism_req_indicators.set_index('iso_code')

    inds = pd.DataFrame()

    for ind in indicators.keys():
        inds[indicators[ind]] = full_tourism_req_indicators[full_tourism_req_indicators["Indicator"] == ind].drop(columns = ["Indicator"]).rename(columns = {'2019': indicators[ind]})[indicators[ind]]

    return inds

def read_live_covid_data():
    covid = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv")

    covid['date'] = pd.to_datetime(covid['date'], format='%Y-%m-%d')

    covid = covid[covid['date'] >= datetime.now() - timedelta(days = 30)]

    return covid

def read_poi_data():
    poi = pd.read_json("data/poi_types.json")

    poi = poi.fillna(0)
    poi = poi.replace(0, np.nan)
    poi = poi.dropna(how='all', axis=0)
    poi = poi.replace(np.nan, 0)

    poi = poi.transpose()

    iso_location = read_iso_loc_data()

    poi = poi.set_index(loc_to_iso_code(loc, iso_location) for loc in poi.index)

    # removing less relevant columns
    poi = poi.drop(columns=['travel_agency',
                            'store',
                            'cemetery',
                            'library',
                            'campground',
                            'lodging',
                            'local_government_office',
                            'liquor_store',
                            'transit_station',
                            'grocery_or_supermarket',
                            'movie_theater',
                            'general_contractor',
                            'parking',
                            'book_store',
                            'city_hall',
                            'health',
                            'hospital'
                        ])

    poi['iso_code'] = poi.index

    return poi

def read_iso_loc_data():
    df = pd.read_csv("data/data.txt")
    df = df.drop(columns='Unnamed: 0')

    iso_location = df[["iso_code", "location"]].drop_duplicates()

    return iso_location

def iso_code_to_loc(iso_code, iso_location):
    return iso_location[iso_location["iso_code"] == iso_code]["location"].iloc[0]

def loc_to_iso_code(loc, iso_location):
    return iso_location[iso_location["location"] == loc]["iso_code"].iloc[0]

def read_smartraveller_data():
    # https://practicaldatascience.co.uk/data-science/how-to-read-an-rss-feed-in-python

    def get_source(url):
        """Return the source code for the provided URL. 

        Args: 
            url (string): URL of the page to scrape.

        Returns:
            response (object): HTTP response object from requests_html. 
        """

        try:
            session = HTMLSession()
            response = session.get(url)
            return response

        except requests.exceptions.RequestException as e:
            print(e)


    def get_feed(url):
        """Return a Pandas dataframe containing the RSS feed contents.

        Args: 
            url (string): URL of the RSS feed to read.

        Returns:
            df (dataframe): Pandas dataframe containing the RSS feed contents.
        """
        
        response = get_source(url)
        
        df = pd.DataFrame(columns = ['title', 'pubDate', 'guid', 'description'])

        with response as r:
            items = r.html.find("item", first=False)

            for item in items:        

                title = item.find('title', first=True).text
                pubDate = item.find('pubDate', first=True).text
                guid = item.find('guid', first=True).text
                description = item.find('description', first=True).text

                row = {'title': [title], 'pubDate': [pubDate], 'guid': [guid], 'description': [description]}
                df = pd.concat([df, pd.DataFrame.from_dict(row)])

        return df

    travel_advice = get_feed("https://www.smartraveller.gov.au/countries/documents/index.rss")

    travel_advice = travel_advice[travel_advice["title"] != "No travel advice"]

    travel_advice = travel_advice.drop(columns=['guid'])

    replacements = {
        "United States of America": "United States",
        "Israel and the Palestinian Territories": "Israel",
        "South Korea (Republic of Korea)": "South Korea"
    }

    for replacement in replacements:
        travel_advice.replace(replacement, replacements[replacement], inplace = True)

    travel_advice.rename(columns={"title": "location", "description": "advice"}, inplace = True)

    travel_advice["advice"] = [BeautifulSoup(s, "lxml").text for s in travel_advice["advice"]]

    return travel_advice

def read_triposo_data():
    descriptions = pd.read_csv("country_descriptions_cleaned_2.csv")

    return descriptions

def integrate_all_data():
    # reading in all data
    original = read_original_data()
    tourism = read_tourism_data()
    covid = read_live_covid_data()
    poi = read_poi_data()
    smartraveller = read_smartraveller_data()
    triposo = read_triposo_data()

    # merging
    full = pd.merge(original, tourism, on="iso_code")
    full = pd.merge(full, covid, on="iso_code")
    full = pd.merge(full, poi, on="iso_code")

    full = pd.merge(full, smartraveller, on="location")
    full = pd.merge(full, triposo, on="iso_code")

    full = full[full["iso_code"] != "AUS"]

    return full[get_all_cols()]

def get_covid_concern_quantile_endpoints(concern):
    quantile_endpoints = {
        'high': (0, 0.33),
        'medium': (0.34, 0.67),
        'low': (0.68, 1)
    }

    return quantile_endpoints[concern]

def get_cost_index_endpoints(cost):
    index_endpoints = {
        'luxury': (0, 0.33),
        'mid-range': (0.34, 0.67),
        'budget': (0.68, 1)
    }

    return index_endpoints[cost]

def prepare_data_for_nn(data, country, covid_concern, cost, continents, weightings):
    # continents filtering
    data = data[(data["continent"].isin(continents)) | (data["location"] == country)]

    data_no_quant = list(set(data.columns).difference(set(data.select_dtypes(include=[np.number]).columns)))
    data_no_quant.remove("date")

    medians = data.groupby(["iso_code"]).median()
    medians = medians.fillna(data.median())

    # COVID concern filtering
    # case_quantile_endpoints = get_covid_concern_quantile_endpoints(covid_concern)
    # medians_cases = medians[medians["new_cases_smoothed_per_million"] >= medians["new_cases_smoothed_per_million"].quantile(case_quantile_endpoints[0])]
    # medians_cases = medians[medians["new_cases_smoothed_per_million"] <= medians["new_cases_smoothed_per_million"].quantile(case_quantile_endpoints[1])]

    # cost filtering
    # cost_index_endpoints = get_cost_index_endpoints(cost)
    # medians_cost = medians[medians["price_competitiveness"] >= medians["price_competitiveness"].quantile(cost_index_endpoints[0])]
    # medians_cost = medians[medians["price_competitiveness"] <= medians["price_competitiveness"].quantile(cost_index_endpoints[1])]

    # medians = pd.merge(medians_cases, medians_cost, how="inner", left_index=True, right_index=True, suffixes=('', '_drop'))
    # medians.drop([col for col in medians.columns if 'drop' in col], axis=1, inplace=True)

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