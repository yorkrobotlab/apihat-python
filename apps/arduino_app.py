# YRL028 - APIHAT - Dash-DAQ Server Version 0.2
#
# Arduino Tab
#
# James Hilder, York Robotics Laboratory, Mar 2019

import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import settings, utils
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from app import app
import css
flex_style =css.flex_style
border_style = css.border_style
block_style = css.block_style

window_size = 120

layout = html.Div([
    html.Div(id='encoder-div',style=border_style),
    dcc.Interval(
            id='encoder-interval-component',
            interval=0.5*1000, # in milliseconds
            n_intervals=0
    ),
])

@app.callback(
    Output('encoder-div','children'),    [Input('encoder-interval-component', 'n_intervals')])
def update_values(n_intervals):
    data = pd.read_csv('/ramdisk/system.csv')
    try:
        current_values = data[['system-time','enc-1-relative','enc-1-cumulative','enc-2-relative','enc-2-cumulative']].tail(2).iloc[0]
        system_time = round(current_values['system-time'],3)
        enc_1_relative = int(current_values['enc-1-relative'])
        enc_2_relative = int(current_values['enc-2-relative'])
        col_positive = "#5EFF5E"
        col_negative = "#FF5E5E"
        enc_1_col = col_positive
        enc_2_col = col_positive
        if(enc_1_relative < 0):
            enc_1_col = col_negative
            enc_1_relative = 0 - enc_1_relative
        if(enc_2_relative < 0):
            enc_2_col = col_negative
            enc_2_relative = 0 - enc_2_relative
        enc_1_cumulative = int(current_values['enc-1-cumulative'])
        enc_2_cumulative = int(current_values['enc-2-cumulative'])
        ret=html.Div([
                html.Div([
                    html.Div([
                        html.H6("Encoder 1"),
                        daq.LEDDisplay(
                            label="Relative",
                            value=("%08d" % (enc_1_relative)),
                            color=enc_1_col,
                            size=36,
                            ),
                        daq.LEDDisplay(
                            label="Cumulative",
                            value=("%08d" % (enc_1_cumulative)),
                            color=col_positive,
                            size=36,
                            ),
                        ],style={"textAlign": "center", "width": "48%"}),
                    html.Div([
                        html.H6("Encoder 2"),
                        daq.LEDDisplay(
                            label="Relative",
                            value=("%08d" % (enc_2_relative)),
                            color=enc_2_col,
                            size=36,
                            ),
                        daq.LEDDisplay(
                            label="Cumulative",
                            value=("%08d" % (enc_2_cumulative)),
                            color=col_positive,
                            size=36,
                            ),
                        ],style={"textAlign": "center", "width": "48%"}),

                ],style=flex_style),
                html.Div('Last response time: {}'.format(utils.decode_time(system_time).rstrip("0"))),
            ])
    except IndexError:
        ret = html.Div('Could not read system status file.\nIs core.py running, ramdisk correctly setup and system polling enabled in settings.py?')
    return ret
