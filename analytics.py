from analytics_helper import *
import random
from datetime import datetime
from typing import List
import pandas as pd

random.seed(3888)

def generate_country_df(countries_data: pd.DataFrame,
                        country: str,
                        covid_concern: str,
                        cost: str,
                        continents: List[str],
                        interests: List[str]) -> pd.DataFrame:
    """Generates a Pandas DataFrame containing information about a particular country, including its 5 nearest neighbours.

    Args:
        country (str): Country selected by user.
        covid_concern (str): Can be one of the following values: {'low', 'medium', 'high'}.
        cost (str): Can be one of the following values: {'budget', 'mid-range', 'luxury'}.
        continents (List[str]): Can be any of the continent names in the OWID dataset (e.g., 'Asia', 'Europe').
        interests (List[str]): Interest(s) selected by user in UI. (These are weighted more in 5-NN.)
                               Interest options:
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
        pandas.DataFrame: DataFrame containing information about a particular country, including its 5 nearest neighbours.
    """
    cols_of_interest = convert_interests_to_cols(interests)
    weightings = generate_feature_weightings_dict(cols_of_interest)

    medians_scaled, medians, data_no_quant = prepare_data_for_nn(countries_data, country, covid_concern, cost, continents, weightings)
    
    if medians.shape[0] != 0:
        return generate_final_df_w_nn(country, medians_scaled, medians, data_no_quant)

    return None

def main():
    # Example usage of function above
    countries_data = integrate_all_data()
    print(generate_country_df(countries_data, "France", 'low', 'luxury', ['Europe', 'Oceania'], ['covid']))

if __name__ == "__main__":
    main()