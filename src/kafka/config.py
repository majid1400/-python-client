from os import environ
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    ######################### Application Config ########################################
    DEBUG = bool(int(environ.get("CONFIG_DEBUG", "0")))
    ENV = environ.get("CONFIG_ENV", "production")
    BASEPATH = Path(__file__).parent.parent / "models"
    ######################### Kafka Application Config ##################################
    TOPIC_INPUT = environ.get('CONFIG_KAFKA_TOPIC_INPUT', None)
    GROUP_ID = environ.get('CONFIG_KAFKA_GROUP_ID', None)
    AUTO_OFFSET_RESET = environ.get('CONFIG_KAFKA_AUTO_OFFSET_RESET', 'earliest')
    BOOTSTRAP_SERVERS = environ.get('CONFIG_KAFKA_BOOTSTRAP_SERVERS', None)
    SASL_USERNAME = environ.get('CONFIG_KAFKA_AUTO_SASL_USERNAME', None)
    SASL_PASSWORD = environ.get('CONFIG_KAFKA_AUTO_SASL_PASSWORD', None)
    ######################### APM Config ################################################
    APM_SERVICE_NAME = environ.get('CONFIG_APM_SERVICE_NAME', None)
    APM_SERVER_URL = environ.get('CONFIG_APM_SERVER_URL', None)
