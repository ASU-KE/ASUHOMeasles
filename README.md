# Measles Data Visualizations


This repository automatically generates interactive charts and tables showing:

- Historical measles cases in the US
- Recent trends in cases and vaccination rates
- State-by-state analysis with vaccination coverage
- Lives saved through vaccination programs
- Disease contagiousness comparisons

## How It Works

- **Daily Updates**: GitHub Actions runs every day at 6 AM UTC
- **Data Sources**: CDC measles data, WHO vaccination impact data, state health departments
- **Backup System**: If data sources are down, uses cached backups
- **GitHub Pages**: Automatically deploys updated visualizations

## Data Sources

**Live Data (Updated Daily):**
- CDC Measles Cases by Year
- CDC Measles Cases by State  
- WHO Vaccine Impact Database

**Static Data (Repository Files):**
- `data/timeline.csv` - Historical timeline with key events
- `data/MMRKCoverage.csv` - MMR vaccination coverage data
- `data/MMRKCoverage25.csv` - 2025 state vaccination rates

## Edits 

- Update colors in `chart_styles.py`
- Modify thresholds in classification functions
- Add timeline events in `timeline.csv`
- Change data sources in `data_manager.py`

## Monitoring

- Check the Actions tab for workflow status
- View logs in `measles_viz.log`
- Backup files stored in `data/backups/`

