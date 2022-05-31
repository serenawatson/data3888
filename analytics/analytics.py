import pandas as pd
import random

from datetime import datetime
from typing import List

from analytics.analytics_helper import *
from analytics.common import *

random.seed(3888)

def generate_country_df(countries_data: pd.DataFrame,
                        country: str,
                        regions: List[str],
                        interests: List[str]) -> pd.DataFrame:
    """Generates a Pandas DataFrame containing information about a particular country, including its 10 nearest neighbours.

    Args:
        countries_data (pd.DataFrame): DataFrame returned by integrate_all_data().
        country (str): Country selected by user.
        regions (List[str]): A list containing 0 or more regions (see list below).
            Region names:
            - Asia-Pacific
            - Americas
            - Europe and Africa
        interests (List[str]): Interest(s) selected by user in UI. (These are weighted more in 10-NN.)
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
        pandas.DataFrame: DataFrame containing information about a particular country, including its 10 nearest neighbours.
    """
    # if user has not selected regions of interests, then we assume they would be fine with travelling to any region
    if len(regions) == 0:
        regions = ['Asia-Pacific', 'Americas', 'Europe and Africa']

    continents = convert_regions_to_continents(regions)

    cols_of_interest = convert_interests_to_cols(interests)
    weightings = generate_feature_weightings_dict(cols_of_interest)

    medians_scaled, medians, data_no_quant = prepare_data_for_nn(countries_data, country, continents, weightings)

    return generate_final_df_w_nn(country, medians_scaled, medians, data_no_quant)

def main():
    # Example usage of function above
    covid = read_live_covid_data()
    countries_data = integrate_all_data(covid)
    df = generate_country_df(countries_data, "Argentina", ['Americas'], [])
    print(df['10NN'])

if __name__ == "__main__":
    main()