FROM python:3.9.5-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install --system --deploy --ignore-pipfile

COPY ./app /app
COPY main.py /

EXPOSE 8001

WORKDIR /

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]