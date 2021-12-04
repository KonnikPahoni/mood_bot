FROM python:3.10

WORKDIR /

COPY requirements.txt /

RUN pip3 install -r requirements.txt

COPY . /

ENV TZ "UTC"

RUN echo "UTC" > /etc/timezone
RUN echo "UTC" > /etc/localtime
RUN dpkg-reconfigure -f noninteractive tzdata