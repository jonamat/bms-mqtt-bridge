FROM python:alpine3.19

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY server.py /app/ 
WORKDIR /app

CMD ["python", "server.py"]
