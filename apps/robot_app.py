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
import led, speech, audio, patterns, display, motors, utils, settings
from user_programs import *

from app import app

flex_style = {"display": "flex","justify-content": "center-top","align-items": "center-top"}
border_style = {"border-radius": "5px","border-width": "5px","border": "1px solid rgb(216, 216, 216)","padding": "4px 10px 10px 10px","margin" : "4px 4px"}
button_style = {"width": "33%"}

def create_div(title,body):
    return html.Div([html.H6(title),html.Div(body,style=flex_style)],style=border_style)

layout = html.Div([
    create_div('User Programs',[
        html.Div([
            dcc.Dropdown(
                id='user-program-dropdown',
                options=[{'label':i,'value':str(count)} for count,i in enumerate(utils.get_program_filelist())]
            ),
            html.Div([
                html.Button('Start', id='prog-start-button',style=button_style),
                html.Button('Pause', id='prog-pause-button',style=button_style),
                html.Button('Stop', id='prog-stop-button',style=button_style),
            ]),
            html.Div(id='prog-start-div'),
            html.Div(id='prog-pause-div'),
            html.Div(id='prog-stop-div'),
            html.Div(id='prog-dropdown-div'),

        ], style = {"width":"75%"}),
    ]),
    create_div('Drive Control',[
        html.Div([
            html.Div([html.Div(style=button_style),html.Button('Forwards', id='forwards-button', style=button_style),html.Div(style=button_style)],style=flex_style),
            html.Div([
                html.Button('Left Turn', id='left-button',style=button_style),
                html.Button('Stop', id='dc-stop-button',style=button_style),
                html.Button('Right Turn', id='right-button',style=button_style),
            ]),
            html.Div([html.Div(style=button_style),html.Button('Backwards', id='backwards-button', style=button_style),html.Div(style=button_style)],style=flex_style),
            html.Div(id='forwards-button-output-div'),
            html.Div(id='right-button-output-div'),
            html.Div(id='left-button-output-div'),
            html.Div(id='stop-button-output-div'),
            html.Div(id='backwards-button-output-div'),
        ], style = {"width":"75%"}),
        daq.Slider(id="motor-speed-slider",value=20,min=0,max=100,handleLabel={"showCurrentValue":True,"label":"SPEED"}),
    ]),
])

#Program control callbacks
@app.callback(
    Output('prog-dropdown-div', 'children'),
    [Input('user-program-dropdown', 'value')])
def prog_request_callback(value):
    if(value == None): return ('')
    utils.request_program(value)
    return html.P("Requesting program...")

@app.callback(
    Output('prog-start-div','children'),
    [Input('prog-start-button','n_clicks')])
def prog_start_callback(c):
    if (c == None): return ('')
    with open(settings.program_state_filename, 'w+') as state_file: state_file.write("START")
    return('')

@app.callback(
    Output('prog-stop-div','children'),
    [Input('prog-stop-button','n_clicks')])
def prog_stop_callback(c):
    if (c == None): return ('')
    with open(settings.program_state_filename, 'w+') as state_file: state_file.write("STOP")
    return('')

@app.callback(
    Output('prog-pause-div','children'),
    [Input('prog-pause-button','n_clicks')])
def prog_pause_callback(c):
    if (c == None): return ('')
    with open(settings.program_state_filename, 'w+') as state_file: state_file.write("PAUSE")
    return('')

#Motor control callbacks
@app.callback(
    Output('stop-button-output-div','children'),
    [Input('dc-stop-button','n_clicks')])
def stop_button_callback(c):
    if (c == None): return ('')
    motors.set_motor_speeds(0,0)
    return('')

@app.callback(
    Output('forwards-button-output-div','children'),
    [Input('forwards-button','n_clicks')],[State('motor-speed-slider','value')])
def forwards_button_callback(c,value):
    if (c == None): return ('')
    motors.set_motor_speeds(value,value)
    return('')

@app.callback(
    Output('backwards-button-output-div','children'),
    [Input('backwards-button','n_clicks')],[State('motor-speed-slider','value')])
def backwards_button_callback(c,value):
    if (c == None): return ('')
    motors.set_motor_speeds(-value,-value)
    return('')

@app.callback(
    Output('left-button-output-div','children'),
    [Input('left-button','n_clicks')],[State('motor-speed-slider','value')])
def left_button_callback(c,value):
    if (c == None): return ('')
    motors.set_motor_speeds(-value,value)
    return('')

@app.callback(
    Output('right-button-output-div','value'),
    [Input('right-button','n_clicks')],[State('motor-speed-slider','value')])
def right_button_callback(c,value):
    if (c == None): return ('')
    motors.set_motor_speeds(value,-value)
    return('')
