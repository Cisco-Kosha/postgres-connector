# Kosha PostgreSQL Connector

PostgreSQL is an open-source, relational database that enable you to efficiently store, retrieve, and manipulate data for your applications. PostgreSQL supports a wide range of data types, advanced querying capabilities, and features such as transactions and concurrency control, making it suitable for complex applications. 

The Kosha PostgreSQL connecter enables you to perform REST API operations from the PostgreSQL API in your Kosha workflow or custom application. Using the Kosha PostgreSQL connecter, you can directly access PostgreSQL to:

* Manage table records
* Get table metadata and schemas
* Manage stored procedures

## Useful Actions

You can use the Kosha PostgreSQL connector to perform a variety of functions related to managing database tables.

Refer to the Kosha PostgreSQL connector [API specification](openapi.json) for details.

### Table records

A table record is a single row of data within a table. Use the PostgreSQL connector to:

* Create, delete, and read records
* Read records by query params

### Table metadata

Table metadata describes tables in the database and includes details such as the table name, column names, and data types of the columns. Use the Kosha PostgreSQL connector to retrieve metadata for tables and table columns.

### Database schemas

A database schema organizes database objects such as tables, views, indexes, procedures, and other related entities. Use the PostgreSQL connector to get schemas for a database.

### Stored procedures

Stored procedures enable you to group related database operations, improve performance, ensure data consistency, and promote code reusability and security in your applications. Use the PostgreSQL connector to:

* Create, get, and delete user-defined functions
* Execute RPC functions

## Authentication

To authenticate when provisioning the Kosha PostgreSQL connector, you need your:

* PostgreSQL database username and password
* PostgreSQL database host
* PostgreSQL database name