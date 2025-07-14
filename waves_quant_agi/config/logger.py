# config/logger.py

import logging
import sys

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler("logs/waves.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger = logging.getLogger("waves")
logger.setLevel(logging.DEBUG)
logger.addHandler(stdout_handler)
logger.addHandler(file_handler)
