from dash import Dash, html, dcc, Input, Output
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

# attraction types
attraction_types = ['amusement_park', 'aquarium', 'art_gallery', 'bar', 'book_store', 'cafe',
                    'campground', 'casino', 'cemetery', 'church', 'city_hall', 'clothing_store',
                    'department_store', 'food', 'general_contractor', 'grocery_or_supermarket',
                    'health', 'hindu_temple', 'hospital', 'library', 'liquor_store', 'local_government_office',
                    'lodging', 'mosque', 'movie_theater', 'museum', 'natural_feature', 'night_club',
                    'park', 'parking', 'place_of_worship', 'restaurant', 'shopping_mall', 'spa',
                    'store', 'synagogue', 'transit_station', 'travel_agency', 'zoo']


locations = ['Albania', 'Algeria', 'Argentina', 'Armenia', 'Australia',
             'Austria', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Barbados',
             'Belgium', 'Bolivia', 'Botswana', 'Brazil', 'Bulgaria', 'Cambodia',
             'Cameroon', 'Canada', 'Chile', 'China', 'Colombia', 'Costa Rica',
             'Croatia', 'Cyprus', 'Denmark', 'Dominican Republic', 'Ecuador',
             'Egypt', 'El Salvador', 'Estonia', 'Ethiopia', 'Finland', 'France',
             'Georgia', 'Germany', 'Ghana', 'Greece', 'Guatemala', 'Honduras',
             'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran',
             'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan',
             'Kazakhstan', 'Kenya', 'Kuwait', 'Latvia', 'Lebanon', 'Lithuania',
             'Luxembourg', 'Malaysia', 'Malta', 'Mauritius', 'Mexico',
             'Moldova', 'Mongolia', 'Montenegro', 'Morocco', 'Myanmar', 'Nepal',
             'Netherlands', 'New Zealand', 'Nicaragua', 'Nigeria',
             'North Macedonia', 'Norway', 'Oman', 'Pakistan', 'Panama',
             'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar',
             'Romania', 'Russia', 'Rwanda', 'Saudi Arabia', 'Senegal', 'Serbia',
             'Seychelles', 'Singapore', 'Slovakia', 'Slovenia', 'South Africa',
             'South Korea', 'Spain', 'Sri Lanka', 'Suriname', 'Sweden',
             'Switzerland', 'Taiwan', 'Tanzania', 'Thailand', 'Tunisia',
             'Turkey', 'Uganda', 'Ukraine', 'United Arab Emirates',
             'United Kingdom', 'United States', 'Uruguay', 'Venezuela',
             'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe']


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
                             html.P('HolidayPlanner',
                                    className='has-text-weight-bold is-size-3'),
                             html.P(
                                 "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore "
                                 "et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
                                 "aliquip ex ea commodo consequat.")
                         ]),
                    html.Div(className='block', children=[
                        html.Label(
                            'Where would you like to go?', className='has-text-weight-medium is-size-5'),
                        dcc.Dropdown(locations, multi=False, id="location_select")
                    ]),
                    html.Div(className='block', children=[
                        html.Div(className='block', children=[
                            html.Label(
                                'Continents', className='has-text-weight-semibold'),
                            dcc.Dropdown(['Asia', 'Africa', 'Oceania', 'Europe', 'North America', 'South America'],
                                         multi=True, id="continent_select")
                        ]),
                        html.Div(className='block', children=[
                            html.Label(
                                'Interests', className='has-text-weight-semibold'),
                            html.Label(''),
                            dcc.Dropdown(attraction_types,
                                         multi=True)
                        ]),
                        html.Div(className='block', children=[
                            html.Label('Covid Concern',
                                       className='has-text-weight-semibold'),
                            dcc.Slider(0, 2, 1, value=1,
                                       marks={
                                           0: {'label': 'Low'},
                                           1: {'label': 'Medium'},
                                           2: {'label': 'High'}
                                       },
                                       included=False)
                        ]),
                        html.Div(className='block', children=[
                            html.Label(
                                'Cost', className='has-text-weight-semibold'),
                            dcc.Slider(0, 2, 1, value=1,
                                       marks={
                                           0: {'label': 'Budget'},
                                           1: {'label': 'Mid Range'},
                                           2: {'label': 'Luxury'}
                                       },
                                       included=False)
                        ])
                    ]),
                ])
            ]),
            html.Div(className='column is-two-thirds', children=[
                html.Div(className='box', children=[
                    html.Div(className="block", children=[
                         dcc.Graph(figure=world_map)]),
                    html.Div(className="box", children=[
                        html.Div(className="columns", children=[
                            html.Div(className="column is-two-fifth", children=[
                                html.Img(src="https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=Aap_uED8BHNIhfvXSZ9OPm-TLTTqImTUHEo2Zk2u2zDIhmcwi5yKt346mgK9EuFMkdJCDvGY4wJYoYJXE3FlGtriqTrb0LjZJhgzi4iOlnm1rLsUGS8ebD-kmxSxiLtEMFDPm4Syy1V6OMy8RMjYnTNY8T7wgeYSKYAQmiHNZkY32Hb-FDIj&key=AIzaSyCl2zou68i4ekrpbo7MwmbLtZBnIsexHqE",
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
                                            html.Img(src="https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=Aap_uEBsbP6F32NI6wKyY9Lz8WO6TigM9MrH4aPC6N-HquyDib5DWNFBzzaUFevJ8dNW6kuQrjdOCmvG2DETSvpbgsRSUdyDi-EcFBSgNcskbIJGSnjmZplQrA9c2EiZkZSrEezSDPdsAs5Mo_1-cCzkR2IgRNXI7C-TWFIEYnCtrzAsD06F&key=AIzaSyCl2zou68i4ekrpbo7MwmbLtZBnIsexHqE",
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
                                            html.Img(src="https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=Aap_uEBrn2VuvoxPgA9p3vER0C06DoV7Vnb-YuY9-XGA-YEggrUvgKt1ma6zUxoP3RTNzotsafnkCi4uEtNPM0Q_oqBxiViGfgK-DhSyg4iAzSQ3L4SOBo4Mz7EOuIwX9XQkvQ9GJUIyK9G1z0PyL4sleILUEC2GVLhyV1UE--LXiP7XEakf&key=AIzaSyCl2zou68i4ekrpbo7MwmbLtZBnIsexHqE",
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
                                            html.Img(src="https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=Aap_uECqJ9aZuugcz4izuTV83N1V_t2E3FIMA43B6bFfcqPs34M-wnbV_fYY7TQG6FXyZ-n7X1-HfJPsDhF3a1S9eaXR_YmjPpVoOYxkOAoY0WgR6d8v0m3iOPdPefwfedPvQr3_XOYsbAspNNav0gZHICyXjl2gt2h06IpdY2XsLP0BkYNP&key=AIzaSyCl2zou68i4ekrpbo7MwmbLtZBnIsexHqE",
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
                                            html.Img(src="https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=Aap_uEDkecjCUPfOe3oXJPw1G8jXoHUudyDPwN0udZ7cJVZzvoEAO0yXpasTaldDogS5IZndSS1V3t_jg9kpOFAWb7c38YGXh1H5twGro7RMsNQsAq7eZz0VH7D2h_RW2zu44GdPIR4BNEbCtmOa8YXGqFiRk0YUeXJi937VioazGloseLbG&key=AIzaSyCl2zou68i4ekrpbo7MwmbLtZBnIsexHqE",
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

@app.callback(
    Output('continent_select', 'value'),
    Input('location_select', 'value')
)
def set_location_values(selected_location):
    if selected_location is not None:
        return continent_dictionary[continent_dictionary['Location'] == selected_location]["Continent"].item()


if __name__ == '__main__':
    app.run_server(debug=True)
