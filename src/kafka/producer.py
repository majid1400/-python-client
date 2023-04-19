import json
import time
from uuid import uuid4
import elasticapm
from confluent_kafka import Producer
from config import Config
from kafka.apm_trans import ApmTransaction
from kafka.log_mangment import logger

# Set up Elastic APM
apm_client = elasticapm.Client(service_name=Config.APM_SERVICE_NAME, server_url=Config.APM_SERVER_URL,
                               environment=Config.ENV)
elasticapm.instrument()

# Set up Kafka producer
producer = Producer({
    'bootstrap.servers': Config.BOOTSTRAP_SERVERS,
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': "SCRAM-SHA-512",
    'sasl.username': Config.SASL_USERNAME,
    'sasl.password': Config.SASL_PASSWORD,
})


# Deliver report callback function
def delivery_report(err, msg):
    if err is not None:
        logger.error(f"message delivery failed: {err}")
        apm_client.capture_exception()
    else:
        logger.info(f"message delivered: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
        with ApmTransaction(apm_client, name=f'kafka_producer_{msg.topic()}'):
            metric_data = {
                'timestamp': time.time(),
                'message': msg,
                'topic': msg.topic(),
                'partition': msg.partition(),
                'offset': msg.offset()
            }
            apm_client.capture_message("Message sent to Kafka topic", custom=metric_data, tags={'status': 'success'})


def send_to_kafka(massege: dict, topic: str) -> None:
    try:
        with elasticapm.capture_span("kafka_producer"):
            producer.produce(topic=topic,
                             value=json.dumps(massege),
                             key=uuid4().hex,
                             callback=delivery_report)
    except KeyboardInterrupt:
        return

    producer.flush()


if __name__ == '__main__':
    # test producer kafka
    for _ in range(1000):
        send_to_kafka({'key': 'value'}, 'test_topic')
