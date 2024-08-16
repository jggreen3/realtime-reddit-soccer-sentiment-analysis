import plotly.graph_objects as go
from dash import Dash, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import datetime
import pandas as pd
from data.source import Comment
from . import ids



def render(app: Dash, data: Comment) -> dcc.Graph:
    initial_figure = go.Figure()

    @app.callback(
        Output(ids.LINE_PLOT_COMMENT_COUNT, 'figure'),
        Input(ids.INTERVAL_COMPONENT, 'n_intervals'),
        Input(ids.TEAM_DROPDOWN, 'value'),
        Input(ids.TIME_WINDOW_BUTTONS, 'value')
    )
    def update_plot(n, selected_team, selected_time_window):

        df = data.query_comments(team_name=selected_team)

        df['date'] = (pd.to_datetime(df['timestamp'].astype(int), unit='s').dt.tz_localize('UTC')
                      .dt.tz_convert('US/Pacific').dt.floor('Min')).dt.tz_localize(None)
        
        df = df.loc[df['date'] > datetime.datetime.now() - pd.to_timedelta(selected_time_window)]

        df_count = (df.groupby(['date'], as_index=False)['id'].count()
                    .rename(columns={'id': 'count'}))

        fig = px.line(df_count,
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

    return dcc.Graph(id=ids.LINE_PLOT_COMMENT_COUNT,
                    figure=initial_figure,
                    )




