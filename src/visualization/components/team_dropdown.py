from dash import Dash, dcc, html
from data.source import Comment
from . import ids

def render(app: Dash, data: Comment) -> html.Div:
    return html.Div(
        children=[
            html.H6('Select a team:',
                    style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id=ids.TEAM_DROPDOWN,  
                options=[{'label': 'Arsenal', 'value': 'arsenal'},
                        {'label': 'Aston Villa', 'value': 'aston villa'},
                        {'label': 'Bournemouth', 'value': 'bournemouth'},
                        {'label': 'Brentford', 'value': 'brentford'},
                        {'label': 'Brighton', 'value': 'brighton'},
                        {'label': 'Chelsea', 'value': 'chelsea'},
                        {'label': 'Crystal Palace', 'value': 'crystal palace'},
                        {'label': 'Everton', 'value': 'everton'},
                        {'label': 'Fulham', 'value': 'fulham'},
                        {'label': 'Ipswich Town', 'value': 'ipswich town'},
                        {'label': 'Leicester City', 'value': 'leicester city'},
                        {'label': 'Liverpool', 'value': 'liverpool'},
                        {'label': 'Manchester City', 'value': 'manchester city'},
                        {'label': 'Manchester United', 'value': 'manchester united'},
                        {'label': 'Newcastle', 'value': 'newcastle'},
                        {'label': 'Nottingham Forest', 'value': 'nottingham forest'},
                        {'label': 'Southampton', 'value': 'southampton'},
                        {'label': 'Tottenham', 'value': 'tottenham'},
                        {'label': 'West Ham', 'value': 'west ham'},
                        {'label': 'Wolves', 'value': 'wolves'}],
                value='arsenal',
                # labelStyle={'display': 'block',
                #             # 'padding-left': '20px'
                #             },
                className='radio'
            )
        ]
    )