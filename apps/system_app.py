# YRL028 - APIHAT - Dash-DAQ Server Version 0.1
#
# System Tab
#
# James Hilder, York Robotics Laboratory, Feb 2019

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
    html.Div(id='system-info-div',style=border_style),
    html.Div([
        html.H5("System Monitor Chart"),
        dcc.Dropdown(
            id='system-app-dropdown',
            options=[
                {'label': 'Chart - {}'.format(i), 'value': i} for i in [
                    'Off','CPU Load','Temperature'
                ]
            ]
        ),
        html.Div(id='system-app-display-value'),
    ],style=border_style),
    dcc.Interval(
            id='system-info-interval-component',
            interval=0.5*1000, # in milliseconds
            n_intervals=0
    ),
    dcc.Interval(
                id='graph-interval-component',
                interval=2*1000, # in milliseconds
                n_intervals=0
    ),
])

@app.callback(
    Output('system-info-div','children'),    [Input('system-app-dropdown', 'value'),Input('system-info-interval-component', 'n_intervals')])
def update_values(value,n_intervals):
    data = pd.read_csv('/ramdisk/system.csv')
    try:
        current_values = data[['system-time','battery-voltage','total-cpu-load','clock-speed','pcb-temp','cpu-temp','gpu-temp','memory-used','memory-total']].tail(1).iloc[0]
        cpu_temp = float(current_values['cpu-temp'])
        pcb_temp = float(current_values['pcb-temp'])
        system_time = round(current_values['system-time'],3)
        b_v = float(current_values['battery-voltage'])
        battery_voltage = "%2.2f" % (b_v)
        memory_usage = int(current_values['memory-used'])
        memory_max = int(current_values['memory-total'])
        cpu_usage = float(current_values['total-cpu-load'])
        clock_speed = "%04d" % int(current_values['clock-speed'])
        cpu_colour = "#44ff00"
        if cpu_temp>70: cpu_colour="#ff0000"
        elif cpu_temp>60: cpu_colour="#ff5500"
        elif cpu_temp>55: cpu_colour="#ff8800"
        elif cpu_temp>50: cpu_colour="#ffaa00"
        elif cpu_temp>45: cpu_colour="#dddd00"
        pcb_colour = "#44ff00"
        if pcb_temp>45: pcb_colour="#ff0000"
        elif pcb_temp>40: pcb_colour="#ff5500"
        elif pcb_temp>35: pcb_colour="#ff8800"
        elif pcb_temp>30: pcb_colour="#ffaa00"
        elif pcb_temp>25: pcb_colour="#dddd00"
        battery_bg_col = "#ffffff"
        battery_fg_col = "#00ff00"
        if(b_v < 10):
            battery_bg_col="#ff0000"
            battery_fg_col="#000000"
        elif(b_v < 11):
            battery_fg_col="#ff0000"
        ret=html.Div([
            html.Div([
                daq.Thermometer(
                    label="PCB Temp",
                    showCurrentValue=True,
                    units="C",
                    value=pcb_temp,
                    color=pcb_colour,
                    min=0,
                    max=100,
                    size=130,
                    style={"textAlign": "center", "width": "15%"},
                    ),
                daq.Thermometer(
                    label="CPU Temp",
                    showCurrentValue=True,
                    units="C",
                    value=cpu_temp,
                    color=cpu_colour,
                    min=0,
                    max=100,
                    size=130,
                    style={"textAlign": "center", "width": "15%"},
                    ),
                html.Div([
                        daq.LEDDisplay(
                            label="Battery Voltage",
                            value=battery_voltage,
                            color=battery_fg_col,
                            backgroundColor=battery_bg_col,
                            size=40,
                            ),
                        daq.LEDDisplay(
                            label="Clock Speed",
                            value=clock_speed,
                            color="#FF5E5E",
                            size=40,
                            ),
                        ],style={"textAlign": "center", "width": "19%"}
                ),
                daq.Gauge(
                    showCurrentValue=True,
                    units="Percent",
                    min=0,
                    max=100,
                    value=cpu_usage,
                    color="#FF5E5E",
                    label="CPU Usage",
                    size=190,
                    style={"textAlign": "center", "width": "23%"},
                    ),
                daq.Gauge(
                    showCurrentValue=True,
                    units="MB",
                    min=0,
                    max=memory_max,
                    value=memory_usage,
                    color="#FF5E5E",
                    label="Memory Usage",
                    size=190,
                    style={"textAlign": "center", "width": "23%"},
                    ),
            ],
            style=flex_style,),
            html.Div('Last response time: {}'.format(utils.decode_time(system_time).rstrip("0"))),
        ])
    except IndexError:
        ret = html.Div('Could not read system status file.\nIs core.py running, ramdisk correctly setup and system polling enabled in settings.py?')
    return ret


@app.callback(
    Output('system-app-display-value', 'children'),
    [Input('system-app-dropdown', 'value'),Input('graph-interval-component', 'n_intervals')])
def display_value(value, n_intervals):
    if value=='Off': return html.Div("Chart Off.")
    data = pd.read_csv('/ramdisk/system.csv').tail(100)
    #Adjust the x-values so they are relative to current time [eg now = 0, 1 minute ago = -60]
    x_unadjusted = data['system-time'].values.tolist()
    x_values = [x - x_unadjusted[-1] for x in x_unadjusted]
    #x_values = data['system-time'].values.tolist()
    if value=='CPU Load':
        #x_values = list(range(0,50))
        cpu0 = data['cpu-0-load'].values.tolist()
        cpu1 = data['cpu-1-load'].values.tolist()
        cpu2 = data['cpu-2-load'].values.tolist()
        cpu3 = data['cpu-3-load'].values.tolist()
        cpu0_trace = go.Scatter(x=x_values,y=cpu0,name='CPU 0',mode='lines',stackgroup='one',line=dict(width=2))
        cpu1_trace = go.Scatter(x=x_values,y=cpu1,name='CPU 1',mode='lines',stackgroup='one',line=dict(width=2))
        cpu2_trace = go.Scatter(x=x_values,y=cpu2,name='CPU 2',mode='lines',stackgroup='one',line=dict(width=2))
        cpu3_trace = go.Scatter(x=x_values,y=cpu3,name='CPU 3',mode='lines',stackgroup='one',line=dict(width=2))
        traces = [cpu0_trace, cpu1_trace, cpu2_trace, cpu3_trace]
        ret_figure=go.Figure(
            data=traces,
            layout=go.Layout(
                title='CPU Load',
                showlegend=True,
                legend=go.layout.Legend(
                    x=0,
                    y=1.0
                ),
                margin=go.layout.Margin(l=40, r=0, t=40, b=30)
            )
        )
    elif value=='Temperature':
        cpu_temp = data['cpu-temp'].values.tolist()
        gpu_temp = data['gpu-temp'].values.tolist()
        pcb_temp = data['pcb-temp'].values.tolist()
        cpu_trace = go.Scatter(x=x_values,y=cpu_temp,name='CPU',mode='lines',line=dict(width=2))
        gpu_trace = go.Scatter(x=x_values,y=gpu_temp,name='GPU',mode='lines',line=dict(width=2))
        pcb_trace = go.Scatter(x=x_values,y=pcb_temp,name='PCB',mode='lines',line=dict(width=2))
        traces = [cpu_trace, gpu_trace, pcb_trace]
        ret_figure=go.Figure(
            data=traces,
            layout=go.Layout(
                title='System Temperature',
                showlegend=True,
                legend=go.layout.Legend(
                    x=0,
                    y=1.0
                ),
                margin=go.layout.Margin(l=40, r=0, t=40, b=30)
            )
        )
    else: return "Select a chart type."
    ret=html.Div([
        dcc.Graph(
            figure=ret_figure,
            style={'height': 400},
            id='my-graph'
        )
    ])
    return ret
