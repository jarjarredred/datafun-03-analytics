"""
Process a JSON file to count milkweed projects by neighborhood and save the result.

JSON file is in the format that lists dictionaries with keys "NEIGHBORHOOD" and "MILKWEED",
among other variables. It's a direct list of project dictionaries at the root.

Example JSON structure:
[
    {
        "ADDRESSNUMBER": "1200",
        "MILKWEED": null,
        "WARD": null,
        "NEIGHBORHOOD": "Downtown"
    },
    {
        "ADDRESSNUMBER": "315",
        "MILKWEED": true,  # Assuming 'true' or a non-null value indicates milkweed
        "WARD": 36,
        "NEIGHBORHOOD": "Shaw"
    },
    {
        "ADDRESSNUMBER": "400",
        "MILKWEED": true,
        "WARD": 15,
        "NEIGHBORHOOD": "Shaw"
    },
    {
        "ADDRESSNUMBER": "500",
        "MILKWEED": false, # Not a milkweed project
        "WARD": 10,
        "NEIGHBORHOOD": "Central West End"
    },
    {
        "ADDRESSNUMBER": "600",
        "MILKWEED": true,
        "WARD": 1,
        "NEIGHBORHOOD": null # Missing neighborhood information
    },
    {
        "ADDRESSNUMBER": "700",
        "MILKWEED": true,
        "WARD": 2,
        "NEIGHBORHOOD": "" # Empty neighborhood string
    },
    // ... more project dictionaries
]
"""

#####################################
# Import Modules
#####################################

# Import from Python Standard Library
import json
import pathlib
import sys
from collections import Counter # Essential for counting items

# Ensure project root is in sys.path for local imports
sys.path.append(str(pathlib.Path(__file__).resolve().parent))

# Import local modules
from utils_logger import logger

#####################################
# Declare Global Variables
#####################################

FETCHED_DATA_DIR: str = "example_data"
PROCESSED_DIR: str = "example_processed"

#####################################
# Define Functions
#####################################

def count_milkweed_by_neighborhood(file_path: pathlib.Path) -> dict:
    """
    Counts the number of milkweed projects in each neighborhood from a JSON file.
    A project is considered a 'milkweed project' if its 'MILKWEED' key
    has a truthy value (e.g., true, "Yes", non-empty string, non-zero number).

    Args:
        file_path: The path to the JSON file.

    Returns:
        A dictionary mapping neighborhood name (str) to the count of milkweed projects
        in that neighborhood, sorted by count from least to greatest.
        Returns an empty dictionary if an error occurs, the file is empty,
        or no milkweed projects are found.
    """
    milkweed_neighborhood_list = []
    try:
        # Open the JSON file using the file_path
        with file_path.open('r') as file:
            # Use json.load() to read the entire JSON into a Python list of dictionaries
            project_data_list: list = json.load(file)

            if not isinstance(project_data_list, list):
                logger.error(f"JSON file {file_path} does not contain a top-level list. Unexpected format.")
                return {}
            
            if not project_data_list:
                logger.warning(f"JSON file {file_path} is empty or contains an empty list. No data to process.")
                return {}

            # Iterate directly through each project dictionary in the list
            for project_dict in project_data_list:
                # Check if "MILKWEED" key exists and its value is truthy
                is_milkweed_project = project_dict.get("MILKWEED")

                # Only process if it's identified as a milkweed project
                if is_milkweed_project:
                    # Get the neighborhood name
                    neighborhood_raw = project_dict.get("NEIGHBORHOOD")

                    # Validate neighborhood value
                    if neighborhood_raw is not None and str(neighborhood_raw).strip() != "":
                        # Convert to string and strip whitespace, in case it's numeric or has extra spaces
                        neighborhood = str(neighborhood_raw).strip()
                        milkweed_neighborhood_list.append(neighborhood)
                    else:
                        logger.warning(f"Skipping milkweed project due to invalid/missing NEIGHBORHOOD value: '{neighborhood_raw}' in {project_dict}")
                # else:
                #     logger.debug(f"Skipping project as it's not a milkweed project: {project_dict.get('MILKWEED')}")


        # Use Counter to get the counts for each neighborhood efficiently
        neighborhood_counts = Counter(milkweed_neighborhood_list)

        # Sort the dictionary by count (value) from least to greatest
        sorted_neighborhood_counts = dict(sorted(neighborhood_counts.items(), key=lambda item: item[1]))

        return sorted_neighborhood_counts

    except FileNotFoundError:
        logger.error(f"Error: JSON file not found at {file_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}. Check if it's valid JSON: {e}")
        return {}
    except Exception as e:
        logger.error(f"An unexpected error occurred while processing {file_path}: {e}")
        return {}


def process_json_file():
    """Read a JSON file, count milkweed projects by Neighborhood, and save the result."""

    # Using the same example data file name, adjust if yours is different
    input_file: pathlib.Path = pathlib.Path(FETCHED_DATA_DIR, "monarchs.json")

    # Output file name changed to reflect neighborhood analysis
    output_file: pathlib.Path = pathlib.Path(PROCESSED_DIR, "json_milkweed_by_neighborhood_counts.txt")
    
    # Call the new function to count milkweed projects by neighborhood
    neighborhood_counts = count_milkweed_by_neighborhood(input_file)

    # Create the output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Open the output file in write mode and write the results
    with output_file.open('w') as file:
        file.write("Milkweed Project Counts by Neighborhood (Least to Greatest):\n")
        if neighborhood_counts: # Check if the dictionary is not empty
            for neighborhood, count in neighborhood_counts.items():
                file.write(f"Neighborhood '{neighborhood}': {count} projects\n")
        else:
            file.write("No milkweed project data found or processed (check JSON structure and 'MILKWEED' values, or 'NEIGHBORHOOD' values).\n")
    
    # Log the processing of the JSON file
    logger.info(f"Processed JSON file: {input_file}, Results saved to: {output_file}")

#####################################
# Main Execution
#####################################

if __name__ == "__main__":
    logger.info("Starting JSON processing...")
    process_json_file()
    logger.info("JSON processing complete.")