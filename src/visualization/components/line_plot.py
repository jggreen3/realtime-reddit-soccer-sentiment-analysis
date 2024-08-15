import plotly.graph_objects as go
from dash import Dash, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
# from src.visualization.data.source import Comment
from data.source import Comment

# from src.visualization.components import ids
from . import ids



def render(app: Dash, data: Comment) -> dcc.Graph:
    initial_figure = go.Figure()

    @app.callback(
        Output(ids.LINE_PLOT, 'figure'),
        Input(ids.INTERVAL_COMPONENT, 'n_intervals'),
        Input(ids.TEAM_DROPDOWN, 'value')
    )
    def update_plot(n, selected_team):

        df = data.query_comments(team_name=selected_team)

        df['date'] = (pd.to_datetime(df['timestamp'].astype(int), unit='s').dt.tz_localize('UTC')
                      .dt.tz_convert('US/Pacific').dt.floor('Min'))

        df_count = (df.groupby(['date', 'sentiment_id'], as_index=False)['id'].count()
                    .rename(columns={'id': 'count'}))

        fig = px.line(df_count,
                    x='date',
                    y='count',
                    color='sentiment_id',
                    template='simple_white',
                    )
        
        return fig

    return dcc.Graph(id=ids.LINE_PLOT,
                    figure=initial_figure,
                    )




