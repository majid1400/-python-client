FROM python:3.7-slim

#ENV http_proxy=http://proxy.kavosh.org:808
#ENV https_proxy=http://proxy.kavosh.org:808

WORKDIR /opt/app
COPY requirements.txt .
RUN pip install  --proxy=http://proxy.kavosh.org:808 -r requirements.txt
RUN pip install  --proxy=http://proxy.kavosh.org:808 nltk
RUN [ "python", "-c", "import nltk; nltk.set_proxy('http://proxy.kavosh.org:808'); nltk.download('punkt')" ]

COPY /src .

ADD ca.crt /usr/local/share/ca-certificates/ca.crt
RUN chmod 644 /usr/local/share/ca-certificates/ca.crt && update-ca-certificates

CMD ["python", "sentiment_tagger.py"]


# docker run -d --restart on-failure -e YEKTA_SENTIMENT_SHAHAB_DOMAIN='10.220.0.49' -e YEKTA_SENTIMENT_SHAHAB_USERNAME='export' -e YEKTA_SENTIMENT_SHAHAB_PASSWORD='shahab123123' -e YEKTA_SENTIMENT_URL_CONNECTION_GET_DB='https://markaz_write:W!_agG:ESstBTKrp@10.250.0.17:22222/es/' -e YEKTA_SENTIMENT_URL_CONNECTION_INSERT_DB='https://markaz_write:W!_agG:ESstBTKrp@10.250.0.17:22222/es/' -e YEKTA_SENTIMENT_RABBITMQ_HOST='10.250.0.128' -e YEKTA_SENTIMENT_CONNECTION_DB='es__twtlginsfb_current__prd02' -e YEKTA_SENTIMENT_RABBITMQ_VIRTUAL_HOST="/" yekta_sentiment:1.0
