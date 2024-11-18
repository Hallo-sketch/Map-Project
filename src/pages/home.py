# pages/home.py

import dash
import os
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import plotly.subplots as sp
from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd
from datetime import datetime
import dash_bootstrap_components as dbc
import numpy as np

def load_and_process_data():
    """Load and process cocoa production and price data"""
    # Get data directory path
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

    try:
        # Read production data
        cocoa_df = pd.read_csv(os.path.join(DATA_DIR, 'cocoa-data.csv'))

        # Read and parse futures data
        futures_df = pd.read_csv(os.path.join(DATA_DIR, 'Daily Prices.csv'))
        futures_df['Date'] = pd.to_datetime(futures_df['Date'], format='%d/%m/%Y')

        # Create consistent date range
        dates_range = pd.date_range(
            start=pd.Timestamp('2013-01-01'),
            end=pd.Timestamp('2023-12-31'),
            freq='D'
        )

        # Map production and estimates to daily data
        production_dict = dict(zip(cocoa_df['season'], cocoa_df['production']))
        estimates_dict = dict(zip(cocoa_df['season'], cocoa_df['estimates']))

        daily_production = pd.DataFrame({
            'date': dates_range,
            'production': [production_dict.get(year, None) for year in dates_range.year],
            'estimates': [estimates_dict.get(year, None) for year in dates_range.year]
        })

        # Filter and clean futures data
        futures_df = futures_df[futures_df['Date'].isin(dates_range)]
        price_columns = [
            'London futures (£ sterling/tonne)',
            'New York futures (US$/tonne)',
            'ICCO daily price (US$/tonne)'
        ]
        
        for col in price_columns:
            futures_df[col] = pd.to_numeric(
                futures_df[col].astype(str).str.replace(',', ''),
                errors='coerce'
            )

        return cocoa_df, futures_df, daily_production

    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None, None, None

# Register the page
dash.register_page(__name__, path='/')

# Update the container style
# Container style configurations
CONTAINER_STYLE = {
    'maxWidth': '2000px',      # Maximum width for very large screens
    'minWidth': '320px',       # Minimum width for mobile screens
    'margin': 'auto',
    'color': '#ffffff',        # Text color for dark aesthetic
    'marginTop': '56px',       # Add margin to account for fixed navbar
    'paddingTop': '20px'       # Additional padding for spacing
}

# Update the card style
CARD_STYLE = {
    'height': '100%',
    'minHeight': '200px',
    'backgroundColor': '#32383e',
    'color': '#ffffff',
    'borderColor': '#444444'
}

# Adjusted graph card style
GRAPH_CARD_STYLE = {
    'height': 'calc(100% + 0px)',
    'minHeight': '400px',
    'backgroundColor': '#32383e',
    'color': '#ffffff',
    'borderColor': '#444444'
}

layout = dbc.Container([
    # Header Section
    dbc.Row([
        dbc.Col(
            html.H1('Cocoa Production and Price Analysis', 
                   className='text-center text-primary my-4',
                   style={'fontSize': 'calc(1.5rem + 1.5vw)'}),  # Responsive font size
            width=12
        )
    ]),

    # Description
    dbc.Row([
        dbc.Col([
            html.P('This dashboard shows the relationship between cocoa production and market prices.',
                  className='text-center mb-4',
                  style={'fontSize': 'calc(0.9rem + 0.5vw)'})  # Responsive font size
        ], width=12)
    ]),

    # Main Graph Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        id='cocoa-production-price-graph',
                        style={'height': '100%'}
                    )
                ])
            ], style=GRAPH_CARD_STYLE)
        ], width=12, className='mb-4')
    ]),

    # Statistical Analysis Section
    dbc.Row([
        dbc.Col([
            html.H3("Statistical Analysis", 
                   className="text-center my-4",
                   style={'fontSize': 'calc(1.2rem + 1vw)'})
        ], width=12)
    ]),
    
    dbc.Row([
        # Correlation Analysis Card
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    "Correlation Analysis",
                    style={'fontSize': 'calc(0.9rem + 0.4vw)'}
                ),
                dbc.CardBody(
                    id='correlation-analysis',
                    style={'fontSize': 'calc(0.8rem + 0.3vw)'}
                )
            ], style=CARD_STYLE)
        ], width=12, lg=4, className='mb-4'),

        # Production Analysis Card
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    "Production Analysis",
                    style={'fontSize': 'calc(0.9rem + 0.4vw)'}
                ),
                dbc.CardBody(
                    id='production-analysis',
                    style={'fontSize': 'calc(0.8rem + 0.3vw)'}
                )
            ], style=CARD_STYLE)
        ], width=12, lg=4, className='mb-4'),

        # Price Analysis Card
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    "Price Analysis",
                    style={'fontSize': 'calc(0.9rem + 0.4vw)'}
                ),
                dbc.CardBody(
                    id='price-analysis',
                    style={'fontSize': 'calc(0.8rem + 0.3vw)'}
                )
            ], style=CARD_STYLE)
        ], width=12, lg=4, className='mb-4')
    ]),

    # Seasonal Decomposition Section
    dbc.Row([
        # Left Column: Graph
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    "Seasonal Decomposition Analysis",
                    style={'fontSize': 'calc(0.9rem + 0.4vw)'}
                ),
                dbc.CardBody([
                    dcc.Graph(
                        id='seasonal-decomposition-graph',
                        style={'height': '100%'}
                    )
                ], style={'height': '100%'})
            ], style={'height': '100%'})
        ], width=12, lg=8, className='mb-4', style={'height': '100%'}),

        # Right Column: Selector, Findings, and New Graph
        dbc.Col([
            # Price Selector
            dbc.Card([
                dbc.CardBody([
                    html.Label("Select Price Series:",
                             style={'fontSize': 'calc(0.9rem + 0.4vw)'}),
                    dcc.Dropdown(
                        id='price-selector',
                        options=[
                            {'label': 'ICCO Daily Price', 'value': 'icco'},
                            {'label': 'London Futures', 'value': 'london'},
                            {'label': 'New York Futures', 'value': 'ny'}
                        ],
                        value='icco',
                        className='mb-3',
                        style={'fontSize': 'calc(0.8rem + 0.3vw)'}
                    )
                ])
            ], className="mb-4"),

            # Findings (cards)
            html.Div(
                id='seasonal-findings',
                style={'fontSize': 'calc(0.8rem + 0.3vw)'}
            ),

            # New Graph: Price Scatter Plot with KDE
            dbc.Card([
                dbc.CardHeader(
                    "Price Scatter Plot with KDE",
                    style={'fontSize': 'calc(0.9rem + 0.4vw)'}
                ),
                dbc.CardBody([
                    dcc.Graph(
                        id='price-scatter-kde',
                        style={'height': '400px'}
                    )
                ])
            ], className="mb-4")
        ], width=12, lg=4, className='mb-4', style={'height': '100%'})
    ], className="mb-4", style={'height': '100%'}),

    # Navigation Buttons
    dbc.Row([
        dbc.Col([
            dbc.Button(
                'Cóte d\'Ivoire GeoSpatial data',
                href='/page1',
                color='primary',
                className='me-2',
                style={'fontSize': 'calc(0.8rem + 0.3vw)'}
            ),
            dbc.Button(
                'Market Analysis',
                href='/page2',
                color='secondary',
                style={'fontSize': 'calc(0.8rem + 0.3vw)'}
            )
        ], width='auto')
    ], justify='center', className='mt-4 mb-5')

], fluid=True, style=CONTAINER_STYLE)

# Load data
cocoa_df, futures_df, daily_production = load_and_process_data()

# Graph style configurations
GRAPH_STYLE = {
    'font': {
        'size': 12,  # Base font size
        'family': 'Arial, sans-serif'
    },
    'line_width': 2,
    'grid_width': 1,
    'marker_size': 6,
    'title_size': 20,
    'axis_title_size': 14,
    'legend_font_size': 12
}

# Color scheme
COLORS = {
    'production': '#1f77b4',
    'estimates': '#2ca02c',
    'london': '#ff7f0e',
    'ny': '#d62728',
    'icco': '#9467bd',
    'grid': 'rgba(255, 255, 255, 0.1)',  # Lighter grid lines
    'background': '#272b30'
}

# Callback for the main cocoa production and price graph
@callback(
    Output('cocoa-production-price-graph', 'figure'),
    Input('cocoa-production-price-graph', 'id')
)
def update_cocoa_graph(_):
    # Create figure with secondary y-axis
    fig = go.Figure()

    # Add production traces
    fig.add_trace(
        go.Scatter(
            x=daily_production['date'],
            y=daily_production['production'],
            name='Actual Production',
            yaxis='y1',
            line=dict(
                color=COLORS['production'],
                width=GRAPH_STYLE['line_width']
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=daily_production['date'],
            y=daily_production['estimates'],
            name='Projected Production',
            yaxis='y1',
            line=dict(
                color=COLORS['estimates'],
                width=GRAPH_STYLE['line_width'],
                dash='dash'
            )
        )
    )

    # Add price traces
    fig.add_trace(
        go.Scatter(
            x=futures_df['Date'],
            y=futures_df['London futures (£ sterling/tonne)'],
            name='London Futures',
            yaxis='y2',
            line=dict(
                color=COLORS['london'],
                width=GRAPH_STYLE['line_width']
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=futures_df['Date'],
            y=futures_df['New York futures (US$/tonne)'],
            name='NY Futures',
            yaxis='y2',
            line=dict(
                color=COLORS['ny'],
                width=GRAPH_STYLE['line_width']
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=futures_df['Date'],
            y=futures_df['ICCO daily price (US$/tonne)'],
            name='ICCO Daily Price',
            yaxis='y2',
            line=dict(
                color=COLORS['icco'],
                width=GRAPH_STYLE['line_width']
            )
        )
    )

    # Update layout with responsive sizing
    fig.update_layout(
    title={
        'text': 'Cocoa Production and Price Analysis',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {
            'size': GRAPH_STYLE['title_size']
        }
    },
    xaxis=dict(
        title='Date',
        rangeslider=dict(visible=True),
        type='date',
        gridcolor=COLORS['grid'],
        gridwidth=GRAPH_STYLE['grid_width'],
        title_font=dict(size=GRAPH_STYLE['axis_title_size'])
    ),
    yaxis=dict(
        title='Production Volume (thousand tonnes)',
        side='left',
        showgrid=True,
        gridcolor=COLORS['grid'],
        gridwidth=GRAPH_STYLE['grid_width'],
        title_font=dict(size=GRAPH_STYLE['axis_title_size'])
    ),
    yaxis2=dict(
        title='Price (US$/tonne, £/tonne)',
        side='right',
        overlaying='y',
        showgrid=False,
        title_font=dict(size=GRAPH_STYLE['axis_title_size'])
    ),
    hovermode='x unified',
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        font=dict(
            size=GRAPH_STYLE['legend_font_size'],
            color='white'
        ),
        bgcolor='rgba(50, 50, 50, 0.9)',
        bordercolor='rgba(255, 255, 255, 0.3)'
    ),
    hoverlabel=dict(
        bgcolor='rgba(50, 50, 50, 0.9)',
        bordercolor='rgba(255, 255, 255, 0.3)',
        font=dict(
            size=GRAPH_STYLE['legend_font_size'],
            color='white'
        )
    ),
    template='plotly_dark',
    paper_bgcolor=COLORS['background'],
    font=dict(color='#ffffff'),
    margin=dict(l=50, r=50, t=80, b=50),  # Responsive margins
    height=650,  # Base height
    autosize=True,  # Allow responsive resizing
    plot_bgcolor=COLORS['background']
    )

    return fig

# Style configurations for statistical analysis
STAT_STYLES = {
    'container': {
        'padding': '0.5rem',
        'height': '100%'
    },
    'stat_item': {
        'marginBottom': 'calc(0.5rem + 0.5vh)',
        'fontSize': 'calc(0.8rem + 0.3vw)'
    },
    'stat_value': {
        'fontSize': 'calc(0.9rem + 0.4vw)',
        'fontWeight': 'bold'
    },
    'label': {
        'fontSize': 'calc(0.8rem + 0.3vw)',
        'color': '#666'
    }
}

def create_stat_item(label, value, additional_class=""):
    """Create a styled statistic item"""
    return html.P(
        [
            html.Span(f"{label}: ", style=STAT_STYLES['label']),
            html.Strong(value, style=STAT_STYLES['stat_value'])
        ],
        style=STAT_STYLES['stat_item'],
        className=additional_class
    )

# Callbacks for statistical analysis
@callback(
    Output('correlation-analysis', 'children'),
    Input('cocoa-production-price-graph', 'id')
)
def update_correlation_analysis(_):
    # Merge production and price data
    merged_df = pd.merge_asof(
        futures_df.sort_values('Date'),
        daily_production.rename(columns={'date': 'Date'}).sort_values('Date'),
        on='Date',
        direction='nearest'
    )
    
    # Calculate correlations
    correlations = {
        'Production vs ICCO Price': merged_df['production'].corr(
            merged_df['ICCO daily price (US$/tonne)']
        ),
        'Production vs London': merged_df['production'].corr(
            merged_df['London futures (£ sterling/tonne)']
        ),
        'Production vs NY': merged_df['production'].corr(
            merged_df['New York futures (US$/tonne)']
        )
    }
    
    return html.Div([
        create_stat_item(k, f"{v:.2f}")
        for k, v in correlations.items()
    ], style=STAT_STYLES['container'])

@callback(
    Output('production-analysis', 'children'),
    Input('cocoa-production-price-graph', 'id')
)
def update_production_analysis(_):
    # Calculate production statistics
    production_stats = {
        'Average Production': {
            'value': cocoa_df['production'].mean(),
            'format': '{:,.0f} tonnes'
        },
        'Growth Rate': {
            'value': (cocoa_df['production'].pct_change() * 100).mean(),
            'format': '{:.1f}%'
        },
        'Estimate Accuracy': {
            'value': (abs(cocoa_df['production'] - cocoa_df['estimates']) 
                     / cocoa_df['estimates'] * 100).mean(),
            'format': '{:.1f}%'
        }
    }
    
    return html.Div([
        create_stat_item(
            label,
            stats['format'].format(stats['value'])
        )
        for label, stats in production_stats.items()
    ], style=STAT_STYLES['container'])

@callback(
    Output('price-analysis', 'children'),
    Input('cocoa-production-price-graph', 'id')
)
def update_price_analysis(_):
    # Calculate price statistics
    price_stats = {
        'Average ICCO Price': {
            'value': futures_df['ICCO daily price (US$/tonne)'].mean(),
            'format': '${:,.0f}'
        },
        'Price Volatility': {
            'value': (futures_df['ICCO daily price (US$/tonne)'].std() / 
                     futures_df['ICCO daily price (US$/tonne)'].mean() * 100),
            'format': '{:.1f}%'
        },
        'London-NY Spread': {
            'value': (futures_df['London futures (£ sterling/tonne)'] - 
                     futures_df['New York futures (US$/tonne)']).mean(),
            'format': '${:,.0f}'
        }
    }
    
    return html.Div([
        create_stat_item(
            label,
            stats['format'].format(stats['value'])
        )
        for label, stats in price_stats.items()
    ], style=STAT_STYLES['container'])

# Style configurations for decomposition analysis
DECOMP_STYLES = {
    'graph': {
        'height': '100%',  # Adjusted height to fill the container
        'min_height': '600px',
        'font_size': 'calc(0.8rem + 0.3vw)',
        'line_width': 2,
        'grid_width': 1,
        'colors': {
            'original': '#1f77b4',
            'trend': '#2ca02c',
            'seasonal': '#ff7f0e',
            'residual': '#d62728',
            'kde': '#9467bd',
            'grid': 'rgba(204, 204, 204, 0.2)'
        }
    },
    'card': {
        'title': {
            'fontSize': 16,  # Numerical value
            'fontWeight': 'bold',
            'marginBottom': '1rem'
        },
        'body': {
            'fontSize': 14,  # Numerical value
            'padding': '1rem'
        },
        'stat': {
            'label': {
                'fontSize': 14,  # Numerical value
                'color': '#666'
            },
            'value': {
                'fontSize': 16,  # Numerical value
                'fontWeight': 'bold'
            },
            'description': {
                'fontSize': 12,  # Numerical value
                'color': '#888',
                'marginTop': '0.25rem'
            }
        }
    }
}

# Price mappings
PRICE_MAPPINGS = {
    'icco': {
        'column': 'ICCO daily price (US$/tonne)',
        'name': 'ICCO Daily Price',
        'currency': '$'
    },
    'london': {
        'column': 'London futures (£ sterling/tonne)',
        'name': 'London Futures',
        'currency': '£'
    },
    'ny': {
        'column': 'New York futures (US$/tonne)',
        'name': 'New York Futures',
        'currency': '$'
    }
}

# Callback for Seasonal Decomposition and Findings
@callback(
    [Output('seasonal-decomposition-graph', 'figure'),
     Output('seasonal-findings', 'children')],
    [Input('price-selector', 'value')]
)
def update_seasonal_analysis(selected_price):
    price_info = PRICE_MAPPINGS[selected_price]
    
    # Prepare monthly price data
    monthly_price = futures_df.set_index('Date')[price_info['column']].resample('M').mean()
    
    # Create decomposition figure
    fig = create_decomposition_figure(monthly_price, price_info)
    
    # Calculate statistics and create findings component
    findings = create_findings_component(monthly_price, price_info)
    
    return fig, findings

def create_decomposition_figure(monthly_price, price_info):
    """Create the seasonal decomposition figure with responsive sizing"""
    # Perform decomposition
    decomposition = seasonal_decompose(
        monthly_price.dropna(), 
        period=12,
        extrapolate_trend=True
    )
    
    # Create subplots with responsive spacing
    fig = sp.make_subplots(
        rows=4, cols=1,
        subplot_titles=(
            'Original Price Series',
            'Trend Component',
            'Seasonal Component',
            'Residual Component'
        ),
        vertical_spacing=0.08,
        shared_xaxes=True
    )
    
    # Add components with consistent styling
    components = [
        (monthly_price, 'Original', DECOMP_STYLES['graph']['colors']['original']),
        (decomposition.trend, 'Trend', DECOMP_STYLES['graph']['colors']['trend']),
        (decomposition.seasonal, 'Seasonal', DECOMP_STYLES['graph']['colors']['seasonal']),
        (decomposition.resid, 'Residual', DECOMP_STYLES['graph']['colors']['residual'])
    ]
    
    for i, (data, name, color) in enumerate(components, 1):
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data.values,
                name=name,
                line=dict(
                    color=color,
                    width=DECOMP_STYLES['graph']['line_width']
                )
            ),
            row=i, col=1
        )
    
    # Update layout with responsive sizing
    fig.update_layout(
        height=1000,  # Adjusted height to match the right column
        title={
            'text': f'Seasonal Decomposition of {price_info["name"]}',
            'y': 0.97,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': DECOMP_STYLES['card']['title']['fontSize']}
        },
        showlegend=True,
                template='plotly_dark',
        paper_bgcolor=COLORS['background'],
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50),  # Responsive margins
        font=dict(size=12, color='#ffffff')  # Base font size
    )
    
    # Update axes with responsive styling
    titles = [
        f'Price ({price_info["currency"]}/tonne)',
        'Trend Value',
        'Seasonal Effect',
        'Residual'
    ]
    
    for i, title in enumerate(titles, 1):
        fig.update_yaxes(
            title_text=title,
            title_font={'size': 14},  # Slightly larger than base font
            showgrid=True,
            gridwidth=DECOMP_STYLES['graph']['grid_width'],
            gridcolor=DECOMP_STYLES['graph']['colors']['grid'],
            row=i, col=1
        )
        
        fig.update_xaxes(
            showgrid=True,
            gridwidth=DECOMP_STYLES['graph']['grid_width'],
            gridcolor=DECOMP_STYLES['graph']['colors']['grid'],
            row=i, col=1
        )
    
    return fig

def create_findings_component(monthly_price, price_info):
    """Create the findings component with cards stacked vertically"""
    decomposition = seasonal_decompose(
        monthly_price.dropna(),
        period=12,
        extrapolate_trend=True
    )
    
    # Calculate statistics
    stats = calculate_statistics(monthly_price, decomposition, price_info)
    
    return html.Div([
        create_stats_card(
            "Seasonal Pattern Analysis",
            stats['seasonal']
        ),
        html.Br(),  # Add space between the cards
        create_stats_card(
            "Price Series Statistics",
            stats['price']
        )
    ])

def calculate_statistics(monthly_price, decomposition, price_info):
    """Calculate all statistics with proper formatting"""
    seasonal_monthly = decomposition.seasonal.groupby(
        decomposition.seasonal.index.month
    ).mean()
    
    return {
        'seasonal': {
            'Seasonal Strength': {
                'value': f"{(decomposition.seasonal.std() / monthly_price.std()) * 100:.1f}%",
                'description': "Percentage of price variation explained by seasonal patterns"
            },
            'Peak Month': {
                'value': datetime.strptime(str(seasonal_monthly.idxmax()), '%m').strftime('%B'),
                'description': f"Average effect: {price_info['currency']}{abs(seasonal_monthly.max()):,.0f}"
            },
            'Lowest Month': {
                'value': datetime.strptime(str(seasonal_monthly.idxmin()), '%m').strftime('%B'),
                'description': f"Average effect: {price_info['currency']}{abs(seasonal_monthly.min()):,.0f}"
            }
        },
        'price': {
            'Average Price': {
                'value': f"{price_info['currency']}{monthly_price.mean():,.0f}",
                'description': "Mean price over the entire period"
            },
            'Price Volatility': {
                'value': f"{(monthly_price.std() / monthly_price.mean()) * 100:.1f}%",
                'description': "Coefficient of variation (standardized volatility)"
            },
            'Annual Growth': {
                'value': f"{((monthly_price.iloc[-1] / monthly_price.iloc[0]) ** (12/len(monthly_price)) - 1) * 100:.1f}%",
                'description': "Compound annual growth rate"
            }
        }
    }

def create_stats_card(title, stats):
    """Create a styled statistics card with adjusted width"""
    return dbc.Card([
        dbc.CardHeader(
            title,
            style=DECOMP_STYLES['card']['title']
        ),
        dbc.CardBody([
            create_decomp_stat_item(label, data['value'], data['description'])
            for label, data in stats.items()
        ], style=DECOMP_STYLES['card']['body'])
    ], style={'marginBottom': '1rem', 'maxWidth': '100%'})

def create_decomp_stat_item(label, value, description):
    """Create a styled statistic item for decomposition analysis"""
    return html.Div([
        html.P([
            html.Span(f"{label}: ", style=DECOMP_STYLES['card']['stat']['label']),
            html.Strong(value, style=DECOMP_STYLES['card']['stat']['value'])
        ], className='mb-1'),
        html.P(
            description,
            style=DECOMP_STYLES['card']['stat']['description']
        )
    ], className='mb-3')

# Callback for Price Scatter Plot with KDE
@callback(
    Output('price-scatter-kde', 'figure'),
    Input('price-selector', 'value')
)
def update_price_scatter_kde(selected_price):
    import pandas as pd
    import plotly.graph_objects as go
    import numpy as np
    from scipy.stats import gaussian_kde

    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    # Load the price data
    price_data = pd.read_csv(os.path.join(DATA_DIR, 'Daily Prices.csv'))  # Update with your actual data file

    # Sort the DataFrame by date
    price_data_sorted = price_data.sort_values('Date')

    # Extract x and y data using the correct column names
    x = price_data_sorted['New York futures (US$/tonne)']
    y = price_data_sorted['London futures (£ sterling/tonne)']

    # Convert x and y to numeric, coercing errors to NaN
    x = pd.to_numeric(x, errors='coerce')
    y = pd.to_numeric(y, errors='coerce')

    # Remove any NaN values
    valid_idx = x.notna() & y.notna()
    x = x[valid_idx]
    y = y[valid_idx]

    # Convert to numpy arrays
    x = x.values
    y = y.values

    # Calculate point density
    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)

    # Sort the points by density
    idx = z.argsort()
    x, y, z = x[idx], y[idx], z[idx]

    # Create scatter plot
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='markers',
            name='Price Data',
            marker=dict(
                size=5,
                color=z,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Density')
            )
        )
    )

    # Update layout
    fig.update_layout(
        height=400,
        showlegend=False,
        margin=dict(l=50, r=20, t=40, b=50),
        template='plotly_dark',
        title={
            'text': 'Scatter Plot of New York vs London Futures Prices with KDE',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 14}
        },
        xaxis=dict(
            title='New York Futures Price (US$/tonne)',
            title_font={'size': 12},
            tickfont={'size': 10}
        ),
        yaxis=dict(
            title='London Futures Price (£ sterling/tonne)',
            title_font={'size': 12},
            tickfont={'size': 10}
        )
    )

    return fig
    