FROM python:3.6-slim-stretch

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
COPY setup.py /usr/src/app/
COPY service /usr/src/app/
COPY api_tools /usr/src/app/api_tools

RUN pip install -e .

EXPOSE 5000
ENV FLASK_APP=run

CMD ["flask", "run", "--host", "0.0.0.0"]