FROM python:3.10-slim-bullseye

RUN apt-get update -yq && \
    apt-get install -y --no-install-recommends glusterfs-client

COPY requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt
RUN pip3 install -r /requirements.txt
COPY *.py /
RUN mkdir /csi
CMD python3 -u /main.py
