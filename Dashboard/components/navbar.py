# components/navbar.py
import dash_bootstrap_components as dbc
from dash import html

def Sidebar():
    sidebar = html.Div(
        [
            dbc.NavbarSimple(
                brand="Cocoa Dashboard",
                brand_href="#",
                color="dark",
                dark=True,
                children=[
                    dbc.DropdownMenu(
                        nav=True,
                        in_navbar=True,
                        label="Navigate",
                        children=[
                            dbc.DropdownMenuItem("Home", href='/'),
                            dbc.DropdownMenuItem("Cóte d\'Ivoire GeoSpatial data", href='/page1'),
                            dbc.DropdownMenuItem("Market Analysis", href='/page2'),
                        ],
                    ),
                ],
            ),
        ],
        style={
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'width': '100%',
            'zIndex': 999,
            'color': 'white'
        },
        className='select-control'
    )
    return sidebar