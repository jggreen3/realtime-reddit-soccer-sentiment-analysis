import plotly.graph_objects as go
from dash import Dash, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import datetime
# from src.visualization.data.source import Comment
from data.source import Comment

# from src.visualization.components import ids
from . import ids



def render(app: Dash, data: Comment) -> dcc.Graph:
    initial_figure = go.Figure()

    @app.callback(
        Output(ids.LINE_PLOT, 'figure'),
        Input(ids.INTERVAL_COMPONENT, 'n_intervals'),
        Input(ids.TEAM_DROPDOWN, 'value'),
        Input(ids.TIME_WINDOW_BUTTONS, 'value'),
        Input(ids.PLOT_TYPE_BUTTONS, 'value')
    )
    def update_plot(n, selected_team, selected_time_window, selected_plot_type):

        df = data.query_comments(team_name=selected_team)

        df['date'] = (pd.to_datetime(df['timestamp'].astype(int), unit='s').dt.tz_localize('UTC')
                      .dt.tz_convert('US/Pacific').dt.floor('Min')).dt.tz_localize(None)
        
        df = df.loc[df['date'] > datetime.datetime.now() - pd.to_timedelta(selected_time_window)]

        # Plot with individual lines for each sentiment category
        if selected_plot_type == 'individual':
            df_count = (df.groupby(['date', 'sentiment_id'], as_index=False)['id'].count()
                        .rename(columns={'id': 'count'}))

            fig = px.line(df_count,
                        x='date',
                        y='count',
                        color='sentiment_id',
                        template='simple_white',
                        color_discrete_map={'positive': '#98df8a',
                                        'negative': '#e37777', 
                                        'neutral': '#b0b0b0'},
                        markers=True
                        )

            fig.update_yaxes(title_text='Comment Count', showgrid=True, gridwidth=1,
                              gridcolor='LightGrey')
            
            fig.update_xaxes(title='Date and Time')

        
        # Plot with aggregated sentiment score
        else:
            df['sentiment_score'] = (df['sentiment_id']
                                     .map({'positive': 1, 'negative': -1, 'neutral': 0}))
            
            df_count = (df.groupby(['date'], as_index=False)['sentiment_score'].sum())

            fig = px.line(df_count,
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

    return dcc.Graph(id=ids.LINE_PLOT,
                    figure=initial_figure,
                    )




