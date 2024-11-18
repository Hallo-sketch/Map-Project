# pages/page2.py
import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__)

layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.H1('Page 2', className='text-center text-info mb-4'),
            width=12
        )
    ]),
    dbc.Row([
        dbc.Col(
            html.P('This is the content of Page 2.', className='text-center'),
            width=12
        )
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Button('Go to Home', href='/', color='primary', className='me-2'),
            width='auto'
        ),
        dbc.Col(
            dbc.Button('Go to Page 1', href='/page1', color='secondary'),
            width='auto'
        )
    ], justify='center')
])
