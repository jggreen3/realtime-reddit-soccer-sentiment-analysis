"""
Defines a line plot component showing comment sentiment over time.
"""

import datetime
import time
import logging
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
    Generates a Graph object containing a line plot of comment sentiment over time.

    Args:
        app: Dash application
        data: Comment object encapsulating database interaction methods.

    Returns:
        dcc.Graph: Graph object containing line plot information.
    """
    initial_figure = go.Figure()

    @app.callback(
        Output(ids.LINE_PLOT, 'figure'),
        Input(ids.INTERVAL_COMPONENT, 'n_intervals'),
        Input(ids.TEAM_DROPDOWN, 'value'),
        Input(ids.TIME_WINDOW_BUTTONS, 'value'),
        Input(ids.PLOT_TYPE_BUTTONS, 'value')
    )
    def update_plot(n: int, selected_team: Optional[str], selected_time_window: str,
                     selected_plot_type: str) -> go.Figure:
        """
        Updates the line plot based on the selected team, time window, and plot type.

        Args:
            n: Interval count (unused).
            selected_team: The team selected from the dropdown.
            selected_time_window: The time window selected for the plot.
            selected_plot_type: The type of plot selected (individual lines or aggregated score).

        Returns:
            go.Figure: Updated line plot figure.
        """
        try:
            start_time = time.mktime((datetime.datetime.now() - pd.to_timedelta(selected_time_window)).timetuple())
            end_time = time.mktime(datetime.datetime.now().timetuple())

            df = data.query_comments(team_name=selected_team, start_time=start_time, end_time=end_time)

            # Convert timestamps and filter based on the selected time window
            df['date'] = (
                pd.to_datetime(df['timestamp'].dropna().astype(int), unit='s')
                .dt.tz_localize('UTC')
                .dt.tz_convert('US/Pacific')
                .dt.floor('10Min')
                .dt.tz_localize(None)
            )

            if selected_plot_type == 'individual':
                df_count = (df.groupby(['date', 'sentiment_id'], as_index=False)['id']
                            .count().rename(columns={'id': 'count'}))

                fig = px.line(
                    df_count,
                    x='date',
                    y='count',
                    color='sentiment_id',
                    template='simple_white',
                    color_discrete_map={
                        'positive': '#98df8a',
                        'negative': '#e37777',
                        'neutral': '#b0b0b0'
                    },
                    markers=True
                )

                fig.update_yaxes(title_text='Comment Count', showgrid=True, gridwidth=1,
                                 gridcolor='LightGrey')
                fig.update_xaxes(title='Date and Time')

            else:
                df['sentiment_score'] = df['sentiment_id'].map({
                    'positive': 1,
                    'negative': -1,
                    'neutral': 0
                })

                df_count = df.groupby(['date'], as_index=False)['sentiment_score'].sum()

                fig = px.line(
                    df_count,
                    x='date',
                    y='sentiment_score',
                    template='simple_white',
                    markers=True
                )

                fig.update_yaxes(title_text='Sentiment Score', showgrid=True, gridwidth=1,
                                 gridcolor='LightGrey')
                fig.update_xaxes(title='Date and Time')
                fig.add_hline(y=0, line_width=3, line_dash='dash', line_color='red')

            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            return fig

        except Exception as e:
            logger.error("Error updating sentiment plot: %s", e)
            return go.Figure()

    return dcc.Graph(id=ids.LINE_PLOT, figure=initial_figure)
