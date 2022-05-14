from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from common import *
from analytics import *
from analytics_clustering import *

countries_data = integrate_all_data()

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
        showframe=False,
        showcoastlines=False,
        projection_type='equirectangular'
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)

#region list
regions = ['Asia-Pacific', 'Americas', 'Europe', 'Africa']

# attraction types
# attraction_types = ['amusement_park', 'aquarium', 'art_gallery', 'bar', 'book_store', 'cafe',
#                     'campground', 'casino', 'cemetery', 'church', 'city_hall', 'clothing_store',
#                     'department_store', 'food', 'general_contractor', 'grocery_or_supermarket',
#                     'health', 'hindu_temple', 'hospital', 'library', 'liquor_store', 'local_government_office',
#                     'lodging', 'mosque', 'movie_theater', 'museum', 'natural_feature', 'night_club',
#                     'park', 'parking', 'place_of_worship', 'restaurant', 'shopping_mall', 'spa',
#                     'store', 'synagogue', 'transit_station', 'travel_agency', 'zoo']

#factors
factors = { 'Covid': "covid", 
            'Infrastructure Quality And Availability': "infrastructure_quality_and_availability",  
            'Health Safety': "health_and_safety", 
            'Cost': "cost"
            }

#poi
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


# locations = ['Albania', 'Algeria', 'Argentina', 'Armenia', 'Australia',
#              'Austria', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Barbados',
#              'Belgium', 'Bolivia', 'Botswana', 'Brazil', 'Bulgaria', 'Cambodia',
#              'Cameroon', 'Canada', 'Chile', 'China', 'Colombia', 'Costa Rica',
#              'Croatia', 'Cyprus', 'Denmark', 'Dominican Republic', 'Ecuador',
#              'Egypt', 'El Salvador', 'Estonia', 'Ethiopia', 'Finland', 'France',
#              'Georgia', 'Germany', 'Ghana', 'Greece', 'Guatemala', 'Honduras',
#              'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran',
#              'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan',
#              'Kazakhstan', 'Kenya', 'Kuwait', 'Latvia', 'Lebanon', 'Lithuania',
#              'Luxembourg', 'Malaysia', 'Malta', 'Mauritius', 'Mexico',
#              'Moldova', 'Mongolia', 'Montenegro', 'Morocco', 'Myanmar', 'Nepal',
#              'Netherlands', 'New Zealand', 'Nicaragua', 'Nigeria',
#              'North Macedonia', 'Norway', 'Oman', 'Pakistan', 'Panama',
#              'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar',
#              'Romania', 'Russia', 'Rwanda', 'Saudi Arabia', 'Senegal', 'Serbia',
#              'Seychelles', 'Singapore', 'Slovakia', 'Slovenia', 'South Africa',
#              'South Korea', 'Spain', 'Sri Lanka', 'Suriname', 'Sweden',
#              'Switzerland', 'Taiwan', 'Tanzania', 'Thailand', 'Tunisia',
#              'Turkey', 'Uganda', 'Ukraine', 'United Arab Emirates',
#              'United Kingdom', 'United States', 'Uruguay', 'Venezuela',
#              'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe']


# read in continent file
continent_dictionary = pd.read_csv("data/ContinentLocation.csv")

app = Dash(__name__)

app.layout = html.Div(children=[
    html.Div(className='block mx-4 mt-4', children=[
        html.Div(className='columns', children=[
            html.Div(className='column is-one-third is-flex ', children=[
                html.Div(className='box', children=[
                    html.Div(className='block',
                         children=[
                             html.P('Holiday Planner',
                                    className='has-text-weight-bold is-size-3 has-text-link-dark'),
                             html.P(
                                 "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore "
                                 "et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
                                 "aliquip ex ea commodo consequat.")
                         ]),
                    html.Div(className='block', children=[
                        html.Label(
                            'What region(s) would you like to visit?', className='has-text-weight-semibold is-size-6'),
                        dcc.Dropdown(regions, multi=True, id="region_select")
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
                        html.Button('Go!', className='button is-link is-light is-large is-fullwidth', id="submit")
                    ])  
                ])
            ]),
            html.Div(className='column is-two-thirds', children=[
                html.Div(className='box', children=[
                    html.Div(className="block", children=[
                         dcc.Graph(figure=world_map)]),
                    html.Div(className="box", children=[
                        html.Div(className="columns", children=[
                            html.Div(className="column is-two-fifth", children=[
                                html.Img(src="https://picsum.photos/128",
                                     className="image is-128x128")
                            ]),
                            html.Div(className="column", children=[
                                html.Div(className="block", children=[
                                    html.P(
                                        'Destination 1', className='has-text-weight-bold is-size-6'),
                                    html.P(
                                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
                                ])
                            ]),
                            html.Div(className="column pb-0 mb-0", children=[
                                html.Div(className="block pb-0 mb-0", children=[
                                    html.Div(className="columns pb-0 mb-0", children=[
                                        html.Div(className="column is-one-fifth is-flex is-align-content-flex-start pb-0 mb-0", children=[
                                            html.P(
                                                '2', className='has-text-weight-bold is-size-4')
                                        ]),
                                        html.Div(className="column pb-0 mb-0", children=[
                                            html.Img(src="https://picsum.photos/96",
                                                 className="image is-96x96"),
                                        ]),
                                    ]),
                                    html.Div(className="block is-flex is-justify-content-right", children=[
                                        html.P(
                                            'Destination 2', className='has-text-weight-bold is-size-7 mx-0 my-0 px-0 py-0')
                                    ])
                                ])
                            ]),
                            html.Div(className="column pb-0 mb-0", children=[
                                html.Div(className="block pb-0 mb-0", children=[
                                    html.Div(className="columns pb-0 mb-0", children=[
                                        html.Div(className="column is-one-fifth is-flex is-align-content-flex-start pb-0 mb-0", children=[
                                            html.P(
                                                '3', className='has-text-weight-bold is-size-4')
                                        ]),
                                        html.Div(className="column pb-0 mb-0", children=[
                                            html.Img(src="https://picsum.photos/96",
                                                 className="image is-96x96"),
                                        ]),
                                    ]),
                                    html.Div(className="block is-flex is-justify-content-right", children=[
                                        html.P(
                                            'Destination 3', className='has-text-weight-bold is-size-7 mx-0 my-0 px-0 py-0')
                                    ])
                                ])
                            ]),
                            html.Div(className="column pb-0 mb-0", children=[
                                html.Div(className="block pb-0 mb-0", children=[
                                    html.Div(className="columns pb-0 mb-0", children=[
                                        html.Div(className="column is-one-fifth is-flex is-align-content-flex-start pb-0 mb-0", children=[
                                            html.P(
                                                '4', className='has-text-weight-bold is-size-4')
                                        ]),
                                        html.Div(className="column pb-0 mb-0", children=[
                                            html.Img(src="https://picsum.photos/96",
                                                 className="image is-96x96"),
                                        ]),
                                    ]),
                                    html.Div(className="block is-flex is-justify-content-right", children=[
                                        html.P(
                                            'Destination 4', className='has-text-weight-bold is-size-7 mx-0 my-0 px-0 py-0')
                                    ])
                                ])
                            ]),
                            html.Div(className="column pb-0 mb-0", children=[
                                html.Div(className="block pb-0 mb-0", children=[
                                    html.Div(className="columns pb-0 mb-0", children=[
                                        html.Div(className="column is-one-fifth is-flex is-align-content-flex-start pb-0 mb-0", children=[
                                            html.P(
                                                '5', className='has-text-weight-bold is-size-4')
                                        ]),
                                        html.Div(className="column pb-0 mb-0", children=[
                                            html.Img(src="https://picsum.photos/96",
                                                 className="image is-96x96"),
                                        ]),
                                    ]),
                                    html.Div(className="block is-flex is-justify-content-right", children=[
                                        html.P(
                                            'Destination 5', className='has-text-weight-bold is-size-7 mx-0 my-0 px-0 py-0')
                                    ])
                                ])
                            ])
                        ])

                    ]),
                ]),
            ])
        ]),
    ]),

    html.Footer(className="footer my-0 py-4", children=[
        html.Div(className="content has-text-centered", children=[
            html.P("DATA3888 Pty. Ltd.")
        ])
    ])
])


# TOOK THIS OUT FOR NOW BECAUSE STORYBOARD DIDN'T HAVE THIS
# @app.callback(
#     Output('continent_select', 'value'),
#     Input('location_select', 'value')
# )
# def set_location_values(selected_location):
#     if selected_location is not None:
#         return continent_dictionary[continent_dictionary['Location'] == selected_location]["Continent"].item()

# @app.callback(
#     Input('region_select', 'value'),
#     Input('factor_select', 'value'),
#     Input('interest_select', 'value')
#     # State(), # WHEN THE BUTTON IS PRESSED
#     # Output() #Something to do with descriptions
# )
# def get_recommended_countries(regions: list, factors: list, poi_interests: list):
#     iso_loc = read_iso_loc_data()
#     rec_countries = []
#     rec_countries_data = []
#     interests = factors + poi_interests
#     interested_filtered = interested.copy()
#     for poi in interests:
#         if interests[poi] in interested_filtered:
#             interested_filtered[interests[poi]] = True
#     rec_list = generate_cluster(countries_data, interested_filtered, regions)
#     #for now i'm just implementing the first five countries
#     if len(rec_list) > 5:
#         rec_list = rec_list[0:5]
#     for iso_code in rec_list:
#         country = iso_loc.loc[iso_loc['iso_code'] == iso_code, 'location'].iloc[0]
#         rec_countries.append(country)
#     for country in rec_countries:
#         series = get_country_data(countries_data, country)
#         rec_countries_data.append(series)


if __name__ == '__main__':
    app.run_server(debug=True)
