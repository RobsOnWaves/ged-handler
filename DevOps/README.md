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

## Using this Image 
For all uses you should download the stacked apps and init files from GitHub

### Local run with default credentials (not to be used for public access)

1. Starting the service

Download the content of the folder [stacked_apps](https://github.com/RobsOnWaves/ged-handler/tree/GED-38-create-a-readme-on-how-to-launch-the-app-with-docker-compose-and-how-to-use-it/DevOps/apps/stacked_apps) in a dedicated folder (for the example, we will keep that is in the repo "stacked_apps").

The content of your dedicated folder should look like this:
	
	── stacked_apps
    	├── docker-compose.yaml
    	└── mongo_ged.js

Then ```cd``` to ```stacked_apps``` and run the following command:

```console
$ docker compose up -d
```
Or (depending of the version of your Docker Engine)

```console
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

### Run with customized credentials (for public access)
1. Getting hashed password for admin and standard user of the app 

You can use this website to generate hashed password (bcrypt is used): [bcrypt online](https://bcrypt.online/)
2. Modifying the MongoDB init files for to implement the new hashed passwords
3. Modifying the docker-compose.yaml for changing the MongoDB admin user password
