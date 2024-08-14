from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
# from src.visualization.components import line_plot, ids
from . import line_plot, ids
from data.source import Comment
# from src.visualization.data.source import Comment



def generate_line_plot(app: Dash, data: Comment):
    return html.Div(
        children=[
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5('How have the quality and quantity of movies changed over time?', className='card-title', style={'font-weight': 'bold'}),
                        html.Hr(),
                        dbc.Spinner(line_plot.render(app, data))
                    ],
                ),
            )
        ]
    )

def create_layout(app: Dash, data: Comment) -> html.Div:
    return html.Div(
        className="app-div",
        style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh', 'overflow-x': 'hidden'},
        children=[
            dbc.Container(
                dbc.Row(
                    dbc.Col(
                        html.Img(src=app.get_asset_url('usf_logo.png'), style={'height': 'auto', 'width': '20%', 'display': 'block'}),
                        style={'padding': 15, 'text-align': 'center'}
                    ),
                    style={'padding': 0, 'margin': 0}
                ),
                fluid=True
            ),
            html.Hr(style={'margin-bottom': 0}),
            dbc.Container(
                fluid=True,
                children=dbc.Row(
                    [
                        dbc.Col(
                            # generate_control_card(app, data),
                            xs=12, md=4,  # Full width on small screens, 1/3 width on medium+
                            style={'padding': '0 10px', 'margin-bottom': '0px', 'background-color': 'rgb(248, 249, 250)'}
                        ),
                        dbc.Col(
                            [
                                dcc.Interval(id=ids.INTERVAL_COMPONENT,
                                             interval=1*10000,
                                             n_intervals=0
                                             ),
                                generate_line_plot(app, data)
                            ],
                            xs=12, md=8,  # Full width on small screens, 2/3 width on medium+
                            style={'backgroundColor': '#e9ecef', 'padding': '20px', 'flex': '1', 'max-width': '100%'}
                        ),
                    ],
                    style={'margin': '0', 'height': '100vh'}
                ),
                style={'--bs-gutter-x': 0}
            )
        ]
    )