from dash import Dash, dcc, html
from data.source import Comment
from . import ids

def render(app: Dash, data: Comment) -> html.Div:
    return html.Div(
        children=[
            html.H6('Select a team',
                    style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id=ids.TEAM_DROPDOWN,  
                options=[{'label': 'arsenal', 'value': 'arsenal'},
                        {'label': 'aston villa', 'value': 'aston villa'},
                        {'label': 'bournemouth', 'value': 'bournemouth'},
                        {'label': 'brentford', 'value': 'brentford'},
                        {'label': 'brighton', 'value': 'brighton'},
                        {'label': 'chelsea', 'value': 'chelsea'},
                        {'label': 'crystal palace', 'value': 'crystal palace'},
                        {'label': 'everton', 'value': 'everton'},
                        {'label': 'fulham', 'value': 'fulham'},
                        {'label': 'ipswich town', 'value': 'ipswich town'},
                        {'label': 'leicester city', 'value': 'leicester city'},
                        {'label': 'liverpool', 'value': 'liverpool'},
                        {'label': 'manchester city', 'value': 'manchester city'},
                        {'label': 'manchester united', 'value': 'manchester united'},
                        {'label': 'newcastle', 'value': 'newcastle'},
                        {'label': 'nottingham forest', 'value': 'nottingham forest'},
                        {'label': 'southampton', 'value': 'southampton'},
                        {'label': 'tottenham', 'value': 'tottenham'},
                        {'label': 'west ham', 'value': 'west ham'},
                        {'label': 'wolves', 'value': 'wolves'}],
                value='arsenal',
                # labelStyle={'display': 'block',
                #             # 'padding-left': '20px'
                #             },
                className='radio'
            )
        ]
    )