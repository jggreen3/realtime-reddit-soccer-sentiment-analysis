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
        Output(ids.PIE_CHART, 'figure'),
        Input(ids.INTERVAL_COMPONENT, 'n_intervals'),
        Input(ids.TEAM_DROPDOWN, 'value')
    )
    def update_plot(n, selected_team):

        df = data.query_comments(team_name=selected_team)

        df_plot = pd.DataFrame(df['sentiment_id'].value_counts(normalize=True)).reset_index()

        fig = px.pie(df_plot,
                    values='proportion',
                    names='sentiment_id',
                    template='simple_white',
                    color='sentiment_id',
                    color_discrete_map={'positive': '#98df8a',
                                        'negative': '#e37777', 
                                        'neutral': '#b0b0b0'})

        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=False)
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))  # Adjust margins within the plot

        
        return fig

    return dcc.Graph(id=ids.PIE_CHART,
                    figure=initial_figure,
                    )




