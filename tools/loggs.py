from datetime import datetime
import logging
import os

version = '1.03 beta'
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, r"Trade-Bot")
user_count = None
actions_log_file_path = os.path.join(files_dir, 'logs', 'actions.log')
error_logs_log_file_path = os.path.join(files_dir, 'logs', 'error_logs.log')
finish_trade_log_file_path = os.path.join(files_dir, 'logs', 'finish_trade_log.log')
system_logs_log_file_path = os.path.join(files_dir, 'logs', 'system_logs.log')
print(system_logs_log_file_path)
# Configure the 'actions.log' logger

error_logs_logger = logging.getLogger('error_logs_log')
error_logs_logger.setLevel(logging.ERROR)
error_logs_handler = logging.FileHandler(error_logs_log_file_path)
error_logs_handler.setFormatter(logging.Formatter(f'{version} - %(asctime)s - %(levelname)s - %(message)s'))
error_logs_logger.addHandler(error_logs_handler)


system_log = logging.getLogger('system_log')
system_log.setLevel(logging.INFO)
system_log_handler = logging.FileHandler(system_logs_log_file_path)
system_log_handler.setFormatter(logging.Formatter(f'{version} - %(asctime)s - %(levelname)s - %(message)s'))
system_log.addHandler(system_log_handler)

