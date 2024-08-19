"""
Defines a group of radio buttons for selecting a sentiment visualization type.
"""

from dash import Dash, dcc, html
from data.source import Comment
from . import ids

def render(app: Dash, data: Comment) -> html.Div:
    """
    Renders a radio button component for selecting sentiment visualization type.

    Args:
        app: Dash application.
        data: Comment object encapsulating database interaction methods.

    Returns:
        html.Div: A Div containing the radio buttons for selecting visualization type.
    """
    return html.Div(
        children=[
            html.H6(
                'Select a Sentiment Visualization Type:',
                style={'font-weight': 'bold'}
            ),
            dcc.RadioItems(
                id=ids.PLOT_TYPE_BUTTONS,
                options=[
                    {'label': '     Aggregate sentiment score', 'value': 'aggregate'},
                    {'label': '     Individual sentiment count', 'value': 'individual'}
                ],
                value='aggregate',
                labelStyle={'display': 'block'},
                className='radio'
            )
        ]
    )
