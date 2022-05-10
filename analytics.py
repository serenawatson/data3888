from analytics_helper import *
import random
from datetime import datetime

random.seed(3888)

countries_data = integrate_all_data()

def generate_country_df(country, covid_concern, cost, continents, interests):
    cols_of_interest = convert_interests_to_cols(interests)
    weightings = generate_feature_weightings_dict(cols_of_interest)

    medians_scaled, medians, data_no_quant = prepare_data_for_nn(countries_data, country, covid_concern, cost, continents, weightings)
    
    if medians.shape[0] != 0:
        return generate_final_df_w_nn(country, medians_scaled, medians, data_no_quant)

    return None

print(generate_country_df("France", 'low', 'luxury', ['Europe', 'Oceania'], ['covid']))