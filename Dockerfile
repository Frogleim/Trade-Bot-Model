FROM python:3.11
RUN apt-get update
RUN mkdir "app"
WORKDIR app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "main.py"]