from dash import Dash
import dash_bootstrap_components as dbc
from components.layout import create_layout
# from src.visualization.data.source import Comment
from data.source import Comment
import boto3

# Instantate dynamodb class and set table
dyn_resource = boto3.resource('dynamodb')
comment_table = Comment(dyn_resource=dyn_resource)
comment_table.exists('soccer_comment_data')

# Define application
app = Dash(external_stylesheets=[dbc.themes.LITERA])
app.title = 'Realtime Soccer Sentiment'
app.layout = create_layout(app=app, data=comment_table)

application = app.server

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8050)
