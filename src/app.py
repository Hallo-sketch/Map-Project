# app.py

import dash
import dash_bootstrap_components as dbc
from dash import html
from components.navbar import Sidebar

app = dash.Dash(
    __name__, 
    use_pages=True, 
    external_stylesheets=[dbc.themes.SLATE]  # Use the SLATE theme
)

# Include the sidebar in the main layout
app.layout = html.Div([
    Sidebar(),          # The fixed navbar
    dash.page_container  # Container for page content
])

server = app.server  # Expose the server variable for deployments

if __name__ == '__main__':
    app.run_server(debug=True)
