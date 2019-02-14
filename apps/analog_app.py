import plotly.plotly as py
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_daq as daq

import smbus2                                                                   #Assume DTO-level i2c switch implementation [ie port 0 = i2c_3 etc]

import utils, json
import sensors, settings
import pandas as pd
import ast
from app import app

def create_div(title,body):
    return html.Div([
        html.H6(title),
        html.Div(body,style=flex_style),
    ],style=border_style)

#Return a #RRGGBB colour string where RED = min val and CYAN = max val
def get_fill_colour(min,max,value):

    val_pct = ((value-min)/(max-min))
    val_pct = 100 - (val_pct * val_pct * 100)
    if val_pct < 0: val_pct = 0
    if val_pct > 100: val_pct = 100
    red_val = int(2.55 * (val_pct))
    blu_val = 255 - red_val
    if(blu_val < 0): blu_val = 0
    #print ("Value: %d Val Pct: %f Red val: %d Blue val: %d" % (value,val_pct,red_val,blu_val))
    return "#%02x%02x%02x" % (red_val,blu_val,blu_val)

def generate_range_data(current_values):
    range_data = []
    for s_def in settings.ROBOT_SENSOR_MODEL:
        distance =  sensors.get_distance(int(current_values[s_def[0]]),s_def[1])
        range_data.append(go.Scatterpolar(r=[0,distance,distance,0],theta=[0,s_def[2]-s_def[3],s_def[2]+s_def[3],0],mode='lines',fill='toself',fillcolor = get_fill_colour(9,80,distance),line =  dict(color = 'black')))
    return range_data

range_layout = go.Layout(
    polar = dict(
        radialaxis = dict(
            visible = True,
            range = [0,80]
        )
    ),
    showlegend = False,
    orientation=180
)

border_style = {"border-radius": "5px","border-width": "5px","border": "1px solid rgb(216, 216, 216)","padding": "4px 10px 10px 10px","margin" : "4px 4px"}
flex_style = {"display": "flex","justify-content": "center-top","align-items": "center-top"}
block_style = {"textAlign": "center", "width": "25%"}

layout = html.Div([
    create_div("Values",[
        daq.BooleanSwitch(label="Distances",id='distances-switch'),
        html.Div(id='analog-raw-div')
    ]),

    dcc.Interval(
            id='analog-interval-component',
            interval=2*1000, # in milliseconds
            n_intervals=0
    ),
])

@app.callback(
    Output('analog-raw-div','children'),    [Input('analog-interval-component', 'n_intervals')], [State('distances-switch','on')])
def update_values(n_intervals,distance_mode):
    data = pd.read_csv('/ramdisk/system.csv')
    try:
        current_values = data[['system-time','analog-1','analog-2','analog-3','analog-4']].tail(1).iloc[0]
        analog_1_raw = int(current_values['analog-1'])
        analog_2_raw = int(current_values['analog-2'])
        analog_3_raw = int(current_values['analog-3'])
        analog_4_raw = int(current_values['analog-4'])
        uns='Raw'
        max_val=255
        g_c="#FF5E5E"
        g_s=190
        g_sty={"textAlign": "center", "width": "23%"},

        if(distance_mode):
            analog_1_raw = sensors.get_distance(analog_1_raw,'2y0a21')
            analog_2_raw = sensors.get_distance(analog_2_raw,'2y0a21')
            analog_3_raw = sensors.get_distance(analog_3_raw,'2y0a21')
            analog_4_raw = sensors.get_distance(analog_4_raw,'2y0a21')
            uns='CM'
            max_val=80
        system_time = round(current_values['system-time'],3)
        range_figure = go.Figure(data=generate_range_data(current_values), layout=range_layout)
        ret=html.Div([
            html.Div([
                daq.Gauge(showCurrentValue=True,units=uns,min=0,max=max_val,value=analog_1_raw,color=g_c,label="Analog-1",size=g_s,style=g_sty),
                daq.Gauge(showCurrentValue=True,units=uns,min=0,max=max_val,value=analog_2_raw,color=g_c,label="Analog-2",size=g_s,style=g_sty),
                daq.Gauge(showCurrentValue=True,units=uns,min=0,max=max_val,value=analog_3_raw,color=g_c,label="Analog-3",size=g_s,style=g_sty),
                daq.Gauge(showCurrentValue=True,units=uns,min=0,max=max_val,value=analog_4_raw,color=g_c,label="Analog-4",size=g_s,style=g_sty),
            ],style=flex_style),
            html.Div([
                dcc.Graph(
                    figure=range_figure,
                    style={'height': 600},
                    id='range-graph'
                )
            ]),
            html.Div('Last response time: {}'.format(utils.decode_time(system_time).rstrip("0"))),
        ])

    except IndexError:
        ret = html.Div('Could not read system status file.\nIs core.py running, ramdisk correctly setup and system polling enabled in settings.py?')
    return ret
