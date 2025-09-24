"""
Table Generation Module
Contains all table visualization functions for measles data
"""

import plotly.graph_objects as go
import pandas as pd
from chart_styles import *

def create_table_base(headers, data, title=None):
    """
    Create a base table with consistent styling
    
    Args:
        headers (list): List of header strings
        data (list): List of data columns
        title (str): Optional table title
        
    Returns:
        go.Figure: Plotly table figure
    """
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[f'<b>{header}</b>' for header in headers],
            font=dict(size=12, family=FONT_FAMILY, color="black"),
            fill_color='#D0D0D0',
            align='left'
        ),
        cells=dict(
            values=data,
            font=dict(size=12, family=FONT_FAMILY, color="black"),
            fill_color=[['#FAFAFA', '#FFFFFF'] * len(data[0])],
            align='left'
        )
    )])

    fig.update_layout(
        title=title,
        font=dict(family=FONT_FAMILY, size=12),
        autosize=True,
        margin=dict(l=20, r=20, t=20, b=100)
    )

    add_footer_annotation(fig)
    return fig

def create_timeline_table(timeline_data):
    """
    Create table showing historical timeline data
    
    Args:
        timeline_data (pd.DataFrame): Timeline data with Year, Cases, Highlight columns
        
    Returns:
        go.Figure: Plotly table figure
    """
    df = timeline_data[['Year', 'Cases', 'Highlight']].copy()
    df['Highlight'] = df['Highlight'].fillna('')

    headers = ['Year', 'Confirmed Measles Cases', 'Measles Historical Highlight']
    data = [
        df['Year'],
        df['Cases'].apply(lambda x: format_number(x, 'comma')),
        df['Highlight']
    ]

    return create_table_base(headers, data)

def create_recent_trends_table(usmeasles_data, mmr_data):
    """
    Create table showing recent trends data
    
    Args:
        usmeasles_data (pd.DataFrame): US measles data
        mmr_data (pd.DataFrame): MMR coverage data
        
    Returns:
        go.Figure: Plotly table figure
    """
    # Prepare data
    us_data = usmeasles_data[['year', 'cases']].copy()
    us_data['Location'] = 'United States'
    us_data = us_data.drop_duplicates(subset=['year'])

    # Merge with MMR data
    if not mmr_data.empty:
        mmr_clean = mmr_data[['year', 'Location', 'MMR']].copy()
        mmr_clean = mmr_clean.drop_duplicates(subset=['year', 'Location'])
        merged_data = pd.merge(us_data, mmr_clean, on=['year', 'Location'], how='left')
    else:
        merged_data = us_data.copy()
        merged_data['MMR'] = None

    # Filter and clean
    merged_data = merged_data[merged_data['year'] > 2014].copy()
    merged_data = merged_data.sort_values('year').reset_index(drop=True)

    # Convert to numeric
    for col in ['year', 'cases', 'MMR']:
        if col in merged_data.columns:
            merged_data[col] = pd.to_numeric(merged_data[col], errors='coerce')

    merged_data = merged_data.dropna(subset=['year', 'cases'])

    headers = ['Year', 'Confirmed Measles Cases', 'MMR Vaccination Coverage (%)']
    data = [
        merged_data['year'],
        merged_data['cases'].apply(lambda x: format_number(x, 'comma')),
        merged_data['MMR'].apply(lambda x: format_number(x, 'percent') if pd.notna(x) else '')
    ]

    return create_table_base(headers, data)

def create_rnaught_table():
    """
    Create table showing R0 values for different diseases
    
    Returns:
        go.Figure: Plotly table figure
    """
    diseases_data = {
        'Disease': ['Ebola', 'HIV', 'COVID-19 (Omicron)', 'Chickenpox', 'Mumps', 'Measles'],
        'R0': [2, 4, 9.5, 12, 14, 18]
    }
    df = pd.DataFrame(diseases_data)

    headers = ['Disease', 'R0 (Basic Reproduction Number)<br><i>(Avg. people infected by one case)</i>']
    data = [
        df['Disease'],
        df['R0']
    ]

    return create_table_base(headers, data)

def create_state_map_table(usmap_data):
    """
    Create table showing state-level map data
    
    Args:
        usmap_data (pd.DataFrame): State map data
        
    Returns:
        go.Figure: Plotly table figure
    """
    df = usmap_data.copy()

    # Find cases column
    cases_col = next((c for c in ['cases_calendar_year', 'cases', 'Cases'] if c in df.columns), None)
    
    if cases_col is None:
        return go.Figure()

    # Calculate derived fields
    df['population'] = df['geography'].map(STATE_POPULATIONS)
    df['state_code'] = df['geography'].map(STATE_ABBREVIATIONS)
    df['case_rate'] = (df[cases_col] / df['population'] * 100000).round(2).fillna(0)
    df['Estimate (%)'] = pd.to_numeric(df['Estimate (%)'], errors='coerce')

    # Apply classification
    classification_results = df.apply(
        lambda row: classify_bivariate(row['case_rate'], row['Estimate (%)']), axis=1
    )

    df['category_label'] = [result[2] for result in classification_results]

    headers = [
        'State', 'Abbr.', 'Total Measles Cases', 'Population', 
        'Measles Case Rate (per 100K)', 'MMR Vaccination Coverage (%)', 'Classification'
    ]
    
    data = [
        df['geography'],
        df['state_code'],
        df[cases_col].apply(lambda x: format_number(x, 'comma') if pd.notna(x) else ''),
        df['population'].apply(lambda x: format_number(x, 'comma') if pd.notna(x) else ''),
        df['case_rate'],
        df['Estimate (%)'].apply(lambda x: format_number(x, 'percent') if pd.notna(x) else ''),
        df['category_label']
    ]

    return create_table_base(headers, data)

def create_lives_saved_table(vaccine_impact_data):
    """
    Create table showing lives saved by vaccination
    
    Args:
        vaccine_impact_data (pd.DataFrame): Vaccine impact data
        
    Returns:
        go.Figure: Plotly table figure
    """
    df = vaccine_impact_data.copy()

    # Find required columns
    lives_saved_col = None
    for col in ['lives_saved', 'Lives_Saved', 'deaths_prevented', 'deaths_averted']:
        if col in df.columns:
            lives_saved_col = col
            break

    year_col = None
    for col in ['year', 'Year', 'calendar_year']:
        if col in df.columns:
            year_col = col
            break

    if lives_saved_col is None or year_col is None:
        return go.Figure()

    # Select and rename columns
    df_clean = df[[year_col, lives_saved_col]].copy()
    df_clean = df_clean.rename(columns={
        year_col: 'Year',
        lives_saved_col: 'Estimated Lives Saved'
    })

    headers = ['Year', 'Estimated Lives Saved']
    data = [
        df_clean['Year'],
        df_clean['Estimated Lives Saved'].apply(lambda x: format_number(x, 'comma'))
    ]

    return create_table_base(headers, data)
