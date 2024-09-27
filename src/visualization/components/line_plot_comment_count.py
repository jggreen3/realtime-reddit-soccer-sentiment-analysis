"""
Defines a line plot showing comment volume over time.
"""

from typing import Optional
import logging
import time
import datetime
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
    Generates a Graph object containing a line plot of comment volume over time.

    Args:
        app: Dash application
        data: Comment object encapsulating database interaction methods.

    Returns:
        dcc.Graph: Graph object containing line plot information.
    """
    initial_figure = go.Figure()

    @app.callback(
        Output(ids.LINE_PLOT_COMMENT_COUNT, 'figure'),
        Input(ids.INTERVAL_COMPONENT, 'n_intervals'),
        Input(ids.TEAM_DROPDOWN, 'value'),
        Input(ids.TIME_WINDOW_BUTTONS, 'value')
    )
    def update_plot(n: int, selected_team: Optional[str], selected_time_window: str) -> go.Figure:
        """
        Updates the line plot based on the selected team and time window.

        Args:
            n: Interval count (unused).
            selected_team: The team selected from the dropdown.
            selected_time_window: The time window selected for the plot.

        Returns:
            go.Figure: Updated line plot figure.
        """
        try:
            start_time = time.mktime((datetime.datetime.now() -
                                      pd.to_timedelta(selected_time_window)).timetuple())
            end_time = time.mktime(datetime.datetime.now().timetuple())

            df = data.query_comments(team_name=selected_team, start_time=start_time,
                                      end_time=end_time)

            # Convert timestamps and filter based on the selected time window
            df['date'] = (
                pd.to_datetime(df['timestamp'].dropna().astype(int), unit='s')
                .dt.tz_localize('UTC')
                .dt.tz_convert('US/Pacific')
                .dt.floor('10Min')
                .dt.tz_localize(None)
            )

            # Group by date and count comments
            df_count = (df.groupby('date', as_index=False)['id']
                        .count().rename(columns={'id': 'count'}))

            # Generate the figure
            fig = px.line(
                df_count,
                x='date',
                y='count',
                template='simple_white',
                markers=True
            )

            fig.update_yaxes(title_text='Comment Count', showgrid=True, gridwidth=1,
                              gridcolor='LightGrey')
            fig.update_xaxes(title='Date and Time')
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))

            return fig

        except Exception as e:
            logger.error("Error updating line plot: %s", e)
            return go.Figure()

    return dcc.Graph(id=ids.LINE_PLOT_COMMENT_COUNT, figure=initial_figure)
