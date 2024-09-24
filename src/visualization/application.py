"""
Defines a Dash application including the layout, server config, and data source.
"""

import os
import logging
import dotenv
from dash import Dash
import dash_bootstrap_components as dbc
from components.layout import create_layout
from data.source import Comment
import boto3

dotenv.load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> Dash:
    """
    Creates a Dash application with the given layout and data source.

    Returns:
        Dash: A configured Dash application.
    """
    comment_table = Comment()
    _app = Dash(external_stylesheets=[dbc.themes.LITERA])
    _app.title = 'Realtime Soccer Sentiment'
    _app.layout = create_layout(app=_app, data=comment_table)
    return _app

app = create_app()
application = app.server

if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG') == 'TRUE'
    host = os.getenv('HOST', 'localhost')
    port = int(os.getenv('PORT', '8050'))
    logger.info("Starting Dash app on %s:%s with debug=%s", host, port, debug_mode)
    app.run(debug=debug_mode, host=host, port=port)
