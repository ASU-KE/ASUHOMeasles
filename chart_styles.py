"""
Chart Styles and Formatting Module
Provides consistent styling across all visualizations
"""

from datetime import datetime

# Enhanced color palette using the original scheme
COLORS = {
    'deep_red': '#a50026',
    'red': '#d73027',
    'orange_red': '#f46d43',
    'orange': '#fdae61',
    'light_orange': '#fee090',
    'pale_yellow': '#ffffbf',
    'pale_blue': '#e0f3f8',
    'light_blue': '#abd9e9',
    'medium_blue': '#74add1',
    'blue': '#4575b4',
    'deep_blue': '#313695',
    'missing_data': '#E0E0E0',
    'white': 'white',
    'black': 'black',
    'gray': 'gray'
}

# Hierarchical font sizing system
FONT_SIZES = {
    'title': 20,           # Chart title
    'axis_title': 16,      # Axis titles
    'axis_tick': 14,       # Axis tick labels
    'legend': 14,          # Legend text
    'annotation': 12,      # Event annotations
    'footer': 10           # Footer/metadata text
}

# Font family
FONT_FAMILY = "Arial"

# Consistent spacing system
SPACING = {
    'margin': {'l': 80, 'r': 80, 't': 100, 'b': 160},  # Standard margins
    'margin_tight': {'l': 60, 'r': 40, 't': 80, 'b': 120},  # Tighter margins for mobile
    'annotation_offset': -65,   # Consistent annotation positioning
    'legend_y': 1.25,          # Legend positioned higher
    'legend_y_tight': 1.2,     # Legend for tighter layouts
    'footer_y': -0.28          # Footer positioning
}

# Bivariate color matrix for choropleth maps
BIVARIATE_COLORS = [
    [COLORS['red'], COLORS['orange_red'], COLORS['orange']],  # High case rate
    [COLORS['light_orange'], COLORS['pale_yellow'], COLORS['pale_blue']],  # Medium case rate
    [COLORS['light_blue'], COLORS['medium_blue'], COLORS['blue']]   # Low case rate
]

# Category labels for bivariate classification
BIVARIATE_LABELS = [
    ["High Cases, Low Vaccination", "High Cases, Medium Vaccination", "High Cases, High Vaccination"],
    ["Medium Cases, Low Vaccination", "Medium Cases, Medium Vaccination", "Medium Cases, High Vaccination"],
    ["Low Cases, Low Vaccination", "Low Cases, Medium Vaccination", "Low Cases, High Vaccination"]
]

# State population data
STATE_POPULATIONS = {
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
STATE_ABBREVIATIONS = {
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

# State centroids for map labels
STATE_CENTROIDS = {
    'AL': [-86.87, 32.78], 'AK': [-153.31, 64.0], 'AZ': [-111.57, 34.29], 'AR': [-92.37, 34.97],
    'CA': [-119.42, 36.78], 'CO': [-105.51, 39.06], 'CT': [-72.76, 41.60], 'DE': [-75.50, 39.00],
    'FL': [-81.69, 27.77], 'GA': [-83.64, 32.99], 'HI': [-157.86, 21.31], 'ID': [-114.58, 43.68],
    'IL': [-89.37, 40.42], 'IN': [-86.44, 40.30], 'IA': [-93.09, 41.88], 'KS': [-98.58, 38.53],
    'KY': [-84.27, 37.84], 'LA': [-91.87, 31.17], 'ME': [-69.39, 45.37], 'MD': [-76.59, 39.05],
    'MA': [-71.72, 42.34], 'MI': [-84.54, 44.18], 'MN': [-93.90, 46.39], 'MS': [-89.87, 32.74],
    'MO': [-92.28, 38.57], 'MT': [-109.45, 46.92], 'NE': [-99.90, 41.50], 'NV': [-116.94, 39.33],
    'NH': [-71.56, 43.45], 'NJ': [-74.52, 40.06], 'NM': [-106.24, 34.84], 'NY': [-75.50, 42.94],
    'NC': [-79.80, 35.63], 'ND': [-100.34, 47.53], 'OH': [-82.77, 40.42], 'OK': [-96.93, 35.56],
    'OR': [-120.57, 43.98], 'PA': [-77.20, 40.59], 'RI': [-71.51, 41.70], 'SC': [-80.95, 33.91],
    'SD': [-99.90, 44.35], 'TN': [-86.69, 35.75], 'TX': [-98.77, 31.17], 'UT': [-111.89, 40.15],
    'VT': [-72.71, 44.04], 'VA': [-78.47, 37.77], 'WA': [-121.75, 47.40], 'WV': [-80.95, 38.49],
    'WI': [-89.99, 43.78], 'WY': [-107.55, 43.08]
}

def get_standard_layout(tight_margins=False):
    """
    Get standard layout configuration
    
    Args:
        tight_margins (bool): Use tighter margins for mobile/responsive design
        
    Returns:
        dict: Layout configuration
    """
    margins = SPACING['margin_tight'] if tight_margins else SPACING['margin']
    legend_y = SPACING['legend_y_tight'] if tight_margins else SPACING['legend_y']
    
    return {
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'font': {
            'family': FONT_FAMILY, 
            'size': FONT_SIZES['axis_tick'], 
            'color': 'black'
        },
        'margin': margins,
        'autosize': True,
        'legend': {
            'orientation': "h",
            'yanchor': "top",
            'y': legend_y,
            'xanchor': "left",
            'x': 0,
            'font': {
                'size': FONT_SIZES['legend'],
                'color': 'black',
                'family': FONT_FAMILY
            }
        }
    }

def get_axis_config(title, is_x_axis=True, show_grid=False, show_line=False):
    """
    Get standardized axis configuration
    
    Args:
        title (str): Axis title
        is_x_axis (bool): Whether this is an x-axis configuration
        show_grid (bool): Whether to show grid lines
        show_line (bool): Whether to show axis line
        
    Returns:
        dict: Axis configuration
    """
    config = {
        'title': {
            'text': f"<b>{title}</b>",
            'font': {
                'size': FONT_SIZES['axis_title'],
                'color': 'black',
                'family': FONT_FAMILY
            }
        },
        'tickfont': {
            'size': FONT_SIZES['axis_tick'],
            'color': 'black',
            'family': FONT_FAMILY
        },
        'showgrid': show_grid,
        'linecolor': 'black' if show_line else 'rgba(0,0,0,0)',
        'linewidth': 2 if show_line else 0
    }
    
    return config

def add_footer_annotation(fig, custom_note=None):
    """
    Add standard footer annotation with timestamp
    
    Args:
        fig: Plotly figure object
        custom_note (str): Optional custom note to add
    """
    last_refreshed = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    footer_text = f"<b>Last refreshed:</b> {last_refreshed}"
    if custom_note:
        footer_text += f"<br><i>{custom_note}</i>"
    
    fig.add_annotation(
        text=footer_text,
        xref="paper", yref="paper",
        x=0.0, y=SPACING['footer_y'],
        xanchor="left", yanchor="top",
        showarrow=False,
        font={
            'size': FONT_SIZES['footer'],
            'color': 'gray',
            'family': FONT_FAMILY
        },
        align="left"
    )

def wrap_text(text, width=25):
    """
    Text wrapping for annotations
    
    Args:
        text (str): Text to wrap
        width (int): Maximum line width
        
    Returns:
        str: Wrapped text with HTML line breaks
    """
    if not text or text == "":
        return None
    
    words = str(text).split()
    lines, line, line_len = [], [], 0
    
    for word in words:
        if line_len + len(word) + 1 <= width:
            line.append(word)
            line_len += len(word) + 1
        else:
            if line:
                lines.append(" ".join(line))
            line = [word]
            line_len = len(word)
    
    if line:
        lines.append(" ".join(line))
    
    return "<br>".join(lines)

def classify_bivariate(case_rate, mmr_coverage):
    """
    Classify states into bivariate categories for choropleth map
    
    Args:
        case_rate (float): Cases per 100,000 population
        mmr_coverage (float): MMR vaccination coverage percentage
        
    Returns:
        tuple: (case_class, mmr_class, category_label, color)
    """
    import pandas as pd
    
    if pd.isna(case_rate) or pd.isna(mmr_coverage):
        return None, None, "Missing Data", COLORS['missing_data']
    
    # Case rate classification (0=high, 1=medium, 2=low)
    if case_rate <= 1.0:
        case_class = 2  # Low cases
    elif case_rate <= 3.0:
        case_class = 1  # Medium cases
    else:
        case_class = 0  # High cases

    # MMR coverage classification (0=low, 1=medium, 2=high)
    if mmr_coverage < 92:
        mmr_class = 0  # Low coverage
    elif mmr_coverage < 96:
        mmr_class = 1  # Medium coverage
    else:
        mmr_class = 2  # High coverage

    category_label = BIVARIATE_LABELS[case_class][mmr_class]
    color = BIVARIATE_COLORS[case_class][mmr_class]
    
    return case_class, mmr_class, category_label, color

def get_text_color(hex_color):
    """
    Determine text color (black or white) based on background color
    
    Args:
        hex_color (str): Hex color code
        
    Returns:
        str: 'black' or 'white'
    """
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Convert to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Calculate luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    # Return black for light backgrounds, white for dark
    return 'black' if luminance > 0.5 else 'white'

def format_number(value, format_type='comma'):
    """
    Format numbers consistently across charts
    
    Args:
        value: Number to format
        format_type (str): Type of formatting ('comma', 'compact', 'percent')
        
    Returns:
        str: Formatted number string
    """
    import pandas as pd
    
    if pd.isna(value):
        return ''
    
    if format_type == 'comma':
        return f"{value:,.0f}"
    elif format_type == 'compact':
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value/1_000:.1f}K"
        else:
            return f"{value:,.0f}"
    elif format_type == 'percent':
        return f"{value:.1f}%"
    else:
        return str(value)
