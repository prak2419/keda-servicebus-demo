FROM python:3.8

RUN apt-get update

WORKDIR /usr/src/app

COPY pysb.py ./

COPY requirements.txt ./

RUN pip install -r requirements.txt

CMD [ "python", "pysb.py" ]