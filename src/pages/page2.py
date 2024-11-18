# pages/page2.py
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dash import callback, Input, Output

# Register the page
dash.register_page(__name__)

# Corrected file path to the CSV
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
file_path = os.path.join(data_dir, '2024 consumption.csv')

# Load and process the data
df = pd.read_csv(file_path)

# Clean column names for easier handling
df.columns = df.columns.str.replace('WhichCountryEatsTheMostChocolate_', '')
df.columns = df.columns.str.replace('_2022', '')

# Container style configurations
CONTAINER_STYLE = {
    'maxWidth': '2000px',      # Maximum width for very large screens
    'minWidth': '320px',       # Minimum width for mobile screens
    'margin': 'auto',
    'color': '#ffffff',        # Text color for dark aesthetic
    'marginTop': '56px',       # Add margin to account for fixed navbar
    'paddingTop': '20px'       # Additional padding for spacing
}

# Layout with dark aesthetic styling
layout = dbc.Container([
    # Header Section
    dbc.Row([
        dbc.Col(
            html.H1("Global Chocolate Consumption Analysis", 
                   className='text-center text-primary my-4',
                   style={'fontSize': 'calc(1.5rem + 1.5vw)'}),
            width=12
        )
    ]),

    # Description Section
    dbc.Row([
        dbc.Col([
            html.P("2022 data on global chocolate consumption was analyzed to identify the top consumers by total consumption and daily per capita consumption. The top 15 countries by each metric are displayed in the charts below. The scatter plot shows the relationship between total and per capita consumption for all countries in the dataset.",
                   className='text-center mb-4',
                   style={'fontSize': 'calc(0.9rem + 0.5vw)'})
        ], width=12)
    ]),
    
    # Row 1: Top consumers charts
    dbc.Row([
        # Total consumption chart
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Top 15 Countries by Total Chocolate Consumption", style={'color': '#ffffff', 'backgroundColor': '#272b30'}),
                dbc.CardBody(
                    dcc.Graph(id='total-consumption-chart')
                )
            ], style={'backgroundColor': '#272b30'})
        ], width=12, lg=6, className="mb-4"),
        
        # Per capita consumption chart
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Top 15 Countries by Daily Per Capita Consumption", style={'color': '#ffffff', 'backgroundColor': '#272b30'}),
                dbc.CardBody(
                    dcc.Graph(id='per-capita-chart')
                )
            ], style={'backgroundColor': '#272b30'})
        ], width=12, lg=6, className="mb-4"),
    ]),
    
    # Row 2: Scatter plot
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Total vs Per Capita Consumption", style={'color': '#ffffff', 'backgroundColor': '#272b30'}),
                dbc.CardBody(
                    dcc.Graph(id='scatter-plot')
                )
            ], style={'backgroundColor': '#272b30'})
        ], width=12, className="mb-4")
    ])
], fluid=True, style=CONTAINER_STYLE)

# Callbacks to update the graphs
@callback(
    Output('total-consumption-chart', 'figure'),
    Input('total-consumption-chart', 'id')
)
def update_total_consumption(dummy):
    # Get top 15 total consumers
    top_total = df.nlargest(15, 'ChocolateProductsNESConsumed_Tonnes')
    
    fig = go.Figure(go.Bar(
        x=top_total['ChocolateProductsNESConsumed_Tonnes'] / 1000,  # Convert to thousands
        y=top_total['country'],
        orientation='h',
        marker_color='#8884d8'
    ))
    
    fig.update_layout(
        xaxis_title="Consumption (thousands of tonnes)",
        yaxis_title=None,
        yaxis={'categoryorder': 'total ascending'},
        height=600,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='#272b30',  # Background to match the dark aesthetic
        plot_bgcolor='#272b30',
        font=dict(color='#ffffff')  # White font for visibility
    )
    
    return fig

@callback(
    Output('per-capita-chart', 'figure'),
    Input('per-capita-chart', 'id')
)
def update_per_capita(dummy):
    # Get top 15 per capita consumers
    top_capita = df.nlargest(15, 'ConsumptionPerCap_GramsPerCapPerDay')
    
    fig = go.Figure(go.Bar(
        x=top_capita['ConsumptionPerCap_GramsPerCapPerDay'],
        y=top_capita['country'],
        orientation='h',
        marker_color='#82ca9d'
    ))
    
    fig.update_layout(
        xaxis_title="Daily Consumption (grams per person)",
        yaxis_title=None,
        yaxis={'categoryorder': 'total ascending'},
        height=600,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='#272b30',  # Background to match the dark aesthetic
        plot_bgcolor='#272b30',
        font=dict(color='#ffffff')  # White font for visibility
    )
    
    return fig

@callback(
    Output('scatter-plot', 'figure'),
    Input('scatter-plot', 'id')
)
def update_scatter(dummy):
    fig = px.scatter(
        df,
        x='ChocolateProductsNESConsumed_Tonnes',
        y='ConsumptionPerCap_GramsPerCapPerDay',
        hover_data=['country'],
        labels={
            'ChocolateProductsNESConsumed_Tonnes': 'Total Consumption (tonnes)',
            'ConsumptionPerCap_GramsPerCapPerDay': 'Per Capita Consumption (g/day)',
            'country': 'Country'
        }
    )
    
    # Add hover text with country names
    fig.update_traces(
        hovertemplate="<br>".join([
            "Country: %{customdata[0]}",
            "Total Consumption: %{x:.0f} tonnes",
            "Per Capita Consumption: %{y:.1f} g/day"
        ])
    )
    
    fig.update_layout(
        height=600,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='#272b30',  # Background to match the dark aesthetic
        plot_bgcolor='#272b30',
        font=dict(color='#ffffff')  # White font for visibility
    )
    
    return fig
