FROM python:3.10.4-slim

ARG GITHUB_API_KEY
WORKDIR /usr/local/app

RUN apt-get update &&\
    apt-get install -y golang-go git make libffi-dev gcc &&\
    git clone https://github.com/go-enry/go-enry

SHELL ["/bin/bash", "-c"]

RUN cd go-enry/python &&\
    pushd .. && make static && popd &&\
    pip install -r requirements.txt &&\
    python build_enry.py &&\
    python setup.py bdist_wheel &&\
    pip install ./dist/*.whl

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENV GITHUB_API_KEY=$GITHUB_API_KEY
ENV PYTHONPATH="$PYTHONPATH:/usr/local/app"
ENTRYPOINT ["python", "-u", "similar_dev_search/cli.py"]
