# Sales Automation - Python 3 (FastAPI)


## Setup

First make sure you `cd` into the `server` folder

Create a `.env` file and add the following (adjust for your own setup):
```
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
```

### Virtual environment

Create and activate your virtual environment and install all dependencies with `pip install -r requirements.txt`

Note: you may be prompted to install rust, since the cryptography package [depends on rust](https://cryptography.io/en/latest/faq/#why-does-cryptography-require-rust)

##### Note for VS Code users:

- if it doesn't detect your venv automatically, make sure to set your python environment manually to, for example `server/venv/bin/python`.
- to maximize the typing benefits, it is encouraged to use the Pylance `python.languageServer` vscode setting.

### Seeding the Postgres database

Note: Make sure the database already exists, and that the name matches in `.env`

### Create the tables
 
`python db_init.py` (use `python db_init.py drop` to reset the database at any point)

### Populate the seed data

`python seed.py`

### Run the server

`python main.py`


## Auto-generated OpenAPI Documentation

##### Once you have the server running, go to `localhost:3001/docs`

![image](https://user-images.githubusercontent.com/14207512/141251730-2394abac-d36a-4d0c-a01b-48da7495b56b.png)


##### You can see alternate version at `localhost:3001/redoc`

![image](https://user-images.githubusercontent.com/14207512/141251662-423b0683-9161-46cd-b721-83b7952c4408.png)

## Formatting

Black is included in the environment, and should be run before committing files.

`cd server`

`black .`

## Environment Variables Required in .env file

ENVIRONMENT VARIABLE | DESCRIPTION
-------------------- | ------
DATABASE_URL | The database URL
CSV_FILES_PATH | The path to the CSV file store on server disk

## API Configuration Parameters

CONFIGURATION PARAMETER | DESCRIPTION | VALUES
----------------------- | ----------- | ------
MAX_FILE_SIZE | The maximum file size allowed | 200 MB
MAX_NUMBER_OF_ROWS | The maximum number of rows that will be processed | 1000000
CSV_FILES_PATH | The file store in server disk | config gets it from .env file
ALLOWED_MIME_TYPES | The file types allowed for upload |  Set in config file: text/csv, text/plain

## Endpoints Implemented

METHOD | ENDPOINT | SUCCESS CODE
------ | -------- | ------------
POST | `/api/prospect_files/import` | 202 (ACCEPTED)
GET | `/api/prospect_files/:id/progress` | 200 (OK)