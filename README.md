# Kosha SQL Connector

## Build

Install Python 3.7 (or later) on your machine.

Install pipenv

```bash
pip install pipenv
```

To start the virtualenv of the project, run
```
    pipenv shell
```

To install dependencies, run
```
    pipenv install
```

## Run

To run the project, simply provide env variables to point the app to a DB backend, currently works with PostgreSQL and Mysql backends

E.g., to start the app with PG backend

```bash
DATABASE=postgresql DB_USER=postgres DB_PASSWORD=<password> DB_SERVER=localhost DB_NAME=postgres uvicorn main:app --reload --workers 1 --host 0.0.0.0 --port 8001
```

E.g., to start the app with MYSQL backend
```bash
DATABASE=mysql DB_USER=root DB_PASSWORD=<password> DB_SERVER=localhost DB_NAME=test uvicorn main:app --reload --workers 1 --host 0.0.0.0 --port 8001

```

This will start a worker and expose the API on port `8001` on the host machine.

Alternatively, 

## Development

To start a postgresql or mysql database locally using docker, run either of the following commands:

```bash
docker run -d \
	--name kosha-postgres \
	-e POSTGRES_PASSWORD=kosha \
	-v ${HOME}/postgres-data/:/var/lib/postgresql/data \
        -p 5432:5432 \
        postgres

docker run \
--detach \
--name=kosha-mysql \
--env="MYSQL_ROOT_PASSWORD=kosha" \
--publish 6603:3306 \
--volume=${HOME}/mysql-data/:/var/lib/mysql \
mysql


```
Also, create a few tables in the database to start playing around. 
Currently, `sql-connector` doesn't support creating new tables, but it is on our TODO list.

## Docs

Swagger docs is available at `https://localhost:8001/docs`
