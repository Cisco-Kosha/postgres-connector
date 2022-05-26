# PostgreSQL Connector


Postgres connector is a standalone web server that turns your PostgreSQL database directly into a RESTful API. The structural constraints and permissions in the database determine the API endpoints and operations.

![Postgres](images/postgresql.png)

## Motivation

Using this connector is an alternative to manual CRUD programming. Custom API servers suffer problems. Writing business logic often duplicates, ignores or hobbles database structure. The connector philosophy establishes a single declarative source of truth: the data itself.

## Security
The connector handles authentication (via JSON Web Tokens) and delegates authorization to the role information defined in the database. This ensures there is a single declarative source of truth for security. When dealing with the database the server assumes the identity of the currently authenticated user, and for the duration of the connection cannot do anything the user themselves couldn't. Other forms of authentication can be built on top of the JWT primitive. See the docs for more information.

## Versioning
A robust long-lived API needs the freedom to exist in multiple versions. PG connector does versioning through database schemas. This allows you to expose tables and views without making the app brittle. Underlying tables can be superseded and hidden behind public facing views.

## Self-documentation
PG connector uses the OpenAPI standard to generate up-to-date documentation for APIs. You can use a tool like Swagger-UI to render interactive documentation for demo requests against the live API server.

## Development
### Build

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

### Running locally

To run the project, simply provide env variables to point the app to a DB backend, currently works with PostgreSQL and Mysql backends


```bash
DATABASE=postgresql DB_USER=postgres DB_PASSWORD=<password> DB_SERVER=localhost DB_NAME=postgres uvicorn main:app --reload --workers 1 --host 0.0.0.0 --port 8001
```


This will start a worker and expose the API on port `8001` on the host machine.


### Running locally via docker

To start a postgresql or mysql database locally using docker, run either of the following commands:

```bash
docker run -d \
	--name postgres-connector \
	-e POSTGRES_PASSWORD=<PW> \
	-v ${HOME}/postgres-data/:/var/lib/postgresql/data \
        -p 5432:5432 \
        postgres


```
