import pandas as pd
import random

from datetime import datetime
from typing import List, Dict

from analytics.analytics_helper_clustering import *
from analytics.common import *

random.seed(3888)

def generate_cluster(countries_data: pd.DataFrame, 
                interested: Dict[str, bool], 
                regions: List[str]) -> List[str]:
    """Generates a list of countries recommended to the user.
    Each country in the list is given as a ISO 3166-1 alpha-3 code.

    Args:
        countries_data (pd.DataFrame): DataFrame returned by integrate_all_data().
        interested (Dict[str, bool]): Keys = variable group names (see list below). Values = True if user is interested in that variable group, False otherwise.
            Variable group names:
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
        regions (List[str]): A list containing 0 or more regions (see list below).
            Region names:
            - Asia-Pacific
            - Americas
            - Europe and Africa
    Returns:
        List[str]: List of countries recommended to the user.
    """
    # if user has not selected regions of interests, then we assume they would be fine with travelling to any region
    if len(regions) == 0:
        regions = ['Asia-Pacific', 'Americas', 'Europe and Africa']

    weightings = convert_interests_to_col_weightings(interested)
    medians_scaled_pca, medians_scaled = prepare_data_for_clustering(countries_data, regions, weightings)

    return generate_best_cluster(medians_scaled_pca, medians_scaled, interested)

def get_country_data(countries_data: pd.DataFrame, country: str) -> pd.Series:
    """Gets all data for the specified country.

    Args:
        countries_data (pd.DataFrame): DataFrame returned by integrate_all_data().
        country (str): Country name.

    Returns:
        pd.Series: All data for the specified country.
    """
    iso_location = read_iso_loc_data()
    medians = pd.DataFrame(compute_medians(countries_data))
    all_data = pd.DataFrame(combine_medians_w_qualitative_cols(countries_data, medians))

    return all_data.loc[loc_to_iso_code(country, iso_location)]