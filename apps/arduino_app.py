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
import arduino
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import logging

from app import app
import css
flex_style =css.flex_style
border_style = css.border_style
block_style = css.block_style
button_style = {"width": "33%"}
encoder_style = {"textAlign": "center", "width": "49%", "border-radius": "1px","border-width": "1px","border": "1px solid rgb(226, 97, 24)","padding": "2px 2px 0px 4px","margin" : "4px 4px"}


#window_size = 120

def create_div(title,body):
    return html.Div([html.H5(title),html.Div(body,style=flex_style)],style=border_style)

layout = html.Div([
    #dcc.Store(id='memory'),
    create_div('Arduino Motor Control',[
        html.Div([
            html.Div([
                html.H6("Motor 1"),
                daq.Slider(id="ard-motor1-slider",value=0,min=-127,max=127,handleLabel={"showCurrentValue":True,"label":"SPEED"}),
            ]),
            html.Div([
                html.H6("Motor 2"),
                daq.Slider(id="ard-motor2-slider",value=0,min=-127,max=127,handleLabel={"showCurrentValue":True,"label":"SPEED"}),
            ]),
        ],style={"width":"40%"}),
        html.Div([
            html.Div([html.Div(style=button_style),html.Button('Forwards', id='ard-forwards-button', style=button_style),html.Div(style=button_style)],style=flex_style),
            html.Div([
                html.Button('Left Turn', id='ard-left-button',style=button_style),
                html.Button('Stop', id='ard-stop-button',style=button_style),
                html.Button('Right Turn', id='ard-right-button',style=button_style),
            ]),
            html.Div([html.Div(style=button_style),html.Button('Backwards', id='ard-backwards-button', style=button_style),html.Div(style=button_style)],style=flex_style),
        ], style = {"width":"49%"}),
        html.Div([daq.Slider(id="ard-motor-speed-slider",vertical=True,value=20,min=0,max=127,size=130,updatemode='drag',handleLabel={"showCurrentValue":True,"label":"SPEED"}),]),
#        html.Div([daq.Slider(id="ard-motor-speed-slider",vertical=True,value=20,min=0,max=127,handleLabel={"showCurrentValue":True,"label":"SPEED"}),],style={"width":"10%"}),

    ]),
    html.Div(id='encoder-div',style=border_style),
    html.Div(id='ard-motor-output-div'),
    dcc.Interval(
            id='encoder-interval-component',
            interval=0.5*1000, # in milliseconds
            n_intervals=0
    ),
])


#Motor control callbacks
@app.callback(
    Output('ard-motor1-slider','value'),
    [Input('memory','modified_timestamp')],
    [State('memory','data')])
def on_data(ts,data):
    if ts is None: raise PreventUpdate
    value = 0
    if data['l_speed'] is not None: value=data['l_speed']
    return value

@app.callback(
    Output('ard-motor2-slider','value'),
    [Input('memory','modified_timestamp')],
    [State('memory','data')])
def on_data(ts,data):
    if ts is None: raise PreventUpdate
    value = 0
    if data['r_speed'] is not None: value=data['r_speed']
    return value

@app.callback(
    Output('ard-motor-output-div', 'children'),
    [Input('ard-motor1-slider', 'value'), Input('ard-motor2-slider','value')])
def motor_speed_callback(m1,m2):
    #motors.set_motor_speeds(m1/100.0,m2/100.0)
    arduino.set_motor_speeds(int(m1),int(m2))
    return(html.P("Setting motor 1 to %d, motor 2 to %d" % (m1,m2)))

# @app.callback(
#     Output('ard-motor-output-div','children'),
#     [Input('memory','modified_timestamp')],
#     [State('memory','data')])
# def on_data(ts,data):
#     if ts is None: raise PreventUpdate
#     data = data or {}
#     #return html.P('Message:' + data.get('message',''))

@app.callback(
    Output('memory','data'),
    [Input('ard-forwards-button','n_clicks'),
    Input('ard-backwards-button','n_clicks'),
    Input('ard-left-button','n_clicks'),
    Input('ard-right-button','n_clicks'),
    Input('ard-stop-button','n_clicks'),
    ],
    [State('memory','data'),
    State('ard-motor-speed-slider','value')])
def on_click(f_click,b_click,l_click,r_click,s_click,data,speed):
    if f_click is None and b_click is None and l_click is None and r_click is None and s_click is None:  raise PreventUpdate
    #print("In memory callback...")
    data = data or {'f_clicks':0, 'b_clicks':0, 'l_clicks':0, 'r_clicks':0, 's_clicks':0, 'message':''}
    if f_click is not None and f_click > data['f_clicks']:
        #Forwards button pressed
        data['message'] = 'Forwards pressed'
        data['l_speed'] = speed
        data['r_speed'] = speed
        data['f_clicks'] = f_click
    if b_click is not None and b_click > data['b_clicks']:
        #Backwards button pressed
        data['message'] = 'Backwards pressed'
        data['l_speed'] = -speed
        data['r_speed'] = -speed
        data['b_clicks'] = b_click
    if l_click is not None and l_click > data['l_clicks']:
        #Left button pressed
        data['message'] = 'Left pressed'
        data['l_speed'] = -speed
        data['r_speed'] = speed
        data['l_clicks'] = l_click
    if r_click is not None and r_click > data['r_clicks']:
        #Right button pressed
        data['message'] = 'Right pressed'
        data['l_speed'] = speed
        data['r_speed'] = -speed
        data['r_clicks'] = r_click
    if s_click is not None and s_click > data['s_clicks']:
        #Stop button pressed
        data['message'] = 'Stop pressed'
        data['l_speed'] = 0
        data['r_speed'] = 0
        data['s_clicks'] = s_click
    return data

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
                        ],style=encoder_style),
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
                        ],style=encoder_style),
                ],style=flex_style),
                #html.Div(info_message),
                html.Div('Last response time: {}'.format(utils.decode_time(system_time).rstrip("0"))),
            ])
    except IndexError:
        ret = html.Div('Could not read system status file.\nIs core.py running, ramdisk correctly setup and system polling enabled in settings.py?')
    return ret
