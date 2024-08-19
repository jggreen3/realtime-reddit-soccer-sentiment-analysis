"""Defines a group of radio buttons for selecting a time window."""

from dash import Dash, html
from data.source import Comment
import dash_bootstrap_components as dbc
from components import ids

def render(app: Dash, data: Comment) -> html.Div:
    """
    Renders a radio button component for selecting a timeframe.

    Args:
        app: Dash application.
        data: Comment object encapsulating database interaction methods.

    Returns:
        html.Div: A Div containing the timeframe selection radio buttons.
    """
    return html.Div(
        children=[
            html.H6(
                'Select a Timeframe:',
                style={'font-weight': 'bold'}
            ),
            dbc.RadioItems(
                id=ids.TIME_WINDOW_BUTTONS,
                className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-primary",
                labelCheckedClassName="active",
                options=[
                    {'label': '1 hour', 'value': '1hour'},
                    {'label': '1 day', 'value': '1day'},
                    {'label': '1 week', 'value': '7days'},
                    {'label': '1 month', 'value': '30days'}
                ],
                value='1hour',
            ),
        ],
        className='radio-group'
    )
