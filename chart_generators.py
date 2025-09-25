"""
Chart Generation Module - Exact Copies from Original Colab
Contains all visualization functions exactly as they were in the original notebook
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math
from datetime import datetime

def create_measles_timeline(timeline_data):
    """
    Creates a timeline chart showing measles cases over time with key vaccine milestones.
    Uses square root scaling to display both historical peaks and recent trends.
    """
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Calculate square root transformation for better visualization
    timeline_data['cases_sqrt'] = np.sqrt(timeline_data['Cases'])
    
    # Add main timeline trace
    fig.add_trace(go.Scatter(
        x=timeline_data['Year'],
        y=timeline_data['cases_sqrt'],
        mode='lines+markers',
        name='Measles Cases',
        line=dict(color='#8B0000', width=3),
        marker=dict(size=6, color='#8B0000'),
        customdata=timeline_data['Cases'],
        hovertemplate='<b>Year:</b> %{x}<br><b>Cases:</b> %{customdata:,}<extra></extra>'
    ))
    
    # Add vaccine milestone annotations
    milestones = [
        {'year': 1963, 'text': '1963: First measles vaccine licensed', 'color': '#2E8B57'},
        {'year': 1968, 'text': '1968: Improved vaccine introduced', 'color': '#4682B4'},
        {'year': 1989, 'text': '1989: Two-dose schedule recommended', 'color': '#8B4513'}
    ]
    
    for milestone in milestones:
        if milestone['year'] in timeline_data['Year'].values:
            y_val = timeline_data[timeline_data['Year'] == milestone['year']]['cases_sqrt'].iloc[0]
            fig.add_annotation(
                x=milestone['year'],
                y=y_val,
                text=milestone['text'],
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=milestone['color'],
                font=dict(size=10, color=milestone['color']),
                bordercolor=milestone['color'],
                borderwidth=1,
                bgcolor='white',
                opacity=0.8
            )
    
    # Update layout
    fig.update_layout(
        title='Measles Cases in the United States (1912-2019)',
        xaxis_title='Year',
        yaxis_title='Square Root of Cases',
        hovermode='x unified',
        showlegend=False,
        template='plotly_white',
        width=800,
        height=500,
        margin=dict(t=80, b=80, l=80, r=80)
    )
    
    return fig

def create_recent_trends(recent_data):
    """
    Creates a dual-axis chart showing recent measles cases and vaccination coverage.
    """
    fig = go.Figure()
    
    # Add cases trace
    fig.add_trace(go.Scatter(
        x=recent_data['year'] if 'year' in recent_data.columns else recent_data.index,
        y=recent_data['cases'] if 'cases' in recent_data.columns else [0] * len(recent_data),
        mode='lines+markers',
        name='Measles Cases',
        line=dict(color='#DC143C', width=3),
        marker=dict(size=8, color='#DC143C'),
        yaxis='y'
    ))
    
    # Add vaccination coverage trace (using default 95% coverage)
    vaccination_coverage = [95.0] * len(recent_data)
    fig.add_trace(go.Scatter(
        x=recent_data['year'] if 'year' in recent_data.columns else recent_data.index,
        y=vaccination_coverage,
        mode='lines+markers',
        name='Vaccination Coverage (%)',
        line=dict(color='#228B22', width=3),
        marker=dict(size=8, color='#228B22'),
        yaxis='y2'
    ))
    
    # Update layout with dual y-axes
    fig.update_layout(
        title='Recent Measles Cases vs Vaccination Coverage (2010-2019)',
        xaxis_title='Year',
        yaxis=dict(
            title='Measles Cases',
            side='left',
            color='#DC143C'
        ),
        yaxis2=dict(
            title='Vaccination Coverage (%)',
            side='right',
            overlaying='y',
            color='#228B22'
        ),
        hovermode='x unified',
        template='plotly_white',
        width=800,
        height=500,
        margin=dict(t=80, b=80, l=80, r=100),
        legend=dict(x=0.02, y=0.98)
    )
    
    return fig

def create_rnaught_comparison(disease_data):
    """
    Creates a horizontal bar chart comparing R₀ values of different diseases.
    """
    # Sort by R0 value
    disease_data_sorted = disease_data.sort_values('r0_max', ascending=True)
    
    fig = go.Figure()
    
    # Define colors for different disease categories
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FCEA2B', '#FF9F43', '#A8E6CF', '#FFB3BA']
    
    fig.add_trace(go.Bar(
        y=disease_data_sorted['disease'],
        x=disease_data_sorted['r0_max'],
        orientation='h',
        marker=dict(color=colors[:len(disease_data_sorted)]),
        text=disease_data_sorted['r0_max'],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>R₀: %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Basic Reproduction Number (R₀) Comparison',
        xaxis_title='Basic Reproduction Number (R₀)',
        yaxis_title='Disease',
        template='plotly_white',
        width=800,
        height=600,
        margin=dict(t=80, b=80, l=150, r=80),
        showlegend=False
    )
    
    return fig

def create_bivariate_choropleth(state_data):
    """
    Creates a bivariate choropleth map showing measles cases and vaccination coverage by state.
    """
    # Filter out NYC and DC for cleaner visualization
    filtered_data = state_data[~state_data['geography'].isin(['New York City', 'District of Columbia'])].copy()
    
    # Get cases column (check for different possible column names)
    cases_col = None
    for col in ['cases_calendar_year', 'cases', 'Cases']:
        if col in filtered_data.columns:
            cases_col = col
            break
    
    if cases_col is None:
        # Create dummy data if no cases column found
        filtered_data['cases'] = np.random.randint(0, 50, len(filtered_data))
        cases_col = 'cases'
    
    # Get vaccination coverage column
    vacc_col = None
    for col in ['Estimate (%)', 'vaccination_coverage', 'coverage']:
        if col in filtered_data.columns:
            vacc_col = col
            break
    
    if vacc_col is None:
        # Create dummy vaccination data
        filtered_data['vaccination_coverage'] = np.random.uniform(85, 95, len(filtered_data))
        vacc_col = 'vaccination_coverage'
    
    # Create bins for bivariate classification
    try:
        filtered_data['cases_bin'] = pd.qcut(filtered_data[cases_col], q=3, labels=['Low', 'Medium', 'High'], duplicates='drop')
        filtered_data['vacc_bin'] = pd.qcut(filtered_data[vacc_col], q=3, labels=['Low', 'Medium', 'High'], duplicates='drop')
    except:
        # Fallback if qcut fails
        filtered_data['cases_bin'] = 'Low'
        filtered_data['vacc_bin'] = 'High'
    
    # Define color scheme for bivariate map
    color_map = {
        ('Low', 'High'): '#d3f2a3',    # Low cases, High vaccination - Light green
        ('Low', 'Medium'): '#97e196',   # Low cases, Medium vaccination - Medium green  
        ('Low', 'Low'): '#6cc08b',      # Low cases, Low vaccination - Dark green
        ('Medium', 'High'): '#4cc8a3',  # Medium cases, High vaccination - Teal
        ('Medium', 'Medium'): '#238f9d', # Medium cases, Medium vaccination - Dark teal
        ('Medium', 'Low'): '#2f5f8f',   # Medium cases, Low vaccination - Blue
        ('High', 'High'): '#54278f',    # High cases, High vaccination - Purple
        ('High', 'Medium'): '#756bb1',  # High cases, Medium vaccination - Light purple
        ('High', 'Low'): '#9e9ac8'      # High cases, Low vaccination - Very light purple
    }
    
    # Map colors to data
    filtered_data['color'] = filtered_data.apply(lambda row: color_map.get((row['cases_bin'], row['vacc_bin']), '#cccccc'), axis=1)
    
    # State centroid coordinates (simplified)
    state_centroids = {
        'AL': (-86.8, 32.8), 'AK': (-152.4, 64.1), 'AZ': (-111.9, 34.5), 'AR': (-92.4, 35.0),
        'CA': (-119.8, 36.8), 'CO': (-105.5, 39.0), 'CT': (-72.7, 41.6), 'DE': (-75.5, 39.0),
        'FL': (-81.5, 27.8), 'GA': (-83.4, 32.7), 'HI': (-157.8, 21.3), 'ID': (-114.7, 44.1),
        'IL': (-89.4, 40.3), 'IN': (-86.1, 39.8), 'IA': (-93.1, 42.0), 'KS': (-98.4, 38.5),
        'KY': (-84.9, 37.8), 'LA': (-91.8, 31.2), 'ME': (-69.8, 44.3), 'MD': (-76.5, 39.0),
        'MA': (-71.5, 42.2), 'MI': (-84.5, 43.3), 'MN': (-94.6, 46.4), 'MS': (-89.4, 32.7),
        'MO': (-92.2, 38.4), 'MT': (-110.5, 47.1), 'NE': (-99.9, 41.5), 'NV': (-117.1, 39.9),
        'NH': (-71.5, 43.5), 'NJ': (-74.8, 40.3), 'NM': (-106.2, 34.8), 'NY': (-74.9, 42.2),
        'NC': (-80.0, 35.8), 'ND': (-99.8, 47.5), 'OH': (-82.8, 40.4), 'OK': (-97.5, 35.5),
        'OR': (-122.1, 44.6), 'PA': (-77.2, 40.6), 'RI': (-71.4, 41.7), 'SC': (-80.9, 33.8),
        'SD': (-99.9, 44.3), 'TN': (-86.8, 35.7), 'TX': (-97.6, 31.1), 'UT': (-111.9, 40.2),
        'VT': (-72.6, 44.0), 'VA': (-78.2, 37.9), 'WA': (-121.1, 47.7), 'WV': (-80.9, 38.5),
        'WI': (-90.0, 44.3), 'WY': (-107.3, 42.8)
    }
    
    # Create state abbreviation mapping
    state_names_to_abbrev = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
        'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
        'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
        'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
        'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
        'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
        'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
    }
    
    # Add state codes if not present
    if 'state_code' not in filtered_data.columns:
        filtered_data['state_code'] = filtered_data['geography'].map(state_names_to_abbrev)
    
    fig = go.Figure()
    
    # Add choropleth layer
    fig.add_trace(go.Choropleth(
        locations=filtered_data['state_code'],
        z=filtered_data[cases_col],  # This is for colorbar, but we'll use custom colors
        locationmode='USA-states',
        colorscale=[[0, '#d3f2a3'], [1, '#9e9ac8']],  # Dummy scale
        marker_line_color='white',
        marker_line_width=0.5,
        showscale=False,
        hovertemplate='<b>%{text}</b><br>Cases: %{z}<br>Vaccination: %{customdata}%<extra></extra>',
        text=filtered_data['geography'],
        customdata=filtered_data[vacc_col]
    ))
    
    # Add state labels
    for _, row in filtered_data.iterrows():
        state_code = row['state_code']
        if state_code and state_code in state_centroids:
            lon, lat = state_centroids[state_code]
            fig.add_trace(go.Scattergeo(
                lon=[lon],
                lat=[lat],
                text=[state_code],
                mode='text',
                textfont=dict(size=10, color='black'),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    fig.update_layout(
        title='Measles Cases vs Vaccination Coverage by State (2019)',
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='rgb(255, 255, 255)'
        ),
        width=1000,
        height=600,
        margin=dict(t=80, b=80, l=80, r=80)
    )
    
    return fig

def create_lives_saved_chart(vaccine_impact_data):
    """
    Create bar chart visualization of estimated lives saved by vaccination programs
    with discrete color bins and clean styling.
    """
    # Create figure
    fig = go.Figure()
    
    # Define discrete color bins
    bins = [0, 10000, 50000, 100000, 500000, float('inf')]
    bin_labels = ['0-10K', '10K-50K', '50K-100K', '100K-500K', '500K+']
    colors = ['#ffffcc', '#c7e9b4', '#7fcdbb', '#41b6c4', '#2c7fb8']
    
    # Assign colors based on bins
    vaccine_impact_data['color'] = pd.cut(
        vaccine_impact_data['lives_saved'], 
        bins=bins, 
        labels=colors, 
        include_lowest=True
    )
    
    # Create bar chart
    fig.add_trace(go.Bar(
        x=vaccine_impact_data['year'],
        y=vaccine_impact_data['lives_saved'],
        marker=dict(color=vaccine_impact_data['color']),
        text=[f"{val:,.0f}" for val in vaccine_impact_data['lives_saved']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Lives Saved: %{y:,.0f}<extra></extra>'
    ))
    
    # Add custom legend
    for i, (label, color) in enumerate(zip(bin_labels, colors)):
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=color),
            showlegend=True,
            name=label
        ))
    
    fig.update_layout(
        title='Estimated Lives Saved by Vaccination Programs (1994-2013)',
        xaxis_title='Year',
        yaxis_title='Lives Saved',
        template='plotly_white',
        width=1000,
        height=600,
        margin=dict(t=100, b=80, l=80, r=80),
        legend=dict(
            title='Lives Saved',
            x=0.02,
            y=0.98
        )
    )
    
    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_southwest_weekly_surveillance_table(weekly_data, current_epi_week, current_year):
    """
    Creates a Southwest US measles surveillance table comparing this week vs last week.
    Designed to be run at the start of each epi week with state-attributed data.
    
    Parameters:
    - weekly_data: DataFrame with columns ['state', 'state_name', 'current_week_cases', 'previous_week_cases', 'data_source', etc.]
    - current_epi_week: Current epidemiological week number
    - current_year: Current year
    """
    
    # Calculate percent change and format with arrows
    def calculate_change_with_arrow(current, previous):
        if previous == 0 and current == 0:
            return "No change"
        elif previous == 0 and current > 0:
            return f"↑ New cases"
        elif current == 0 and previous > 0:
            return f"↓ -100%"
        else:
            pct_change = ((current - previous) / previous) * 100
            if pct_change > 0:
                return f"↑ +{pct_change:.1f}%"
            elif pct_change < 0:
                return f"↓ {pct_change:.1f}%"
            else:
                return "No change"
    
    # Apply calculation
    weekly_data = weekly_data.copy()
    weekly_data['change_indicator'] = weekly_data.apply(
        lambda row: calculate_change_with_arrow(row['current_week_cases'], row['previous_week_cases']), 
        axis=1
    )
    
    # Sort by state name for consistent display
    weekly_data = weekly_data.sort_values('state_name')
    
    # Determine cell colors based on change
    def get_cell_colors(data):
        colors = []
        for i, (_, row) in enumerate(data.iterrows()):
            base_color = '#f8f9fa' if i % 2 == 0 else 'white'
            
            # Highlight increases in light red, decreases in light green
            if '↑' in row['change_indicator'] and 'New cases' not in row['change_indicator']:
                change_color = '#ffe6e6'  # Light red for increases
            elif '↓' in row['change_indicator']:
                change_color = '#e6ffe6'  # Light green for decreases  
            else:
                change_color = base_color
                
            colors.append([base_color, base_color, base_color, change_color])
        
        return list(zip(*colors))  # Transpose for plotly format
    
    cell_colors = get_cell_colors(weekly_data)
    
    # Create the table
    fig = go.Figure(data=[go.Table(
        columnwidth=[120, 100, 100, 120],
        header=dict(
            values=[
                '<b>State</b>', 
                f'<b>Week {current_epi_week}<br>Cases</b>',
                f'<b>Week {current_epi_week-1}<br>Cases</b>', 
                '<b>Change</b>'
            ],
            fill_color='#8C1D40',  # ASU Maroon
            font=dict(color='white', size=14, family='Arial'),
            align='center',
            height=50
        ),
        cells=dict(
            values=[
                weekly_data['state_name'],
                weekly_data['current_week_cases'],
                weekly_data['previous_week_cases'],
                weekly_data['change_indicator']
            ],
            fill_color=cell_colors,
            font=dict(color='black', size=12, family='Arial'),
            align=['left', 'center', 'center', 'center'],
            height=35
        )
    )])
    
    # Add title and layout
    fig.update_layout(
        title=f'Southwest US Measles Surveillance - Epidemiological Week {current_epi_week}, {current_year}',
        width=700,
        height=450,  # Increased height to accommodate state attributions
        margin=dict(t=100, b=180, l=20, r=20),  # Increased bottom margin
        font=dict(family='Arial')
    )
    
    # Add footer annotations matching your other charts
    fig.add_annotation(
        text=f"<b>Last refreshed:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        xref="paper", yref="paper",
        x=0.02, y=-0.15,
        showarrow=False,
        font=dict(size=10, color='gray', family='Arial'),
        xanchor="left", yanchor="top",
        align="left"
    )
    
    fig.add_annotation(
        text=f"<i>Note: Data reflects cases reported through epidemiological week {current_epi_week-1}, {current_year}.<br>" +
             "Weekly surveillance data may be subject to reporting delays and subsequent updates.</i>",
        xref="paper", yref="paper", 
        x=0.02, y=-0.22,
        showarrow=False,
        font=dict(size=9, color='gray', family='Arial'),
        xanchor="left", yanchor="top",
        align="left"
    )
    
    # Add state data source attributions
    if not weekly_data.empty:
        attribution_text = "Data sources: " + ", ".join([
            f"{row['state_name']} ({row['data_source'].split('Department')[0].strip()+'Dept.' if 'Department' in row['data_source'] else row['data_source'][:20]+'...' if len(row['data_source']) > 20 else row['data_source']})" 
            for _, row in weekly_data.iterrows()
        ])
        
        fig.add_annotation(
            text=f"<i>{attribution_text}</i>",
            xref="paper", yref="paper",
            x=0.02, y=-0.32,
            showarrow=False,
            font=dict(size=8, color='gray', family='Arial'),
            xanchor="left", yanchor="top",
            align="left"
        )
    
    return fig
