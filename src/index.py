import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from components.navbar import Sidebar

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    Sidebar(),
    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)
