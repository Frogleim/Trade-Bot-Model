FROM python:3.11
RUN apt-get update
RUN mkdir "btc"
WORKDIR btc
COPY . /btc
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "main.py"]