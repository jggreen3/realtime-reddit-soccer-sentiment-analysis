from dash import Dash, dcc, html
from data.source import Comment
from components import ids

def render(app: Dash, data: Comment) -> html.Div:
    return html.Div(
        children=[
            html.H6('Select a Sentiment Visualization Type:',
                    style={'font-weight': 'bold'}),
            dcc.RadioItems(
                id=ids.PLOT_TYPE_BUTTONS,  
                options=[{'label': '     Aggregate sentiment score', 'value': 'aggregate'},
                         {'label': '     Individual sentiment count', 'value': 'individual'}],
                value='aggregate',
                labelStyle={'display': 'block',

                            },
                className='radio'
            )
        ]
    )