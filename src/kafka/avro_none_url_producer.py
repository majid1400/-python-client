import time
from uuid import uuid4
import elasticapm
from confluent_kafka import Producer
from config import Config
from kafka.apm_trans import ApmTransaction
from kafka.log_mangment import logger
from avro import schema, io
from avro.io import DatumWriter
from io import BytesIO

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
    avro_schema_file = "file_avro/schema-raw-data-model-value-v1.avsc"
    with open(avro_schema_file, "rb") as f:
        avro_schema = schema.parse(f.read())
    try:
        # Serialize message payload using Avro schema
        bytes_writer = BytesIO()
        datum_writer = DatumWriter(avro_schema)
        encoder = io.BinaryEncoder(bytes_writer)
        datum_writer.write(massege, encoder)
        avro_data = bytes_writer.getvalue()

        with elasticapm.capture_span("kafka_producer"):
            producer.produce(topic=topic, value=avro_data, key=uuid4().hex, callback=delivery_report)
    except KeyboardInterrupt:
        return

    producer.flush()


if __name__ == '__main__':
    # test producer kafka
    msg = {"ts": int(time.time()),
           "country": "iran",
           "platform": "twitter",
           "sub_platform": "post",
           "user_id": "123456789",
           "raw_data": "{'tes':'value'}",
           "fetch_ts": int(time.time()),
           "fetch_info": "hatagh crwler"}
    send_to_kafka(msg, 'raw-data-model')
