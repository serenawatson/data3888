from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import pandas as pd

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

app = Dash(__name__)

app.layout = html.Div(className='block ml-4 mt-4', children=[
    html.Div(className='columns', children=[
        html.Div(className='column is-one-third', children=[
            html.Div(className='box', children=[
                html.Div(className='block',
                         children=[html.P('HolidayPlanner', className='has-text-weight-bold is-size-3')]),
                html.Div(className='block', children=[
                    html.P(
                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore "
                        "et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
                        "aliquip ex ea commodo consequat.")]),
                html.Div(className='block', children=[
                    html.Div(className='block', children=[
                        html.Label('Covid Concern', className='has-text-weight-semibold'),
                        dcc.Slider(0, 2, 1, value=1,
                                   marks={
                                       0: {'label': 'Low'},
                                       1: {'label': 'Medium'},
                                       2: {'label': 'High'}
                                   },
                                   included=False)
                    ]),
                    html.Div(className='block', children=[
                        html.Label('Cost', className='has-text-weight-semibold'),
                        dcc.Slider(0, 2, 1, value=1,
                                   marks={
                                       0: {'label': 'Budget'},
                                       1: {'label': 'Mid Range'},
                                       2: {'label': 'Luxury'}
                                   },
                                   included=False)
                    ])
                ]),

                html.Div(className='block', children=[
                    html.Label('Continents', className='has-text-weight-semibold'),
                    dcc.Dropdown(['Asia', 'Africa', 'Oceania', 'Europe', 'North America', 'South America'],
                                 multi=True)
                ]),
                html.Div(className='block', children=[
                    html.Label('Interests', className='has-text-weight-semibold'),
                    html.Label(''),
                    dcc.Dropdown(attraction_types,
                                 multi=True)
                ])
            ])
        ]),
        html.Div(className='column is-two-thirds', children=[
            html.Div(className='box', children=[
                html.Div(className="block", children=[dcc.Graph(figure=world_map)]),
                html.Div(className="box", children=[
                    html.Div(className="columns", children=[
                        html.Div(className="column is-two-fifth", children=[
                            html.Img(src="https://picsum.photos/128", className="image is-128x128")
                        ]),
                        html.Div(className="column", children=[
                            html.Div(className="block", children=[
                                html.P('Country 1', className='has-text-weight-bold is-size-5'),
                                html.P(
                                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
                            ])
                        ]),
                        html.Div(className="column", children=[
                            html.Img(src="https://picsum.photos/96", className="image is-96x96"),
                            html.P('Country 2', className='has-text-weight-bold is-size-6')
                        ]),
                        html.Div(className="column", children=[
                            html.Img(src="https://picsum.photos/96", className="image is-96x96"),
                            html.P('Country 3', className='has-text-weight-bold is-size-6')
                        ]),
                        html.Div(className="column", children=[
                            html.Img(src="https://picsum.photos/96", className="image is-96x96"),
                            html.P('Country 4', className='has-text-weight-bold is-size-6')
                        ]),
                        html.Div(className="column", children=[
                            html.Img(src="https://picsum.photos/96", className="image is-96x96"),
                            html.P('Country 5', className='has-text-weight-bold is-size-6')
                        ])
                    ])

                ]),
            ]),
        ])
    ])
])
html.Footer(className="footer", children=[
    html.Div(className="content has-text-centered", children=[
        html.P("Best Team Pty. Ltd.")
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
