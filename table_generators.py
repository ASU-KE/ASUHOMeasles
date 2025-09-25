"""
Table Generation Module - Exact Copies from Original Colab
Contains all table functions exactly as they were in the original notebook
"""

import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

def create_timeline_table(timeline_data):
    """
    Create timeline table exactly as in original Colab
    """
    # Use the original timeline_data without dropping rows with NaN in 'Highlight'
    timeline_df = timeline_data[['Year', 'Cases', 'Highlight']].copy()

    # Replace NaN values in 'Highlight' with empty strings for display
    timeline_df['Highlight'] = timeline_df['Highlight'].fillna('')

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Year</b>', '<b>Confirmed Measles Cases</b>', '<b>Measles Historical Highlight</b>'],
            font=dict(size=12, family="Arial", color="black"),
            fill_color='#D0D0D0',
            align='left'
        ),
        cells=dict(
            values=[timeline_df['Year'], timeline_df['Cases'].apply(lambda x: f'{x:,}'), timeline_df['Highlight']],
            font=dict(size=12, family="Arial", color="black"),
            fill_color=[['#FAFAFA', '#FFFFFF'] * len(timeline_df)],
            align='left'
        )
    )])

    fig.update_layout(
        font=dict(family="Arial", size=12),
        # Add autosize layout parameter for potentially better column width fitting
        autosize=True,
        margin=dict(l=20, r=20, t=20, b=100) # Add some margin
    )

    # Add Last refreshed note
    fig.add_annotation(
        text=f"<b>Last refreshed:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        xref="paper", yref="paper",
        x=0.0, y=-0.2,  # Adjust y position as needed
        showarrow=False,
        font=dict(size=10, color='gray'),
        xanchor="left", yanchor="top",
        align="left"
    )

    return fig

def create_recent_trends_table(usmeasles_data, mmr_data):
    """
    Create recent trends table exactly as in original Colab
    """
    # 1. Create a copy of the usmeasles DataFrame and select the 'year' and 'cases' columns.
    us_data = usmeasles_data[['year', 'cases']].copy()

    # 2. Add a 'Location' column to this copied DataFrame and set its value to 'United States' for all rows.
    us_data['Location'] = 'United States'

    # 3. Remove duplicate rows based on the 'year' column from the copied usmeasles DataFrame.
    us_data = us_data.drop_duplicates(subset=['year'])

    # 4. Create a copy of the mmr DataFrame and select the 'year', 'Location', and 'MMR' columns.
    mmr_clean = mmr_data[['year', 'Location', 'MMR']].copy()

    # 5. Remove duplicate rows based on the 'year' and 'Location' columns from the copied mmr DataFrame.
    mmr_clean = mmr_clean.drop_duplicates(subset=['year', 'Location'])

    # 6. Merge the processed usmeasles and mmr DataFrames on the 'year' and 'Location' columns using a left merge, keeping all rows from the usmeasles DataFrame.
    merged_recent_trends = pd.merge(us_data, mmr_clean, on=['year', 'Location'], how='left')

    # 7. Filter the merged DataFrame to include data only for years after 2014.
    merged_recent_trends = merged_recent_trends[merged_recent_trends['year'] > 2014].copy()

    # 8. Sort the filtered DataFrame by 'year' and reset the index.
    merged_recent_trends = merged_recent_trends.sort_values('year').reset_index(drop=True)

    # 9. Convert the 'year', 'cases', and 'MMR' columns to numeric types, coercing errors.
    numeric_cols = ['year', 'cases', 'MMR']
    for col in numeric_cols:
        merged_recent_trends[col] = pd.to_numeric(merged_recent_trends[col], errors='coerce')

    # 10. Drop rows with missing values in the 'year' and 'cases' columns.
    merged_recent_trends = merged_recent_trends.dropna(subset=['year', 'cases'])

    # 11. Create a Plotly table using go.Figure and go.Table.
    fig = go.Figure(data=[go.Table(
        # 12. Define the table header with bold text for 'Year', 'Confirmed Measles Cases', and 'MMR Coverage (%)', using Arial font size 12 and black color, with a background color of '#D0D0D0' and left alignment.
        header=dict(
            values=['<b>Year</b>', '<b>Confirmed Measles Cases</b>', '<b>MMR Vaccination Coverage (%)</b>'], # Added "MMR Vaccination Coverage"
            font=dict(size=12, family="Arial", color="black"),
            fill_color='#D0D0D0',
            align='left'
        ),
        # 13. Define the table cells using the data from the processed DataFrame, with Arial font size 12 and black color, alternating background colors between '#FAFAFA' and '#FFFFFF', and left alignment.
        cells=dict(
            values=[merged_recent_trends['year'], merged_recent_trends['cases'].apply(lambda x: f'{x:,}'), merged_recent_trends['MMR']],
            font=dict(size=12, family="Arial", color="black"),
            fill_color=[['#FAFAFA', '#FFFFFF'] * len(merged_recent_trends)],
            align='left'
        )
    )])

    # 14. Update the figure layout to set the default font to Arial size 12.
    fig.update_layout(
        font=dict(family="Arial", size=12),
         # Add autosize layout parameter for potentially better column width fitting
        autosize=True,
        margin=dict(l=20, r=20, t=20, b=100) # Add some margin
    )

    # Add Last refreshed note
    fig.add_annotation(
        text=f"<b>Last refreshed:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        xref="paper", yref="paper",
        x=0.0, y=-0.2,  # Adjust y position as needed
        showarrow=False,
        font=dict(size=10, color='gray'),
        xanchor="left", yanchor="top",
        align="left"
    )

    # 15. Display the generated Plotly table.
    return fig

def create_rnaught_table():
    """
    Create R0 table exactly as in original Colab
    """
    # 1. Define a dictionary containing the disease names and their corresponding R₀ values.
    diseases_data = {
        'Disease': ['Ebola', 'HIV', 'COVID-19 (Omicron)', 'Chickenpox', 'Mumps', 'Measles'],
        'R0': [2, 4, 9.5, 12, 14, 18],
        # Removed the 'Description' column data as requested
    }

    # 2. Convert the dictionary into a pandas DataFrame with columns 'Disease' and 'R0'.
    df_rnaught = pd.DataFrame(diseases_data)

    # 3. Create a Plotly table using go.Figure and go.Table.
    fig = go.Figure(data=[go.Table(
        # 4. Define the table header with bold text for 'Disease' and 'R0', using Arial font size 12 and black color, with a background color of '#D0D0D0' and left alignment.
        header=dict(
            # Updated header values
            values=['<b>Disease</b>', '<b>R0 (Basic Reproduction Number)</b><br><i>(Avg. people infected by one case)</i>'],
            font=dict(size=12, family="Arial", color="black"),
            fill_color='#D0D0D0',
            align='left'
        ),
        # 5. Define the table cells using the data from the DataFrame, with Arial font size 12 and black color, alternating background colors between '#FAFAFA' and '#FFFFFF', and left alignment.
        cells=dict(
            # Updated cell values
            values=[df_rnaught['Disease'], df_rnaught['R0']],
            font=dict(size=12, family="Arial", color="black"),
            fill_color=[['#FAFAFA', '#FFFFFF'] * len(df_rnaught)],
            align='left'
        )
    )])

    # 6. Update the figure layout to set the default font to Arial size 12 and add a title.
    fig.update_layout(
        title=None, # Removed the title
        font=dict(family="Arial", size=12),
         # Add autosize layout parameter for potentially better column width fitting
        autosize=True,
        margin=dict(l=20, r=20, t=20, b=100) # Add some margin
    )

    # Add Last refreshed note
    fig.add_annotation(
        text=f"<b>Last refreshed:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        xref="paper", yref="paper",
        x=0.0, y=-0.2,  # Adjust y position as needed
        showarrow=False,
        font=dict(size=10, color='gray'),
        xanchor="left", yanchor="top",
        align="left"
    )

    # 7. Display the generated Plotly table.
    return fig

def create_state_map_table(usmap_data):
    """
    Create state map table exactly as in original Colab
    """
    # State population lookup
    state_populations = {
        'Alabama': 5108468, 'Alaska': 733406, 'Arizona': 7431344, 'Arkansas': 3067732,
        'California': 38965193, 'Colorado': 5877610, 'Connecticut': 3617176, 'Delaware': 1031890,
        'Florida': 23244842, 'Georgia': 11029227, 'Hawaii': 1435138, 'Idaho': 1964726,
        'Illinois': 12569321, 'Indiana': 6862199, 'Iowa': 3207004, 'Kansas': 2940865,
        'Kentucky': 4555777, 'Louisiana': 4573749, 'Maine': 1395722, 'Maryland': 6164660,
        'Massachusetts': 7001399, 'Michigan': 10037261, 'Minnesota': 5757976, 'Mississippi': 2940057,
        'Missouri': 6196357, 'Montana': 1122069, 'Nebraska': 1988536, 'Nevada': 3194176,
        'New Hampshire': 1402054, 'New Jersey': 9290841, 'New Mexico': 2114371, 'New York': 19299981,
        'North Carolina': 10835491, 'North Dakota': 783926, 'Ohio': 11785935, 'Oklahoma': 4019800,
        'Oregon': 4233358, 'Pennsylvania': 12972008, 'Rhode Island': 1095962, 'South Carolina': 5373555,
        'South Dakota': 919318, 'Tennessee': 7126489, 'Texas': 30503301, 'Utah': 3417734,
        'Vermont': 647464, 'Virginia': 8715698, 'Washington': 7812880, 'West Virginia': 1770071,
        'Wisconsin': 5910955, 'Wyoming': 584057
    }

    # State abbreviations
    state_abbrev = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
        'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
        'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
        'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
    }

    # 1. Create a copy of the `usmap` DataFrame.
    df_usmap = usmap_data.copy()

    # 4. Identify the column containing case data.
    cases_col = next((c for c in ['cases_calendar_year', 'cases', 'Cases'] if c in df_usmap.columns), None)

    # 5. Calculate the `case_rate` per 100,000 population, handling potential division by zero and missing population data by filling with 0. Round the result to 2 decimal places.
    df_usmap['population'] = df_usmap['geography'].map(state_populations)
    df_usmap['case_rate'] = (df_usmap[cases_col] / df_usmap['population'] * 100000).round(2).fillna(0)

    # 6. Map state names to their abbreviations and store them in a new column named `state_code`.
    df_usmap['state_code'] = df_usmap['geography'].map(state_abbrev)

    # 7. Convert the 'Estimate (%)' column to numeric, coercing errors.
    df_usmap['Estimate (%)'] = pd.to_numeric(df_usmap['Estimate (%)'], errors='coerce')

    # 8. Define a function `classify_detailed_bivariate` that takes a case rate and MMR coverage as input and returns the case class (0, 1, or 2), MMR class (0, 1, or 2), and a detailed category label based on predefined thresholds.
    def classify_detailed_bivariate(case_rate, mmr_coverage):
        """Classify states into detailed 3x3 bivariate categories"""
        # Case rate classification (0=high, 1=medium, 2=low)
        if case_rate <= 1.0:
            case_class = 2  # Low cases (bottom row)
        elif case_rate <= 3.0:
            case_class = 1  # Medium cases (middle row)
        else:
            case_class = 0  # High cases (top row)

        # MMR coverage classification (0=low, 1=medium, 2=high)
        if mmr_coverage < 92:
            mmr_class = 0  # Low coverage
        elif mmr_coverage < 96:
            mmr_class = 1  # Medium coverage
        else:
            mmr_class = 2  # High coverage

        category_labels = [
            ["High Cases, Low Vaccination", "High Cases, Medium Vaccination", "High Cases, High Vaccination"],
            ["Medium Cases, Low Vaccination", "Medium Cases, Medium Vaccination", "Medium Cases, High Vaccination"],
            ["Low Cases, Low Vaccination", "Low Cases, Medium Vaccination", "Low Cases, High Vaccination"]
        ]

        if pd.isna(case_rate) or pd.isna(mmr_coverage):
            return None, None, "Missing Data"
        else:
            return case_class, mmr_class, category_labels[case_class][mmr_class]

    # 9. Apply the `classify_detailed_bivariate` function to the DataFrame to create new columns: `case_class`, `mmr_class`, and `category_label`.
    classification_results = df_usmap.apply(
        lambda row: classify_detailed_bivariate(row['case_rate'], row['Estimate (%)']), axis=1
    )

    df_usmap['case_class'] = [result[0] for result in classification_results]
    df_usmap['mmr_class'] = [result[1] for result in classification_results]
    df_usmap['category_label'] = [result[2] for result in classification_results]

    # 10. Create a Plotly table using `go.Figure` and `go.Table`.
    fig = go.Figure(data=[go.Table(
        # 11. Define the table header with bold text for 'State', 'Abbr.', 'Total Measles Cases', 'Population', 'Measles Case Rate (per 100K)', 'MMR Vaccination Coverage (%)', and 'Classification', using Arial font size 12 and black color, with a background color of '#D0D0D0' and left alignment.
        header=dict(
            values=['<b>State</b>', '<b>Abbr.</b>', '<b>Total Measles Cases</b>', '<b>Population</b>', '<b>Measles Case Rate (per 100K)</b>', '<b>MMR Vaccination Coverage (%)</b>', '<b>Classification</b>'],
            font=dict(size=12, family="Arial", color="black"),
            fill_color='#D0D0D0',
            align='left',
            height=40  # Set equal header height
        ),
        # 12. Define the table cells using the data from the processed DataFrame, with Arial font size 12 and black color, alternating background colors between '#FAFAFA' and '#FFFFFF', and left alignment.
        cells=dict(
            values=[
                df_usmap['geography'],
                df_usmap['state_code'],
                 df_usmap[cases_col].apply(lambda x: f'{x:,}' if pd.notna(x) else ''), # Moved to 3rd position
                df_usmap['population'].apply(lambda x: f'{x:,.0f}' if pd.notna(x) else ''), # Moved to 4th position
                df_usmap['case_rate'], # Moved to 5th position
                df_usmap['Estimate (%)'].round(1), # Moved to 6th position
                df_usmap['category_label'] # Moved to 7th position
            ],
            font=dict(size=12, family="Arial", color="black"),
            fill_color=[['#FAFAFA', '#FFFFFF'] * len(df_usmap)],
            align='left',
            height=30  # Set equal row height for all cells
        ),
        # Set proportional column widths based on content
        columnwidth=[2, 0.8, 1.5, 1.5, 2, 2, 4]  # Proportional widths: State, Abbr, Cases, Population, Case Rate, Coverage, Classification
    )])

    # 13. Update the figure layout to set the default font to Arial size 12.
    fig.update_layout(
        font=dict(family="Arial", size=12),
         # Add autosize layout parameter for potentially better column width fitting
        autosize=True,
        margin=dict(l=20, r=20, t=20, b=100) # Add some margin
    )

    # Add Last refreshed note
    fig.add_annotation(
        text=f"<b>Last refreshed:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        xref="paper", yref="paper",
        x=0.0, y=-0.2,  # Adjust y position as needed
        showarrow=False,
        font=dict(size=10, color='gray'),
        xanchor="left", yanchor="top",
        align="left"
    )

    # 14. Display the generated Plotly table.
    return fig
    
def create_lives_saved_table(vaccine_impact_data):
    """
    Create lives saved table exactly as in original Colab
    """
    # 1. Create a copy of the `vaccine_impact` DataFrame.
    df_vaccine_impact = vaccine_impact_data.copy()

    # 2. Identify the column containing estimated lives saved data.
    lives_saved_col = None
    for col in ['lives_saved', 'Lives_Saved', 'deaths_prevented', 'deaths_averted']:
        if col in df_vaccine_impact.columns:
            lives_saved_col = col
            break

    # 3. Identify the column containing year data.
    year_col = None
    for col in ['year', 'Year', 'calendar_year']:
        if col in df_vaccine_impact.columns:
            year_col = col
            break

    # Ensure the columns were found, otherwise, the task cannot be completed.
    if lives_saved_col is None or year_col is None:
        print("Required columns for lives saved data not found.")
        return go.Figure()
    else:
        # Select only the necessary columns
        df_vaccine_impact = df_vaccine_impact[[year_col, lives_saved_col]]

        # Rename columns for clarity in the table
        df_vaccine_impact = df_vaccine_impact.rename(columns={
            year_col: 'Year',
            lives_saved_col: 'Estimated Lives Saved'
        })

        # 4. Create a Plotly table using go.Figure and go.Table.
        fig = go.Figure(data=[go.Table(
            # 5. Define the table header with bold text for 'Year' and 'Estimated Lives Saved', using Arial font size 12 and black color, with a background color of '#D0D0D0' and left alignment.
            header=dict(
                values=['<b>Year</b>', '<b>Estimated Lives Saved</b>'],
                font=dict(size=12, family="Arial", color="black"),
                fill_color='#D0D0D0',
                align='left'
            ),
            # 6. Define the table cells using the data from the processed DataFrame, with Arial font size 12 and black color, alternating background colors between '#FAFAFA' and '#FFFFFF', and left alignment.
            cells=dict(
                values=[df_vaccine_impact['Year'], df_vaccine_impact['Estimated Lives Saved'].apply(lambda x: f'{x:,.0f}')],
                font=dict(size=12, family="Arial", color="black"),
                fill_color=[['#FAFAFA', '#FFFFFF'] * len(df_vaccine_impact)],
                align='left'
            )
        )])

        # 7. Update the figure layout to set the default font to Arial size 12.
        fig.update_layout(
            font=dict(family="Arial", size=12),
             # Add autosize layout parameter for potentially better column width fitting
            autosize=True,
            margin=dict(l=20, r=20, t=20, b=100) # Add some margin
        )

        # Add Last refreshed note
        fig.add_annotation(
            text=f"<b>Last refreshed:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            xref="paper", yref="paper",
            x=0.0, y=-0.2,  # Adjust y position as needed
            showarrow=False,
            font=dict(size=10, color='gray'),
            xanchor="left", yanchor="top",
            align="left"
        )

    # Add note about data nature - Adjusted position to be below the timestamp
        fig.add_annotation(
            text="<i>Note: These are mathematical model estimates, not observed deaths</i>",
            xref="paper", yref="paper",
            x=0.0, y=SPACING['footer_y'] - 0.03, # Positioned below timestamp
            showarrow=False,
            font=dict(size=FONT_SIZES['footer'] - 1, color='gray', family=FONT_FAMILY), # Slightly smaller font
            xanchor="left", yanchor="top", # Anchor to top
            align="left"
        )

        # 8. Display the generated Plotly table.
        return fig
