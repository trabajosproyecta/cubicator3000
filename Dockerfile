FROM python:3.6.5-stretch
RUN apt-get update -y

RUN mkdir /app
WORKDIR /app

# TODO: copy all neded files and serialized models 

COPY ./app .

RUN pip install -r /app/requirements.txt
