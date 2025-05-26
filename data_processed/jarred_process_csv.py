"""
Process a CSV file on animal bites in STL city from 2013 to 2025.
"""

#####################################
# Import Modules
#####################################

# Import from Python Standard Library
import pathlib
import csv
import sys
from collections import Counter # Import Counter for easy counting

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

def analyze_by_ward(file_path: pathlib.Path) -> dict:
    """
    Analyzes how many animal bites happen per ward, considering only rows past 3900.
    Returns a dictionary mapping ward number (int) to bite count,
    sorted by bite count from least to greatest.
    """
    ward_list = []
    # Define the row number from which to start processing
    START_ROW_FOR_PROCESSING = 3900 

    try:
        with file_path.open('r') as file:
            dict_reader = csv.DictReader(file)
            
            # Use enumerate to get both the row number (starting from 0 for header, 1 for first data row)
            # and the row dictionary. We add 1 to `idx` to get the actual line number.
            for idx, row in enumerate(dict_reader):
                current_row_number = idx + 2 # +1 for 0-based index, +1 for header row

                # Only process rows if their number is greater than START_ROW_FOR_PROCESSING
                if current_row_number > START_ROW_FOR_PROCESSING:
                    try:
                        # Convert to int, as ward numbers are typically integers
                        ward = int(float(row["WARD"]))
                        if 1 <= ward <= 14: # Assuming valid wards are 1 through 14
                            ward_list.append(ward)
                        else:
                            logger.warning(f"Ward number out of expected range (1-14) at row {current_row_number}: {row['WARD']}")
                    except ValueError as e:
                        logger.warning(f"Skipping row {current_row_number} due to invalid WARD value: '{row.get('WARD', 'N/A')}' ({e})")
                    except KeyError:
                        logger.warning(f"Skipping row {current_row_number} as 'WARD' column not found.")

        # Use collections.Counter to efficiently count occurrences
        ward_counts = Counter(ward_list)

        # Convert to a regular dictionary and sort by count (value)
        sorted_stats = dict(sorted(ward_counts.items(), key=lambda item: item[1]))

        return sorted_stats

    except FileNotFoundError:
        logger.error(f"Error: CSV file not found at {file_path}")
        return {}
    except Exception as e:
        logger.error(f"An unexpected error occurred while processing {file_path}: {e}")
        return {}


def process_csv_file():
    """Read a CSV file, analyze animal bites by ward, and save the results."""
    
    input_file = pathlib.Path(FETCHED_DATA_DIR, "animal_bites.csv")
    output_file = pathlib.Path(PROCESSED_DIR, "animal_bites_stats.txt")
    
    # Call your new function to process YOUR CSV file
    stats = analyze_by_ward(input_file)

    # Create the output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Open the output file in write mode and write the results
    with output_file.open('w') as file:
        file.write(f"Animal Bites by Ward (Least to Greatest, from row 3901 onwards):\n")
        if stats:
            for ward, count in stats.items():
                file.write(f"Ward {ward}: {count} bites\n")
        else:
            file.write("No data processed or found (possibly due to row limit).\n")
    
    logger.info(f"Processed CSV file: {input_file}, Statistics saved to: {output_file}")

#####################################
# Main Execution
#####################################

if __name__ == "__main__":
    logger.info("Starting CSV processing...")
    process_csv_file()
    logger.info("CSV processing complete.")