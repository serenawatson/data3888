import re
from dash import Dash, html, dcc, Input, Output, State
from numpy import empty
import plotly.graph_objects as go
import pandas as pd
from common import *
from analytics import *
from analytics_clustering import *
from mapping import *
import json

countries_data = integrate_all_data()
rec_countries = []


# blank map
df = pd.read_csv("data/data.txt")
df = df.drop(columns='Unnamed: 0')
world_map = go.Figure(data=go.Choropleth(
    locations=df['iso_code'],
    colorscale='Reds',
    autocolorscale=False,
    marker_line_color='darkgray'
))

world_map.update_layout(
    geo=dict(
        showcoastlines=False,
        showframe=False
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)
# read in place photos url
with open("place_photos_url.json") as f:
    urls = json.load(f)

# region list
regions = ['Asia-Pacific', 'Americas', 'Europe and Africa']

# attraction types
# attraction_types = ['amusement_park', 'aquarium', 'art_gallery', 'bar', 'book_store', 'cafe',
#                     'campground', 'casino', 'cemetery', 'church', 'city_hall', 'clothing_store',
#                     'department_store', 'food', 'general_contractor', 'grocery_or_supermarket',
#                     'health', 'hindu_temple', 'hospital', 'library', 'liquor_store', 'local_government_office',
#                     'lodging', 'mosque', 'movie_theater', 'museum', 'natural_feature', 'night_club',
#                     'park', 'parking', 'place_of_worship', 'restaurant', 'shopping_mall', 'spa',
#                     'store', 'synagogue', 'transit_station', 'travel_agency', 'zoo']

# factors
factors = {'Covid': "covid",
           'Infrastructure Quality And Availability': "infrastructure_quality_and_availability",
           'Health Safety': "health_and_safety",
           'Cost': "cost"
           }

# poi
interests = {'Fun': "fun",
             'Nature': "nature",
             'Food': "food",
             'Museums': "museums",
             'Shows/Theatres/Music': "showstheatresandmusic",
             'Wellness': "wellness",
             'Wildlife': "wildlife"}

interested = {}

interested["covid"] = False
interested["infrastructure_quality_and_availability"] = False
interested["health_and_safety"] = False
interested["cost"] = False
interested["fun"] = False
interested["nature"] = False
interested["food"] = False
interested["museums"] = False
interested["showstheatresandmusic"] = False
interested["wellness"] = False
interested["wildlife"] = False


locations = ['Albania', 'Algeria', 'Argentina', 'Armenia', 'Austria',
             'Azerbaijan', 'Bahrain', 'Bangladesh', 'Belgium', 'Bolivia',
             'Botswana', 'Brazil', 'Bulgaria', 'Cambodia', 'Cameroon',
             'Canada', 'Chile', 'China', 'Colombia', 'Costa Rica',
             'Croatia', 'Cyprus', 'Denmark', 'Dominican Republic', 'Ecuador',
             'Egypt', 'El Salvador', 'Estonia', 'Ethiopia', 'Finland', 'France',
             'Germany', 'Ghana', 'Greece', 'Guatemala', 'Honduras', 'Hungary',
             'Iceland', 'India', 'Indonesia', 'Iran', 'Israel', 'Italy', 'Jamaica',
             'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kuwait', 'Latvia', 'Lebanon',
             'Lithuania', 'Malaysia', 'Malta', 'Mauritius', 'Mexico', 'Moldova',
             'Mongolia', 'Montenegro', 'Morocco', 'Myanmar', 'Nepal', 'Netherlands',
             'New Zealand', 'Nicaragua', 'Nigeria', 'North Macedonia', 'Norway', 'Oman',
             'Pakistan', 'Panama', 'Paraguay', 'Peru', 'Philippines', 'Poland',
             'Portugal', 'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saudi Arabia',
             'Senegal', 'Serbia', 'Seychelles', 'Slovakia', 'Slovenia', 'South Africa',
             'South Korea', 'Spain', 'Sri Lanka', 'Sweden', 'Switzerland', 'Taiwan',
             'Tanzania', 'Thailand', 'Tunisia', 'Turkey', 'Uganda', 'Ukraine',
             'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Venezuela',
             'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe']


# read in continent file
continent_dictionary = pd.read_csv("data/ContinentLocation.csv")

app = Dash(__name__, prevent_initial_callbacks=True)

app.layout = html.Div(className="block mx-4 my-4", children=[
    html.Div(className='columns', children=[
        html.Div(className='column is-one-third is-flex is-align-content-center', children=[
            html.Div(id="left_panel", className='box is-fullheight is-fullwidth', children=[
                html.Div(className='block',
                         children=[
                             html.P('Holiday Planner',
                                    className='is-size-2 has-text-link-dark'),
                             html.P(
                                 "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore "
                                 "et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
                                 "aliquip ex ea commodo consequat.")
                         ]),
                html.Div(className='block', children=[
                    html.Label(
                        'Have you got a destination in mind?', className='has-text-weight-semibold is-size-6'),
                    dcc.Dropdown(locations, multi=False,
                                 id="location_select", placeholder="Choose, or leave blank to let us decide for you...")
                ]),
                html.Div(className='block', children=[
                    html.Label(
                        'What region(s) would you like to visit?', className='has-text-weight-semibold is-size-6'),
                    dcc.Dropdown(regions, multi=True,
                                 id="region_select")
                ]),
                html.Div(className='block', children=[
                    html.Div(className='block', children=[
                        html.Label(
                            'What factor(s) are you most concerned about?', className='has-text-weight-semibold is-size-6'),
                        dcc.Dropdown(list(factors.keys()),
                                     multi=True, id="factor_select")
                    ]),
                    html.Div(className='block', children=[
                        html.Label(
                            'What interests you the most?', className='has-text-weight-semibold is-size-6'),
                        dcc.Dropdown(list(interests.keys()),
                                     multi=True, id="interest_select")
                    ])
                ]),
                html.Div(className='block', children=[
                    html.Button(
                        'Go!', className='button is-link is-light is-large is-fullwidth', id="submit", n_clicks=0)
                ])
            ])
        ]),
        html.Div(className='column is-two-thirds', children=[
            html.Div(id="right_panel", className='box is-fullheight', children=[
                html.Div(className="block", children=[
                    html.Div(className="block mb-4", children=[
                        dcc.Graph(figure=world_map, style={'width': '100%', 'height': '55vh'}, id="graph")])
                ]),
                html.Div(className="block", children=[
                    html.Div(className="tile is-ancestor is-vertical", children=[
                        html.Div(className="tile is-parent is-12", children=[
                            html.Div(
                                className="tile is-child is-2", children=[
                                    html.Div(className="block px-2", children=[
                                        html.A(id='a1', children=[
                                            html.Img(
                                                className="image is-2by1 pt-0", src="assets/white.png", id="p1"),
                                            html.Div(className="content has-text-centered", children=[
                                                html.P(
                                                    "", className="has-text-weight-semibold is-size-7", id="1")
                                            ])
                                        ])
                                    ])
                                ]),
                            html.Div(
                                className="tile is-child is-2", children=[
                                    html.Div(className="block px-2", children=[
                                        html.A(id='a2', children=[
                                            html.Img(
                                                className="image is-2by1 pt-0", src="assets/white.png", id="p2"),
                                            html.Div(className="content has-text-centered", children=[
                                                html.P(
                                                    "", className="has-text-weight-semibold is-size-7", id="2")
                                            ])
                                        ])
                                    ])
                                ]),
                            html.Div(
                                className="tile is-child is-2", children=[
                                    html.Div(className="block px-2", children=[
                                        html.A(id='a3', children=[
                                            html.Img(
                                                className="image is-2by1 pt-0", src="assets/white.png", id="p3"),
                                            html.Div(className="content has-text-centered", children=[
                                                html.P(
                                                    "", className="has-text-weight-semibold is-size-7", id="3")
                                            ])
                                        ])
                                    ])
                                ]),
                            html.Div(
                                className="tile is-child is-2", children=[
                                    html.Div(className="block px-2", children=[
                                        html.A(id='a4', children=[
                                            html.Img(
                                                className="image is-2by1 pt-0", src="assets/white.png", id="p4"),
                                            html.Div(className="content has-text-centered", children=[
                                                html.P(
                                                    "", className="has-text-weight-semibold is-size-7", id="4")
                                            ])
                                        ])
                                    ])
                                ]),
                            html.Div(
                                className="tile is-child is-2", children=[
                                    html.Div(className="block px-2", children=[
                                        html.A(id='a5', children=[
                                            html.Img(
                                                className="image is-2by1 pt-0", src="assets/white.png", id="p5"),
                                            html.Div(className="content has-text-centered", children=[
                                                html.P(
                                                    "", className="has-text-weight-semibold is-size-7", id="5")
                                            ])
                                        ])
                                    ])
                                ]),
                            html.Div(
                                className="tile is-child is-2", children=[
                                    html.Div(className="block px-2", children=[
                                        html.A(id='a6', children=[
                                            html.Img(
                                                className="image is-2by1 pt-0", src="assets/white.png", id="p6"),
                                            html.Div(className="content has-text-centered", children=[
                                                html.P(
                                                    "", className="has-text-weight-semibold is-size-7", id="6")
                                            ])
                                        ])
                                    ])
                                ])
                        ]),
                        html.Div(className="tile is-parent is-12", children=[
                            html.Div(
                                className="tile is-child is-2", children=[
                                    html.Div(className="block px-2", children=[
                                        html.A(id='a7', children=[
                                            html.Img(
                                                className="image is-2by1 pt-0", src="assets/white.png", id="p7"),
                                            html.Div(className="content has-text-centered", children=[
                                                html.P(
                                                    "", className="has-text-weight-semibold is-size-7", id="7")
                                            ])
                                        ])
                                    ])
                                ]),
                            html.Div(
                                className="tile is-child is-2", children=[
                                    html.Div(className="block px-2", children=[
                                        html.A(id='a8', children=[
                                            html.Img(
                                                className="image is-2by1 pt-0", src="assets/white.png", id="p8"),
                                            html.Div(className="content has-text-centered", children=[
                                                html.P(
                                                    "", className="has-text-weight-semibold is-size-7", id="8")
                                            ])
                                        ])
                                    ])
                                ]),
                            html.Div(
                                className="tile is-child is-2", children=[
                                    html.Div(className="block px-2", children=[
                                        html.A(id="a9", children=[
                                            html.Img(
                                                className="image is-2by1 pt-0", src="assets/white.png", id="p9"),
                                            html.Div(className="content has-text-centered", children=[
                                                html.P(
                                                    "", className="has-text-weight-semibold is-size-7", id="9")
                                            ])
                                        ])
                                    ])
                                ]),
                            html.Div(
                                className="tile is-child is-2", children=[
                                    html.Div(className="block px-2", children=[
                                        html.A(id='a10', children=[
                                            html.Img(
                                                className="image is-2by1 pt-0", src="assets/white.png", id="p10"),
                                            html.Div(className="content has-text-centered", children=[
                                                html.P(
                                                    "", className="has-text-weight-semibold is-size-7", id="10")
                                            ])
                                        ])
                                    ])
                                ]),
                            html.Div(
                                className="tile is-child is-2", children=[
                                    html.Div(className="block px-2", children=[
                                        html.A(id='a11', children=[
                                            html.Img(
                                                className="image is-2by1 pt-0", src="assets/white.png", id="p11"),
                                            html.Div(className="content has-text-centered", children=[
                                                html.P(
                                                    "", className="has-text-weight-semibold is-size-7", id="11")
                                            ])
                                        ])
                                    ])
                                ]),
                            html.Div(
                                className="tile is-child is-2", children=[
                                    html.Div(className="block px-2", children=[
                                        html.A(id="a12", children=[
                                            html.Img(
                                                className="image is-2by1 pt-0", src="assets/white.png", id="p12"),
                                            html.Div(className="content has-text-centered", children=[
                                                html.P(
                                                    "", className="has-text-weight-semibold is-size-7", id="12")
                                            ])
                                        ])
                                    ])
                                ])
                        ])
                    ])
                ])
            ]),
        ])
    ]),
    html.Div(className="footer py-4 mx-0", children=[
        html.Div(className="content has-text-centered", children=[
            html.P("HolidayPlanning Inc. 2022")
        ])
    ])
])


@app.callback(
    Output('region_select', 'value'),
    Input('location_select', 'value')
)
def set_location_values(selected_location):
    if selected_location is not None:
        region_area = continent_dictionary[continent_dictionary['Location']
                                           == selected_location]["Region"].item()
        return [region_area]


@app.callback(
    [Output('1', 'children'),
     Output('2', 'children'),
     Output('3', 'children'),
     Output('4', 'children'),
     Output('5', 'children'),
     Output('6', 'children'),
     Output('7', 'children'),
     Output('8', 'children'),
     Output('9', 'children'),
     Output('10', 'children'),
     Output('11', 'children'),
     Output('12', 'children'),
     Output('graph', 'figure'),
     Output('submit', 'n_clicks')],
    Input('location_select', 'value'),
    Input('region_select', 'value'),
    Input('factor_select', 'value'),
    Input('interest_select', 'value'),
    Input('submit', 'n_clicks')
)
def get_recommended_countries(location: str, chosen_regions: list, chosen_factors: list, chosen_interests: list, submit: int):
    global rec_countries
    global world_map
    iso_loc = read_iso_loc_data()
    rec_list = None
    if location is None:
        location = ""
    if chosen_regions is None:
        chosen_regions = ['Asia-Pacific', 'Americas', 'Europe and Africa']
    if chosen_factors is None:
        chosen_factors = []
    if chosen_interests is None:
        chosen_interests = []
    if submit != 0:
        if location != "":
            rec_countries.clear()
            for i in range(len(chosen_factors)):
                val = factors[chosen_factors[i]]
                chosen_factors[i] = val
            for i in range(len(chosen_interests)):
                val = interests[chosen_interests[i]]
                chosen_interests[i] = val
            combined = chosen_factors + chosen_interests
            df = generate_country_df(
                countries_data, location, chosen_regions, combined)
            rec_countries = df['10NN'].tolist()[0].copy()
            if location not in rec_countries:
                rec_countries.insert(0, location)
            rec_countries = rec_countries[0:10]
        else:
            rec_countries.clear()
            interested_filtered = interested.copy()
            for poi in chosen_factors:
                interested_filtered[factors[poi]] = True
            for poi in chosen_interests:
                interested_filtered[interests[poi]] = True
            rec_list = generate_cluster(
                countries_data, interested_filtered, chosen_regions)
            if rec_list is not None:
                rec_list = rec_list[0:12]
                for iso in rec_list:
                    country = iso_loc.loc[iso_loc['iso_code']
                                          == iso, 'location'].iloc[0]
                    rec_countries.append(country)
    # if recommended countries list is not len 12, it will pad with empty strings for output purposes
    while len(rec_countries) < 12:
        rec_countries.append("")
    # defaults n_clicks back to 0 clicks
    output_list = list(rec_countries)
    world_map = update_map(world_map, countries_data, rec_countries)
    output_list.append(world_map)
    if output_list[-1] != 0:
        output_list.append(0)

    return output_list


@app.callback(
    [Output('p1', 'src'),
     Output('p2', 'src'),
     Output('p3', 'src'),
     Output('p4', 'src'),
     Output('p5', 'src'),
     Output('p6', 'src'),
     Output('p7', 'src'),
     Output('p8', 'src'),
     Output('p9', 'src'),
     Output('p10', 'src'),
     Output('p11', 'src'),
     Output('p12', 'src')],
    Input(component_id='1', component_property='children'),
    Input(component_id='2', component_property='children'),
    Input(component_id='3', component_property='children'),
    Input(component_id='4', component_property='children'),
    Input(component_id='5', component_property='children'),
    Input(component_id='6', component_property='children'),
    Input(component_id='7', component_property='children'),
    Input(component_id='8', component_property='children'),
    Input(component_id='9', component_property='children'),
    Input(component_id='10', component_property='children'),
    Input(component_id='11', component_property='children'),
    Input(component_id='12', component_property='children')
)
def update_desinaions_div(destination1: str, destination2: str, destination3: str, destination4: str, destination5: str, destination6: str, destination7: str, destination8: str, destination9: str, destination10: str, destination11: str, destination12: str):
    src = []
    if destination1 in locations:
        src.append(urls[destination1])
    else:
        src.append("assets/white.png")
    if destination2 in locations:
        src.append(urls[destination2])
    else:
        src.append("assets/white.png")
    if destination3 in locations:
        src.append(urls[destination3])
    else:
        src.append("assets/white.png")
    if destination4 in locations:
        src.append(urls[destination4])
    else:
        src.append("assets/white.png")
    if destination5 in locations:
        src.append(urls[destination5])
    else:
        src.append("assets/white.png")
    if destination6 in locations:
        src.append(urls[destination6])
    else:
        src.append("assets/white.png")
    if destination7 in locations:
        src.append(urls[destination7])
    else:
        src.append("assets/white.png")
    if destination8 in locations:
        src.append(urls[destination8])
    else:
        src.append("assets/white.png")
    if destination9 in locations:
        src.append(urls[destination9])
    else:
        src.append("assets/white.png")
    if destination10 in locations:
        src.append(urls[destination10])
    else:
        src.append("assets/white.png")
    if destination11 in locations:
        src.append(urls[destination11])
    else:
        src.append("assets/white.png")
    if destination12 in locations:
        src.append(urls[destination12])
    else:
        src.append("assets/white.png")
    return src


if __name__ == '__main__':
    app.run_server(debug=True)
