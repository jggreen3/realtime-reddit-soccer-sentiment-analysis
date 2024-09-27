"""
Defines a group of summary topics and associated details.
"""

import datetime
import time
import logging
from typing import Optional
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from data.source import Comment
from . import ids

logger = logging.getLogger(__name__)

def render(app: Dash, data: Comment) -> html.Div:
    """
    Renders the Accordion component for summary topics and associated details.    

    Args:
        app: Dash application
        data: Comment object encapsulating database interaction methods.

    Returns:
        dcc.Graph: Graph object containing line plot information.
    """

    @app.callback(
        Output(ids.SUMMARY_ACCORDION, 'children'),
        Input(ids.INTERVAL_COMPONENT, 'n_intervals'),
        Input(ids.TEAM_DROPDOWN, 'value'),
    )
    def update_plot(n: int, selected_team: Optional[str]) -> html.Div:
        """
        Updates the accordion based on the chosen team.
        
        Args:
            n: Interval count (unused).
            selected_team: The team selected from the dropdown.

        Returns:
            html.Div: The updated Div component
        """
        try:

            df = data.get_most_recent_summary(team_name=selected_team)

            if df.empty:
                return dbc.Accordion([dbc.AccordionItem("No data available", title="No Topics")])

            accordion_items = [
                dbc.AccordionItem(item['Description'], title=item['Title']) 
                for _, item in df.iterrows()
            ]
            print(accordion_items)

            return dbc.Accordion(accordion_items, start_collapsed=True, flush=True)

        except Exception as e:
            logger.error("Error updating sentiment plot: %s", e)
            return dbc.Accordion(id=ids.SUMMARY_ACCORDION)

    return html.Div(dbc.Accordion(id=ids.SUMMARY_ACCORDION))
