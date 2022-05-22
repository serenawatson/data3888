def fetch_mapping_df(df, recommended_countries):
    recommended_countries_dict = {"location" : recommended_countries}
    recommended_countries_df = pd.DataFrame(recommended_countries_dict)

    mapping_df = pd.merge(recommended_countries_df, df, on = "location")
    mapping_df["recommended"] = [1 for location in mapping_df["location"]]
    
    return mapping_df

def update_map(world_map, df, recommended_countries):
    mapping_df = fetch_mapping_df(df, recommended_countries)
    
    world_map.update_traces(locations = mapping_df["iso_code"],
                            autocolorscale = False,
                            marker_line_color = "white",
                            colorscale = ["#3069bf", "#3069bf"],
                            hovertext = mapping_df["location"],
                            hovertemplate = "%{hovertext}<extra></extra>",
                            z = mapping_df["recommended"],
                            showscale = False)
    
    return world_map

def update_map_on_click(world_map, df, recommended_countries, location_string):
    mapping_df = fetch_mapping_df(df, recommended_countries)
    mapping_df.loc[mapping_df["location"] == location_string,"recommended"] = 2
    
    world_map.update_traces(locations = mapping_df["iso_code"],
                            autocolorscale = False,
                            marker_line_color = "white",
                            colorscale = ["#3069bf", "#ff0000"],
                            hovertext = mapping_df["location"],
                            hovertemplate = "%{hovertext}<extra></extra>",
                            z = mapping_df["recommended"],
                            showscale = False)
    
    return world_map

def covid_graph(df, location_string):
    country_data = df[df.location == location_string]
    figure = px.line(country_data, 
                     x = "date", 
                     y = "new_cases_smoothed_per_million", 
                     labels={"date": "Date",
                             "new_cases_smoothed_per_million": "New cases per million (smoothed)"},
                     title = "Covid cases in " + location_string)
    
    return figure