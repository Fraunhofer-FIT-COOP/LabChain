import dash
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash()

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.layout = html.Div(children=[
    html.H1(children='Labchain My Dashboard', style={'textAlign': 'center'}),

    html.Button(children='Start Mining', id='mine-button'),

    html.Div(children='Current status: ', style={'textAlign': 'center'}),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'scatter', 'name': 'Difficulty'}
            ],
            'layout': {
                'title': 'Change of Difficulty'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)