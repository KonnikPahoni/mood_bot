FROM python:3.10

WORKDIR /

COPY . /

RUN pip3 install -r requirements.txt

EXPOSE 80
EXPOSE 443

ENV TZ "UTC"

RUN echo "UTC" > /etc/timezone
RUN echo "UTC" > /etc/localtime
RUN dpkg-reconfigure -f noninteractive tzdata

CMD ["main.py"]

ENTRYPOINT ["python3"]