import re
import textwrap
from dash import Dash, html, dcc, State, ctx
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform
from numpy import empty, mean, array, arange
import plotly.graph_objects as go
import pandas as pd
from common import *
from analytics import *
from analytics_clustering import *
from mapping import *
import json
import re

covid = read_live_covid_data()
countries_data = integrate_all_data(covid)

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

app = DashProxy(__name__, prevent_initial_callbacks=True,
                transforms=[MultiplexerTransform()])


dummy_divs_left = [
    html.Button(id='back', style={'display': 'none'}),
    html.Div(id="hide_advice_btn", style={'display': 'none'}),
    html.Div(id="advice", style={'display': 'none'}),
    html.Div(id="advice_summary", style={'display': 'none'}),
    html.Div(id="advice_div", style={'display': 'none'}),
    html.Div(id='user_choices', style={'display': 'none'})
]

app.layout = html.Div(className="block mx-4 my-4", children=[
    html.Div(id='location_title', style={'display': 'none'}),
    # cache data
    dcc.Store(id="store_left", storage_type="session"),
    dcc.Store(id="store_right", storage_type="session"),
    dcc.Store(id='countries', storage_type='session'),
    dcc.Store(id='factor_store', storage_type='session'),
    dcc.Store(id='interest_store', storage_type='session'),
    # hidden button to stop callback errors
    html.Div(className='columns', children=[
        html.Div(className='column is-one-third is-flex is-align-content-center', children=[
            html.Div(id="left_panel", className='box is-fullheight is-fullwidth', children=[
                # hidden button to stop callback errors
                *dummy_divs_left,
                html.Div(className='block',
                         children=[
                             html.P('Holiday Planner',
                                    className='is-size-2 has-text-link-dark'),
                             html.P(
                                 """If you would like to have a wonderful trip outside Australia,
                                  we can help you.""", className="is-size-6 has-text-justified"),
                             html.P("""Whether or not you already have a destination in mind, or if you're looking for the best local food,
                                   landmarks, or you're just concerned about COVID cases; this application can give you multiple recommendations with relevant
                                    information.""", className="is-size-6 has-text-justified")
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
# save left and right panels on submit
@app.callback(
    Output('store_left', 'data'),
    Output('store_right', 'data'),
    Input('submit', 'n_clicks'),
    Input('left_panel', 'children'),
    Input('right_panel', 'children')
)
def store_initial_input(submit_clicks, left, right):
    triggered_id = list(ctx.triggered_prop_ids.values())[0]
    if triggered_id != 'submit':
        raise PreventUpdate
    return left, right

@app.callback(
    Output('factor_store', 'data'),
    Output('interest_store', 'data'),
    Input('submit', 'n_clicks'),
    State('factor_select', 'value'),
    State('interest_select', 'value'),
    State('submit', 'style')
)
def store_factors_and_interests(submit, factor, interest, submit_style):
    triggered_id = list(ctx.triggered_prop_ids.values())[0]
    if triggered_id != 'submit':
        raise PreventUpdate

    if submit_style is not None:
        if dict(submit_style)['display'] == 'none':
            raise PreventUpdate

    print(factor, interest)
    return factor, interest


# make info panel
dummy_divs = [html.Button(id='submit', style={'display': 'none'}),
              html.Div(id='location_select', style={'display': 'none'}),
              html.Div(id='region_select', style={'display': 'none'}),
              html.Div(id='factor_select', style={'display': 'none'}),
              html.Div(id='interest_select', style={'display': 'none'})
              ]

advice_levels = ["Exercise normal safety precautions",
                 "Exercise a high degree of caution", "Reconsider your need to travel",
                 "Do not travel"]


def find_advice_class(advice_levels, advice):
    className_dict = {
        "Exercise normal safety precautions": "notification is-primary",
        "Exercise a high degree of caution": "notification is-warning",
        "Reconsider your need to travel": "notification is-danger",
        "Do not travel": "notification"
    }
    for level in advice_levels:
        if bool(re.search(level.lower(), advice.lower())):
            return [className_dict[level], level]


variable_groups = get_variable_groups()


def generate_factor_interest_scores(type, user_list, iso_code, variable_groups, df):
    names = []
    values = []
    if not user_list is None:
        for factor in user_list:
            if factor != 'Covid':
                names.append(factor)
                mean_arr = []
                for group in variable_groups[type[factor]]:
                    mean_arr.append(
                        df.loc[df['iso_code'] == iso_code, [group]].iloc[0].item())
                mean_arr = array(mean_arr)
                values.append(round(mean_arr.mean(), 2))
    return names, values


def get_tag_colours(values):
    colours = []
    for value in values:
        if 0 <= float(value) < 3:
            colours.append("tag is-rounded is-danger")
        elif 3 <= float(value) < 6:
            colours.append("tag is-rounded is-warning")
        elif 6 <= float(value) < 8:
            colours.append("tag is-rounded is-success")
        else:
            colours.append("tag is-rounded is-primary")
    return colours


@app.callback(
    Output('left_panel', 'children'),
    Output('right_panel', 'children'),
    Output('countries', 'data'),
    Input('a1', 'n_clicks'),
    Input('a2', 'n_clicks'),
    Input('a3', 'n_clicks'),
    Input('a4', 'n_clicks'),
    Input('a5', 'n_clicks'),
    Input('a6', 'n_clicks'),
    Input('a7', 'n_clicks'),
    Input('a8', 'n_clicks'),
    Input('a9', 'n_clicks'),
    Input('a10', 'n_clicks'),
    Input('a11', 'n_clicks'),
    Input('a12', 'n_clicks'),
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
    Input(component_id='12', component_property='children'),
    Input('store_left', 'data'),
    Input('store_right', 'data'),
    State('factor_store', 'data'),
    State('interest_store', 'data'),
)
def generate_info_panel(a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12,
                        d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12,
                        store_left, store_right, factor_store, interest_store):

    destination_dict = {
        'a1': d1,
        'a2': d2,
        'a3': d3,
        'a4': d4,
        'a5': d5,
        'a6': d6,
        'a7': d7,
        'a8': d8,
        'a9': d9,
        'a10': d10,
        'a11': d11,
        'a12': d12
    }

    left = store_left
    right = store_right
    triggered_id = list(ctx.triggered_prop_ids.values())[0]

    if '' in [d1, d2, d3, d4, d5, d6, d7, d8, d9, d10]:
        raise PreventUpdate

    if triggered_id in ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10', 'a11', 'a12']:

        iso_loc = read_iso_loc_data()
        destination = destination_dict[triggered_id]
        destination_code = loc_to_iso_code(destination, iso_loc)

        description = countries_data.loc[countries_data['iso_code'] == destination_code, [
            'description']].iloc[0].item()

        advice = countries_data.loc[countries_data['iso_code']
                                    == destination_code, ['advice']].iloc[0].item()
        advice_class, advice_summary = find_advice_class(advice_levels, advice)

        new_cases = countries_data.loc[countries_data['iso_code'] == destination_code, [
            'new_cases_smoothed_per_million']].iloc[0].item()
        new_deaths = countries_data.loc[countries_data['iso_code'] == destination_code, [
            'new_deaths_smoothed_per_million']].iloc[0].item()

        iso_loc = read_iso_loc_data()
        destination_code = loc_to_iso_code(destination, iso_loc)

        factor_names, factor_scores = generate_factor_interest_scores(factors,
                                                                      factor_store, destination_code, variable_groups, countries_data)
        factor_colours = get_tag_colours(factor_scores)

        if len(factor_names) < 3:
            to_append = 3 - len(factor_names)
            for i in range(to_append):
                factor_names.append(None)
                factor_scores.append(None)
                factor_colours.append(None)

        interest_names, interest_scores = generate_factor_interest_scores(interests,
                                                                          interest_store, destination_code, variable_groups, countries_data)

        interest_colours = get_tag_colours(interest_scores)
        if len(interest_names) < 7:
            to_append = 7 - len(interest_names)
            for i in range(to_append):
                interest_names.append(None)
                interest_scores.append(None)
                interest_colours.append(None)

        left = html.Div(
            children=[
                html.Div(className='columns', id="user_choices",
                         children=[
                             html.Div(className="column is-one-third", children=[
                                 html.Button(
                                     'Back', className="button is-medium is-link is-light", id="back")
                             ]),
                             html.Div(className="column is-two-thirds", children=[
                                 html.P(
                                     destination, className="is-size-3 has-text-link-dark", id="location_title")])
                         ]),
                html.Div(id="advice_div", className=advice_class, children=[
                    html.Button(className="delete", id="hide_advice_btn"),
                    html.P(advice_summary, className="has-text-weight-bold",
                           id="advice_summary"),
                    html.P(advice, id="advice")
                ]),
                html.Div(className='block', children=[
                    html.P(textwrap.shorten(description,
                                            width=250, placeholder="..."))
                ]),
                html.Div(className='block', children=[
                    html.P('Covid Statistics',
                           className="has-text-weight-bold"),
                    html.Div(className="columns", children=[
                        html.Div(className="column", children=[
                            html.P("New Cases Per Million:",
                                   className="has-text-weight-semibold is-flex"),
                            html.P("New Deaths Per Million:",
                                   className="has-text-weight-semibold is-flex")
                        ]),
                        html.Div(className="column", children=[
                            html.P(new_cases, className='has-text-right'),
                            html.P(new_deaths, className='has-text-right')
                        ])
                    ])
                ]), html.Div(className='block', children=[
                    html.P('Factors',
                           className="has-text-weight-bold"),
                    html.Div(className="columns", children=[
                        html.Div(className="column is-four-fifths", children=[
                            html.P(
                                factor_names[0], className="has-text-weight-semibold"),
                            html.P(
                                factor_names[1], className="has-text-weight-semibold"),
                            html.P(
                                factor_names[2], className="has-text-weight-semibold"),
                        ]),
                        html.Div(className="column", children=[
                            html.Div(factor_scores[0],
                                     className=factor_colours[0]),
                            html.Div(factor_scores[1],
                                     className=factor_colours[1]),
                            html.Div(factor_scores[2],
                                     className=factor_colours[2]),
                        ])
                    ])
                ]),
                html.Div(className='block', children=[
                    html.P('Interests',
                           className="has-text-weight-bold"),
                    html.Div(className="columns", children=[
                        html.Div(className="column is-four-fifths", children=[
                            html.P(
                                interest_names[0], className="has-text-weight-semibold"),
                            html.P(
                                interest_names[1], className="has-text-weight-semibold"),
                            html.P(
                                interest_names[2], className="has-text-weight-semibold"),
                            html.P(
                                interest_names[3], className="has-text-weight-semibold"),
                            html.P(
                                interest_names[4], className="has-text-weight-semibold"),
                            html.P(
                                interest_names[5], className="has-text-weight-semibold"),
                            html.P(
                                interest_names[6], className="has-text-weight-semibold")
                        ]),
                        html.Div(className="column", children=[
                            html.Div(
                                interest_scores[0], className=interest_colours[0]),
                            html.Div(
                                interest_scores[1], className=interest_colours[1]),
                            html.Div(
                                interest_scores[2], className=interest_colours[2]),
                            html.Div(
                                interest_scores[3], className=interest_colours[3]),
                            html.Div(
                                interest_scores[4], className=interest_colours[4]),
                            html.Div(
                                interest_scores[5], className=interest_colours[5]),
                            html.Div(
                                interest_scores[6], className=interest_colours[6])
                        ])
                    ])
                ]),
                *dummy_divs
            ])

    return left, right, [d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12]


@app.callback(
    Output('graph', 'figure'),
    Input(component_id='location_title', component_property='children'),
    State('countries', 'data'),
    State('back', 'style'),

)
def update_map_with_colour(location, countries, back):

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

    if back is not None:
        if dict(back)['display'] == 'none':
            raise PreventUpdate

    return update_map_on_click(world_map, countries_data, countries, location)


@app.callback(
    [Output('advice_div', 'style'),
     Output('hide_advice_btn', 'style'),
     Output('advice_summary', 'style'),
     Output('advice', 'style')],
    Input('hide_advice_btn', 'n_clicks')
)
def hide_advice_div(n_clicks):
    triggered_id = list(ctx.triggered_prop_ids.values())[0]
    if triggered_id != 'hide_advice_btn':
        raise PreventUpdate
    return [{'display': 'none'}] * 4


@app.callback(
    Output('left_panel', 'children'),
    Input('back', 'n_clicks'),
    Input('store_left', 'data')
)
def restore_stored_data(back_clicks, store_left):
    if back_clicks == 0 or back_clicks == None:
        raise PreventUpdate

    return store_left

# auto fill regions


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
    Input('submit', 'n_clicks'),
    Input('countries', 'data'),
    State('factor_select', 'value'),
    State('interest_select', 'value'),
)
def get_recommended_countries(location: str, chosen_regions: list, submit: int, countries: list, chosen_factors: list, chosen_interests: list):
    df = pd.read_csv("data/data.txt")
    df = df.drop(columns='Unnamed: 0')

    rec_countries = []
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

    if not countries is None and len(countries) > 0:
        rec_countries = countries

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

    if submit != 0 and not submit is None:
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
    app.run_server(debug=False)
