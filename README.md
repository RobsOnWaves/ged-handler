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

It also can be used as a FastAPI with OAuth2 + MongoDB boilerplate

The project is managed through Jira contact me through [GitHub](https://github.com/RobsOnWaves) if you want to get involved in the roadmap.

The code is PEP8 compliant, scanned with Sonarlint in PyCharm and linked to SonarCloud.

[![SonarCloud](https://sonarcloud.io/images/project_badges/sonarcloud-white.svg)](https://sonarcloud.io/summary/new_code?id=RobsOnWaves_ged-handler)

# Using the Docker image 
For all uses you should download the stacked apps and init files from GitHub

## Local run with default credentials (not to be used for public access)

1. Starting the service

Download the content of the folder [stacked_apps](https://github.com/RobsOnWaves/ged-handler/tree/master/DevOps/apps/stacked_apps) in a dedicated folder (for the example, we will keep that is in the repo "stacked_apps").

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

# Dev zone
## Philosophy of the project
Though this project is aimed to be a ged files handling app, it's also a playground for Python, FastAPI & DevOps.

The code is object-oriented.

### For now, the toys I'm playing with on that project:

- Jira
- CodeSee
- Docker
- Python
- PyCharm
- Sonarlint
- SonarCloud
- PEP8 compliance

### Toys that I didn't bring to the project for now but I'm planning to bring: 
- Postman
- Jenkins (but no server = no Jenkins...)



There is no frontend for now, as I am not a frontend developer, and some help/advices would be appreciated.

## GEDCOM existing package

Please note that I found just before releasing this that there is a full package for parsing GEDCOM here : [GEDCOM](https://pypi.org/project/python-gedcom/).

I didn't conduct any kind of comparison of what it does ***vs*** what ged-handler does.

## Source treeview and files purpose
Here is a tree view of the source files with comments:

```console
`-- ged-handler
    |-- Code
    |   |-- data_in -> empty dir for internal use             
    |   |-- docker_images_builder_cross_build.sh -> script that handles docker building (called by "docker_images_builder.sh")
    |   |-- libs
    |   |   |-- ged_file_handler.py -> class for handling ged-files, standalone lib that can be used just for ged-files convertion
    |   |   |-- __init__.py
    |   |   |-- messages.py -> class where are defined all messages returned by the app
    |   |   `-- mongo_db_handler.py -> class where are abstracted all MongoDB operations
    |   |-- main.py -> used as a sandbox to test classes usages
    |   |-- public_api.py -> FastAPI routes defintions and operations
    |   |-- requirements.txt
    |   `-- tmp -> empty dir for internal use
    |-- DevOps
    |   |-- apps
    |   |   |-- ged_handler
    |   |   |   |-- docker-compose.yaml -> Standalone docker compose for ged-handler app, before launching it, be sure to create the network "ged_network" (see below for command)
    |   |   |   `-- Dockerfile -> Dockerfile for building ged-handler docker image
    |   |   |-- mongo
    |   |   |   |-- docker-compose.yaml -> Standalone docker compose for mongo app, before launching it, be sure to create the network "ged_network" (see below for command)
    |   |   |   `-- mongo_ged.js -> initialization javascript file for creating default API users
    |   |   `-- stacked_apps
    |   |       |-- docker-compose.yaml -> MongoDB + ged-handler app docker compose
    |   |       `-- mongo_ged.js -> initialization javascript file for creating default API users
    |   `-- docker_images_builder.sh -> script to build and push docker images
    |-- LICENSE
    `-- README.md
```

Command to create a docker network (when using the ```docker-compose.yaml``` that are not in stacked_apps):
```console
docker network create ged_network
```
