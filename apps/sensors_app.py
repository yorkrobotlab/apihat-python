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
import css
flex_style =css.flex_style
border_style = css.border_style
block_style = css.block_style

def get_layout(sensors_list, data_filename, i2c_bus, led_address):
    has_tof = False
    has_alp = False
    has_colour = False
    has_adc = False
    has_gas_sensor = False
    has_gas_sensor_gpio = False
    has_humidity = False
    has_led = False
    for entry in sensors_list:
        if entry=='TOF': has_tof = True
        if entry=='ALP': has_alp = True
        if entry=='COLOUR': has_colour = True
        if entry=='IR ADC': has_adc = True
        if entry=='GAS ADC': has_gas_sensor = True
        if entry=='GAS GPIO': has_gas_sensor_gpio = True
        if entry=='HUMIDITY': has_humidity = True
        if entry=='LED': has_led = True
    data_entry = [i2c_bus, data_filename, has_tof, has_alp, has_colour, has_adc, has_gas_sensor, has_gas_sensor_gpio, has_humidity, has_led, led_address]
    led_panel = []
    if has_led:
        led_panel = create_div(('LED Driver'),[
            html.Div([
                daq.ColorPicker(id='led-colour-picker',label='LED Colour Picker',value={'hex': '#5a94af', 'rgb': {'a': 1, 'g': 148, 'b': 175, 'r': 90}}),
                daq.BooleanSwitch(on=True,color="#9B51E0",id='led-switch-1'),
                daq.BooleanSwitch(on=True,color="#9B51E0",id='led-switch-2'),
                daq.BooleanSwitch(on=True,color="#9B51E0",id='led-switch-3'),
                daq.BooleanSwitch(on=True,color="#9B51E0",id='led-switch-4'),
            ]),
            html.Div(id='colour-picker-output-div')
        ])
    heater_panel = []
    if has_gas_sensor_gpio:
        heater_panel = create_div(('Gas Sensor Heaters'),[
                daq.BooleanSwitch(on=True,color="#E05190",id='heater-switch-1',label="Heater 1",labelPosition="top",style=block_style),
                daq.BooleanSwitch(on=True,color="#E05190",id='heater-switch-2',label="Heater 2",labelPosition="top",style=block_style),
                daq.BooleanSwitch(on=True,color="#E05190",id='heater-switch-3',label="Heater 3",labelPosition="top",style=block_style),
                daq.BooleanSwitch(on=True,color="#E05190",id='heater-switch-4',label="Heater 4",labelPosition="top",style=block_style)
        ])
    layout = html.Div([
        html.Div(json.dumps(data_entry),id='json-data-div', style={'display':'none'}),
        html.Div(id='sensor-body-div'),
        html.Div(id='heater-output-div'), #Null
        dcc.Interval(
        id='sensor-interval-component',
        interval=0.5*1000, # in milliseconds
        n_intervals=0
        ),
        html.Div(heater_panel),
        html.Div(led_panel),
        html.Div([
            html.H6('Chart'),
            html.Div([
                html.P("Autorefresh rate:"),
                dcc.Dropdown(
                id='sensors-app-autorefresh-dropdown',
                options=[
                    {'label': 'Off', 'value': 0},
                    {'label': '0.5 s', 'value': 500},
                    {'label': '1 s', 'value': 1000},
                    {'label': '2 s ', 'value': 2000},
                    {'label': '5 s', 'value': 5000},
                    {'label': '10 s', 'value': 10000}
                    ])
                ]),
            html.Div(id='sensors-app-autorefresh-display-value')
        ], style = border_style),
    ])
    return layout

#This is a bit of a hack - we directly control the gpio driver rather that using the Sensor.class methods [as we aren't sharing the classes with the server]
@app.callback(Output('heater-output-div', 'children'),[Input('heater-switch-1', 'on'),Input('heater-switch-2', 'on'),Input('heater-switch-3', 'on'),Input('heater-switch-4', 'on')],[State('json-data-div','children')])
def set_heater(h1,h2,h3,h4,values):
    data_entry = json.loads(values)
    i2c_bus = int(data_entry[0])+2
    bus=smbus2.SMBus(i2c_bus)
    byte_data = ((h4 << 3) + (h3 << 2) + (h2 << 1) + h1)
    bus.write_byte_data(settings.GAS_SENSOR_GPIO_ADDRESS, 0x01, byte_data)

#This is also a bit of a hack - we directly control the LED driver rather that using the Sensor.class methods [as we aren't sharing the classes with the server]
@app.callback(
    Output('colour-picker-output-div', 'children'),
    [Input('led-colour-picker', 'value')],
    [State('led-switch-1', 'on'),State('led-switch-2', 'on'),State('led-switch-3', 'on'),State('led-switch-4', 'on'),State('json-data-div','children')])
def update_output(value,sw1,sw2,sw3,sw4,values):
    data_entry = json.loads(values)
    i2c_bus = int(data_entry[0])+2
    led_address = int(data_entry[10])
    rgb=value.get("rgb")
    bus=smbus2.SMBus(i2c_bus)
    blue=rgb.get("b")
    green=rgb.get("g")
    red=rgb.get("r")
    led_status = bus.read_i2c_block_data(led_address, 0x86, 12)
    print (sw1)
    if(sw1):
        led_status[0]=blue
        led_status[1]=green
        led_status[2]=red
    if(sw2):
        led_status[3]=blue
        led_status[4]=green
        led_status[5]=red
    if(sw3):
        led_status[6]=blue
        led_status[7]=green
        led_status[8]=red
    if(sw4):
        led_status[9]=blue
        led_status[10]=green
        led_status[11]=red
    bus.write_i2c_block_data(led_address, 0x86, led_status)
    return 'Setting colour on bus %d to %s' % (i2c_bus, value)



@app.callback(
    Output('sensor-body-div','children'),    [Input('sensor-interval-component', 'n_intervals'), Input('json-data-div','children')])
def update_values(n_intervals, values):
    try:
        data_entry = json.loads(values)
        i2c_bus = data_entry[0]
        data_filename = data_entry[1]
        data = pd.read_csv(data_filename)
        has_tof = data_entry[2]
        has_alp = data_entry[3]
        has_colour = data_entry[4]
        has_adc = data_entry[5]
        has_gas_sensor = data_entry[6]
        has_gas_sensor_gpio = data_entry[7]
        has_humidity = data_entry[8]
        has_led = data_entry[9]
        led_address = data_entry[10]
        system_timev = data[['system-time']].tail(1).iloc[0]
        system_time = round(system_timev[0],3)

        ret_body = []
        if(has_tof):
            tof_value=data[['TOF']].tail(1).iloc[0]
            ret_body.append(create_div(('TOF Sensor'),[
                daq.Tank(label="Distance",showCurrentValue=True,min=0,max=1000,value=tof_value['TOF'],size=80,style=block_style),
                #html.P(tof_value) #Replace with something pretty!
            ]))
        if(has_alp):
            als_value=data[['ALS:IR PROX','ALS:LIGHT','ALS:WB']].tail(1).iloc[0]
            ret_body.append(create_div(('Ambient Light & Proximity Sensor'),[
                daq.Tank(label="Proximity",showCurrentValue=True,min=0,max=400,value=als_value['ALS:IR PROX'],size=80,style=block_style),
                daq.Tank(label="Ambient Light",showCurrentValue=True,min=0,max=32000,value=als_value['ALS:LIGHT'],size=80,style=block_style),
                daq.Tank(label="White Balance",showCurrentValue=True,min=0,max=32000,value=als_value['ALS:WB'],size=80,style=block_style),
                #html.P(str(als_value))
            ]))
        if(has_colour):
            col_value=data[['RED','GREEN','BLUE','WHITE']].tail(1).iloc[0]
            ret_body.append(create_div(('Colour Sensor'),[
                daq.Tank(label="Red",showCurrentValue=True,min=0,max=64000,value=col_value['RED'],size=80,color="#FFBBBB",style=block_style),
                daq.Tank(label="Green",showCurrentValue=True,min=0,max=64000,value=col_value['GREEN'],size=80,color="#BBFFBB",style=block_style),
                daq.Tank(label="Blue",showCurrentValue=True,min=0,max=64000,value=col_value['BLUE'],size=80,color="#BBBBFF",style=block_style),
                daq.Tank(label="White",showCurrentValue=True,min=0,max=64000,value=col_value['WHITE'],size=80,color="#BBBBBB",style=block_style),
                #html.P(str(col_value))
            ]))
        if(has_adc):
            ir_value=data[['IR']].tail(1).iloc[0]
            ret_body.append(create_div(('Analogue Infrared Phototransistor'),[
                daq.Tank(label="Raw Value",showCurrentValue=True,min=0,max=400,value=ir_value['IR'],size=80,style=block_style),
                #html.P(str(ir_value))
            ]))
        if(has_gas_sensor):
            gas_value=data[['GAS0','GAS1','GAS2','GAS3']].tail(1).iloc[0]
            ret_body.append(create_div(('Analog Inputs (Gas Sensor)'),[
                daq.Tank(label="Sensor 0",showCurrentValue=True,min=0,max=64000,value=gas_value['GAS0'],size=80,style=block_style),
                daq.Tank(label="Sensor 1",showCurrentValue=True,min=0,max=64000,value=gas_value['GAS1'],size=80,style=block_style),
                daq.Tank(label="Sensor 2",showCurrentValue=True,min=0,max=64000,value=gas_value['GAS2'],size=80,style=block_style),
                daq.Tank(label="Sensor 3",showCurrentValue=True,min=0,max=64000,value=gas_value['GAS3'],size=80,style=block_style),
                #html.P(str(gas_value))
            ]))
        if(has_humidity):
            hum_value=data[['HUMIDITY','TEMPERATURE']].tail(1).iloc[0]
            ret_body.append(create_div(('Humidity + Temperature Sensor'),[
                #daq.Thermometer(label="Temperature",showCurrentValue=True,units="C",value=hum_value['TEMPERATURE'],min=0,max=100,size=60,style=block_style),
                daq.Tank(label="Temperature",showCurrentValue=True,units="C",value=hum_value['TEMPERATURE'],min=0,max=100,size=80,style=block_style),
                daq.Tank(label="Humidity",showCurrentValue=True,min=0,max=100,value=hum_value['HUMIDITY'],size=80,style=block_style,units="%"),
                #html.P(str(hum_value))
            ]))
        ret_body.append(html.Div('Last response time: {}'.format(utils.decode_time(system_time).rstrip("0"))))
        return html.Div(ret_body)
    except  IOError:
        print ("Error reading file %s in sensors_app.py" % data_filename)
        return (html.Div("Error reading data file"))

def create_div(title,body):
    return html.Div([
        html.H6(title),
        html.Div(body,style=flex_style),
    ],style=border_style)

@app.callback(
    Output('sensors-app-autorefresh-display-value', 'children'),
    [Input('sensors-app-autorefresh-dropdown', 'value')])
def display_value(value):
    return 'You have selected "{}"'.format(value)
