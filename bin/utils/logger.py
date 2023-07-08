import logging
import os

# Create a custom logger
logger = logging.getLogger(__name__)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('app.log')

# Set level for handlers based on environment variable
log_level = os.getenv('LOG_LEVEL', 'WARNING').upper()
log_level_file = os.getenv('LOG_LEVEL_FILE', 'ERROR').upper()
valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

if log_level not in valid_log_levels:
    raise ValueError(f'Invalid log level: {log_level}')

if log_level_file not in valid_log_levels:
    raise ValueError(f'Invalid log level: {log_level_file}')

# Set level for handlers
console_handler.setLevel(log_level)
file_handler.setLevel(log_level_file)

# Create formatters and add it to handlers
console_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_format)

file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
