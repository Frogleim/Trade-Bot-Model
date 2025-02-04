FROM python:3.11

RUN pip install --upgrade pip


ENV PYTHONDONTWRITEBYTECODE=1\
PYTHONNUNBUFFERED=1

COPY requirements.txt .
RUN apt-get update \
    && apt-get -y install libpq-dev gcc && apt-get install -y iputils-ping
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app


ENTRYPOINT ["python3", "main.py"]