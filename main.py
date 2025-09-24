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

def create_html_page(fig, title, filename, description=""):
    """
    Create a standalone HTML page with the visualization
    
    Args:
        fig: Plotly figure object
        title (str): Page title
        filename (str): Output filename
        description (str): Page description
    """
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Measles Data Visualization</title>
    <meta name="description" content="{description}">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }}
        .description {{
            text-align: center;
            color: #666;
            margin-bottom: 20px;
        }}
        .nav {{
            text-align: center;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }}
        .nav a {{
            margin: 0 15px;
            text-decoration: none;
            color: #007bff;
            font-weight: 500;
        }}
        .nav a:hover {{
            text-decoration: underline;
        }}
        .chart-container {{
            width: 100%;
            height: auto;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 4px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="description">{description}</div>
        
        <div class="nav">
            <a href="index.html">Home</a> |
            <a href="timeline.html">Historical Timeline</a> |
            <a href="recent_trends.html">Recent Trends</a> |
            <a href="rnaught_comparison.html">Disease Comparison</a> |
            <a href="state_map.html">State Map</a> |
            <a href="lives_saved.html">Lives Saved</a>
        </div>
        
        <div class="chart-container">
            {fig.to_html(include_plotlyjs='cdn', div_id='chart')}
        </div>
        
        <div class="footer">
            <p><strong>Data Sources:</strong> CDC, WHO, State Health Departments</p>
            <p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
            <p><a href="https://github.com/yourusername/measles-viz" target="_blank">View Source Code</a></p>
        </div>
    </div>
</body>
</html>
"""
    
    output_dir = Path('docs')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / filename, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    logging.info(f"Created {filename}")

def create_index_page():
    """Create the main index page"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Measles Data Visualization Dashboard</title>
    <meta name="description" content="Interactive visualizations of measles case data, vaccination coverage, and public health trends">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 40px;
            font-size: 1.2em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin: 40px 0;
        }
        .card {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 25px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .card h3 {
            margin-top: 0;
            color: #007bff;
            font-size: 1.3em;
        }
        .card p {
            color: #666;
            margin: 15px 0;
        }
        .card-links {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }
        .btn {
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 500;
            transition: background-color 0.2s;
        }
        .btn-primary {
            background-color: #007bff;
            color: white;
        }
        .btn-primary:hover {
            background-color: #0056b3;
        }
        .btn-secondary {
            background-color: #6c757d;
            color: white;
        }
        .btn-secondary:hover {
            background-color: #545b62;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 4px;
            color: #666;
        }
        .key-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
            text-align: center;
        }
        .stat-box {
            background-color: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #1976d2;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Measles Data Visualization</h1>
        <div class="subtitle">Interactive visualizations of measles case data, vaccination coverage, and public health trends</div>
        
        <div class="key-stats">
            <div class="stat-box">
                <div class="stat-number">18</div>
                <div class="stat-label">R₀ Value for Measles<br>(Most Contagious)</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">95%</div>
                <div class="stat-label">Vaccination Rate Needed<br>for Herd Immunity</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">1963</div>
                <div class="stat-label">Year MMR Vaccine<br>Was Licensed</div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Historical Timeline</h3>
                <p>Explore measles case trends from 1944 to present, with key vaccine milestones and public health events highlighted.</p>
                <div class="card-links">
                    <a href="timeline.html" class="btn btn-primary">View Chart</a>
                    <a href="timeline_table.html" class="btn btn-secondary">View Data</a>
                </div>
            </div>
            
            <div class="card">
                <h3>Recent Trends</h3>
                <p>Recent measles cases and vaccination coverage rates, showing the relationship between immunization and disease prevention.</p>
                <div class="card-links">
                    <a href="recent_trends.html" class="btn btn-primary">View Chart</a>
                    <a href="recent_trends_table.html" class="btn btn-secondary">View Data</a>
                </div>
            </div>
            
            <div class="card">
                <h3>Disease Comparison</h3>
                <p>Compare the contagiousness of measles with other diseases using basic reproduction number (R₀) values.</p>
                <div class="card-links">
                    <a href="rnaught_comparison.html" class="btn btn-primary">View Chart</a>
                    <a href="rnaught_table.html" class="btn btn-secondary">View Data</a>
                </div>
            </div>
            
            <div class="card">
                <h3>State-by-State Analysis</h3>
                <p>Interactive map showing measles case rates and vaccination coverage by state, with bivariate color coding.</p>
                <div class="card-links">
                    <a href="state_map.html" class="btn btn-primary">View Map</a>
                    <a href="state_map_table.html" class="btn btn-secondary">View Data</a>
                </div>
            </div>
            
            <div class="card">
                <h3>Lives Saved by Vaccination</h3>
                <p>Estimated lives saved through measles vaccination programs, based on WHO modeling data.</p>
                <div class="card-links">
                    <a href="lives_saved.html" class="btn btn-primary">View Chart</a>
                    <a href="lives_saved_table.html" class="btn btn-secondary">View Data</a>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>About This Dashboard:</strong> This visualization dashboard presents measles surveillance data from the CDC, WHO, and state health departments. All visualizations are automatically updated daily with the latest available data.</p>
            <p><strong>Data Sources:</strong> CDC Wonder, WHO Vaccine Impact Database, State Health Department Reports</p>
            <p>Last updated: """ + datetime.now().strftime("%B %d, %Y at %I:%M %p") + """</p>
            <p><a href="https://github.com/yourusername/measles-viz" target="_blank">View Source Code on GitHub</a></p>
        </div>
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
            create_html_page(
                timeline_fig,
                "Historical Measles Timeline",
                "timeline.html",
                "Historical timeline of measles cases with vaccine milestones"
            )
        except Exception as e:
            logging.error(f"Failed to create timeline chart: {e}")
        
        # Recent trends chart
        try:
            recent_fig = create_recent_trends(data['usmeasles'], data.get('mmr', pd.DataFrame()))
            create_html_page(
                recent_fig,
                "Recent Measles Trends",
                "recent_trends.html",
                "Recent measles cases and vaccination coverage trends"
            )
        except Exception as e:
            logging.error(f"Failed to create recent trends chart: {e}")
        
        # R0 comparison chart
        try:
            rnaught_fig = create_rnaught_comparison()
            create_html_page(
                rnaught_fig,
                "Disease Contagiousness Comparison",
                "rnaught_comparison.html",
                "Comparison of basic reproduction numbers across diseases"
            )
        except Exception as e:
            logging.error(f"Failed to create R0 comparison chart: {e}")
        
        # State map
        try:
            map_fig = create_bivariate_choropleth(data['usmap'])
            create_html_page(
                map_fig,
                "State-by-State Measles Analysis",
                "state_map.html",
                "Interactive map showing measles cases and vaccination coverage by state"
            )
        except Exception as e:
            logging.error(f"Failed to create state map: {e}")
        
        # Lives saved chart
        try:
            lives_fig = create_lives_saved_chart(data.get('vaccine_impact', pd.DataFrame()))
            create_html_page(
                lives_fig,
                "Lives Saved by Vaccination",
                "lives_saved.html",
                "Estimated lives saved through measles vaccination programs"
            )
        except Exception as e:
            logging.error(f"Failed to create lives saved chart: {e}")
        
        # Generate tables
        logging.info("Generating tables...")
        
        # Timeline table
        try:
            timeline_table = create_timeline_table(data['timeline'])
            create_html_page(
                timeline_table,
                "Historical Timeline Data",
                "timeline_table.html",
                "Historical measles case data in table format"
            )
        except Exception as e:
            logging.error(f"Failed to create timeline table: {e}")
        
        # Recent trends table
        try:
            recent_table = create_recent_trends_table(data['usmeasles'], data.get('mmr', pd.DataFrame()))
            create_html_page(
                recent_table,
                "Recent Trends Data",
                "recent_trends_table.html",
                "Recent measles and vaccination data in table format"
            )
        except Exception as e:
            logging.error(f"Failed to create recent trends table: {e}")
        
        # R0 table
        try:
            rnaught_table = create_rnaught_table()
            create_html_page(
                rnaught_table,
                "Disease R0 Values",
                "rnaught_table.html",
                "Basic reproduction numbers for various diseases"
            )
        except Exception as e:
            logging.error(f"Failed to create R0 table: {e}")
        
        # State map table
        try:
            map_table = create_state_map_table(data['usmap'])
            create_html_page(
                map_table,
                "State Analysis Data",
                "state_map_table.html",
                "State-by-state measles and vaccination data"
            )
        except Exception as e:
            logging.error(f"Failed to create state map table: {e}")
        
        # Lives saved table
        try:
            lives_table = create_lives_saved_table(data.get('vaccine_impact', pd.DataFrame()))
            create_html_page(
                lives_table,
                "Lives Saved Data",
                "lives_saved_table.html",
                "Estimated lives saved by vaccination in table format"
            )
        except Exception as e:
            logging.error(f"Failed to create lives saved table: {e}")
        
        logging.info("Successfully generated all visualizations")
        logging.info(f"Output files created in {output_dir} directory")
        
    except Exception as e:
        logging.error(f"Critical error in main application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
