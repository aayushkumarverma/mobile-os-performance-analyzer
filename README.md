# Mobile OS Performance Analyzer

A Python-based project that connects to an Android smartphone using Android Debug Bridge (ADB) and collects real-time operating system performance data.

## Planned Features

- Running process monitoring
- CPU usage monitoring
- RAM usage analysis
- Thread count monitoring
- Battery information
- Pandas-based data analysis
- Performance graphs and visualizations

## Technologies

- Python
- Android Debug Bridge (ADB)
- Pandas
- Matplotlib

## Project Structure

- `main.py` - Main program
- `adb_collector.py` - Collects Android system data through ADB
- `parser.py` - Parses raw ADB output
- `analyzer.py` - Performs data analysis
- `visualizer.py` - Creates graphs
- `data/` - Stores sample/raw data
- `output/` - Stores generated results
