# YRL028 - APIHAT - Dash-DAQ Server Version 0.1
#
# Robot Tab - Visible if ENABLE_ROBOT_TAB=True in settings.py
#
# James Hilder, York Robotics Laboratory, Feb 2019

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
import led, speech, audio, patterns, display, motors

from app import app

flex_style = {"display": "flex","justify-content": "center-top","align-items": "center-top"}
border_style = {"border-radius": "5px","border-width": "5px","border": "1px solid rgb(216, 216, 216)","padding": "4px 10px 10px 10px","margin" : "4px 4px"}
block_style = {"textAlign": "center", "width": "25%"}

def create_div(title,body):
    return html.Div([html.H6(title),html.Div(body,style=flex_style)],style=border_style)

layout = html.Div([
    create_div('Drive Control',[
        html.Button('Forwards', id='forwards-button'),
        html.Div(id='forwards-button-output-div'),
        html.Button('Backwards', id='backwards-button'),
        html.Div(id='backwards-button-output-div'),
        html.Button('Left Turn', id='left-button'),
        html.Div(id='left-button-output-div'),
        html.Button('Right Turn', id='right-button'),
        html.Div(id='right-button-output-div'),
        html.Button('Stop', id='dc-stop-button'),
        html.Div(id='stop-button-output-div'),
        daq.Slider(id="motor-speed-slider",value=20,min=0,max=100,handleLabel={"showCurrentValue":True,"label":"SPEED"}),

    ]),
])

#Motor control callbacks
@app.callback(
    Output('stop-button-output-div','children'),
    [Input('dc-stop-button','n_clicks')])
def stop_button_callback(c):
    motors.set_motor_speeds(0,0)
    return('')

@app.callback(
    Output('forwards-button-output-div','children'),
    [Input('forwards-button','n_clicks')],[State('motor-speed-slider','value')])
def forwards_button_callback(c,value):
    motors.set_motor_speeds(value,value)
    return('')

@app.callback(
    Output('backwards-button-output-div','children'),
    [Input('backwards-button','n_clicks')],[State('motor-speed-slider','value')])
def backwards_button_callback(c,value):
    motors.set_motor_speeds(-value,-value)
    return('')

@app.callback(
    Output('left-button-output-div','children'),
    [Input('left-button','n_clicks')],[State('motor-speed-slider','value')])
def left_button_callback(c,value):
    motors.set_motor_speeds(-value,value)
    return('')

@app.callback(
    Output('right-button-output-div','value'),
    [Input('right-button','n_clicks')],[State('motor-speed-slider','value')])
def right_button_callback(c,value):
    motors.set_motor_speeds(value,-value)
    return('')
