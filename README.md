# data3888

## Integrating analytics into the app

### Nearest neighbours

- All the required imports are already in `main.py`
- All you need to do is call `generate_country_df()` in `main.py`. This will give you all the info about the given country, including its 5 nearest neighbours.
    - First arg to `generate_country_df()` should just be `countries_data`.
    - Other args should come from user inputs in UI.
    - i.e., your call to this function should look something like `generate_country_df(countries_data, ...)`
- For more about the `generate_country_df()` function, as well as an example of how it should be used, check out the file `analytics.py`. This contains a full docstring for the function as well as example usage.

### Clustering (extension recommended during consultation on 11 May)

- All the required imports are already in `main.py`.
- The two functions you'll need to call in `main.py` are `generate_cluster()` and `get_country_data()`.
    1. `generate_cluster()` will give you a list of countries recommended for the user.
        - First arg to `generate_cluster()` should just be `countries_data`.
        - Other args should come from user inputs in UI.
        - i.e., your call to this function should look something like `generate_cluster(countries_data, ...)`
        - **Important note: Prior to calling `generate_cluster()`, ensure that the user has selected at least 1 variable group/interest, and at least 1 region.**
    2. `get_country_data()` will give you all the data (including description, travel advice, COVID cases/deaths, etc.) for a given country.
        - First arg to `get_country_data()` should just be `countries_data`.
        - Second arg should be a (valid) country name.
        - i.e., your call to this function should look something like `get_country_data(countries_data, ...)`
- For more about these 2 functions, as well as examples of how they should be used, check out the file `analytics_clustering.py`. This contains a full docstring and example usage for each function.