# Kansas City Crime Data Streaming Pipeline

## Project Overview

This project streams Kansas City Police Department crime data from 2025 through a Kafka pipeline and visualizes incidents in real-time. The system simulates live crime reporting by reading historical CSV data and processing it as if incidents are being reported as they occur.

## Key Insight

The visualization reveals crime distribution patterns across Kansas City, showing both geographic clustering and crime type prevalence. By categorizing over 150 specific offense types into 11 broader categories (Violent Crime, Theft, Vehicle Crime, Burglary, Robbery, Property Crime, Drug Offense, Weapons, Fraud, Domestic Violence, and Other), we can identify crime hotspots and understand which types of incidents are most common in the city.

## Data Processing

As each crime incident message arrives via Kafka, the consumer:

1. **Extracts location data** - Parses latitude/longitude coordinates from the POINT format
2. **Categorizes the offense** - Groups specific crimes into broader analytical categories
3. **Updates the map** - Plots the incident location on an interactive Kansas City street map with color coding by crime type
4. **Updates statistics** - Increments category counts displayed in the bar chart

This real-time processing is valuable because it demonstrates how streaming analytics can help law enforcement identify emerging crime patterns, allocate resources to high-incident areas, and understand the composition of criminal activity across different neighborhoods.

## Prerequisites

Before running this project, you need:

- **Python 3.11+** installed on your system
- **Apache Kafka** installed and configured
- **Git** for cloning the repository

## Complete Setup Instructions

### Step 1: Install Kafka

#### For Windows:
1. Install WSL2 (Windows Subsystem for Linux) if not already installed
2. Follow the Linux instructions below within WSL2

#### For Mac:
```bash
# Install Java (required for Kafka)
brew install java11

# Download Kafka
cd ~
curl -O https://archive.apache.org/dist/kafka/3.6.1/kafka_2.13-3.6.1.tgz
tar -xzf kafka_2.13-3.6.1.tgz
mv kafka_2.13-3.6.1 kafka

# Set environment variable (add to ~/.zshrc or ~/.bash_profile)
export KAFKA_HOME=~/kafka
```

#### For Linux:
```bash
# Install Java (required for Kafka)
sudo apt update
sudo apt install openjdk-11-jdk

# Download Kafka
cd ~
wget https://archive.apache.org/dist/kafka/3.6.1/kafka_2.13-3.6.1.tgz
tar -xzf kafka_2.13-3.6.1.tgz
mv kafka_2.13-3.6.1 kafka

# Set environment variable (add to ~/.bashrc)
export KAFKA_HOME=~/kafka
```

### Step 2: Prepare Kafka

Run the preparation script to format Kafka storage:

```bash
# Mac/Linux/WSL
cd ~/kafka
chmod +x ~/path/to/project/scripts/prepare_kafka.sh
~/path/to/project/scripts/prepare_kafka.sh
```

### Step 3: Start Kafka Server

In a dedicated terminal window, start Kafka:

```bash
cd ~/kafka
bin/kafka-server-start.sh config/kraft/server.properties
```

**Important**: Keep this terminal window open while running the project. Kafka must be running before starting the producer and consumer.

### Step 4: Clone the Repository

```bash
git clone https://github.com/AdriannaWebb/buzzline-06-webb.git
cd buzzline-06-webb
```

### Step 5: Create Virtual Environment

#### Windows (PowerShell):
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
```

#### Mac/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 6: Install Python Dependencies

#### Windows:
```powershell
py -m pip install --upgrade pip setuptools wheel
py -m pip install -r requirements.txt
```

#### Mac/Linux:
```bash
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt
```

### Step 7: Verify Environment Configuration

Check that the `.env` file exists in the project root with these settings:

```
CRIME_TOPIC=kc_crime_2025
CRIME_INTERVAL_SECONDS=2
CRIME_CONSUMER_GROUP_ID=crime_group
CRIME_MAX_POINTS_DISPLAY=500
KAFKA_BROKER_ADDRESS=localhost:9092
```

## Running the Pipeline

### Start the Producer

Open a new terminal, activate your virtual environment, and run:

#### Windows:
```powershell
.\.venv\Scripts\activate
py -m producers.crime_producer_webb
```

#### Mac/Linux:
```bash
source .venv/bin/activate
python3 -m producers.crime_producer_webb
```

You should see messages indicating crimes are being sent to Kafka.

### Start the Consumer

Open another new terminal, activate your virtual environment, and run:

#### Windows:
```powershell
.\.venv\Scripts\activate
py -m consumers.crime_consumer_webb
```

#### Mac/Linux:
```bash
source .venv/bin/activate
python3 -m consumers.crime_consumer_webb
```

The visualization window will appear showing the real-time crime map and bar chart.

### Stop the Pipeline

To stop the pipeline:
1. Press `Ctrl+C` in the consumer terminal
2. Press `Ctrl+C` in the producer terminal
3. Press `Ctrl+C` in the Kafka server terminal (if you want to stop Kafka)

## Configuration

Key settings in `.env`:
- `CRIME_INTERVAL_SECONDS=2` - Controls streaming speed (seconds between incidents)
- `CRIME_MAX_POINTS_DISPLAY=500` - Maximum points shown on map
- `CRIME_TOPIC=kc_crime_2025` - Kafka topic name

## Crime Categories

The system groups 150+ specific offenses into 11 categories:
- **Violent Crime**: Assault, Murder, Rape, Kidnapping
- **Theft**: Stealing, Shoplifting, Larceny
- **Vehicle Crime**: Auto theft, Recovered stolen vehicles
- **Burglary**: Residential and non-residential break-ins
- **Robbery**: Armed and strong-arm robbery
- **Property Crime**: Vandalism, Arson, Property damage
- **Drug Offense**: Controlled substance violations
- **Weapons**: Firearm possession and violations
- **Fraud**: Identity theft, Embezzlement, Forgery
- **Domestic Violence**: DV-related incidents
- **Other**: All other offense types

## Visualization

The consumer generates a dual-panel visualization that updates in real-time:

![Kansas City Crime Visualization](images/KC_crime_visualizations.png)

**Left Panel**: Interactive map showing crime incident locations plotted on actual Kansas City streets. Each point is color-coded by crime category, allowing quick identification of crime type distribution across different areas.

**Right Panel**: Bar chart displaying the count of incidents by category, providing insight into which types of crimes are most prevalent in the dataset.

## Troubleshooting

### Kafka Connection Errors
- Ensure Kafka is running: check the terminal where you started Kafka
- Verify `KAFKA_BROKER_ADDRESS=localhost:9092` in `.env`
- Wait a few seconds after starting Kafka before starting the producer

### Import Errors
- Ensure virtual environment is activated (you should see `(.venv)` in terminal)
- Reinstall requirements: `pip install -r requirements.txt`

### Visualization Not Appearing
- On Mac/Linux: Ensure you have a display server running
- Try closing other matplotlib windows
- Check that `contextily` and `matplotlib` are installed

### Producer/Consumer Not Finding Modules
- Run commands as modules: `python -m producers.crime_producer_webb`
- Ensure you're in the project root directory

## Project Structure

```
buzzline-06-webb/
├── data/                          # Crime data CSV
├── consumers/                     # Consumer scripts
│   └── crime_consumer_webb.py
├── producers/                     # Producer scripts
│   └── crime_producer_webb.py
├── utils/                         # Utility functions
│   ├── utils_consumer.py
│   ├── utils_producer.py
│   └── utils_logger.py
├── scripts/                       # Setup scripts
│   └── prepare_kafka.sh
├── logs/                          # Application logs
├── images/                        # Visualization screenshots
├── .env                           # Environment configuration
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Data Source

KCPD Crime Data 2025 from Kansas City Open Data Portal (data.kcmo.org)
- Dataset contains January 1, 2025 through September 29, 2025
- Original dataset includes 24 fields per incident
- Location data provided in POINT format (longitude, latitude)

## License

This project is licensed under the MIT License - see the LICENSE.txt file for details.