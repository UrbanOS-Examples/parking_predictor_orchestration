FROM microsoft/mssql-tools:latest

RUN apt-get clean \
    && apt-get -y update

RUN apt-get -y install python3 \
    && apt-get -y install python3-pip \
    && apt-get -y install python3-dev \
    && apt-get -y install libpcre3 libpcre3-dev \
    && apt-get -y install build-essential \
    && apt-get -y install unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8
    
RUN pip3 install pipenv

ADD Pipfile* /

RUN pipenv lock --requirements > requirements.txt \
  && pip3 install --requirement requirements.txt

CMD [ "pipenv", "run", "python", "conductor.py" ]