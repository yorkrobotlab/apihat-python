# YRL028 - APIHAT - Dash-DAQ Server Version 0.1
#
# Control Tab
#
# James Hilder, York Robotics Laboratory, Feb 2019

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
import led, speech, audio, patterns, display, motors, settings, utils, os

from app import app

audio.start_audio_thread()

flex_style = {"display": "flex","justify-content": "center-top","align-items": "center-top"}
border_style = {"border-radius": "5px","border-width": "5px","border": "1px solid rgb(216, 216, 216)","padding": "4px 10px 10px 10px","margin" : "4px 4px"}
block_style = {"textAlign": "center", "width": "25%"}

def create_div(title,body):
    return html.Div([html.H6(title),html.Div(body,style=flex_style)],style=border_style)

layout = html.Div([
    create_div('Audio',[
        html.Div([
            html.Div([
                html.H6("Volume"),
                daq.Slider(id="volume-slider",value=settings.AUDIO_VOLUME,min=0,max=100,updatemode="drag",handleLabel={"showCurrentValue":True,"label":"SPEED"}),
            ]),
            dcc.Dropdown(
                id='audio-file-dropdown',
                options=[{'label':i,'value':str(count)} for count,i in enumerate(utils.get_audio_filelist())]
            ),
            html.Div(id='playback-div'),
            html.Div(id='volume-callback-div'),
        ]),
    ]),
    create_div('Text to Speech',[
        dcc.Input(placeholder='Text to say...',type='text',value='',id=('speech-text-field')),
        html.Button('Speak', id='speak-button'),
        html.Div(id='speech-callback-div')
    ]),
    create_div('Speech to Text',[
        html.Button('Start Recording', id='record-button'),
        html.Div(id='speech-to-text-callback-div')
    ]),
    create_div('I2C Motors',[
        html.Div([
            html.H6("Motor 1"),
            daq.Slider(id="motor1-slider",value=0,min=-100,max=100,updatemode="drag",handleLabel={"showCurrentValue":True,"label":"SPEED"}),
        ]),
        html.Div([
            html.H6("Motor 2"),
            daq.Slider(id="motor2-slider",value=0,min=-100,max=100,updatemode="drag",handleLabel={"showCurrentValue":True,"label":"SPEED"}),
        ]),
        html.Button('Stop', id='stop-button'),
        html.Div(id='motor-output-div'),
    ]),
    create_div('Body LED',[
        html.Div([
            html.H6("Solid Colour"),
            dcc.Dropdown(id='control-app-bodyled-dropdown',options=[{'label':i[0],'value':str(count)} for count,i in enumerate(patterns.solid_colours)])
        ],style=block_style),
        html.Div(id='control-app-bodyled'),
        html.Div([
            html.H6("Animation"),
            dcc.Dropdown(id='animation-dropdown',options=[{'label':i[0],'value':str(count)} for count,i in enumerate(patterns.body_animations)]),
        ],style=block_style),
        html.Div(id='animation-div'),
        ]),
    create_div('OLED Display',[
        dcc.Input(placeholder='Text to display...',type='text',value='',id=('display-text-field')),
        html.Button('Display', id='display-button'),
        html.Div(id='display-callback-div')
    ]),
])

#Audio callbacks
@app.callback(
    Output('volume-callback-div', 'children'),
    [Input('volume-slider', 'value')])
def volume_callback(v):
    audio.set_volume(v)
    return(html.P("Setting volume to %d" % (v)))

@app.callback(
    Output('playback-div', 'children'),
    [Input('audio-file-dropdown', 'value')])
def audio_callback(value):
    if(value==None): return('')
    audio.play_audio_file(os.path.join(settings.AUDIO_FILEPATH,utils.get_audio_filelist()[int(value)]))
    return html.P("Playing audio file %s" % (utils.get_audio_filelist()[int(value)]))


#Motor control callbacks
@app.callback(
    Output('motor1-slider','value'),
    [Input('stop-button','n_clicks')])
def stop_motor1_callback(c):
    return 0

@app.callback(
    Output('motor2-slider','value'),
    [Input('stop-button','n_clicks')])
def stop_motor2_callback(c):
    return 0

@app.callback(
    Output('motor-output-div', 'children'),
    [Input('motor1-slider', 'value'), Input('motor2-slider','value')])
def motor_speed_callback(m1,m2):
    motors.set_motor_speeds(m1/100.0,m2/100.0)
    return(html.P("Setting motor 1 to %d, motor 2 to %d" % (m1,m2)))

#Speech to text callback
@app.callback(
    Output('speech-to-text-callback-div', 'children'),
    [Input('record-button', 'n_clicks')])
def speech_to_text_callback(c):
    if c == None: return ''
    if c % 2 == 1:
        #Odd number: start Recording
        led.animation(2)
        speech.start_recording()
        return (html.P("Recording audio - press again to stop"))
    response = speech.end_recording()
    led.animation(0)
    return (html.P("Google Response: %s" % response))

@app.callback(
    Output('speech-callback-div', 'children'),
    [Input('speak-button', 'n_clicks')],
    [State('speech-text-field','value')])
def speech_callback(c,value):
    if c == None: return ''
    audio.unmute()
    audio.IF_say(value)
    return (html.P("%s spoken." % value))

@app.callback(
    Output('display-callback-div', 'children'),
    [Input('display-button', 'n_clicks')],
    [State('display-text-field','value')])
def speech_callback(c,value):
    if c == None: return ''
    display.one_line_text_wrapped(value)
    return (html.P("%s sent to OLED display." % value))


@app.callback(
    Output('animation-div', 'children'),
    [Input('animation-dropdown', 'value')])
def animation_callback(value):
    if value == None: return ''
    led.animation(int(value))
    return ''

@app.callback(
    Output('control-app-bodyled', 'children'),
    [Input('control-app-bodyled-dropdown', 'value')])
def control_app_bodyled_callback(value):
    if value== None: return ''
    led.set_colour_solid(int(value))
    return ''
