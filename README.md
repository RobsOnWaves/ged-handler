# GED-Handler

# Quick reference

-	**Maintained by**:  
	[RobsOnWaves](https://github.com/RobsOnWaves)

-	**Where to get help**:  
	[GitHub GED-Handler](https://github.com/RobsOnWaves/ged-handler)

# About

GED-Handler is an authenticated app that allows you to : 
1) Store GED-files in a MongoDB database
2) Retrieve JSON genealogy objects files (imported from 1.)
3) Direct conversions from GED-files to JSON genealogy objects files

GED-Handler is written in Python with [FastAPI](https://fastapi.tiangolo.com/) and deployed with Docker (details of the code at: [GitHub GED-Handler repo](https://github.com/RobsOnWaves/ged-handler))

## Using this Image 
For all uses you should download the stacked apps and init files from GitHub

### Local run with default credentials (not to be used for public access)

1. Starting the service

Default administator credentials (to be used without the quotes):
- login: "admin"
- password: "ThisIsADummyPasswordForAdmin"

Default user credentials (to be used without the quotes):
- login: "user"
- password: "ThisIsADummyPasswordForUser"

2. Using the service

### Run with customized credentials (for public access)
1. Getting hashed password for admin and standard user of the app 

You can use this website to generate hashed password (bcrypt is used): [bcrypt online](https://bcrypt.online/)
2. Modifying the MongoDB init files for to implement the new hashed passwords
3. Modifying the docker-compose.yaml for changing the MongoDB admin user password
