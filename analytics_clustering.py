import pandas as pd
import random

from datetime import datetime
from typing import List, Dict

from analytics_helper_clustering import *


def generate_cluster(countries_data: pd.DataFrame, 
                interested: Dict[str, bool], 
                regions: List[str]) -> List[str]:
    """Generates a list of countries recommended to the user.
    Each country in the list is given as a ISO 3166-1 alpha-3 code.

    Args:
        countries_data (pd.DataFrame): DataFrame returned by integrate_all_data().
        interested (Dict[str, bool]): Keys = variable group names (see list below). Values = True if user is interested in that variable group, False otherwise. Example shown in main() function in this code file.
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
        regions (List[str]): A list containing 1 or more regions (see list below).
            Region names:
            - Asia-Pacific
            - Americas
            - Europe and Africa
    Returns:
        List[str]: List of countries recommended to the user. Returns None if
            - the user hasn't selected any interests/variable groups, or
            - the user hasn't selected any regions.
    """
    if list(interested.values()).count(True) == 0 or len(regions) == 0:
        return None

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

def main():
    # Example usage of generate_cluster() function above
    interested = {}

    interested["covid"] = True
    interested["infrastructure_quality_and_availability"] = True
    interested["health_and_safety"] = False
    interested["cost"] = False
    interested["fun"] = False
    interested["nature"] = False
    interested["food"] = False
    interested["museums"] = False
    interested["showstheatresandmusic"] = False
    interested["wellness"] = False
    interested["wildlife"] = False

    countries_data = integrate_all_data()
    print(generate_cluster(countries_data, interested, ['Asia-Pacific', 'Europe']))

    # Example usage of get_country_data() function above
    print(get_country_data(countries_data, "United States"))

if __name__ == "__main__":
    main()