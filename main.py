# scripts/main.py
import os
import sys
import logging
import shutil
import yaml
from concurrent.futures import ThreadPoolExecutor
# Add the parent directory to the system path to import processor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from processor.processor import process_file, setup_logging

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

def main():
    """
    Main function to process files and handle the entire workflow.
    """
    # Load configuration
    config = load_config('./config/settings.yaml')
    
    # Setup logging
    setup_logging(config['log_directory'])
    
    # Create output directories if not exist
    os.makedirs(config['output_directory'], exist_ok=True)
    os.makedirs(config['archive_directory'], exist_ok=True)
    
    # List all files in the input directory
    files = os.listdir(config['input_directory'])
    
    if len(files) == 1:
        # Process a single file without threading
        file_path = os.path.join(config['input_directory'], files[0])
        process_file(file_path, config)
    else:
        # Use a thread pool to process files concurrently
        with ThreadPoolExecutor(max_workers=config['max_concurrent_files']) as executor:
            for filename in files:
                file_path = os.path.join(config['input_directory'], filename)
                executor.submit(process_file, file_path, config)

if __name__ == '__main__':
    main()
