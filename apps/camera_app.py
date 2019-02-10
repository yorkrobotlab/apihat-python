# YRL028 - APIHAT - Dash-DAQ Server Version 0.1
#
# Control Tab
#
# James Hilder, York Robotics Laboratory, Feb 2019

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import base64
from dash.dependencies import Input, Output, State
import led, speech, audio, patterns, display, motors, subprocess

from app import app

flex_style = {"display": "flex","justify-content": "center-top","align-items": "center-top"}
border_style = {"border-radius": "5px","border-width": "5px","border": "1px solid rgb(216, 216, 216)","padding": "4px 10px 10px 10px","margin" : "4px 4px"}
block_style = {"textAlign": "center", "width": "25%"}

def create_div(title,body):
    return html.Div([html.H6(title),html.Div(body,style=flex_style)],style=border_style)

layout = html.Div([
    create_div('Raspistill',[
        html.Div([
            html.Div([
                html.Button('Start raspistill', id='start-raspistill-button'),
                html.Button('Kill raspistill', id='kill-raspistill-button'),
            ],style=flex_style),
            dcc.Interval(
                id='raspistill-interval-component',
                interval=0.5*1000, # in milliseconds
                n_intervals=0
            ),
            html.Div(id='image-callback-div',style=flex_style),
            html.Div(id='startbutton-callback-div'),
            html.Div(id='killbutton-callback-div'),
        ]),
    ]),
])

@app.callback(
    dash.dependencies.Output('image-callback-div', 'children'),
    [dash.dependencies.Input('raspistill-interval-component', 'n_intervals')])
def update_image_src(n):
    try:
        encoded_image = base64.b64encode(open("/ramdisk/raspistill.png", 'rb').read())
    except OSError:
        return "No raspistill image to display."
    return html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))

@app.callback(
    Output('startbutton-callback-div', 'children'),
    [Input('start-raspistill-button', 'n_clicks')])
def start_raspistill_callback(c):
    if c == None: return ''
    subprocess.Popen(["raspistill","-tl","500","-n","-o","/ramdisk/raspistill.png","-t","60000","-w","800","-h","600","-bm"])
    return ''

#Speech to text callback
@app.callback(
    Output('killbutton-callback-div', 'children'),
    [Input('kill-raspistill-button', 'n_clicks')])
def kill_raspistill_callback(c):
    if c == None: return ''
    subprocess.Popen(["killall","raspistill"])
    return ''
