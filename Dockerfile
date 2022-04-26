FROM python:3.9-slim

RUN pip install pipenv

COPY Pipfile* /tmp

RUN cd /tmp && pipenv lock --keep-outdated --requirements > requirements.txt

RUN pip install -r /tmp/requirements.txt


COPY ./app /app
COPY main.py /

RUN pip install -r /tmp/requirements.txt

EXPOSE 8001

WORKDIR /

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]