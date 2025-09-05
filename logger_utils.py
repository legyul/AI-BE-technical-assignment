import logging
import os
from datetime import datetime

# Path of the log file
LOG_DIR = "./implement_logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y%m%d')}.log")

# Generate logger
logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)

# Set the formatter
formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# File handler
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Conect the handler
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)