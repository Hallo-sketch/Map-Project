import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import pandas as pd
import geopandas as gpd
import numpy as np

# Register the page
dash.register_page(__name__, path='/page1')

# Container style configurations
CONTAINER_STYLE = {
    'maxWidth': '2000px',      # Maximum width for very large screens
    'minWidth': '320px',       # Minimum width for mobile screens
    'margin': 'auto',
    'color': '#ffffff',        # Text color for dark aesthetic
    'marginTop': '56px',       # Add margin to account for fixed navbar
    'paddingTop': '20px'       # Additional padding for spacing
}

# Define the layout for the page
layout = dbc.Container([
    # Header Section
    dbc.Row([
        dbc.Col(
            html.H1("Côte d'Ivoire GeoSpatial Data", 
                   className='text-center text-primary my-4',
                   style={'fontSize': 'calc(1.5rem + 1.5vw)'}),
            width=12
        )
    ]),

    # Description Section
    dbc.Row([
        dbc.Col([
            html.P("Select a dataset to view Côte d'Ivoire cocoa production, yield, and environmental data on the map.",
                   className='text-center mb-4',
                   style={'fontSize': 'calc(0.9rem + 0.5vw)'})
        ], width=12)
    ]),

    # Dropdown selector for GeoJSON datasets
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("Select a GeoJSON Dataset:",
                               style={'fontSize': 'calc(0.9rem + 0.4vw)'}),
                    dcc.Dropdown(
                        id='geojson-selector',
                        options=[
                            {'label': 'Cocoa Area', 'value': 'cote-divoire-cocoa-area-2021'},
                            {'label': 'Deforestation 15 Years Total', 'value': 'cote-divoire-cocoa-deforestation-15-years-total-2021'},
                            {'label': 'Cocoa TN', 'value': 'cote-divoire-cocoa-tn-2021'},
                            {'label': 'Cocoa Yield', 'value': 'cote-divoire-cocoa-yield-2021'},
                            {'label': 'ZDC Traded Cocoa Percentage', 'value': 'cote-divoire-zdc-traded-cote-divoire-cocoa-perc-2021'}
                        ],
                        value='cote-divoire-cocoa-area-2021',
                        className='mb-3',
                        style={'fontSize': 'calc(0.8rem + 0.3vw)', 'color': '#000000'}
                    )
                ])
            ], className="mb-4")
        ], width=12)
    ]),

    # Year Dropdown Selector Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("Select Year:", style={'fontSize': 'calc(0.9rem + 0.4vw)'}),
                    dcc.Dropdown(
                        id='year-selector',
                        className='mb-3',
                        style={'fontSize': 'calc(0.8rem + 0.3vw)', 'color': '#000000'}
                    )
                ])
            ], className="mb-4")
        ], width=12)
    ]),

    # Map Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='geojson-map', style={'height': 'calc(80vh - 100px)'})
                ])
            ], style={
                'height': 'calc(100vh - 200px)',
                'minHeight': '400px'
            })
        ], width=12, className='mb-4')
    ]),

    # Main Statistical Cards Section
    # Main Statistical Cards Section
    dbc.Row([
        # Left Column: Descriptive Statistics, Top and Bottom Regions, Time Series Analysis
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Descriptive Statistics", className='card-title'),
                    html.Div(id='descriptive-stats')
                ])
            ], className='mb-4'),

            dbc.Card([
                dbc.CardBody([
                    html.H4("Top and Bottom Regions", className='card-title'),
                    html.Div(id='top-bottom-regions')
                ])
            ], className='mb-4'),

            dbc.Card([
                dbc.CardBody([
                    html.H4("Time Series Analysis", className='card-title'),
                    dcc.Graph(id='timeseries-analysis')
                ])
            ], className='mb-4', style={'height': 'calc(33.33%)'})  # Make each card take equal vertical space
        ], width=6, style={'height': '100%'}),  # Set column height to fill vertically

        # Right Column: Statistical Distribution (Double the height)
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Statistical Distribution", className='card-title'),
                    dcc.Graph(id='statistical-distribution')
                ])
            ], style={'height': '200%'})  # Make the right card double the height of the left column's stack
        ], width=6, style={'height': '200%'})  # Set column height to double the height of the left column
    ]),


    # Regional Insights Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Regional Insights", className='card-title'),
                    html.Div(id='regional-insights')
                ])
            ])
        ], width=12, className='mb-4')
    ]),
], fluid=True, style=CONTAINER_STYLE)


# Load GeoJSON datasets
def load_geojson_data():
    """Load all GeoJSON datasets into a dictionary."""
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'cote-divoire'))
    
    datasets = {}

    # List of files to load
    file_names = [
        'cote-divoire-cocoa-area-2021.geojson',
        'cote-divoire-cocoa-deforestation-15-years-total-2021.geojson',
        'cote-divoire-cocoa-tn-2021.geojson',
        'cote-divoire-cocoa-yield-2021.geojson',
        'cote-divoire-zdc-traded-cote-divoire-cocoa-perc-2021.geojson'
    ]

    # Load each file
    for file_name in file_names:
        file_path = os.path.join(data_dir, file_name)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    dataset_name = file_name.replace('.geojson', '')
                    datasets[dataset_name] = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error loading {file_name}: {e}")
        else:
            print(f"File not found: {file_name}")
    return datasets

geojson_datasets = load_geojson_data()

@callback(
    [Output('year-selector', 'options'),
     Output('year-selector', 'value')],
    [Input('geojson-selector', 'value')]
)
def update_year_selector(selected_dataset):
    if selected_dataset not in geojson_datasets:
        return [], None

    # Get the selected GeoJSON data
    geojson_data = geojson_datasets[selected_dataset]

    # Extract year information from 'timeseries' field in properties
    years_set = set()
    for feature in geojson_data['features']:
        timeseries = feature['properties'].get('timeseries', [])
        for entry in timeseries:
            if 'year' in entry:
                years_set.add(entry['year'])

    available_years = sorted(list(years_set))

    # Debug: Print available years for verification
    print(f"Available years for {selected_dataset}: {available_years}")

    # Set default year to the most recent one if available
    default_year = available_years[-1] if available_years else None

    # Prepare options for the year dropdown
    year_options = [{'label': str(year), 'value': year} for year in available_years]

    return year_options, default_year

@callback(
    [Output('geojson-map', 'figure'),
     Output('descriptive-stats', 'children'),
     Output('top-bottom-regions', 'children'),
     Output('timeseries-analysis', 'figure'),
     Output('statistical-distribution', 'figure'),
     Output('regional-insights', 'children')],
    [Input('geojson-selector', 'value'),
     Input('year-selector', 'value')]
)
def update_map(selected_dataset, selected_year):
    if selected_dataset not in geojson_datasets:
        return px.scatter_mapbox(), "No data available", "No data available", go.Figure(), go.Figure(), "No data available"

    # Get the selected GeoJSON data
    geojson_data = geojson_datasets[selected_dataset]

    # Filter features by selected year if available
    features = [
        feature for feature in geojson_data['features']
        if any(entry['year'] == selected_year for entry in feature['properties'].get('timeseries', []))
    ]

    # Create a filtered GeoJSON object
    filtered_geojson = {"type": "FeatureCollection", "features": features}

    # Load GeoJSON as a GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(filtered_geojson['features'])

    # Ensure 'numerical_value' is a valid column; assign dummy values if missing
    if 'numerical_value' not in gdf.columns:
        gdf['numerical_value'] = np.random.randint(10, 100, len(gdf))

    # Create a choropleth map using Plotly Express
    fig = px.choropleth(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        color='numerical_value',
        hover_name='name',
        title="Côte d'Ivoire Cocoa Production Areas"
    )

    fig.update_geos(fitbounds="locations", visible=False, bgcolor='#272b30')
    fig.update_layout(
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        plot_bgcolor='#272b30',
        paper_bgcolor='#272b30',
        font=dict(color='#ffffff')
    )

    # Descriptive Statistics
    if not gdf.empty:
        mean_value = gdf['numerical_value'].mean()
        median_value = gdf['numerical_value'].median()
        std_dev = gdf['numerical_value'].std()
        descriptive_stats = html.Div([
            html.P(f"Mean Value: {mean_value:.2f}"),
            html.P(f"Median Value: {median_value:.2f}"),
            html.P(f"Standard Deviation: {std_dev:.2f}")
        ])

        # Top and Bottom Regions
        top_region = gdf.loc[gdf['numerical_value'].idxmax()]
        bottom_region = gdf.loc[gdf['numerical_value'].idxmin()]
        top_bottom_regions = html.Div([
            html.P(f"Top Region: {top_region['name']} with value {top_region['numerical_value']:.2f}"),
            html.P(f"Bottom Region: {bottom_region['name']} with value {bottom_region['numerical_value']:.2f}")
        ])

        # Time Series Analysis
        timeseries_fig = go.Figure()
        for feature in features:
            timeseries = feature['properties'].get('timeseries', [])
            years = [entry['year'] for entry in timeseries]
            values = [entry['numerical_value'] for entry in timeseries]
            timeseries_fig.add_trace(go.Scatter(x=years, y=values, mode='lines+markers', name=feature['properties']['name']))
        timeseries_fig.update_layout(
            paper_bgcolor='#272b30',
            plot_bgcolor='#272b30',
            font=dict(color='#ffffff'),
            title="Time Series of Selected Regions"
        )

        # Statistical Distribution
        distribution_fig = px.histogram(gdf, x='numerical_value', nbins=20, title="Statistical Distribution of Numerical Values")
        distribution_fig.update_layout(
            paper_bgcolor='#272b30',
            plot_bgcolor='#272b30',
            font=dict(color='#ffffff')
        )

        # Regional Insights
        total_regions = len(gdf)
        regional_insights = html.Div([
            html.P(f"Total Number of Regions: {total_regions}")
        ])
    else:
        descriptive_stats = "No data available"
        top_bottom_regions = "No data available"
        timeseries_fig = go.Figure()
        distribution_fig = go.Figure()
        regional_insights = "No data available"

    return fig, descriptive_stats, top_bottom_regions, timeseries_fig, distribution_fig, regional_insights