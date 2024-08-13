from dash import Dash, dcc
from src.visualization.data.source import Comment
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
from src.visualization.components import ids
import plotly.graph_objects as go


def render(app: Dash, data: Comment) -> dcc.Graph:
    initial_figure = go.Figure()

    @app.callback(
        Output(ids.LINE_PLOT, 'figure'),
        Input(ids.INTERVAL_COMPONENT, 'n_intervals')
    )
    def update_plot(n):

        df = data.query_comments(match_id_date='1_2024-08-13')
        df['date'] = pd.to_datetime(df['timestamp'].astype(int), unit='s').dt.floor('Min')
        df_count = (df.groupby(['date', 'sentiment_id'], as_index=False)['id'].count()
                    .rename(columns={'id': 'count'}))

        fig = px.line(df_count,
                    x='date',
                    y='count',
                    color='sentiment_id')
        
        return fig

    return dcc.Graph(id=ids.LINE_PLOT,
                    figure=initial_figure,
                    )




