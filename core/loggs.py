import os
import logging
from datetime import datetime


base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, r"coins_trade")
user_count = None
actions_log_file_path = os.path.join(files_dir, 'logs', 'actions.log')
error_logs_log_file_path = os.path.join(files_dir, 'logs', 'error_logs.log')
finish_trade_log_file_path = os.path.join(files_dir, 'logs', 'finish_trade_log.log')
system_logs_log_file_path = os.path.join(files_dir, 'logs', 'system_logs.log')

# Configure the 'actions.log' logger
actions_logger = logging.getLogger('actions_log')
actions_logger.setLevel(logging.INFO)
actions_handler = logging.FileHandler(actions_log_file_path)
actions_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
actions_logger.addHandler(actions_handler)

finish_trade_log = logging.getLogger('finish_trade_log')
finish_trade_log.setLevel(logging.INFO)
finish_trade_handler = logging.FileHandler(finish_trade_log_file_path)
finish_trade_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
finish_trade_log.addHandler(finish_trade_handler)

# Configure the 'error_logs.log' logger
error_logs_logger = logging.getLogger('error_logs_log')
error_logs_logger.setLevel(logging.ERROR)
error_logs_handler = logging.FileHandler(error_logs_log_file_path)
error_logs_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
error_logs_logger.addHandler(error_logs_handler)


system_log = logging.getLogger('system_log')
system_log.setLevel(logging.WARNING)
system_log_handler = logging.FileHandler(system_logs_log_file_path)
system_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
system_log.addHandler(system_log_handler)

current_datetime = datetime.now()
print(current_datetime)

