FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /code
RUN apt update
RUN apt install -y netcat
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
