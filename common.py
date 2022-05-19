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
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from statistics import mean

def convert_regions_to_continents(regions):
    regions_to_convert = {
        'Asia-Pacific': ['Asia', 'Oceania'],
        'Americas': ['North America', 'South America'],
        'Europe and Africa': ['Europe', 'Africa']
    }

    continents = []

    for region in regions:
        if not region in regions_to_convert:
            continents.append(region)
        else:
            region_continents = regions_to_convert[region]
            for continent in region_continents:
                continents.append(continent)

    return continents

def get_variable_groups():
    variable_groups = {}
    variable_groups["covid"] = ['new_cases_smoothed_per_million', 'new_deaths_smoothed_per_million']
    variable_groups["infrastructure_quality_and_availability"] = ['tourist_service', 'air_transport', 'ground_port']
    variable_groups["health_and_safety"] = ['safety_security', 'health_hygiene']
    variable_groups["cost"] = ['price_competitiveness']
    
    # POIs
    variable_groups["fun"] = ['amusementparks', 'nightlife']
    variable_groups["nature"] = ['beaches', 'camping', 'exploringnature']
    variable_groups["food"] = ['eatingout']
    variable_groups["museums"] = ['museums']
    variable_groups["showstheatresandmusic"] = ['showstheatresandmusic']
    variable_groups["wellness"] = ['wellness']
    variable_groups["wildlife"] = ['zoos']

    return variable_groups

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
    poi = pd.read_csv("data/triposo_poi.csv", index_col = 0)
    poi = poi.apply(pd.to_numeric)
    
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

                title = item.find('title', first=True).text.split("\n")[0]
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

    print("Smartraveller location column:")
    print(smartraveller["location"])

    triposo = read_triposo_data()

    # merging
    full = pd.merge(original, tourism, on="iso_code")
    full = pd.merge(full, covid, on="iso_code")
    full = pd.merge(full, poi, on="iso_code")

    full = pd.merge(full, smartraveller, on="location")
    full = pd.merge(full, triposo, on="iso_code")

    full = full[full["iso_code"] != "AUS"]
    
    return full[get_all_cols()]