import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

root_path = Path(__file__).parent
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# add handler
file_h = RotatingFileHandler(f'{root_path}/kafka.log', maxBytes=200000, backupCount=2)
stream_h = logging.StreamHandler()

# create formatter
formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s')

# add the formatter to the handler
file_h.setFormatter(formatter)
stream_h.setFormatter(formatter)

# add the setLevel to the handler
file_h.setLevel(logging.ERROR)
stream_h.setLevel(logging.DEBUG)

# add the handlers to the logger
logger.addHandler(file_h)
logger.addHandler(stream_h)
