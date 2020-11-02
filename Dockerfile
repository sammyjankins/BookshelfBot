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
RUN pip3 install psycopg2-binary
RUN pip3 install -r requirements.txt


# ENV LANG en_US.UTF-8
RUN apt-get install -y language-pack-ru
ENV LANGUAGE ru_RU.UTF-8
ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8
RUN locale-gen ru_RU.UTF-8 && dpkg-reconfigure locales

COPY . /code/

