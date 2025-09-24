"""
Main Application File
Generates all visualizations and saves them as HTML files for GitHub Pages
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Import our modules
from data_manager import *
from chart_generators import *
from table_generators import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('measles_viz.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def create_html_page(fig, filename):
    """
    Create a simple HTML page with just the visualization for iframe embedding
    
    Args:
        fig: Plotly figure object
        filename (str): Output filename
    """
    # Generate the HTML with minimal styling for iframe embedding
    html_content = fig.to_html(
        include_plotlyjs='cdn',
        div_id='chart',
        config={'displayModeBar': False, 'responsive': True}
    )
    
    # Add minimal CSS for iframe compatibility
    full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Measles Data Visualization</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: white;
            font-family: Arial, sans-serif;
        }}
        #chart {{
            width: 100%;
            height: 100vh;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""
    
    output_dir = Path('docs')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / filename, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    logging.info(f"Created {filename}")

def create_index_page():
    """Create a simple index page with links to all visualizations"""
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Measles Data Visualizations</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .link-list {{
            list-style: none;
            padding: 0;
        }}
        .link-list li {{
            margin: 15px 0;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 5px;
        }}
        .link-list a {{
            color: #007bff;
            text-decoration: none;
            font-weight: bold;
            font-size: 16px;
        }}
        .link-list a:hover {{
            text-decoration: underline;
        }}
        .description {{
            color: #666;
            margin-top: 5px;
            font-size: 14px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h1>Measles Data Visualizations</h1>
    <p>Individual visualizations for iframe embedding:</p>
    
    <ul class="link-list">
        <li>
            <a href="timeline.html" target="_blank">Historical Timeline</a>
            <div class="description">Historical measles cases with vaccine milestones</div>
        </li>
        <li>
            <a href="recent_trends.html" target="_blank">Recent Trends</a>
            <div class="description">Recent cases and vaccination coverage</div>
        </li>
        <li>
            <a href="rnaught_comparison.html" target="_blank">Disease Comparison</a>
            <div class="description">Contagiousness comparison across diseases</div>
        </li>
        <li>
            <a href="state_map.html" target="_blank">State Map</a>
            <div class="description">State-by-state cases and vaccination coverage</div>
        </li>
        <li>
            <a href="lives_saved.html" target="_blank">Lives Saved</a>
            <div class="description">Estimated lives saved by vaccination</div>
        </li>
        <li>
            <a href="timeline_table.html" target="_blank">Timeline Data Table</a>
            <div class="description">Historical data in table format</div>
        </li>
        <li>
            <a href="recent_trends_table.html" target="_blank">Recent Trends Table</a>
            <div class="description">Recent data in table format</div>
        </li>
        <li>
            <a href="rnaught_table.html" target="_blank">Disease R0 Table</a>
            <div class="description">Disease reproduction numbers</div>
        </li>
        <li>
            <a href="state_map_table.html" target="_blank">State Data Table</a>
            <div class="description">State-by-state data in table format</div>
        </li>
        <li>
            <a href="lives_saved_table.html" target="_blank">Lives Saved Table</a>
            <div class="description">Lives saved data in table format</div>
        </li>
    </ul>
    
    <div class="footer">
        <p>Last updated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        <p>Data automatically refreshes daily</p>
    </div>
</body>
</html>
"""
    
    output_dir = Path('docs')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logging.info("Created index.html")

def main():
    """Main application function"""
    logging.info("Starting Measles Data Visualization Generator")
    
    try:
        # Initialize data manager
        data_manager = DataManager()
        
        # Fetch all data
        logging.info("Fetching data from sources...")
        data = data_manager.fetch_all_data()
        
        if data is None:
            logging.error("Failed to fetch required data. Exiting.")
            sys.exit(1)
        
        # Validate data
        validation_results = data_manager.validate_data(data)
        logging.info("Data validation results:")
        for dataset, result in validation_results.items():
            if result['valid']:
                logging.info(f"  {dataset}: Valid ({result.get('rows', 0)} rows)")
            else:
                logging.warning(f"  {dataset}: Invalid - {result['error']}")
        
        # Check if any critical datasets failed validation
        critical_datasets = ['timeline', 'usmeasles', 'usmap']
        failed_critical = [ds for ds in critical_datasets 
                          if not validation_results.get(ds, {}).get('valid', False)]
        
        if failed_critical:
            logging.error(f"Critical datasets failed validation: {failed_critical}")
            sys.exit(1)
        
        # Create output directory
        output_dir = Path('docs')
        output_dir.mkdir(exist_ok=True)
        
        # Generate index page
        create_index_page()
        
        # Generate charts
        logging.info("Generating charts...")
        
        # Timeline chart
        try:
            timeline_fig = create_measles_timeline(data['timeline'])
            create_html_page(timeline_fig, "timeline.html")
        except Exception as e:
            logging.error(f"Failed to create timeline chart: {e}")
        
        # Recent trends chart
        try:
            recent_fig = create_recent_trends(data['usmeasles'], data.get('mmr', pd.DataFrame()))
            create_html_page(recent_fig, "recent_trends.html")
        except Exception as e:
            logging.error(f"Failed to create recent trends chart: {e}")
        
        # R0 comparison chart
        try:
            rnaught_fig = create_rnaught_comparison()
            create_html_page(rnaught_fig, "rnaught_comparison.html")
        except Exception as e:
            logging.error(f"Failed to create R0 comparison chart: {e}")
        
        # State map
        try:
            map_fig = create_bivariate_choropleth(data['usmap'])
            create_html_page(map_fig, "state_map.html")
        except Exception as e:
            logging.error(f"Failed to create state map: {e}")
        
        # Lives saved chart
        try:
            lives_fig = create_lives_saved_chart_redesigned(data.get('vaccine_impact', pd.DataFrame()))
            create_html_page(lives_fig, "lives_saved.html")
        except Exception as e:
            logging.error(f"Failed to create lives saved chart: {e}")
        
        # Generate tables
        logging.info("Generating tables...")
        
        # Timeline table
        try:
            timeline_table = create_timeline_table(data['timeline'])
            create_html_page(timeline_table, "timeline_table.html")
        except Exception as e:
            logging.error(f"Failed to create timeline table: {e}")
        
        # Recent trends table
        try:
            recent_table = create_recent_trends_table(data['usmeasles'], data.get('mmr', pd.DataFrame()))
            create_html_page(recent_table, "recent_trends_table.html")
        except Exception as e:
            logging.error(f"Failed to create recent trends table: {e}")
        
        # R0 table
        try:
            rnaught_table = create_rnaught_table()
            create_html_page(rnaught_table, "rnaught_table.html")
        except Exception as e:
            logging.error(f"Failed to create R0 table: {e}")
        
        # State map table
        try:
            map_table = create_state_map_table(data['usmap'])
            create_html_page(map_table, "state_map_table.html")
        except Exception as e:
            logging.error(f"Failed to create state map table: {e}")
        
        # Lives saved table
        try:
            lives_table = create_lives_saved_table(data.get('vaccine_impact', pd.DataFrame()))
            create_html_page(lives_table, "lives_saved_table.html")
        except Exception as e:
            logging.error(f"Failed to create lives saved table: {e}")
        
        logging.info("Successfully generated all visualizations")
        logging.info(f"Output files created in {output_dir} directory")
        
    except Exception as e:
        logging.error(f"Critical error in main application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
