from analytics_helper_clustering import *
import random
from datetime import datetime
from typing import List, Dict
import pandas as pd

def generate_cluster(countries_data: pd.DataFrame, 
                interested: Dict[str, bool], 
                continents: List[str]) -> List[str]:
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
        continents (List[str]): Can be any of the continent names in the OWID dataset (e.g., 'Asia', 'Europe').
    Returns:
        List[str]: List of countries recommended to the user.
    """
    weightings = convert_interests_to_col_weightings(interested)
    medians_scaled, medians, data_no_quant = prepare_data_for_clustering(countries_data, continents, weightings)

    return generate_best_cluster(medians_scaled, medians, interested)

def main():
    # Example usage of generate_cluster() function above
    interested = {}

    interested["covid"] = False
    interested["infrastructure_quality_and_availability"] = True
    interested["health_and_safety"] = True
    interested["cost"] = False
    interested["fun"] = False
    interested["nature"] = False
    interested["food"] = False
    interested["museums"] = False
    interested["showstheatresandmusic"] = False
    interested["wellness"] = False
    interested["wildlife"] = False

    countries_data = integrate_all_data()
    print(generate_cluster(countries_data, interested, ['Asia', 'Europe']))

if __name__ == "__main__":
    main()