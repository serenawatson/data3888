import pandas as pd
import random

from datetime import datetime
from typing import List

from analytics_helper import *
from common import *

random.seed(3888)

def generate_country_df(countries_data: pd.DataFrame,
                        country: str,
                        regions: List[str],
                        interests: List[str]) -> pd.DataFrame:
    """Generates a Pandas DataFrame containing information about a particular country, including its 5 nearest neighbours.

    Args:
        countries_data (pd.DataFrame): DataFrame returned by integrate_all_data().
        country (str): Country selected by user.
        regions (List[str]): A list containing 1 or more regions (see list below).
            Region names:
            - Asia-Pacific
            - Americas
            - Europe
            - Africa
        interests (List[str]): Interest(s) selected by user in UI. (These are weighted more in 5-NN.)
                               Interest options:
                               - covid
                               - infrastructure_quality_and_availability
                               - health_and_safety
                               - cost
                               - fun
                               - nature
                               - food
                               - museums
                               - showstheatresandmusic
                               - wellness
                               - wildlife

    Returns:
        pandas.DataFrame: DataFrame containing information about a particular country, including its 5 nearest neighbours. Returns None if
            - the user hasn't selected any interests/variable groups, or
            - the user hasn't selected any regions.
    """
    if len(interests) == 0 or len(regions) == 0:
        return None

    continents = convert_regions_to_continents(regions)

    cols_of_interest = convert_interests_to_cols(interests)
    weightings = generate_feature_weightings_dict(cols_of_interest)

    medians_scaled, medians, data_no_quant = prepare_data_for_nn(countries_data, country, continents, weightings)

    return generate_final_df_w_nn(country, medians_scaled, medians, data_no_quant)

def main():
    # Example usage of function above
    countries_data = integrate_all_data()
    print(generate_country_df(countries_data, "France", ['Asia-Pacific'], ['covid']))

if __name__ == "__main__":
    main()