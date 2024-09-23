"""
Defines a pie chart showing sentiment distribution.
"""

import logging
import time
import datetime
from typing import Optional
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc
from dash.dependencies import Input, Output
import pandas as pd
from data.source import Comment
from . import ids

logger = logging.getLogger(__name__)

def render(app: Dash, data: Comment) -> dcc.Graph:
    """
    Generates a Graph object containing a pie chart of comment sentiment distribution.

    Args:
        app: Dash application.
        data: Comment object encapsulating database interaction methods.

    Returns:
        dcc.Graph: Graph object containing pie chart information.
    """
    initial_figure = go.Figure()

    @app.callback(
        Output(ids.PIE_CHART, 'figure'),
        Input(ids.INTERVAL_COMPONENT, 'n_intervals'),
        Input(ids.TEAM_DROPDOWN, 'value'),
        Input(ids.TIME_WINDOW_BUTTONS, 'value')
    )
    def update_plot(n: int, selected_team: Optional[str], selected_time_window: str) -> go.Figure:
        """
        Updates the pie chart based on the selected team.

        Args:
            n: Interval count (unused).
            selected_team: The team selected from the dropdown.

        Returns:
            go.Figure: Updated pie chart figure.
        """
        try:
            start_time = time.mktime((datetime.datetime.now() - pd.to_timedelta(selected_time_window)).timetuple())
            end_time = time.mktime(datetime.datetime.now().timetuple())

            df = data.query_comments(team_name=selected_team, start_time=start_time, end_time=end_time)

            df_plot = pd.DataFrame(df['sentiment_id'].value_counts(normalize=True)).reset_index()
            df_plot.columns = ['sentiment_id', 'proportion']

            fig = px.pie(
                df_plot,
                values='proportion',
                names='sentiment_id',
                template='simple_white',
                color='sentiment_id',
                color_discrete_map={
                    'positive': '#98df8a',
                    'negative': '#e37777',
                    'neutral': '#b0b0b0'
                }
            )

            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10))

            return fig

        except Exception as e:
            logger.error("Error updating pie chart: %s", e)
            return go.Figure()

    return dcc.Graph(id=ids.PIE_CHART, figure=initial_figure)
