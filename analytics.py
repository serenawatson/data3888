from analytics_helper import *
import random
from datetime import datetime
from typing import List
import pandas as pd

random.seed(3888)

countries_data = integrate_all_data()


def generate_country_df(country: str, covid_concern: str, cost: str, continents: List[str], interests: List[str]) -> pd.DataFrame:
    """Generates a Pandas DataFrame containing information about a particular country, as well as its 5 nearest neighbours.

    Args:
        country (str): Country selected by user.
        covid_concern (str): Can be one of the following values: {'low', 'medium', 'high'}, depending on user input.
        cost (str): Can be one of the following values: {'budget', 'mid-range', 'luxury'}, depending on user input.
        continents (List[str]): Can be any of the continent names in the OWID dataset (e.g., 'Asia', 'Europe').
        interests (List[str]): Variable group(s) selected by user in UI.
                               Variable group options:
                               - covid
                               - infrastructure_quality_and_availability
                               - health_and_safety
                               - cost
                               - food
                               - places_of_worship
                               - indoor_attractions
                               - outdoor_attractions
                               - nature
                               - nightlife
                               - shopping
                               - relaxation

    Returns:
        pandas.DataFrame: DataFrame containing information about a particular country, as well as its 5 nearest neighbours.
    """
    cols_of_interest = convert_interests_to_cols(interests)
    weightings = generate_feature_weightings_dict(cols_of_interest)

    medians_scaled, medians, data_no_quant = prepare_data_for_nn(countries_data, country, covid_concern, cost, continents, weightings)
    
    if medians.shape[0] != 0:
        return generate_final_df_w_nn(country, medians_scaled, medians, data_no_quant)

    return None

# Example usage of function above
# print(generate_country_df("France", 'low', 'luxury', ['Europe', 'Oceania'], ['covid']))