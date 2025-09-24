"""
Chart Generation Module
Contains all visualization functions for measles data
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math
from chart_styles import *

def create_measles_timeline(timeline_data):
    """
    Creates a timeline chart showing measles cases over time with key vaccine milestones.
    Uses square root scaling for better visibility of both historical peaks and recent trends.
    
    Args:
        timeline_data (pd.DataFrame): DataFrame with columns 'Year', 'Cases', optional 'Highlight'
        
    Returns:
        go.Figure: Plotly figure object
    """
    df = timeline_data.copy()
    
    # Process highlight text
    df["Label_wrapped"] = df.get("Highlight", "").apply(wrap_text)
    has_highlights = df["Label_wrapped"].notna()
    df['Cases_sqrt'] = np.sqrt(df['Cases'])  # Square root scale

    fig = go.Figure()

    # Main timeline - cases over time
    fig.add_trace(go.Scatter(
        x=df["Year"],
        y=df["Cases_sqrt"],
        mode="lines",
        line=dict(color=COLORS['deep_blue'], width=4),
        hovertemplate="<b>Year:</b> %{x}<br><b>Measles Cases:</b> %{customdata:,}<extra></extra>",
        customdata=df['Cases'],
        name="Annual Measles Cases",
        showlegend=True
    ))

    # Vaccine milestones
    # 1963 - MMR vaccine licensing
    fig.add_trace(go.Scatter(
        x=[1963, 1963],
        y=[0, df['Cases_sqrt'].max()],
        mode='lines',
        line=dict(color='black', width=3, dash="solid"),
        name="MMR Vaccine Licensed (1963)",
        showlegend=True,
        hoverinfo='skip'
    ))

    # 1989 - Two MMR doses recommendation
    fig.add_trace(go.Scatter(
        x=[1989 - 0.2, 1989 - 0.2],
        y=[0, df['Cases_sqrt'].max()],
        mode='lines',
        line=dict(color='black', width=3, dash="dash"),
        name="Two MMR Doses Recommended (1989)",
        showlegend=True,
        hoverinfo='skip'
    ))

    fig.add_trace(go.Scatter(
        x=[1989 + 0.2, 1989 + 0.2],
        y=[0, df['Cases_sqrt'].max()],
        mode='lines',
        line=dict(color='black', width=3, dash="dash"),
        showlegend=False,
        hoverinfo='skip'
    ))

    # Event markers if highlights exist
    if has_highlights.any():
        highlight_data = df[has_highlights]

        # Separate Arizona events from national events
        arizona_years = [2008, 2016]
        arizona_events = highlight_data[highlight_data['Year'].isin(arizona_years)]
        national_events = highlight_data[~highlight_data['Year'].isin(arizona_years)]

        # National events - circles
        if not national_events.empty:
            fig.add_trace(go.Scatter(
                x=national_events["Year"],
                y=national_events["Cases_sqrt"],
                mode="markers",
                marker=dict(
                    size=20,
                    color=COLORS['medium_blue'],
                    symbol="circle",
                    line=dict(color=COLORS['deep_blue'], width=2)
                ),
                hovertemplate="<b>Year:</b> %{x}<br><b>Cases:</b> %{customdata:,}<br><b>Event:</b> %{text}<extra></extra>",
                customdata=national_events['Cases'],
                text=national_events['Label_wrapped'],
                name="National Events",
                showlegend=True
            ))

        # Arizona events - diamonds
        if not arizona_events.empty:
            fig.add_trace(go.Scatter(
                x=arizona_events["Year"],
                y=arizona_events["Cases_sqrt"],
                mode="markers",
                marker=dict(
                    size=20,
                    color=COLORS['orange'],
                    symbol="diamond",
                    line=dict(color=COLORS['deep_blue'], width=2)
                ),
                hovertemplate="<b>Year:</b> %{x}<br><b>Cases:</b> %{customdata:,}<br><b>Arizona Event:</b> %{text}<extra></extra>",
                customdata=arizona_events['Cases'],
                text=arizona_events['Label_wrapped'],
                name="Arizona Events",
                showlegend=True
            ))

        # Add annotations for highlighted events
        def create_annotations(data):
            annotations = []
            for _, row in data.iterrows():
                # Format case numbers
                cases = row['Cases']
                cases_text = format_number(cases, 'compact')

                # Create annotation text
                annotation_text = f"<b>{int(row['Year'])}</b><br>{cases_text} cases"

                # Add milestone context
                if row['Year'] == 1963:
                    annotation_text += "<br><i>MMR vaccine licensed</i>"
                elif row['Year'] == 1989:
                    annotation_text += "<br><i>Two MMR doses recommended</i>"

                annotations.append(dict(
                    x=row["Year"],
                    y=row["Cases_sqrt"],
                    text=annotation_text,
                    showarrow=True,
                    arrowhead=0,
                    arrowsize=0.6,
                    arrowwidth=2,
                    arrowcolor='gray',
                    ax=0,
                    ay=SPACING['annotation_offset'],
                    font=dict(
                        size=FONT_SIZES['annotation'],
                        color='black',
                        family=FONT_FAMILY
                    ),
                    align="center",
                    bgcolor="rgba(255, 255, 255, 0.95)"
                ))
            return annotations

        fig.update_layout(annotations=create_annotations(highlight_data))

    # Apply standard layout
    fig.update_layout(get_standard_layout())
    fig.update_layout(title=None, showlegend=True)

    # Configure axes
    fig.update_xaxes(get_axis_config("Year"))
    fig.update_xaxes(dtick=5)
    
    fig.update_yaxes(
        title=" ",  # Hidden since using square root scale
        showgrid=False,
        showticklabels=False,
        showline=False
    )

    # Add footer
    add_footer_annotation(fig, "Chart uses square-root scale to show both historical peaks and recent trends")

    return fig


def create_recent_trends(usmeasles_data, mmr_data):
    """
    Creates a dual-axis chart showing recent measles cases (bars) and MMR vaccination
    coverage (line) with herd immunity threshold.
    
    Args:
        usmeasles_data (pd.DataFrame): DataFrame with columns 'year', 'cases'
        mmr_data (pd.DataFrame): DataFrame with columns 'year', 'Location', 'MMR'
        
    Returns:
        go.Figure: Plotly figure object
    """
    if usmeasles_data.empty:
        return go.Figure()

    # Prepare data
    us_data = usmeasles_data.copy()
    us_data['Location'] = 'United States'
    us_data = us_data.drop_duplicates(subset=['year'])

    # Merge with vaccination data if available
    if not mmr_data.empty:
        mmr_clean = mmr_data.copy().drop_duplicates(subset=['year', 'Location'])
        us_data = pd.merge(us_data, mmr_clean, on=['year', 'Location'], how='left')

    # Filter to recent years and clean data
    us_data = us_data[us_data['year'] > 2014].copy()
    us_data = us_data.drop_duplicates(subset=['year']).sort_values('year').reset_index(drop=True)

    # Convert to numeric
    for col in ['year', 'cases', 'MMR']:
        if col in us_data.columns:
            us_data[col] = pd.to_numeric(us_data[col], errors='coerce')

    us_data = us_data.dropna(subset=['year', 'cases'])

    if us_data.empty:
        return go.Figure()

    fig = go.Figure()

    # Primary chart - measles cases as bars
    fig.add_trace(go.Bar(
        x=us_data["year"],
        y=us_data["cases"],
        name="Annual Measles Cases",
        marker=dict(color=COLORS['deep_blue']),
        hovertemplate="<b>Year:</b> %{x}<br><b>Cases:</b> %{y:,}<extra></extra>",
        text=us_data["cases"],
        textfont=dict(size=FONT_SIZES['annotation'], family=FONT_FAMILY, color="white"),
        textposition='auto',
        showlegend=True
    ))

    # Secondary chart - vaccination coverage line
    has_vaccination_data = False
    if 'MMR' in us_data.columns and not us_data['MMR'].isna().all():
        valid_vaccination = us_data.dropna(subset=['MMR'])

        if not valid_vaccination.empty:
            has_vaccination_data = True

            # Herd immunity threshold line
            fig.add_hline(
                y=95,
                line=dict(dash="dash", color="black", width=3),
                yref="y2"
            )

            # Add threshold to legend
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode="lines",
                line=dict(dash="dash", color="black", width=3),
                name="95% Herd Immunity Threshold",
                showlegend=True,
                hoverinfo='skip'
            ))

            # MMR coverage line
            fig.add_trace(go.Scatter(
                x=valid_vaccination["year"],
                y=valid_vaccination["MMR"],
                name="MMR Vaccination Coverage (%)",
                mode="lines+markers",
                line=dict(color=COLORS['orange'], width=4),
                marker=dict(
                    size=16,
                    color=COLORS['orange'],
                    line=dict(color='white', width=2)
                ),
                hovertemplate="<b>Year:</b> %{x}<br><b>Coverage:</b> %{y:.1f}%<extra></extra>",
                yaxis="y2",
                showlegend=True
            ))

    # Apply layout
    layout_config = get_standard_layout(tight_margins=True)
    if has_vaccination_data:
        layout_config['margin']['r'] = 80  # Extra space for secondary axis

    fig.update_layout(layout_config)
    fig.update_layout(title=None)

    # Configure axes
    fig.update_xaxes(get_axis_config("Year"))
    fig.update_xaxes(
        dtick=2,
        range=[us_data["year"].min() - 0.5, us_data["year"].max() + 0.5]
    )

    fig.update_yaxes(get_axis_config("Confirmed Measles Cases"))
    fig.update_yaxes(range=[0, max(us_data["cases"]) * 1.1])

    # Secondary Y-axis for vaccination coverage
    if has_vaccination_data:
        fig.update_layout(
            yaxis2=dict(
                title=dict(
                    text="<b>MMR Vaccination Coverage (%)</b>",
                    font=dict(
                        size=FONT_SIZES['axis_title'],
                        color='black',
                        family=FONT_FAMILY
                    )
                ),
                tickfont=dict(
                    size=FONT_SIZES['axis_tick'],
                    color='black',
                    family=FONT_FAMILY
                ),
                overlaying="y",
                side="right",
                range=[85, 100],
                showgrid=False
            )
        )

        # Threshold annotation
        fig.add_annotation(
            x=2020.5,
            y=95,
            text="<b>95% HERD IMMUNITY THRESHOLD</b>",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="black",
            ax=1,
            ay=-40,
            font=dict(size=FONT_SIZES['annotation'], color="white", family=FONT_FAMILY),
            align="center",
            bgcolor="black",
            borderpad=8,
            yref="y2"
        )

    add_footer_annotation(fig)
    return fig


def create_rnaught_comparison():
    """
    Creates a comparative visualization of basic reproduction numbers (R₀) across diseases.
    
    Returns:
        go.Figure: Plotly figure object
    """
    diseases_data = {
        'Disease': ['Ebola', 'HIV', 'COVID-19 (Omicron)', 'Chickenpox', 'Mumps', 'Measles'],
        'R0': [2, 4, 9.5, 12, 14, 18]
    }
    df = pd.DataFrame(diseases_data)

    fig = go.Figure()

    # Layout parameters for dot plot
    TOTAL_DISEASES = len(df)
    X_SPACING = 5
    Y_POSITION = 0
    TOTAL_DOTS = 20
    DOT_SIZE = 16
    CIRCLE_RADIUS = 1.3
    CENTER_DOT_SIZE = 22

    # Generate visualization for each disease
    for i, (disease, r0) in enumerate(zip(df['Disease'], df['R0'])):
        cx = i * X_SPACING  # Center X coordinate
        cy = Y_POSITION     # Center Y coordinate

        # Calculate positions for 20 people in circular arrangement
        angles = np.linspace(0, 2 * math.pi, TOTAL_DOTS, endpoint=False)
        x_coords = cx + CIRCLE_RADIUS * np.cos(angles)
        y_coords = cy + CIRCLE_RADIUS * np.sin(angles)

        # Add dots representing individual people
        for j in range(TOTAL_DOTS):
            if j < r0:  # This person could be infected
                dot_color = COLORS['red']
                hover_text = f"{disease}: This person could be infected"
            else:       # This person remains uninfected
                dot_color = COLORS['missing_data']
                hover_text = f"{disease}: This person is not infected"

            fig.add_trace(go.Scatter(
                x=[x_coords[j]],
                y=[y_coords[j]],
                mode='markers',
                marker=dict(
                    size=DOT_SIZE,
                    color=dot_color,
                    line=dict(width=2, color='white')
                ),
                hovertemplate=f"<b>{hover_text}</b><extra></extra>",
                showlegend=False
            ))

        # Add central index case
        fig.add_trace(go.Scatter(
            x=[cx],
            y=[cy],
            mode='markers',
            marker=dict(
                size=CENTER_DOT_SIZE,
                color=COLORS['orange'],
                line=dict(color='white', width=2)
            ),
            hovertemplate=f"<b>Original infected person</b><br><b>{disease}</b> (R₀ = {r0})<extra></extra>",
            showlegend=False
        ))

        # Add transmission lines
        line_x, line_y = [], []
        for j in range(TOTAL_DOTS):
            if j < r0:
                line_x.extend([cx, x_coords[j], None])
                line_y.extend([cy, y_coords[j], None])

        if line_x:
            fig.add_trace(go.Scatter(
                x=line_x,
                y=line_y,
                mode='lines',
                line=dict(width=2, color=COLORS['red']),
                opacity=0.6,
                hoverinfo='skip',
                showlegend=False
            ))

        # Add disease label
        fig.add_annotation(
            x=cx,
            y=cy - CIRCLE_RADIUS - 1.0,
            text=f"<b>{disease}</b><br>R₀ = {r0}",
            showarrow=False,
            xanchor="center",
            yanchor="top",
            font=dict(size=FONT_SIZES['annotation'], color="black", family=FONT_FAMILY),
            align="center"
        )

    # Calculate layout bounds
    x_min = -CIRCLE_RADIUS - 1.0
    x_max = (TOTAL_DISEASES - 1) * X_SPACING + CIRCLE_RADIUS + 1.0
    y_min = Y_POSITION - CIRCLE_RADIUS - 2.5
    y_max = Y_POSITION + CIRCLE_RADIUS + 1.0

    # Configure layout
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family=FONT_FAMILY, size=FONT_SIZES['axis_tick'], color='black'),
        margin=SPACING['margin'],
        autosize=True,
        xaxis=dict(
            visible=False,
            range=[x_min, x_max]
        ),
        yaxis=dict(
            visible=False,
            range=[y_min, y_max],
            scaleanchor="x",
            scaleratio=1
        ),
        showlegend=False
    )

    # Add legend explanation
    fig.add_annotation(
        text='Each circle shows 20 people. The orange ● dot is the first infected person. Red ● dots show potential infections (R₀). Grey ● dots are not infected people.',
        xref="paper", yref="paper",
        x=0.0, y=1.15,
        xanchor="left", yanchor="top",
        showarrow=False,
        font=dict(size=FONT_SIZES['legend'], color="black", family=FONT_FAMILY),
        align="left"
    )

    add_footer_annotation(fig)
    return fig


def create_bivariate_choropleth(usmap_data):
    """
    Creates a bivariate choropleth map showing both MMR coverage and measles case rates.
    
    Args:
        usmap_data (pd.DataFrame): Map data with cases and vaccination coverage
        
    Returns:
        go.Figure: Plotly figure object
    """
    if usmap_data.empty:
        return go.Figure()

    df = usmap_data.copy()

    # Find cases column
    cases_col = next((c for c in ['cases_calendar_year', 'cases', 'Cases'] if c in df.columns), None)
    vaccination_col = 'Estimate (%)'

    if cases_col is None or vaccination_col not in df.columns:
        return go.Figure()

    # Prepare data
    df['population'] = df['geography'].map(STATE_POPULATIONS)
    df['state_code'] = df['geography'].map(STATE_ABBREVIATIONS)
    df['case_rate'] = (df[cases_col] / df['population'] * 100000).round(2).fillna(0)
    df[vaccination_col] = pd.to_numeric(df[vaccination_col], errors='coerce')

    # Identify missing data
    missing_mmr_states_df = df[df[vaccination_col].isna()].copy()
    df_clean = df.dropna(subset=[vaccination_col, 'case_rate']).copy()

    # Apply bivariate classification
    classification_results = df_clean.apply(
        lambda row: classify_bivariate(row['case_rate'], row[vaccination_col]), axis=1
    )

    df_clean['case_class'] = [result[0] for result in classification_results]
    df_clean['mmr_class'] = [result[1] for result in classification_results]
    df_clean['category_label'] = [result[2] for result in classification_results]
    df_clean['color'] = [result[3] for result in classification_results]

    # Add color to main df
    df = df.merge(df_clean[['state_code', 'color']], on='state_code', how='left')
    df['color'] = df['color'].fillna(COLORS['missing_data'])

    fig = go.Figure()

    # Add traces for missing data
    if not missing_mmr_states_df.empty:
        fig.add_trace(go.Choropleth(
            locations=missing_mmr_states_df['state_code'],
            z=[1] * len(missing_mmr_states_df),
            locationmode='USA-states',
            marker_line_color='white',
            marker_line_width=0.5,
            colorscale=[[0, COLORS['missing_data']], [1, COLORS['missing_data']]],
            showscale=False,
            hovertemplate=(
                '<b>%{customdata[0]}</b><br>'
                'Classification: Missing Data<br>'
                'Case Rate: %{customdata[1]:.1f} per 100K<br>'
                'Total Cases: %{customdata[2]}<br>'
                'Population: %{customdata[3]:,}<br>'
                '<extra></extra>'
            ),
            customdata=list(zip(
                missing_mmr_states_df['geography'],
                missing_mmr_states_df['case_rate'],
                missing_mmr_states_df[cases_col],
                missing_mmr_states_df['population']
            )),
            showlegend=False
        ))

    # Create traces for each bivariate category
    for case_class in range(3):
        for mmr_class in range(3):
            subset = df_clean[(df_clean['case_class'] == case_class) & (df_clean['mmr_class'] == mmr_class)]

            if len(subset) > 0:
                fig.add_trace(go.Choropleth(
                    locations=subset['state_code'],
                    z=[1] * len(subset),
                    locationmode='USA-states',
                    marker_line_color='white',
                    marker_line_width=0.5,
                    colorscale=[[0, BIVARIATE_COLORS[case_class][mmr_class]],
                               [1, BIVARIATE_COLORS[case_class][mmr_class]]],
                    showscale=False,
                    hovertemplate=(
                        '<b>%{customdata[0]}</b><br>'
                        'Classification: %{customdata[4]}<br>'
                        'MMR Coverage: %{customdata[1]:.1f}%<br>'
                        'Case Rate: %{customdata[2]:.1f} per 100K<br>'
                        'Total Cases: %{customdata[3]}<br>'
                        'Population: %{customdata[5]:,}<br>'
                        '<extra></extra>'
                    ),
                    customdata=list(zip(
                        subset['geography'],
                        subset[vaccination_col],
                        subset['case_rate'],
                        subset[cases_col],
                        subset['category_label'],
                        subset['population']
                    )),
                    showlegend=False
                ))

    # Configure layout
    fig.update_layout(
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
            domain=dict(x=[0, 1.0], y=[0.15, 0.85])
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family=FONT_FAMILY, size=12),
        width=1000,
        height=800,
        margin=dict(l=20, r=20, t=20, b=100)
    )

    # Add 3x3 bivariate legend
    legend_x = 0.03
    legend_y = 0.95
    cell_size = 0.032
    spacing = 0.005

    # Add legend grid
    for i in range(3):  # Case rate (rows)
        for j in range(3):  # MMR coverage (cols)
            fig.add_shape(
                type="rect",
                xref="paper", yref="paper",
                x0=legend_x + j * (cell_size + spacing),
                y0=legend_y - (i + 1) * (cell_size + spacing) - 0.025,
                x1=legend_x + j * (cell_size + spacing) + cell_size,
                y1=legend_y - i * (cell_size + spacing) - 0.025,
                fillcolor=BIVARIATE_COLORS[i][j],
                line=dict(color="white", width=1)
            )

    # Add missing data legend square
    fig.add_shape(
        type="rect",
        xref="paper", yref="paper",
        x0=legend_x,
        y0=legend_y - 4.0 * (cell_size + spacing) - 0.025,
        x1=legend_x + cell_size,
        y1=legend_y - 3.0 * (cell_size + spacing) - 0.025,
        fillcolor=COLORS['missing_data'],
        line=dict(color="white", width=1)
    )

    # Add legend labels
    fig.add_annotation(
        text="Missing Data",
        xref="paper", yref="paper",
        x=legend_x + cell_size + spacing,
        y=legend_y - 3.5 * (cell_size + spacing) - 0.025,
        showarrow=False,
        font=dict(size=14, color='black'),
        xanchor="left", yanchor="middle"
    )

    # Add axis titles
    fig.add_annotation(
        text="← MMR Vaccine Coverage →",
        xref="paper", yref="paper",
        x=legend_x + 1.5 * (cell_size + spacing),
        y=legend_y - 0.005,
        showarrow=False,
        font=dict(size=14, color='black'),
        xanchor="center", yanchor="bottom"
    )

    fig.add_annotation(
        text="← Case Rate →",
        xref="paper", yref="paper",
        x=legend_x - 0.035,
        y=legend_y - 1.5 * (cell_size + spacing) - 0.025,
        showarrow=False,
        font=dict(size=14, color='black'),
        xanchor="center", yanchor="middle",
        textangle=90
    )

    # Add state abbreviation labels
    black_text_states = []
    white_text_states = []

    for index, row in df.iterrows():
        state_code = row.get('state_code')
        if state_code and state_code in STATE_CENTROIDS:
            lon, lat = STATE_CENTROIDS[state_code]
            background_color = row.get('color', COLORS['missing_data'])
            text_color = get_text_color(background_color)

            state_info = {
                'lon': lon,
                'lat': lat,
                'text': state_code,
                'state': row.get('geography', state_code)
            }

            if text_color == 'black':
                black_text_states.append(state_info)
            else:
                white_text_states.append(state_info)

    # Add text labels
    if black_text_states:
        fig.add_trace(go.Scattergeo(
            lon=[s['lon'] for s in black_text_states],
            lat=[s['lat'] for s in black_text_states],
            text=[s['text'] for s in black_text_states],
            mode='text',
            textfont=dict(size=10, color='black', family=FONT_FAMILY),
            showlegend=False,
            hoverinfo='skip'
        ))

    if white_text_states:
        fig.add_trace(go.Scattergeo(
            lon=[s['lon'] for s in white_text_states],
            lat=[s['lat'] for s in white_text_states],
            text=[s['text'] for s in white_text_states],
            mode='text',
            textfont=dict(size=10, color='white', family=FONT_FAMILY),
            showlegend=False,
            hoverinfo='skip'
        ))

    add_footer_annotation(fig, "Grey states are missing vaccination coverage data from the 2024-2025 school year")
    return fig


def create_lives_saved_chart(vaccine_impact_data):
    """
    Create bar chart visualization of estimated lives saved by vaccination programs.
    
    Args:
        vaccine_impact_data (pd.DataFrame): Vaccine impact data
        
    Returns:
        go.Figure: Plotly figure object
    """
    if vaccine_impact_data.empty:
        return go.Figure()

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

    # Create color bins
    increment = 200
    min_val = df[lives_saved_col].min()
    max_val = df[lives_saved_col].max()

    start_bin = math.floor(min_val / increment) * increment
    end_bin = math.ceil(max_val / increment) * increment + increment

    custom_bins = list(range(start_bin, end_bin, increment))

    if custom_bins[0] > min_val:
        custom_bins.insert(0, min_val)
    if custom_bins[-1] < max_val:
        custom_bins.append(max_val)

    custom_bins = sorted(list(set(custom_bins)))

    # Create color palette
    color_palette = [COLORS['blue'], COLORS['medium_blue'], COLORS['light_blue'], 
                    COLORS['pale_blue'], COLORS['light_orange'], COLORS['orange'], COLORS['red']]
    
    num_bins = len(custom_bins) - 1
    if num_bins > len(color_palette):
        color_indices = np.linspace(0, len(color_palette) - 1, num_bins, dtype=int)
        bin_colors = [color_palette[i] for i in color_indices]
    else:
        color_indices = np.linspace(0, len(color_palette) - 1, num_bins, dtype=int)
        bin_colors = [color_palette[i] for i in color_indices]

    # Create bin labels
    bin_labels = []
    for i in range(len(custom_bins) - 1):
        lower_bound = custom_bins[i]
        upper_bound = custom_bins[i+1]
        if i == 0 and lower_bound == df[lives_saved_col].min():
            label = f"≤{upper_bound:,.0f}"
        elif i == len(custom_bins) - 2 and upper_bound == df[lives_saved_col].max():
            label = f"≥{lower_bound:,.0f}"
        else:
            label = f"{lower_bound:,.0f}-{upper_bound:,.0f}"
        bin_labels.append(label)

    # Assign bins
    df['bin_index'] = pd.cut(df[lives_saved_col], bins=custom_bins, labels=False, include_lowest=True)
    df['color'] = df['bin_index'].map(lambda x: bin_colors[int(x)] if pd.notna(x) and int(x) < len(bin_colors) else bin_colors[0])
    df['bin_label'] = df['bin_index'].map(lambda x: bin_labels[int(x)] if pd.notna(x) and int(x) < len(bin_labels) else bin_labels[0])

    fig = go.Figure()

    # Create bars
    fig.add_trace(go.Bar(
        x=df[year_col],
        y=df[lives_saved_col],
        marker=dict(
            color=df['color'],
            line=dict(color='white', width=0.5)
        ),
        hovertemplate=(
            '<b>Year: %{x}</b><br>'
            'Lives Saved: %{y:,.0f}<br>'
            'Range: %{customdata}<br>'
            '<extra></extra>'
        ),
        customdata=df['bin_label'],
        showlegend=False
    ))

    # Configure layout
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family=FONT_FAMILY, size=FONT_SIZES['axis_tick'], color='black'),
        width=1000,
        height=600,
        margin=SPACING['margin']
    )

    # Configure axes
    fig.update_xaxes(get_axis_config("Year"))
    fig.update_yaxes(get_axis_config("Lives Saved (Estimated)"))
    fig.update_yaxes(tickformat=',.0f')

    # Create horizontal legend
    legend_x = 0.0
    legend_y = SPACING['legend_y']
    cell_height = 0.03
    cell_width = 0.02
    spacing = 0.005

    # Add legend title
    legend_text = "Lives Saved Range: "
    current_x = legend_x + 0.01

    fig.add_annotation(
        text=legend_text,
        xref="paper", yref="paper",
        x=current_x, y=legend_y + cell_height/2,
        showarrow=False,
        font=dict(size=14, color='black', family=FONT_FAMILY),
        xanchor="left", yanchor="middle"
    )

    estimated_title_width_paper_units = 0.13
    current_x += estimated_title_width_paper_units + 0.005

    # Show subset of bins in legend
    display_bin_indices = np.linspace(0, len(bin_labels) - 1, min(len(bin_labels), 8), dtype=int)

    for i in display_bin_indices:
        # Add colored rectangle
        fig.add_shape(
            type="rect",
            xref="paper", yref="paper",
            x0=current_x, y0=legend_y,
            x1=current_x + cell_width, y1=legend_y + cell_height,
            fillcolor=bin_colors[i],
            line=dict(color="white", width=1)
        )

        # Add label
        label_text = bin_labels[i]
        label_x_position = current_x + cell_width + spacing
        fig.add_annotation(
            text=label_text,
            xref="paper", yref="paper",
            x=label_x_position, y=legend_y + cell_height/2,
            showarrow=False,
            font=dict(size=14, color='black', family=FONT_FAMILY),
            xanchor="left", yanchor="middle"
        )

        # Update position for next item
        estimated_label_width_paper_units = len(label_text) * 0.008
        current_x = label_x_position + estimated_label_width_paper_units + spacing

    add_footer_annotation(fig, "These are mathematical model estimates, not observed deaths")
    return fig
