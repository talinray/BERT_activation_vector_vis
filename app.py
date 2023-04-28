import base64
import datetime
import io
from sklearn.cluster import KMeans
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
import plotly.express as px
import math
import plotly.graph_objects as go
from plotly_resampler import FigureResampler
from plotly.subplots import make_subplots

import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)

app.layout = html.Div([ # this code section taken from Dash docs https://dash.plotly.com/dash-core-components/upload
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'textAlign': 'center',
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-div', style={"height":"100%","width":"100%"})
])


@app.callback(Output('output-div', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(contents, file_names):
    if contents is not None:
        colors=['#0000FF','#FF0000','#FFFF00','#00FF00','#A020F0']
        name = ''
        actual_contents = ''
        predicted_contents = ''
        data = {}
        for i, name in enumerate(file_names):
            components = name.split('_')
            cluster = ''
            actual_label = ''
            if(len(components) == 2):
                cluster=int(components[0][-1])
                actual_label=components[-1][:-4]
                if actual_label not in data:
                    data[actual_label] = {}
                if cluster not in data[actual_label]:
                    data[actual_label][cluster] = {}
                actual_contents = base64.b64decode(contents[i].split(',')[1]).decode('utf-8').rstrip().split('\n')
                data[actual_label][cluster]['actual_contents'] = actual_contents
            else:
                cluster=int(components[1][-1])
                actual_label=components[-1][:-4]
                if actual_label not in data:
                    data[actual_label] = {}
                if cluster not in data[actual_label]:
                    data[actual_label][cluster] = {}
                predicted_contents = base64.b64decode(contents[i].split(',')[1])
                predicted_contents = list(map(int, predicted_contents.decode('utf-8').rstrip().split('\n')))
                data[actual_label][cluster]['predicted_contents'] = predicted_contents

                
        cols = len(data)
        rows = 0
        for act in data:
            rows = max(rows, len(data[act]))
        print(rows)
        act_labels = data.keys()
        titles = []
        for i in range(1, rows+1):
            for label in act_labels:
                title = 'Cluster{cluster}_{label}'.format(cluster=i-1,label=label)
                titles.append(title)
        fig = make_subplots(rows=rows, cols=cols, subplot_titles=titles)
        used_vals = set()
        for col, act in enumerate(data.keys()):
            for row, cluster in enumerate(data[act].keys()):
                actual_contents = data[act][cluster]['actual_contents']
                for i in range(len(actual_contents)):
                    y = list(map(float, actual_contents[i].split()))
                    x = [k for k in range(len(y))]
                    show = True
                    pred_val = data[act][cluster]['predicted_contents'][i]
                    if pred_val in used_vals:
                        show = False
                    used_vals.add(pred_val)
                    pred_color = colors[pred_val]
                    fig.add_trace(
                        go.Scattergl(x=x,
                                    y=y,
                                    mode='lines',
                                    name='Predicted Value {x}'.format(x=pred_val),
                                    line=dict(color=pred_color,width=1),
                                    legendgroup=pred_val,
                                    showlegend=show,
                                    legendgrouptitle=dict(text=pred_val)),
                                    row=row+1,
                                    col=col+1)
        fig.update_annotations(font_size=25)
        return dcc.Graph(figure=fig,style={'height': '90vh'})
    


if __name__ == '__main__':
    app.run_server(host='localhost',port=8005, debug=True)