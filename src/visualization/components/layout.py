from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
# from src.visualization.components import line_plot, ids
from . import line_plot, ids, team_dropdown, pie_chart, line_plot_comment_count
from data.source import Comment
# from src.visualization.data.source import Comment


def generate_control_card(app: Dash, data: Comment):
    return html.Div(
        children=[
            dbc.Card(
                dbc.CardBody(
                    [
                        # html.H2('Live Premier League Team Sentiment'),
                        html.Br(),
                        html.H5(
                            children="""How do fans and rivals on Reddit feel about Premier League
                              teams?"""),
                        html.Br(),
                        html.Div(
                            children="""This dashboard is designed to explore trends in comment
                            sentiment overtime in the biggest soccer subredddits, tracking how fans 
                            feel about their team's throughout the season."""
                        ),
                        html.Br(),
                        html.Div(children="""Select a team to start exploring realtime sentiment
                                  data."""),
                        html.Br(),
                        html.Div(team_dropdown.render(app, data))
                    ]
                ),
                style={'border': 'none', 'backgroundColor': '#f8f9fa'}
            )
        ],
        style={'margin-bottom': '20px'}
    )

def generate_line_plot(app: Dash, data: Comment):
    return html.Div(
        children=[
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5('Team Sentiment Over Time', className='card-title', style={'font-weight': 'bold'}),
                        html.Hr(),
                        dbc.Spinner(line_plot.render(app, data))
                    ],
                ),
            )
        ]
    )

def generate_pie_chart(app: Dash, data: Comment):
    return html.Div(
        children=[
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5('Total Sentiment Proportion', className='card-title', style={'font-weight': 'bold'}),
                        html.Hr(),
                        dbc.Spinner(pie_chart.render(app, data))
                    ],
                ),
            )
        ]
    )

def generate_line_plot_comment_count(app: Dash, data: Comment):
    return html.Div(
        children=[
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5('Comment Volume Over Time', className='card-title', style={'font-weight': 'bold'}),
                        html.Hr(),
                        dbc.Spinner(line_plot_comment_count.render(app, data))
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
                        html.H2('Premier League Reddit Sentiment Monitoring'),
                        # html.Img(src=app.get_asset_url('usf_logo.png'), style={'height': 'auto', 'width': '20%', 'display': 'block'}),
                        style={'padding': 15, 'text-align': 'Left'}
                    ),
                    style={'padding': 0, 'margin': 0}
                ),
                fluid=True
            ),
            html.Hr(style={'margin': 0}),
            dbc.Container(
                fluid=True,
                children=[
                    dbc.Row(
                    [
                        dbc.Col(
                            generate_control_card(app, data),
                            xs=12, md=3,  # Full width on small screens, 1/3 width on medium+
                            style={'padding': '0 10px', 'margin-bottom': '0px', 'background-color': 'rgb(248, 249, 250)'}
                        ),
                        dbc.Col(
                            [
                                dcc.Interval(id=ids.INTERVAL_COMPONENT,
                                             interval=1*10000,
                                             n_intervals=0
                                             ),
                                generate_line_plot(app, data),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            generate_pie_chart(app, data),
                                            xs=12, md=6,  # Half the width on medium+ screens
                                            style={'padding': '10px'}
                                        ),
                                        dbc.Col(
                                            generate_line_plot_comment_count(app, data),
                                            xs=12, md=6,  # Half the width on medium+ screens
                                            style={'padding': '10px'}
                                        )
                                    ]
                                )
                            ],
                            xs=12, md=8,  # Full width on small screens, 2/3 width on medium+
                            style={'backgroundColor': '#e9ecef', 'padding': '20px', 'flex': '1', 'max-width': '100%'}
                        ),
                    ],
                    style={'margin': '0', 'height': '100vh'}
                ),
                ],
                style={'--bs-gutter-x': 0},
            )
        ]
    )