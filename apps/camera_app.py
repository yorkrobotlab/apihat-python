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
import led, speech, audio, patterns, display, motors, subprocess, settings
from app import app

opencv_filter_modes = ["No Filter","Canny Edge Detection","Hough Line Detection","Hough Circle Detection","ORB Keypoint Detection","Blob Detection","ARUCO Tag Detection"]

import css
flex_style =css.flex_style
border_style = css.border_style
block_style = css.block_style

def create_div(title,body):
    return html.Div([html.H6(title),html.Div(body,style=flex_style)],style=border_style)

layout = html.Div([
    create_div('Still Image Processing',[
        html.Div([
            dcc.Dropdown(
                id='camera-filter-dropdown',
                options=[{'label':i,'value':str(count)} for count,i in enumerate(opencv_filter_modes)]
            ),
            html.Div([
                html.Button('Start camera server',id='start-camera-button'),
                html.Button('Stop camera server',id='stop-camera-button'),
                html.Button('Start raspistill', id='start-raspistill-button'),
                html.Button('Kill raspistill', id='kill-raspistill-button'),
            ],style=flex_style),
            dcc.Interval(
                id='raspistill-interval-component',
                interval=0.8*1000, # in milliseconds
                n_intervals=0
            ),
            html.Div(id='image-callback-div',style=flex_style),
            html.Div(id='camera-mode-div'),
            html.Div(id='start-camera-button-callback-div'),
            html.Div(id='stop-camera-button-callback-div'),
            html.Div(id='startbutton-callback-div'),
            html.Div(id='killbutton-callback-div'),
        ]),
    ]),
])

@app.callback(
    Output('camera-mode-div', 'children'),
    [Input('camera-filter-dropdown', 'value')])
def filter_mode_callback(value):
    if(value==None): return('')
    with open(settings.camera_request_filename, 'w+') as camera_file: camera_file.write("MODE %s" % value)
    return ('')


@app.callback(
    dash.dependencies.Output('image-callback-div', 'children'),
    [dash.dependencies.Input('raspistill-interval-component', 'n_intervals')])
def update_image_src(n):
    try:
        encoded_image = base64.b64encode(open("/ramdisk/image.png", 'rb').read())
    except OSError:
        return "No camera image to display."
    return html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))

@app.callback(
    Output('start-camera-button-callback-div', 'children'),
    [Input('start-camera-button', 'n_clicks')])
def start_camera_callback(c):
    if c == None: return ''
    with open(settings.camera_request_filename, 'w+') as camera_file: camera_file.write("START")
    return ''

@app.callback(
    Output('stop-camera-button-callback-div', 'children'),
    [Input('stop-camera-button', 'n_clicks')])
def stop_camera_callback(c):
    if c == None: return ''
    with open(settings.camera_request_filename, 'w+') as camera_file: camera_file.write("STOP")
    return ''


@app.callback(
    Output('startbutton-callback-div', 'children'),
    [Input('start-raspistill-button', 'n_clicks')])
def start_raspistill_callback(c):
    if c == None: return ''
    subprocess.Popen(["raspistill","-tl","500","-n","-o","/ramdisk/image.png","-t","60000","-w","800","-h","600","-bm"])
    return ''

#Speech to text callback
@app.callback(
    Output('killbutton-callback-div', 'children'),
    [Input('kill-raspistill-button', 'n_clicks')])
def kill_raspistill_callback(c):
    if c == None: return ''
    subprocess.Popen(["killall","raspistill"])
    return ''
