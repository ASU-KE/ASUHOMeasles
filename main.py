"""
Main Application File
Generates all visualizations and saves them as HTML files for GitHub Pages
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

# Import our modules
from data_manager import DataManager
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
            font-family: Arial, sans-serif;
            background-color: white;
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
    
    # Create docs directory if it doesn't exist
    docs_dir = Path('docs')
    docs_dir.mkdir(exist_ok=True)
    
    # Save the HTML file
    output_path = docs_dir / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    logging.info(f"Created HTML page: {output_path}")

def generate_all_visualizations(data_manager):
    """
    Generate all charts and tables and save as individual HTML files
    
    Args:
        data_manager: DataManager instance with loaded data
    """
    logging.info("Starting visualization generation...")
    
    # Fetch all data
    all_data = data_manager.fetch_all_data()
    
    if all_data is None:
        logging.error("Failed to load data. Exiting.")
        return False
    
    # Validate data
    validation_results = data_manager.validate_data(all_data)
    
    logging.info("Data validation results:")
    for dataset, result in validation_results.items():
        if result['valid']:
            logging.info(f"  ✓ {dataset}: {result['rows']} rows")
        else:
            logging.error(f"  ✗ {dataset}: {result['error']}")
    
    # Check if all required data is valid
    invalid_datasets = [name for name, result in validation_results.items() if not result['valid']]
    if invalid_datasets:
        logging.error(f"Invalid datasets: {invalid_datasets}. Stopping visualization generation.")
        return False
    
    logging.info("All data validation passed. Generating visualizations...")
    
    try:
        # Generate Charts
        logging.info("Creating timeline chart...")
        timeline_fig = create_measles_timeline(all_data['timeline'])
        create_html_page(timeline_fig, 'timeline.html')
        
        logging.info("Creating recent trends chart...")
        # For recent trends, we'll use the most recent 10 years of data
        recent_data = all_data['usmeasles'].tail(10)  
        recent_trends_fig = create_recent_trends(recent_data)
        create_html_page(recent_trends_fig, 'recent_trends.html')
        
        logging.info("Creating R-naught comparison chart...")
        # Sample disease data for R0 comparison
        disease_data = pd.DataFrame({
            'disease': ['COVID-19', 'Influenza', 'Measles', 'Pertussis', 'Mumps', 'Rubella'],
            'r0_max': [3.0, 2.0, 18.0, 17.0, 12.0, 7.0]
        })
        rnaught_fig = create_rnaught_comparison(disease_data)
        create_html_page(rnaught_fig, 'rnaught_comparison.html')
        
        logging.info("Creating bivariate choropleth map...")
        bivariate_fig = create_bivariate_choropleth(all_data['usmap'])
        create_html_page(bivariate_fig, 'state_map.html')
        
        logging.info("Creating lives saved chart...")
        lives_saved_fig = create_lives_saved_chart(all_data['vaccine_impact'])
        create_html_page(lives_saved_fig, 'lives_saved.html')
        
        logging.info("Creating weekly surveillance table...")
        # Get current epi week for the weekly surveillance table
        current_epi_week, current_year = data_manager.get_current_epi_week()
        weekly_surveillance_fig = create_southwest_weekly_surveillance_table(
            weekly_data=all_data['weekly_surveillance'],
            current_epi_week=current_epi_week,
            current_year=current_year
        )
        create_html_page(weekly_surveillance_fig, 'weekly_surveillance.html')
        
        # Generate Tables
        logging.info("Creating ASU Unity measles table...")
        asu_table_fig = create_asu_unity_measles_table(all_data['timeline'])
        create_html_page(asu_table_fig, 'measles_table.html')
        
        logging.info("Creating complete ASU Unity measles table...")
        complete_table_fig = create_complete_asu_unity_measles_table(all_data['timeline'])
        create_html_page(complete_table_fig, 'measles_table_complete.html')
        
        # Generate additional table versions
        logging.info("Creating recent trends table...")
        recent_table_fig = create_recent_trends_table(recent_data)
        create_html_page(recent_table_fig, 'recent_trends_table.html')
        
        logging.info("Creating R-naught comparison table...")
        rnaught_table_fig = create_rnaught_comparison_table(disease_data)
        create_html_page(rnaught_table_fig, 'rnaught_table.html')
        
        logging.info("Creating lives saved table...")
        lives_saved_table_fig = create_lives_saved_table(all_data['vaccine_impact'])
        create_html_page(lives_saved_table_fig, 'lives_saved_table.html')
        
        logging.info("All visualizations generated successfully!")
        return True
        
    except Exception as e:
        logging.error(f"Error generating visualizations: {e}")
        return False

def create_index_page():
    """
    Create an index.html page with links to all visualizations
    """
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASU Health Observatory - Measles Surveillance Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f8f9fa;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #8C1D40;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 40px;
            font-size: 18px;
        }
        .viz-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .viz-card {
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: border-color 0.3s;
        }
        .viz-card:hover {
            border-color: #8C1D40;
        }
        .viz-card h3 {
            color: #8C1D40;
            margin: 0 0 10px 0;
        }
        .viz-card p {
            color: #666;
            margin: 10px 0;
            font-size: 14px;
        }
        .viz-card a {
            display: inline-block;
            background-color: #8C1D40;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            margin: 5px;
        }
        .viz-card a:hover {
            background-color: #6d1631;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>ASU Health Observatory</h1>
        <div class="subtitle">Measles Surveillance Dashboard</div>
        
        <div class="viz-grid">
            <div class="viz-card">
                <h3>Historical Timeline</h3>
                <p>Measles cases in the US since 1912 with key vaccine milestones</p>
                <a href="timeline.html" target="_blank">View Chart</a>
                <a href="measles_table.html" target="_blank">View Table</a>
            </div>
            
            <div class="viz-card">
                <h3>Recent Trends</h3>
                <p>Cases vs vaccination coverage in recent years</p>
                <a href="recent_trends.html" target="_blank">View Chart</a>
                <a href="recent_trends_table.html" target="_blank">View Table</a>
            </div>
            
            <div class="viz-card">
                <h3>Disease Contagiousness</h3>
                <p>Basic reproduction number (R₀) comparison across diseases</p>
                <a href="rnaught_comparison.html" target="_blank">View Chart</a>
                <a href="rnaught_table.html" target="_blank">View Table</a>
            </div>
            
            <div class="viz-card">
                <h3>State-by-State Analysis</h3>
                <p>Measles cases and vaccination coverage by state</p>
                <a href="state_map.html" target="_blank">View Map</a>
            </div>
            
            <div class="viz-card">
                <h3>Lives Saved by Vaccines</h3>
                <p>Estimated lives saved through vaccination programs</p>
                <a href="lives_saved.html" target="_blank">View Chart</a>
                <a href="lives_saved_table.html" target="_blank">View Table</a>
            </div>
            
            <div class="viz-card">
                <h3>Weekly Surveillance</h3>
                <p>Southwest US states weekly measles surveillance</p>
                <a href="weekly_surveillance.html" target="_blank">View Table</a>
            </div>
        </div>
        
        <div class="footer">
            <p>Last updated: """ + datetime.now().strftime('%B %d, %Y at %I:%M %p UTC') + """</p>
            <p>Data sources: CDC, WHO, State Health Departments | ASU Health Observatory</p>
        </div>
    </div>
</body>
</html>
"""
    
    docs_dir = Path('docs')
    docs_dir.mkdir(exist_ok=True)
    
    with open(docs_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logging.info("Created index.html")

def main():
    """
    Main execution function
    """
    logging.info("=" * 50)
    logging.info("Starting ASU Measles Data Visualization Pipeline")
    logging.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logging.info("=" * 50)
    
    try:
        # Initialize data manager
        logging.info("Initializing DataManager...")
        data_manager = DataManager()
        
        # Generate all visualizations
        success = generate_all_visualizations(data_manager)
        
        if success:
            # Create index page
            create_index_page()
            logging.info("✓ All visualizations generated successfully!")
            logging.info("✓ Files are ready for GitHub Pages deployment")
        else:
            logging.error("✗ Visualization generation failed")
            return 1
            
    except Exception as e:
        logging.error(f"Unexpected error in main execution: {e}")
        return 1
    
    logging.info("Pipeline completed successfully!")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
