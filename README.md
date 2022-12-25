# GED-Handler

# Quick reference

-	**Maintained by**:  
	[RobsOnWaves](https://github.com/RobsOnWaves)

-	**Where to get help**:  
	[GitHub GED-Handler](https://github.com/RobsOnWaves/ged-handler)

# About

GED-Handler is an authenticated (OAuth2) Rest API that allows you to : 
1) Store GED-files in a MongoDB database
2) Retrieve JSON genealogy objects files (imported from 1.)
3) Direct conversions from GED-files to JSON genealogy objects files
4) Use directly API routes from the Swagger UI

GED-Handler is written in Python with [FastAPI](https://fastapi.tiangolo.com/) and deployed with Docker (details of the code at: [GitHub GED-Handler repo](https://github.com/RobsOnWaves/ged-handler))

It's an opensource project opened to contributions, it misses frontend developments for example.

The project is managed through Jira contact me through [GitHub](https://github.com/RobsOnWaves) if you want to get involved in the roadmap.

The code is PEP8 compliant and scanned with Sonarlint.

# Using the Docker image 
For all uses you should download the stacked apps and init files from GitHub

## Local run with default credentials (not to be used for public access)

1. Starting the service

Download the content of the folder [stacked_apps](https://github.com/RobsOnWaves/ged-handler/tree/GED-38-create-a-readme-on-how-to-launch-the-app-with-docker-compose-and-how-to-use-it/DevOps/apps/stacked_apps) in a dedicated folder (for the example, we will keep that is in the repo "stacked_apps").

The content of your dedicated folder should look like this:
	
	── stacked_apps
    	├── docker-compose.yaml
    	└── mongo_ged.js

Then ```cd``` to ```stacked_apps``` and run the following command:

```bash
$ docker compose up -d
```
Or (depending on the version of your Docker Engine)

```bash
$ docker-compose up -d
```


2. Using the service

Go to [http://localhost:5555](http://localhost:5555)

You can log in with one of those credentials:

Default administrator credentials that allows you to modify passwords for a given user (to be used without the quotes):
- login: "admin"
- password: "ThisIsADummyPasswordForAdmin"

Default user credentials (to be used without the quotes):
- login: "user"
- password: "ThisIsADummyPasswordForUser"

If you just want to convert a ged file to a json file use the ```ged_file_to_json_file``` route, load ged file, click *Execute* button and in the *response body* section click *Download*.

All routes are documented in the Swagger UI you can find at [http://localhost:5555](http://localhost:5555)

## Run with customized credentials (for public access)
1. Getting hashed password for admin and standard user of the app 

Password are stored in a MongoDB initialized in ```mongo_ged.js``` (see below).

You can use this website to generate hashed password (bcrypt is used): [bcrypt online](https://bcrypt.online/)

2. Modifying the MongoDB init files for to implement the new hashed passwords

In ```mongo_ged.js``` modify the content to replace the standard hashed passwords by the ones generated before as stated here :


```javascript

db = new Mongo().getDB("GED");

db = new Mongo().getDB("USERS");

db.users.createIndex({ "user_name": 1 }, { unique: true })

db.users.insert({
    "user_name": "admin",

    "admin": {
        "username": "admin",
        "full_name": "first_name last_name",
        "email": "dummy@test.com",
        "hashed_password": "<You genrated hashed password for admin here>",
        "disabled": false,
        "created_at": ISODate("1986-06-16T17:00:00.000+02:00"),
        "created_by": "init_script",
        "role": "admin"
    }

}
)


db.users.insert({
    "user_name": "user",

    "user": {
        "username": "user",
        "full_name": "user",
        "email": "dummy@test.com",
        "hashed_password": "<You genrated hashed password for user here>",
        "disabled": false,
        "created_at": ISODate("1986-06-16T17:00:00.000+02:00"),
        "created_by": "init_script",
        "role": "user"
    }

}
)

```
Note: you can add custom users by using ```db.users.insert()``` method.

/!\ Beware, ```the mongo_ged.js``` is executed the first time you launch the MongoDB service, so, if you already launched it before you made modifications, you should delete your Docker volume attached to the MongoDB service.

3. Modifying the docker-compose.yaml for changing the MongoDB admin user password

The MongoDB root database login and password are defined in ```MONGO_INITDB_ROOT_USERNAME``` and ```MONGO_INITDB_ROOT_PASSWORD``` environment variables defined in ```docker-compose.yaml```. 

The ***ged_handler*** services uses ```USR_MONGO``` and ```PWD_MONGO``` environment variables to authenticated to the database. 

So, in order to modify the ***root*** login and password with custom ones, you should modify ```docker-compose.yaml``` as stated here:

```yaml
version: '3.7'

volumes:
  mongogeddata:

services:

  ged_handler:
    image: ged_handler
    restart: always
    environment:
      'URL_MONGO': "mongo:27017"

      'USR_MONGO': "<Name of the root user>"

      'PWD_MONGO': "<Password of the root user>"

    ports:
      - "5555:8000"

  mongo:
    image: mongo:5.0.6-focal
    restart: always
    environment:

      MONGO_INITDB_ROOT_PASSWORD: "<Password of the root user>"

      MONGO_INITDB_ROOT_USERNAME: "<Name of the root user>"

    volumes:
      - mongogeddata:/data/db
      - $PWD/mongo_ged.js:/docker-entrypoint-initdb.d/mongo-init.js:ro

    #port publishing to be removed in production
    ports:
      - "27017:27017"
```

/!\ Beware, the root user is created the first time you launch the MongoDB service, so, if you already launched it before you made modifications, you should delete your Docker volume attached to the MongoDB service.

# Sources presentation

```console
.
|-- Code
|   |-- data_in
|   |-- docker_images_builder_cross_build.sh
|   |-- libs
|   |   |-- ged_file_handler.py
|   |   |-- __init__.py
|   |   |-- messages.py
|   |   |-- mongo_db_handler.py
|   |-- main.py
|   |-- public_api.py
|   |-- requirements.txt
|   |-- tmp
|-- DevOps
|   |-- apps
|   |   |-- ged_handler
|   |   |   |-- docker-compose.yaml
|   |   |   |-- Dockerfile
|   |   |-- mongo
|   |   |   |-- docker-compose.yaml
|   |   |   |-- mongo_ged.js
|   |   |-- stacked_apps
|   |       |-- docker-compose.yaml
|   |       |-- mongo_ged.js
|   |-- docker_images_builder.sh
|   |-- install_docker.sh
|-- LICENSE
|-- README.md
```
