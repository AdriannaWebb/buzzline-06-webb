"""
crime_consumer_webb.py

Consume Kansas City crime data from Kafka and visualize in real-time.

Displays crime incidents as they are reported.
"""

#####################################
# Configure matplotlib backend for Windows
#####################################

import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend which works better on Windows


#####################################
# Import Modules
#####################################

# Import packages from Python Standard Library
import os
import json  # handle JSON parsing

# Use a deque ("deck") - a double-ended queue data structure
# A deque is a good way to monitor a certain number of "most recent" messages
# A deque is a great data structure for time windows (e.g. the last 5 messages)
from collections import defaultdict

# Import external packages
from dotenv import load_dotenv

# IMPORTANT
# Import Matplotlib.pyplot for live plotting
# Use the common alias 'plt' for Matplotlib.pyplot
# Know pyplot well
import matplotlib.pyplot as plt
import contextily as ctx

# Import functions from local modules
from utils.utils_consumer import create_kafka_consumer
from utils.utils_logger import logger

#####################################
# Load Environment Variables
#####################################

load_dotenv()

#####################################
# Getter Functions for .env Variables
#####################################


def get_kafka_topic() -> str:
    """Fetch Kafka topic from environment or use default."""
    topic = os.getenv("CRIME_TOPIC", "kc_crime_2025")
    logger.info(f"Kafka topic: {topic}")
    return topic


def get_kafka_consumer_group_id() -> str:
    """Fetch Kafka consumer group id from environment or use default."""
    group_id: str = os.getenv("CRIME_CONSUMER_GROUP_ID", "crime_group")
    logger.info(f"Kafka consumer group id: {group_id}")
    return group_id

#####################################
# Crime Categorization Function
#####################################

def categorize_crime(offense):
    """
    Group crimes into broader categories based on KC crime data.
    
    Args:
        offense (str): The specific offense description
        
    Returns:
        str: The broader crime category
    """
    if not offense:
        return "Other"
    
    offense_upper = offense.upper()
    
    # Violent Crimes
    if any(word in offense_upper for word in ["ASSAULT", "MURDER", "HOMICIDE", "RAPE", "SODOMY", "KIDNAP"]):
        return "Violent Crime"
    
    # Theft/Stealing
    elif any(word in offense_upper for word in ["STEALING", "THEFT", "LARCENY", "SHOPLIFT", "PURSE SNATCH"]):
        return "Theft"
    
    # Vehicle Related
    elif any(word in offense_upper for word in ["VEHICLE", "AUTO", "STOLEN AUTO", "RECOVERED STOLEN AUTO"]):
        return "Vehicle Crime"
    
    # Burglary
    elif "BURGLARY" in offense_upper or "BREAKING" in offense_upper:
        return "Burglary"
    
    # Robbery
    elif "ROBBERY" in offense_upper:
        return "Robbery"
    
    # Property Crimes
    elif any(word in offense_upper for word in ["PROPERTY DAMAGE", "VANDAL", "ARSON", "TAMPERING"]):
        return "Property Crime"
    
    # Drugs
    elif any(word in offense_upper for word in ["DRUG", "NARCOTIC", "CONTROLLED SUBSTANCE"]):
        return "Drug Offense"
    
    # Weapons
    elif any(word in offense_upper for word in ["WEAPON", "FIREARM", "GUN"]):
        return "Weapons"
    
    # Fraud/Financial
    elif any(word in offense_upper for word in ["FRAUD", "EMBEZZLE", "FORGERY", "IDENTITY THEFT", "CREDIT"]):
        return "Fraud"
    
    # Domestic Violence
    elif "DOMESTIC VIOLENCE" in offense_upper:
        return "Domestic Violence"
    
    # Other
    else:
        return "Other"
    

#####################################
# Set up data structures
#####################################

crime_types = []  # To store crime types for counting
crime_counts = defaultdict(int)  # To count occurrences of each crime type
crime_locations = []  # To store lat/lon coordinates for mapping

#####################################
# Set up live visuals
#####################################

# Use the subplots() method to create a tuple containing
# two objects at once:
# - a figure (which can have many axis)
# - an axis (what they call a chart in Matplotlib)
# Create figure with two subplots side by side: map and bar chart
fig, (ax_map, ax_bar) = plt.subplots(1, 2, figsize=(16, 6))

# Use the ion() method (stands for "interactive on")
# to turn on interactive mode for live updates
plt.ion()


#####################################
# Define an update chart function for live plotting
# This will get called every time a new message is processed
#####################################


def update_chart():
    """
    Update both the crime map and bar chart.
    """
    # Clear both subplots
    ax_map.clear()
    ax_bar.clear()
    
# MAP SUBPLOT 
    # Define colors for each crime category
    crime_colors = {
        "Violent Crime": "#ED8B00",
        "Theft": "#00AFD7",
        "Vehicle Crime": "#002F6C",
        "Burglary": "#F2A900",
        "Robbery": "#078385",
        "Property Crime": "#007398",
        "Drug Offense": "#005F86",
        "Weapons": "#8B0000",
        "Fraud": "#9370DB",
        "Domestic Violence": "#DC143C",
        "Other": "#808080"
    }
    
    if crime_locations:
        # Group locations by crime category
        from collections import defaultdict
        locations_by_category = defaultdict(list)
        
        for loc in crime_locations:
            if loc["latitude"] and loc["longitude"]:
                category = loc.get("category", "Other")
                locations_by_category[category].append((loc["longitude"], loc["latitude"]))
        
        # Plot each category with its own color
        for category, coords in locations_by_category.items():
            if coords:
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                color = crime_colors.get(category, "#808080")
                ax_map.scatter(lons, lats, c=color, alpha=0.7, s=50, 
                             edgecolors='black', linewidths=1, zorder=5, label=category)
        
        # Add basemap
        try:
            ctx.add_basemap(ax_map, crs="EPSG:4326", source=ctx.providers.CartoDB.Positron)
        except:
            pass  # If map download fails, just show points
        
        # Add legend
        ax_map.legend(loc='upper right', fontsize=8)
    
    # Configure map
    ax_map.set_xlabel("Longitude", fontfamily="Verdana")
    ax_map.set_ylabel("Latitude", fontfamily="Verdana")
    ax_map.set_title("Kansas City Crime Locations Map", fontfamily="Verdana", fontweight="bold")
    
    # Set fixed boundaries for Kansas City to prevent shifting
    ax_map.set_xlim(-94.75, -94.40)
    ax_map.set_ylim(38.85, 39.35)

    # BAR CHART SUBPLOT 
    if crime_counts:
        # Get the crime types and their counts
        types_list = list(crime_counts.keys())
        counts_list = list(crime_counts.values())

        # Create a bar chart
        ax_bar.bar(types_list, counts_list, color="#007398")

        # Set labels and title
        ax_bar.set_xlabel("Crime Type", fontfamily="Verdana")
        ax_bar.set_ylabel("Number of Incidents", fontfamily="Verdana")
        ax_bar.set_title("Crime Type Distribution", fontfamily="Verdana", fontweight="bold")

        # Rotate x-axis labels for readability
        ax_bar.set_xticklabels(types_list, rotation=45, ha="right")

    # Adjust layout and draw
    plt.tight_layout()
    plt.draw()
    plt.pause(0.01)

#####################################
# Function to process a single message
# #####################################


def process_message(message: str) -> None:
    """
    Process a single JSON message from Kafka.

    Args:
        message (str): JSON message received from Kafka.
    """
    try:
        # Log the raw message for debugging
        logger.debug(f"Raw message: {message}")

        # Parse the JSON string into a Python dictionary
        data: dict = json.loads(message)
        logger.info(f"Processed JSON message: {data}")

        # Extract and categorize the crime type
        raw_offense = data.get("offense", "Unknown")
        crime_type = categorize_crime(raw_offense)
        
        # Increment the count for this crime type
        crime_counts[crime_type] += 1
        
        # Store location if available
        if data.get("latitude") and data.get("longitude"):
            crime_locations.append({
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "category": crime_type
            })

        # Log the updated counts
        logger.info(f"Crime: {crime_type} at {data.get('address', 'Unknown location')}")

        # Update the chart
        update_chart()

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error for message '{message}': {e}")
    except Exception as e:
        logger.error(f"Error processing message '{message}': {e}")


#####################################
# Define main function for this module
#####################################


def main() -> None:
    """
    Main entry point for the consumer.

    - Reads the Kafka topic name and consumer group ID from environment variables.
    - Creates a Kafka consumer using the `create_kafka_consumer` utility.
    - Polls messages and updates a live chart.
    """
    logger.info("START consumer.")

    # Clear previous run's data
    crime_types.clear()
    crime_counts.clear()
    crime_locations.clear()

    # fetch .env content
    topic = get_kafka_topic()
    group_id = get_kafka_consumer_group_id()
    logger.info(f"Consumer: Topic '{topic}' and group '{group_id}'...")

    # Create the Kafka consumer using the helpful utility function.
    consumer = create_kafka_consumer(topic, group_id)

    # Poll and process messages
    logger.info(f"Polling messages from topic '{topic}'...")
    try:
        while True:
            # Poll with a timeout to avoid blocking matplotlib
            message_batch = consumer.poll(timeout_ms=100, max_records=10)
            
            for topic_partition, messages in message_batch.items():
                for message in messages:
                    message_str = message.value
                    logger.debug(f"Received message at offset {message.offset}")
                    process_message(message_str)
            
            # Small pause to let matplotlib update
            plt.pause(0.01)
            
    except KeyboardInterrupt:
        logger.warning("Consumer interrupted by user.")
    except Exception as e:
        logger.error(f"Error while consuming messages: {e}")
    finally:
        consumer.close()
        logger.info(f"Kafka consumer for topic '{topic}' closed.")


#####################################
# Conditional Execution
#####################################

# Ensures this script runs only when executed directly (not when imported as a module).
if __name__ == "__main__":
    main()
    plt.ioff()  # Turn off interactive mode after completion
    plt.show()
