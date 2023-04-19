import json
import os
import elasticapm
from elasticapm.metrics.base_metrics import MetricSet
from kafka.apm_trans import ApmTransaction
from kafka.config import Config
from kafka.log_mangment import logger
from confluent_kafka import Consumer


def _process_msg(msg, c):
    """ process message from kafka
    with it is commit kafka offset and the message is removed from the queue.
    :param msg: message row from kafka with it is processed with msg.value()
    :param c: it is an object of consumer
    :return: None
    """
    with ApmTransaction(apm_client, name="data_raw"):  # sample send transaction to apm
        data_raw = json.loads(msg.value())  # sample process message from kafka
    c.commit(msg)


def main(config):
    c = Consumer(**config['kafka_kwargs'])
    c.subscribe([config['topic']])

    while True:
        try:
            msg = c.poll(60)

            if msg is None:
                continue

            if msg.error():
                logger.error(f"#{os.getpid()} - Consumer error: {msg.error()}")
                apm_client.capture_exception()
                continue

            logger.info(f"#{os.getpid()} - Worker start - send data to _process_msg")
            print('message')
            _process_msg(msg, c)
            metricset.counter("poll_msg_counter").inc()

        except Exception as e:
            logger.exception(f'sentiment tagger #{os.getpid()} - Worker terminated {e}')
            apm_client.capture_exception()
            c.close()


def is_environment_variable():
    list_environment = {
        'TOPIC_INPUT': Config.TOPIC_INPUT,
        'GROUP_ID': Config.GROUP_ID,
        'BOOTSTRAP_SERVERS': Config.BOOTSTRAP_SERVERS,
        'SASL_USERNAME': Config.SASL_USERNAME,
        'SASL_PASSWORD': Config.SASL_PASSWORD,
        'APM_SERVER_URL': Config.APM_SERVER_URL,
        'APM_SERVICE_NAME': Config.APM_SERVICE_NAME,
    }
    for environment in list_environment:
        if list_environment[environment] is None:
            logger.error(f"The {environment} environment variable is not set.")
            exit(0)


if __name__ == '__main__':
    is_environment_variable()

    apm_client = elasticapm.Client(service_name=Config.APM_SERVICE_NAME, server_url=Config.APM_SERVER_URL)
    metricset = apm_client.metrics.register(MetricSet)
    elasticapm.instrument()

    logger.info('initial config consumer kafka')
    main(config={
        'topic': Config.TOPIC_INPUT,
        'kafka_kwargs': {
            'bootstrap.servers': Config.BOOTSTRAP_SERVERS,
            'group.id': Config.GROUP_ID,
            'auto.offset.reset': Config.AUTO_OFFSET_RESET,
            'enable.auto.commit': False,
            'security.protocol': 'SASL_SSL',
            'sasl.mechanisms': "SCRAM-SHA-512",
            'sasl.username': Config.SASL_USERNAME,
            'sasl.password': Config.SASL_PASSWORD,
        },
    })
