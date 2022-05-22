import pandas as pd
import random

from datetime import datetime
from typing import List, Dict

from analytics_helper_clustering import *
from common import *

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
        regions (List[str]): A list containing 0 or more regions (see list below).
            Region names:
            - Asia-Pacific
            - Americas
            - Europe and Africa
    Returns:
        List[str]: List of countries recommended to the user.
    """
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

def get_country_covid_data(covid: pd.DataFrame, country: str) -> pd.DataFrame:
    """Gets COVID cases data for the specified country over the past 30 days.

    Args:
        covid (pd.DataFrame): DataFrame returned by read_live_covid_data().
        country (str): Country name.

    Returns:
        pd.DataFrame: COVID cases data for the specified country over the past 30 days.
    """
    iso_location = read_iso_loc_data()
    cases = covid[['iso_code', 'date', 'new_cases_smoothed_per_million']]
    cases = cases.rename(columns={'new_cases_smoothed_per_million': 'daily_new_cases_smoothed_per_million'})
    cases = cases.set_index('iso_code')
    
    return cases.loc[loc_to_iso_code(country, iso_location)]

def main():
    # Example usage of generate_cluster() function above
    interested = {}

    interested["covid"] = False
    interested["infrastructure_quality_and_availability"] = True
    interested["health_and_safety"] = False
    interested["cost"] = False
    interested["fun"] = False
    interested["nature"] = True
    interested["food"] = False
    interested["museums"] = False
    interested["showstheatresandmusic"] = False
    interested["wellness"] = False
    interested["wildlife"] = False

    covid = read_live_covid_data()
    countries_data = integrate_all_data(covid)
    print(generate_cluster(countries_data, interested, ['Europe and Africa', 'Asia-Pacific']))

    # Example usage of get_country_data() function above
    print(get_country_data(countries_data, "United States"))

    # Example usage of get_country_covid_data() function above
    print(get_country_covid_data(covid, "United States"))

if __name__ == "__main__":
    main()