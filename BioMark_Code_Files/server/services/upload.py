import os, sys
import pandas as pd
import json
import time

# Add modules directory to path and import helper
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.utils import load_table
from modules.logger import logging


def load_data(data_path, outdir):
    os.makedirs(outdir, exist_ok=True)
    logging.info(f"load_data: Trying to load '{data_path}'.")
    
    # Retry reading the file several times (retry mechanism)
    max_retries = 5
    for attempt in range(max_retries):
        try:
            # Wait a bit before each attempt, increase delay each time
            time.sleep(0.5 * (attempt + 1)) # Delay increases each attempt (0.5s, 1s, 1.5s...)

            if not os.path.exists(data_path):
                logging.warning(f"load_data (Attempt {attempt+1}/{max_retries}): '{data_path}' not found yet. Waiting...")
                continue # Go to next attempt
            
            file_size = os.path.getsize(data_path)
            if file_size == 0:
                logging.warning(f"load_data (Attempt {attempt+1}/{max_retries}): '{data_path}' is empty (0 bytes). Waiting...")
                continue # Go to next attempt
                
            logging.info(f"load_data (Attempt {attempt+1}/{max_retries}): '{data_path}' file size: {file_size} bytes.")

            # Use engine='python' and sep=',' for more flexible reading
            # on_bad_lines='skip' is used for error tolerance
            df = load_table(data_path)
            
            if df.empty:
                logging.warning(f"load_data (Attempt {attempt+1}/{max_retries}): '{data_path}' read but DataFrame is empty. Probably no header or no data.")
                continue # Go to next attempt
            
            logging.info(f"load_data: '{data_path}' successfully read. Shape: {df.shape}")
            return df

        except pd.errors.EmptyDataError as e:
            logging.error(f"load_data (Attempt {attempt+1}/{max_retries}): EmptyDataError in '{data_path}': {e}")
            if attempt == max_retries - 1:
                raise # Raise if still error on last attempt
        except pd.errors.ParserError as e:
            logging.error(f"load_data (Attempt {attempt+1}/{max_retries}): ParserError in '{data_path}': {e}")
            if attempt == max_retries - 1:
                raise # Raise if still error on last attempt
        except FileNotFoundError:
            logging.error(f"load_data (Attempt {attempt+1}/{max_retries}): '{data_path}' not found.")
            if attempt == max_retries - 1:
                raise
        except Exception as e:
            logging.critical(f"load_data (Attempt {attempt+1}/{max_retries}): Unexpected error while reading '{data_path}': {e}", exc_info=True)
            if attempt == max_retries - 1:
                raise # Raise if still error on last attempt
    
    # If all attempts fail
    raise Exception(f"'{data_path}' could not be read after {max_retries} attempts.")


def get_columns(data_path):
    logging.info(f"get_columns: Trying to get columns from '{data_path}'.")
    max_retries = 3 # Fewer attempts are enough for get_columns
    for attempt in range(max_retries):
        try:
            time.sleep(0.2 * (attempt + 1)) # Short delay
            
            if not os.path.exists(data_path):
                logging.warning(f"get_columns (Attempt {attempt+1}/{max_retries}): '{data_path}' not found yet.")
                continue
            
            file_size = os.path.getsize(data_path)
            if file_size == 0:
                logging.warning(f"get_columns (Attempt {attempt+1}/{max_retries}): '{data_path}' is empty (0 bytes).")
                continue
            
            logging.info(f"get_columns (Attempt {attempt+1}/{max_retries}): '{data_path}' file size: {file_size} bytes.")

            # Read only the header row to get column names
            df = load_table(data_path, header_only=True)
            columns = df.columns.tolist()
            if not columns: # If column list is empty
                logging.warning(f"get_columns (Attempt {attempt+1}/{max_retries}): '{data_path}' returned empty column list after reading.")
                continue

            logging.info(f"get_columns: Columns successfully retrieved from '{data_path}': {columns}")
            return columns
        except pd.errors.EmptyDataError as e:
            logging.error(f"get_columns (Attempt {attempt+1}/{max_retries}): EmptyDataError in '{data_path}': {e}")
            if attempt == max_retries - 1:
                return []
        except pd.errors.ParserError as e:
            logging.error(f"get_columns (Attempt {attempt+1}/{max_retries}): ParserError in '{data_path}': {e}")
            if attempt == max_retries - 1:
                return []
        except FileNotFoundError:
            logging.error(f"get_columns (Attempt {attempt+1}/{max_retries}): '{data_path}' not found.")
            if attempt == max_retries - 1:
                return []
        except Exception as e:
            logging.critical(f"get_columns (Attempt {attempt+1}/{max_retries}): Unexpected error while reading columns from '{data_path}': {e}", exc_info=True)
            if attempt == max_retries - 1:
                return []
    return [] # Return empty list if all attempts fail

# Main script execution
if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Usage: python upload.py <data_file_path>")
        sys.exit(1)
        
    data_path = sys.argv[1]
    base_name = os.path.basename(data_path)
    file_name_without_ext = os.path.splitext(base_name)[0]
    outdir = os.path.join("results", file_name_without_ext)

    try:
        columns = get_columns(data_path)
        
        print(json.dumps(columns))

    except Exception as e:
        logging.critical(f"Main script error: Error occurred while processing '{data_path}': {e}", exc_info=True)
        sys.stderr.write(f"Python script execution failed: {e}\n")
        sys.exit(1)