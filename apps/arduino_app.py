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
        tail_data = data[['system-time','enc-1-relative','enc-1-cumulative','enc-2-relative','enc-2-cumulative']].tail(2)
        current_values = tail_data.iloc[1]
        previous_values = tail_data.iloc[0]
        system_time = round(current_values['system-time'],3)
        previous_time = round(previous_values['system-time'],3)
        time_delta = system_time-previous_time
        enc_1_relative = int(current_values['enc-1-relative'])
        enc_2_relative = int(current_values['enc-2-relative'])
        enc_1_previous = int(previous_values['enc-1-relative'])
        enc_2_previous = int(previous_values['enc-2-relative'])
        enc_1_dif = enc_1_relative - enc_1_previous
        enc_2_dif = enc_2_relative - enc_2_previous
        col_positive = "#5EFF5E"
        col_negative = "#FF5E5E"
        enc_1_tcol = col_positive
        enc_2_tcol = col_positive
        if(enc_1_dif < 0):
            enc_1_tcol = col_negative
            enc_1_dif = 0 - enc_1_dif
        if(enc_2_dif < 0):
            enc_2_tcol = col_negative
            enc_2_dif = 0 - enc_2_dif
        enc_1_pps = enc_1_dif / time_delta
        enc_2_pps = enc_2_dif / time_delta
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
        info_message = "Time delta:%f Enc1-PPS:%f Enc2-PPS:%f" % (time_delta,enc_1_pps,enc_2_pps)
        ret=html.Div([
                html.Div([
                    html.Div([
                        html.H5("Encoder 1"),
                        html.Div([
                            html.Div([
                                daq.LEDDisplay(
                                    label="Relative",
                                    value=("%08d" % (enc_1_relative)),
                                    color=enc_1_col,
                                    size=32,
                                    ),
                                html.H6(""),
                                daq.LEDDisplay(
                                    label="Cumulative",
                                    value=("%08d" % (enc_1_cumulative)),
                                    color=col_positive,
                                    size=32,
                                    ),
                            ]),
                        daq.Gauge(
                          showCurrentValue=True,
                          units="PPS",
                          min=0,
                          max=2000,
                          size=168,
                          value=enc_1_pps,
                          color=enc_1_tcol,
                          label="Tachometer"),
                        ],style=flex_style),
                        ],style={"textAlign": "center", "width": "49%"}),
                    html.Div([
                        html.H5("Encoder 2"),
                        html.Div([
                            html.Div([
                                daq.LEDDisplay(
                                    label="Relative",
                                    value=("%08d" % (enc_2_relative)),
                                    color=enc_2_col,
                                    size=32,
                                    ),
                                html.H6(""),
                                daq.LEDDisplay(
                                    label="Cumulative",
                                    value=("%08d" % (enc_2_cumulative)),
                                    color=col_positive,
                                    size=32,
                                    ),
                            ]),
                        daq.Gauge(
                          showCurrentValue=True,
                          units="PPS",
                          min=0,
                          max=2000,
                          size=168,
                          value=enc_2_pps,
                          color=enc_2_tcol,
                          label="Tachometer"),
                        ],style=flex_style),
                        ],style={"textAlign": "center", "width": "49%"}),
                ],style=flex_style),
                #html.Div(info_message),
                html.Div('Last response time: {}'.format(utils.decode_time(system_time).rstrip("0"))),
            ])
    except IndexError:
        ret = html.Div('Could not read system status file.\nIs core.py running, ramdisk correctly setup and system polling enabled in settings.py?')
    return ret
