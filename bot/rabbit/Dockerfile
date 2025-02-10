FROM python:3.9

WORKDIR /app

COPY receiver.py ./

RUN pip install pika

CMD ["python", "receiver.py"]