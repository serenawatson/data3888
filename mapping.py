import plotly.graph_objects as go
import pandas as pd


def fetch_mapping_df(df, recommended_countries):
    recommended_countries_dict = {"location" : recommended_countries}
    recommended_countries_df = pd.DataFrame(recommended_countries_dict)

    mapping_df = pd.merge(recommended_countries_df, df, on = "location")
    mapping_df["recommended"] = [1 for location in df["location"] if location in recommended_countries]
    
    return mapping_df

def update_map(world_map, df, recommended_countries = [""]):
    mapping_df = fetch_mapping_df(df, recommended_countries)
    
    world_map.update_traces(locations = mapping_df["iso_code"],
                            autocolorscale = False,
                            marker_line_color = "white",
                            colorscale = ["#6baed6", "#08306b"],
                            hovertext = mapping_df["location"],
                            hovertemplate = "%{hovertext}<extra></extra>",
                            z = mapping_df["recommended"],
                            showscale = False)
    
    return world_map