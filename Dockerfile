FROM ubuntu:18.04

RUN apt-get -yqq update
RUN apt-get -yqq install python3-pip python3-dev python-pip
RUN apt-get install -yqq libzbar-dev

#RUN pip install --upgrade pip

RUN mkdir /code
WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /code/
RUN pip install zbar
RUN pip3 install -r requirements.txt

COPY . /code/

