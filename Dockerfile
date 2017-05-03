FROM ubuntu:16.04

RUN apt-get update && apt-get install -y git python3 python3-pip python3-venv && \
    ln -s /usr/bin/python3 /usr/bin/python

RUN git clone https://github.com/spoorcc/Holtenizer.git && \
    cd Holtenizer && \
    git submodule init && \
    git submodule update && \
    pip3 install --upgrade pip && \
    pip3 install pycparser

EXPOSE 80

CMD cd Holtenizer && /bin/bash
