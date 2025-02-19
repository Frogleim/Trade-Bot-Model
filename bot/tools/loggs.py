from datetime import datetime
import logging
import os

version = '1.03 beta'
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, r"app")
print(files_dir)

user_count = None

# Define log file paths
actions_log_file_path = os.path.join(files_dir, 'logs', 'actions.log')
error_logs_log_file_path = os.path.join(files_dir, 'logs', 'error_logs.log')
debug_logs_log_file_path = os.path.join(files_dir, 'logs', 'debug_trade_log.log')
system_logs_log_file_path = os.path.join(files_dir, 'logs', 'system_logs.log')

print(system_logs_log_file_path)

# Common formatter
formatter = logging.Formatter(f'{version} - %(asctime)s - %(levelname)s - %(message)s')

# Function to configure a logger
def setup_logger(name, log_file, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console (terminal) handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Configure loggers
error_logs_logger = setup_logger('error_logs_log', error_logs_log_file_path, logging.ERROR)
system_log = setup_logger('system_log', system_logs_log_file_path, logging.INFO)
debug_log = setup_logger('debug_trade_log', debug_logs_log_file_path, logging.DEBUG)

# Example usage
system_log.info("✅ System log initialized.")
debug_log.debug("🔍 Debug log started.")
error_logs_logger.error("❌ Example error log.")