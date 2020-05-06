# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from plotly import subplots
import folium
from folium.features import DivIcon
from dash.dependencies import Input, Output, State
from rec_sys import RecSys
from load import Load
import time

df_rightmove = Load('rightmove').read_db()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


class NoRecsReturnedError(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return repr(self.data)


def temp_treat_price_string(row):
    if type(row) == str:
        splitted_row = row.split(' ')
        if 'pcm' in splitted_row:
            index_pcm = splitted_row.index('pcm')
            value = ''.join(i for i in splitted_row[index_pcm - 1] if i.isdigit())
            return float(value)
        elif 'pw' in splitted_row:
            index_pw = splitted_row.index('pw')
            value = ''.join(i for i in splitted_row[index_pw - 1] if i.isdigit())
            return round((float(value) * 52) / 12, 2)
        else:
            return 1500
    else:
        return row


def make_rec_areas_time_subplots(df=None, list_time_to_work=[40, 10, 25],
                                 list_rec_areas=['Greenwich', 'City', 'Brixton']):
    if df is None:
        list_avg_price = [1000, 1220, 1525]
    elif df.empty:
        list_avg_price = [0, 0, 0]
        list_time_to_work = [0, 0, 0]
    else:
        df_area1 = df[df['area'] == list_rec_areas[0]]
        df_area2 = df[df['area'] == list_rec_areas[1]]
        df_area3 = df[df['area'] == list_rec_areas[2]]

        avg_price_area1 = df_area1['price'].mean()
        avg_price_area2 = df_area2['price'].mean()
        avg_price_area3 = df_area3['price'].mean()
        list_avg_price = [avg_price_area1, avg_price_area2, avg_price_area3]

    trace1 = go.Bar(
        x=[list_rec_areas[0], list_rec_areas[1], list_rec_areas[2]],
        y=list_avg_price,
        marker=dict(color=['lightgreen', 'limegreen', 'lightseagreen'])
    )
    trace2 = go.Bar(
        x=[list_rec_areas[0], list_rec_areas[1], list_rec_areas[2]],
        y=list_time_to_work,
        marker=dict(color=['lightgreen', 'limegreen', 'lightseagreen'])
    )

    fig = subplots.make_subplots(rows=1, cols=2, shared_xaxes=False,
                                 shared_yaxes=False, subplot_titles=("Average Price/ Areas",
                                                                     "Average Time to Work/ Areas"))

    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 1, 2)

    # Update xaxis properties
    fig.update_xaxes(title_text="Area", row=1, col=1)
    fig.update_xaxes(title_text="Area", row=1, col=2)

    # Update yaxis properties
    fig.update_yaxes(title_text="Average Price (£)", row=1, col=1)
    fig.update_yaxes(title_text="Average Time to Work (min)", row=1, col=2)

    fig['layout'].update(title_text='Comparing Time to Center/Work for your recommended areas',
                         title_x=0.5, showlegend=False,
                         paper_bgcolor='rgba(0,0,0,0)',
                         plot_bgcolor='rgba(0,0,0,0)')
    return fig


def make_rec_areas_price_subplots(df=None, area='Greenwich'):
    if df is None:
        list_trace_bedrooms = [1200, 1800, 2100]
        list_trace_furniture = [2100, 1800, 2000, 2200]
        list_trace_y_extras = [2000, 1900, 2100]
        list_trace_n_extras = [1800, 1700, 1900]
    elif df.empty:
        list_trace_bedrooms = [0, 0, 0]
        list_trace_furniture = [0, 0, 0, 0]
        list_trace_y_extras = [0, 0, 0]
        list_trace_n_extras = [0, 0, 0]
        list_time_to_work = [0, 0, 0]
        list_rec_areas = ['', '', '']
    else:
        df_area = df[df['area'] == area]
        df_area['price'] = df_area['price'].apply(temp_treat_price_string)

        # Studio
        df_area_studio = df_area[df_area['number_bedrooms'] == 0]
        avg_price_studio = df_area_studio['price'].mean()
        # 1 Bedroom
        df_area_1bed = df_area[df_area['number_bedrooms'] == 1]
        avg_price_1bed = df_area_1bed['price'].mean()
        # 2 Bedroom
        df_area_2bed = df_area[df_area['number_bedrooms'] == 2]
        avg_price_2bed = df_area_2bed['price'].mean()
        list_trace_bedrooms = [avg_price_studio, avg_price_1bed, avg_price_2bed]

        # Furnished
        df_area_furnished = df_area[df_area['furnished'] == 1]
        avg_price_furnished = df_area_furnished['price'].mean()
        # Unfurnished
        df_area_unfurnished = df_area[df_area['furnished'] == 0]
        avg_price_unfurnished = df_area_unfurnished['price'].mean()
        # Part Furnished
        df_area_part_furnished = df_area[df_area['furnished'] == 2]
        avg_price_part_furnished = df_area_part_furnished['price'].mean()
        # Flexible
        df_area_flexible = df_area[df_area['furnished'] == 4]
        avg_price_flexible = df_area_flexible['price'].mean()
        list_trace_furniture = [avg_price_furnished, avg_price_unfurnished, avg_price_part_furnished,
                                avg_price_flexible]

        # YES Balcony
        df_area_y_balcony = df_area[df_area['balcony'] == 1]
        avg_price_y_balcony = df_area_y_balcony['price'].mean()
        # YES Garden
        df_area_y_garden = df_area[df_area['garden'] == 1]
        avg_price_y_garden = df_area_y_garden['price'].mean()
        # YES Refurbished
        df_area_y_refurbished = df_area[df_area['refurbished'] == 1]
        avg_price_y_refurbished = df_area_y_refurbished['price'].mean()
        list_trace_y_extras = [avg_price_y_balcony, avg_price_y_garden, avg_price_y_refurbished]

        # NO Balcony
        df_area_n_balcony = df_area[df_area['balcony'] == 0]
        avg_price_n_balcony = df_area_n_balcony['price'].mean()
        # NO Garden
        df_area_n_garden = df_area[df_area['garden'] == 0]
        avg_price_n_garden = df_area_n_garden['price'].mean()
        # NO Refurbished
        df_area_n_refurbished = df_area[df_area['refurbished'] == 0]
        avg_price_n_refurbished = df_area_n_refurbished['price'].mean()
        list_trace_n_extras = [avg_price_n_balcony, avg_price_n_garden, avg_price_n_refurbished]

    trace1 = go.Bar(
        x=['Studio', 'One', 'Two'],
        y=list_trace_bedrooms,
        marker=dict(color=['lightgreen', 'limegreen', 'lightseagreen'])
    )
    trace2 = go.Bar(
        x=['Furnished', 'Not Furnished', 'Part Furnished', 'Landlord is flexible'],
        y=list_trace_furniture,
        marker=dict(color=['lightgreen', 'limegreen', 'lightseagreen', 'darkolivegreen'])
    )
    trace3 = go.Bar(
        x=['Balcony', 'Garden', 'Refurbished'],
        y=list_trace_y_extras,
        marker=dict(color=['lightgreen', 'lightgreen', 'lightgreen']),
        name="YES",
        orientation='v'
    )
    trace4 = go.Bar(
        x=['Balcony', 'Garden', 'Refurbished'],
        y=list_trace_n_extras,
        marker=dict(color=['lightseagreen', 'lightseagreen', 'lightseagreen']),
        name="NO",
        orientation='v'
    )
    fig = subplots.make_subplots(rows=1, cols=3, shared_xaxes=False,
                                 shared_yaxes=False, subplot_titles=("Average Price/ Number of Bedrooms",
                                                                     "Average Price/ Furniture",
                                                                     "Average Price/ Extras"))
    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 1, 2)
    fig.append_trace(trace3, 1, 3)
    fig.append_trace(trace4, 1, 3)

    # Update xaxis properties
    fig.update_xaxes(title_text="Number of Bedrooms", row=1, col=1)
    fig.update_xaxes(title_text="Furniture", row=1, col=2)
    fig.update_xaxes(title_text="Extras", row=1, col=3)

    # Update yaxis properties
    fig.update_yaxes(title_text="Average Price (£)", row=1, col=1)
    fig.update_yaxes(title_text="Average Price (£)", row=1, col=2)
    fig.update_yaxes(title_text="Average Price (£)", row=1, col=3)

    fig['layout'].update(title_text='Comparing Prices for your recommended Areas',
                         title_x=0.5, showlegend=False,
                         paper_bgcolor='rgba(0,0,0,0)',
                         plot_bgcolor='rgba(0,0,0,0)'
                         )
    return fig


def make_heatmap(df=None):
    x_axis = ['Studio', 'One Bedroom', 'Two Bedrooms']
    y_axis = ['0-10', '10-20', '20-30', '30-40', '40-50', '>50']
    if df is None:
        z_axis = [[1800, 2200, 3000], [1600, 2000, 2800], [1400, 1800, 2600], [1200, 1600, 2400],
                  [1000, 1400, 2200], [800, 1200, 2000]]
    elif df.empty:
        z_axis = [[None, None, None], [None, None, None], [None, None, None], [None, None, None],
                  [None, None, None], [None, None, None]]
    else:
        df_0_10 = df[df['time_to_work'] <= 10]
        df_10_20 = df[(df['time_to_work'] > 10) & (df['time_to_work'] <= 20)]
        df_20_30 = df[(df['time_to_work'] > 20) & (df['time_to_work'] <= 30)]
        df_30_40 = df[(df['time_to_work'] > 30) & (df['time_to_work'] <= 40)]
        df_40_50 = df[(df['time_to_work'] > 40) & (df['time_to_work'] <= 50)]
        df_50 = df[df['time_to_work'] > 50]

        dfs = [df_0_10, df_10_20, df_20_30, df_30_40, df_40_50, df_50]
        z = []
        for df in dfs:
            z_df = [df[df['number_bedrooms'] == 0]['price'].mean() if df[df['number_bedrooms'] == 0][
                                                                          'price'].mean() != np.nan else 0,
                    df[df['number_bedrooms'] == 1]['price'].mean() if df[df['number_bedrooms'] == 1][
                                                                          'price'].mean() != np.nan else 0,
                    df[df['number_bedrooms'] == 2]['price'].mean() if df[df['number_bedrooms'] == 2][
                                                                          'price'].mean() != np.nan else 0]
            z.append(z_df)
        z_axis = z

    fig = go.Figure(data=go.Heatmap(
        z=z_axis,
        x=x_axis,
        y=y_axis,
        colorbar=dict(title="Average Price (£)"),
        coloraxis="coloraxis"))
    fig.update_xaxes(title_text="Number of Bedrooms")
    fig.update_yaxes(title_text="Average Time to Work (min)")
    fig['layout'].update(title_text='General Analysis',
                         title_x=0.5)
    fig.update_layout(coloraxis={'colorscale': 'viridis'})
    return fig


def make_ldn_map(coord1=[51.476852, -0.000500], coord2=[51.509865, -0.118092], coord3=[51.457331504, -0.109666228]):
    ldn = [51.506949, -0.122876]
    m = folium.Map(width='100%', height=480, location=ldn)

    if not coord1 and not coord2 and not coord3:
        m.save('london.html')
        return 'london.html'
    else:
        p1 = tuple(coord1)
        folium.Marker(p1, icon=DivIcon(
            icon_size=(150, 36),
            icon_anchor=(7, 20),
            html='<div style="font-size: 20pt; color : white; font-family: arial">1</div>',
        )).add_to(m)
        m.add_child(folium.CircleMarker(p1, radius=15, fill=True,
                                        fill_opacity=0.8))

        p2 = tuple(coord2)
        folium.Marker(p2, icon=DivIcon(
            icon_size=(150, 36),
            icon_anchor=(7, 20),
            html='<div style="font-size: 20pt; color : white; font-family: arial">2</div>',
        )).add_to(m)
        m.add_child(folium.CircleMarker(p2, radius=15, fill=True,
                                        fill_opacity=0.8))
        p3 = tuple(coord3)
        folium.Marker(p3, icon=DivIcon(
            icon_size=(150, 36),
            icon_anchor=(7, 20),
            html='<div style="font-size: 20pt; color : white; font-family: arial">3</div>',
        )).add_to(m)
        m.add_child(folium.CircleMarker(p3, radius=15, fill=True,
                                        fill_opacity=0.8))

        m.save('london.html')
        return 'london.html'


app.layout = html.Div(children=[

    html.P(style={'margin': '2em 0 0 0'}),

    html.H1(children='Find Your Home', style={'text-align': 'center'}),

    html.Div(children='''
        Find the London areas that fit your budget and desired time to work
    ''', style={'text-align': 'center'}),

    html.P(style={'margin': '3em 0 0 0'}),

    html.Div(children=[

        html.Div(style={'width': '1%', 'display': 'inline-block'}
                 ),

        html.Div(children=[
            html.Label('Work Address'),
            dcc.Input(id='input-work-address', value='Old St, London', type='text')],
            style={'width': '19%', 'display': 'inline-block'}
        ),

        html.Div(children=[
            html.Label('Max. Time to work (min)'),
            dcc.Input(id='input-time-work', value='10', type='text')],
            style={'width': '19%', 'display': 'inline-block'}
        ),

        html.Div(children=[
            html.Label('Max. Budget (£)'),
            dcc.Input(
                id='input-max-budget', value='1000', type='text')],
            style={'width': '19%', 'display': 'inline-block'}
        ),

        html.Div(children=[
            html.Label('Number of Bedrooms'),
            dcc.Dropdown(
                id='dropdown-number-bedrooms',
                options=[{'label': 'Studio', 'value': 'Studio'},
                         {'label': 'One', 'value': 'One'},
                         {'label': 'Two', 'value': 'Two'}],
                value='Studio')],
            style={'width': '19%', 'display': 'inline-block', 'vertical-align': 'top'},
        ),

        html.Div(children=html.Button(id='submit-button-state',
                                      n_clicks=0,
                                      children='Find',
                                      style={'width': '50%', 'text-align': 'center',
                                             'float': 'right', 'background-color': '#0C71E0', 'color': 'white'}),
                 style={'width': '19%', 'display': 'inline-block', 'vertical-align': 'bottom'}
                 ),
    ]),

    dcc.Loading(id='loading',
                children=[

                    html.P(style={'margin': '1em 0 0 0'}),

                    html.Div(id='error', children='', style={'text-align': 'center', 'font-weight': 'bold'}),

                    html.P(style={'margin': '4em 0 0 0'}),

                    html.H6(children='Recommended for you',
                            style={'text-align': 'center'}),

                    html.Iframe(id='iframe-london-map',
                                srcDoc=open(make_ldn_map(), 'r').read(),
                                width='100%',
                                height=480,
                                style={'display': 'inline-block', 'width': '100%'}
                                ),

                    dcc.Markdown(id='markdown-rec-areas',
                                 children=''' **Your recommended areas**
                                    1. Greenwich
                                    2. City
                                    3. Brixton''',
                                 style={'display': 'inline-block', 'vertical-align': 'top'}),

                    dcc.Graph(
                        id='graph-rec-areas-time',
                        figure=make_rec_areas_time_subplots()
                    ),

                    html.H6(children='Choose from your recommended areas',
                            style={'text-align': 'center'}),
                    dcc.Dropdown(
                        id='dropdown-rec-area',
                        options=[{'label': 'Greenwich', 'value': 'Greenwich'},
                                 {'label': 'City', 'value': 'City'},
                                 {'label': 'Brixton', 'value': 'Brixton'}],
                        value='Greenwich',
                        style={'height': '30px', 'width': '50%', 'text-align': 'center', 'left': '75%', 'right': 'auto'}
                    ),

                    dcc.Graph(
                        id='graph-rec-areas-price',
                        figure=make_rec_areas_price_subplots()
                    ),

                    dcc.Graph(
                        id='graph-bedrooms-time-price-heatmap',
                        figure=make_heatmap()
                    )],
                type='circle',
                )
])


@app.callback(
    [Output('iframe-london-map', 'srcDoc'),
     Output('markdown-rec-areas', 'children'),
     Output('graph-rec-areas-time', 'figure'),
     Output('dropdown-rec-area', 'options'),
     Output('graph-bedrooms-time-price-heatmap', 'figure'),
     Output('error', 'children')],
    [Input('submit-button-state', 'n_clicks')],
    [State('input-work-address', 'value'),
     State('input-time-work', 'value'),
     State('input-max-budget', 'value'),
     State('dropdown-number-bedrooms', 'value')])
def update_app_part1(n_clicks, work_address, time_work, max_budget, number_bedrooms):
    if n_clicks == 0:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    else:
        try:
            # Create User Vector
            if number_bedrooms == 'Studio':
                user_vector = [0, int(max_budget), work_address, int(time_work)]
            elif number_bedrooms == 'One':
                user_vector = [1, int(max_budget), work_address, int(time_work)]
            else:
                user_vector = [2, int(max_budget), work_address, int(time_work)]

            # Get Recommended Areas
            rec_obj = RecSys(user_vector, df_rightmove)
            rec_areas = rec_obj.get_rec_areas()
            if len(rec_areas) < 3:
                raise NoRecsReturnedError("Number of Recommended Areas can't be < 3")
            coord_rec_areas = rec_obj.get_rec_areas_coord()
            times_to_work_rec_areas = rec_obj.get_rec_areas_time_work()
            df_homes_vec_time_work = rec_obj.get_df_heatmap()

            # Update iFrame
            coord1_strings = coord_rec_areas[0].split(',')
            coord1 = list(map(float, coord1_strings))
            coord2_strings = coord_rec_areas[1].split(',')
            coord2 = list(map(float, coord2_strings))
            coord3_strings = coord_rec_areas[2].split(',')
            coord3 = list(map(float, coord3_strings))
            updated_src_doc = open(make_ldn_map(coord1, coord2, coord3), 'r').read()
            # Update Markdown
            updated_children_markdown = '''
                **Your recommended areas**
                                1. {0}
                                2. {1}
                                3. {2}
                '''.format(rec_areas[0], rec_areas[1], rec_areas[2])

            # Update Subplots Rec Areas Time
            updated_figure_rec_areas_time = make_rec_areas_time_subplots(df_rightmove,
                                                                         list_time_to_work=times_to_work_rec_areas,
                                                                         list_rec_areas=rec_areas)

            # Options Dropdown Rec Areas
            options_dropdown = [{'label': rec_areas[0], 'value': rec_areas[0]},
                                {'label': rec_areas[1], 'value': rec_areas[1]},
                                {'label': rec_areas[2], 'value': rec_areas[2]}]

            # Update Heatmap Figure
            updated_fig_bed_time_price_heatmap = make_heatmap(df_homes_vec_time_work)

            # Don't show error message
            no_error = ''

            return updated_src_doc, updated_children_markdown, updated_figure_rec_areas_time, options_dropdown, \
                   updated_fig_bed_time_price_heatmap, no_error
        except NoRecsReturnedError as e:

            empty_df = pd.DataFrame()

            # Update iFrame
            updated_src_doc = open(make_ldn_map([], [], []), 'r').read()

            # Update Markdown
            updated_children_markdown = ''' There are no recommended areas '''

            # Update Subplots Rec Areas Time
            updated_figure_rec_areas_time = make_rec_areas_time_subplots(empty_df)

            # Options Dropdown Rec Areas
            options_dropdown = []

            # Update Heatmap Figure
            updated_fig_bed_time_price_heatmap = make_heatmap(empty_df)

            # Show error message
            error = ''' No areas matched your search. Please increase your Maximum Time to Work and/or Budget.'''
            return updated_src_doc, updated_children_markdown, updated_figure_rec_areas_time, options_dropdown,\
                   updated_fig_bed_time_price_heatmap, error


@app.callback(
    Output('graph-rec-areas-price', 'figure'),
    [Input('dropdown-rec-area', 'value'),
     Input('dropdown-rec-area', 'options')])
def update_app_part2(rec_area, options):
    if not options:
        # Update Subplots Rec Areas Price
        updated_figure_rec_areas_price = make_rec_areas_price_subplots(pd.DataFrame())
    else:
        # Update Subplots Rec Areas Price
        updated_figure_rec_areas_price = make_rec_areas_price_subplots(df_rightmove, area=rec_area)
    return updated_figure_rec_areas_price


if __name__ == '__main__':
    app.run_server(debug=True)
