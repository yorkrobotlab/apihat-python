import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_daq as daq
import settings
import pickle
import base64

from app import app
from apps import system_app, control_app, sensors_app, camera_app, analog_app

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>YRL028 APIHAT</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
        </footer>
        <div>(C) York Robotics Laboratory, University of York, 2019</div>
    </body>
</html>
'''

tabs_styles = {
    'height': '44px'
}

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

with open("%slist.pickle" % settings.sensor_datafilename, "rb") as pickler:
    import_sensor_list = pickle.load(pickler)

sensor_tab_list = []
for sensor in import_sensor_list:
    sensor_tab_list.append(sensors_app)
#print (import_sensor_list)

root_layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(
            [
                daq.ToggleSwitch(
                    id="toggleTheme",
                    style={"position": "absolute", "transform": "translate(-50%, 20%)"},
                    size=25,
                )
            ],
            id="toggleDiv",
            style={"width": "fit-content", "margin": "0 auto"},
        ),
        html.Div(id="page-content"),
    ]
)

app.layout = root_layout

tab_list = [
    dcc.Tab(label='System', value='system-tab', style=tab_style, selected_style=tab_selected_style),
    dcc.Tab(label='Control', value='control-tab', style=tab_style, selected_style=tab_selected_style),
    dcc.Tab(label='Analogue', value='analog-tab', style=tab_style, selected_style=tab_selected_style),
    dcc.Tab(label='Camera', value='camera-tab', style=tab_style, selected_style=tab_selected_style)
]

tab_index_list = []
for sensor in import_sensor_list:
    tab_index = "%s" % sensor[0]
    tab_index_list.append(tab_index)
    tab_label = ("Sensor %s" % sensor[0])
    if int(sensor[0]) == 5: tab_label="Board Sensor"
    tab_list.append(dcc.Tab(label=tab_label, value=tab_index, style=tab_style, selected_style=tab_selected_style))

image_filename = "images/uoy-logo.png"
encoded_image = base64.b64encode(open(image_filename,'rb').read())
app.layout = html.Div(
    [
        html.Div(
            id="container",
            style={"background-color": "#20304C"},
            children=[
                html.H2("YRL028 APIHAT"),
                html.A(
                    #html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())),
                    html.Img(src='/assets/uoy-logo.png')
                ),
            ],
            className="banner",
        ),
        dcc.Tabs(id="tabs", value='tab-1-example', children=tab_list, style=tabs_styles),
        html.Div(id='tabs-pages')
    ],
    style={
        "padding": "0px 10px 10px 10px",
        "marginLeft": "auto",
        "marginRight": "auto",
        "width": "960",
        "height": "1800",
        "boxShadow": "0px 0px 5px 5px rgba(204,204,204,0.4)",
    },
)

app.scripts.config.serve_locally = True
app.config["suppress_callback_exceptions"] = True


@app.callback(Output('tabs-pages', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'system-tab': return system_app.layout
    elif tab == 'control-tab': return control_app.layout
    elif tab == 'camera-tab': return camera_app.layout
    elif tab == 'analog-tab': return analog_app.layout
    else:
        for c, index in enumerate(tab_index_list):
            if tab == index: return sensor_tab_list[c].get_layout(import_sensor_list[c][1],"%s%s.csv" % (settings.sensor_datafilename,index),index,import_sensor_list[c][2])

def index_run():
    app.run_server(host='0.0.0.0',port=8082,debug=True)

if __name__ == '__main__':
    index_run()
