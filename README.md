

# Quarrel!

## Getting Started

### **Satisfy Python Requirements**
Before getting started, ensure you have python3 installed on your workstation. If python2 is the default, run the following commands with `python3` and `pip3`. To install all necessary python packages run:

`pip install -r requirements.txt`

#### **Ensure Database is Running**
A database should be up and running before trying to start up QUARREL. The project is currently configured to use a postgres database.

#### **Running set_environment.sh**
Run the following command:
`source scripts/set_environment.sh`

This script will set the following environmental variables.
```
   QUARREL_DATABASE_HOST     - Default localhost
   QUARREL_DATABASE_PORT     - Default 5432
   QUARREL_DATABASE_NAME     - Default quarrel
   QUARREL_DATABASE_ADMIN    - Default postgres
   QUARREL_DATABSE_PASSWORD  - Required
   EMAIL_HOST_USER         - Required
   EMAIL_HOST_PASSWORD     - Required
   BEANSTALK_FRONTEND_URL  - Default http://localhost:3000
   
```

> **_NOTE:_**  The creators of this app have stood up a testing Database that can be used freely. The connection parameters can be found in /scripts/psql_connection.sh

If you prefer to constantly be working with the same database and AWS credentials throughout multiple sessions, you can make these variables more permanent by adding them to your ~/.bashrc file, ~/.profile, or whatever startup file you use for your default shell.

If this is this is a brand new database, run the following commands to populate the database with tables based on Djongo's `models.py` file.
```
cd quarrel-backend
pyhton manage.py migrate
```

#### Start the QUARREL Application
Once the database parameters are set simply run the following commands to start the application:
```
cd quarrel-backend
python manage.py runserver
```

## Docker

If your system has [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed, we have provided accompanying Docker files with the application. This serves for quick stand-up/tear-down operations that should work across all systems.

The following commands will start up a fresh back-end of the stack (database and roots instance) with the version of the source code found on disk.

```
docker-compose build
docker-compose up -d
```
