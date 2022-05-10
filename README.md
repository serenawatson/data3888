# data3888

## Integrating analytics into the app

- All the required imports are already in `main.py`
- All you need to do is call `generate_country_df()` in `main.py`. This will give you all the info about the given country, including its 5 nearest neighbours.
    - First arg to `generate_country_df()` should just be `countries_data`.
    - Other args should come from user inputs in UI.
    - i.e., your call to this function should look something like `generate_country_df(countries_data, ...)`
- For more about the `generate_country_df()` function, as well as an example of how it should be used, check out the file `analytics.py`. This contains a full docstring for the function as well as example usage.