# scripts/processor.py

import os
import pandas as pd
import polars as pl
import shutil
import yaml
import logging
import time

def load_config(config_path):
    """
    Load configuration from a YAML file.
    
    Args:
        config_path (str): Path to the configuration file.
    
    Returns:
        dict: Loaded configuration as a dictionary.
    """
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
        
def process_with_pandas(file_path, output_dir, rows_per_file):
    """
    Process a file using Pandas and split it into multiple smaller files.
    
    Args:
        file_path (str): Path to the input file (.xlsx or .csv).
        output_dir (str): Directory to store the output files.
        rows_per_file (int): Number of rows per split file.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    # Read the file based on its extension
    if ext == '.xlsx':
        df = pd.read_excel(file_path, engine='openpyxl')
        num_rows = len(df)
        write_chunk = lambda chunk, i: chunk.to_excel(os.path.join(output_dir, f'part_{i+1}.xlsx'), index=False)
    elif ext == '.csv':
        num_rows = sum(1 for _ in open(file_path)) - 1  # Get number of rows excluding header
        write_chunk = lambda chunk, i: chunk.to_csv(os.path.join(output_dir, f'part_{i+1}.csv'), index=False)
    else:
        logging.error(f'Unsupported file type: {ext}')
        return

    num_chunks = num_rows // rows_per_file + (1 if num_rows % rows_per_file else 0)
    
    # Process CSV in chunks to save memory
    if ext == '.csv':
        for i, chunk in enumerate(pd.read_csv(file_path, chunksize=rows_per_file)):
            write_chunk(chunk, i)
    else:
        for i in range(num_chunks):
            start_row = i * rows_per_file
            end_row = min(start_row + rows_per_file, num_rows)
            chunk = df.iloc[start_row:end_row]
            write_chunk(chunk, i)
    
    logging.info(f'Processed {file_path} with Pandas into {num_chunks} files.')

def process_with_polars(file_path, output_dir, rows_per_file):
    """
    Process a file using Polars and split it into multiple smaller files.
    
    Args:
        file_path (str): Path to the input file (.xlsx or .csv).
        output_dir (str): Directory to store the output files.
        rows_per_file (int): Number of rows per split file.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    # Read the file based on its extension
    if ext == '.xlsx':
        df = pl.read_excel(file_path)
        write_chunk = lambda chunk, i: chunk.write_excel(os.path.join(output_dir, f'part_{i+1}.xlsx'))
    elif ext == '.csv':
        df = pl.read_csv(file_path)
        write_chunk = lambda chunk, i: chunk.write_csv(os.path.join(output_dir, f'part_{i+1}.csv'))
    else:
        logging.error(f'Unsupported file type: {ext}')
        return

    num_rows = len(df)
    num_chunks = num_rows // rows_per_file + (1 if num_rows % rows_per_file else 0)
    
    for i in range(num_chunks):
        chunk = df[i * rows_per_file : (i + 1) * rows_per_file]
        write_chunk(chunk, i)
    
    logging.info(f'Processed {file_path} with Polars into {num_chunks} files.')

def retry_on_failure(func, *args, **kwargs):
    """
    Retry a function call on failure based on the configuration settings.
    
    Args:
        func (callable): The function to call.
        *args: Variable length argument list for the function.
        **kwargs: Arbitrary keyword arguments for the function.
    """
    config = load_config('./config/settings.yaml')
    retries = config['max_retries']
    delay = config['retry_delay_seconds']
    
    for attempt in range(retries):
        try:
            func(*args, **kwargs)
            break
        except Exception as e:
            logging.error(f'Attempt {attempt + 1} failed: {e}')
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                logging.error(f'All {retries} attempts failed.')

def setup_logging(log_directory):
    """
    Set up logging configuration.
    
    Args:
        log_directory (str): Directory to store log files.
    """
    os.makedirs(log_directory, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(log_directory, 'processor.log'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def process_file(file_path, config):
    """
    Process a single file based on its size using either Pandas or Polars.
    
    Args:
        file_path (str): Path to the file to be processed.
        config (dict): Configuration dictionary.
    """
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    try:
        if file_size_mb < config['pandas_threshold_mb']:
            retry_on_failure(process_with_pandas, file_path, config['output_directory'], config['rows_per_file'])
        else:
#            retry_on_failure(process_with_polars, file_path, config['output_directory'], config['rows_per_file'])
             raise Exception(f"File size {file_size_mb:.2f} MB exceeds the Pandas threshold of {config['pandas_threshold_mb']} MB. Processing stopped.")
        
        # Move processed file to archive
        shutil.move(file_path, config['archive_directory'])
    except Exception as e:
        logging.error(f'Error processing {file_path}: {e}')



