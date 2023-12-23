import uvicorn
import os
from datetime import datetime, timedelta
from typing import Union
from enum import Enum
from fastapi import Depends, FastAPI, HTTPException, status, Form, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, RedirectResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from libs.mongo_db_handler import MongoDbGed
from libs.ged_file_handler import GedFileHandler
from libs.messages import Messages
from libs.gold_digger import GoldDigger


class Roles(str, Enum):
    admin = "admin"
    user = "user"


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "11088b752484acda51943b487d8657e142e91e085187c110e0967650e7526784"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

JSON_EXTENSION = ".json"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    role: str


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(description="""
#About

GED-Handler is an authenticated app that allows you to : 
1) Store GED-files in a MongoDB database
2) Retrieve JSON genealogy objects files (imported from 1.)
3) Direct conversions from GED-files to JSON genealogy objects files

GED-Handler is written in Python with [FastAPI](https://fastapi.tiangolo.com/) and deployed with Docker (details of the 
code at: [GitHub GED-Handler repo](https://github.com/RobsOnWaves/ged-handler))
""", title="GED-Handler")


def el_parametrizor(mode_debug=False):
    if mode_debug:
        os.environ['URL_MONGO'] = "localhost:27017"

        os.environ['USR_MONGO'] = "root"

        os.environ['PWD_MONGO'] = "rootmongopwd"


el_parametrizor(False)

mongo_handler = MongoDbGed(address=os.environ['URL_MONGO'], user=os.environ['USR_MONGO'],
                           password=os.environ['PWD_MONGO'])


messages = Messages()
gold_handler = GoldDigger()


def time_window_control(date_start: datetime, date_end: datetime, current_user: User):
    time_window_validated = False
    diff_time = date_end - date_start

    if date_start.date() != date_end.date():
        status_date = "hi " + str(current_user.username) + messages.nok_string + \
                      " the dates of start and stop must be the same"

        time_window_validated = False

    elif date_start > date_end:
        status_date = "hi " + str(current_user.username) + messages.nok_string +\
                      " you can't finish before you start"

        time_window_validated = False

    elif diff_time.total_seconds() > 10800.0:
        status_date = "hi " + str(current_user.username) + messages.nok_string + \
                      " for the sake of our servers, time window limited to three hours"

        time_window_validated = False

    elif date_start > datetime.utcnow() or date_end > datetime.utcnow():
        status_date = "hi " + str(current_user.username) + messages.nok_string +\
                      " ged-handler is futuristic but does not accept dates in the future"
        time_window_validated = False
    else:
        time_window_validated = True
        status_date = messages.nok_string + "Unhandled time_window_control case"

    return {'status_date': status_date, 'time_window_validated': time_window_validated}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(users_db, username: str, password: str):
    user = get_user(users_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(mongo_handler.get_users(), username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/")
async def docs_redirect():
    return RedirectResponse(url='/docs')


@app.post("/token", response_model=Token, description="Returns a token after successful authentication")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(mongo_handler.get_users(), form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User, description="Returns information about the current logged in user")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.post("/create_user", description="Creating a new user, restricted to admin privileges")
async def create_user(user_name: str = Form(),
                      email: str = Form(regex=r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                                        description="must be an email address"),
                      full_name: str = Form(),
                      password: str = Form(min_length=10, description="mini. 10 characters"),
                      role: Roles = Form(),
                      current_user: User = Depends(get_current_active_user)):
    if current_user.role == "admin":
        return {'response': mongo_handler.insert_user(user_name, full_name, email, get_password_hash(password),
                                                      current_user.username, role)}
    else:
        return {'response': messages.nok_string}


@app.post("/ged_file", description="Uploading a ged-file to the database, restricted to admin privileges")
async def upload_ged_file(file: UploadFile,
                          ged_import_name: str = Form(description="import name: must not exist already"),
                          current_user: User = Depends(get_current_active_user)):
    if current_user.role == "admin":
        ged_handler = GedFileHandler()
        ged_handler.from_file_to_list_of_dict_with_cleanup(file, path="tmp/")
        return mongo_handler.insert_list_of_ged_objets(collection_name=ged_import_name, ged_handler=ged_handler)

    else:
        return {'response': messages.denied_entry}


@app.get("/ged_stored_collection_to_json_answer", description="Returns a JSON answer from a stored collection")
async def ged_stored_collection_to_json_answer(ged_collection_name: str,
                                               current_user: User = Depends(get_current_active_user)):

    if current_user.role in ['admin', 'user']:
        return mongo_handler.from_mongo_to_ged_list_dict(collection_name=ged_collection_name)
    else:
        return {'response': messages.nok_string}


@app.get("/ged_stored_collection_to_json_file", description="Returns a JSON file from a stored collection")
async def ged_stored_collection_to_json_file(ged_collection_name: str,
                                             current_user: User = Depends(get_current_active_user)):

    if current_user.role in ['admin', 'user']:

        with open(ged_collection_name + JSON_EXTENSION, 'w') as convert_file:
            ged_listed_dict = mongo_handler.from_mongo_to_ged_list_dict(collection_name=ged_collection_name)
            ged_handler = GedFileHandler()
            jsoned_ged = ged_handler.jsonize_ged_dict(ged_listed_dict)
            convert_file.write(jsoned_ged)

        return FileResponse(ged_collection_name + JSON_EXTENSION)

    else:
        return {'response': messages.nok_string}


@app.post("/ged_file_to_json_answer", description="Returns a converted JSON file from a ged-file"
                                                  " without storing it in the database")
async def ged_collection_to_json_answer(file: UploadFile,
                                        current_user: User = Depends(get_current_active_user)):

    if current_user.role in ['admin', 'user']:

        ged_handler = GedFileHandler()
        ged_handler.from_file_to_list_of_dict_with_cleanup(file, path="tmp/")
        return ged_handler.listed_documents

    else:
        return {'response': messages.nok_string}


@app.get("/ged_stored_collections", description="Returns a list of all stored collections")
async def ged_stored_collections(current_user: User = Depends(get_current_active_user)):

    if current_user.role in ['admin', 'user']:

        return mongo_handler.get_collections()

    else:
        return {'response': messages.nok_string}


@app.post("/ged_file_to_json_file", description="Returns a converted JSON file from a ged-file"
                                                "without storing it in the database")
async def ged_collection_to_json_file(file: UploadFile,
                                      current_user: User = Depends(get_current_active_user)
                                      ):

    if current_user.role in ['admin', 'user']:

        ged_handler = GedFileHandler()
        ged_handler.from_file_to_list_of_dict_with_cleanup(file, path="tmp/")

        with open("tmp/" + file.filename + JSON_EXTENSION, 'w') as convert_file:
            convert_file.write(ged_handler.jsonize_ged_dict(ged_handler.listed_documents))
        return FileResponse("tmp/" + file.filename + JSON_EXTENSION)

    else:
        return {'response': messages.nok_string}


@app.post("/modify_user_password", description="Modify an exiting user password, restricted to admin privileges")
async def modify_user_password(
                                          user_name: str = Form(description="user name that needs its password to "
                                                                            "be modified"),
                                          password: str = Form(min_length=10, description="mini. 10 characters"),
                                          current_user: User = Depends(get_current_active_user)):

    if current_user.role in ['admin']:

        return {'response': mongo_handler.modify_user_password(user_name=user_name,
                                                               hashed_password=get_password_hash(password))}

    else:
        return {'response': messages.nok_string}


@app.post("/gold_file_converter", description="Returns an Excel with the estimated value in euros")
async def ged_collection_to_json_file(file: UploadFile,
                                        price_per_kg: int,
                                      current_user: User = Depends(get_current_active_user)
                                      ):
    if current_user.role in ['admin', 'user']:
        coeffs = mongo_handler.get_gold_coeffs()
        return FileResponse(await gold_handler.compute_excel_file(upload_file=file,
                                                                  price_per_kg=price_per_kg,
                                                                  gold_coeffs=coeffs))

    else:
        return {'response': messages.nok_string}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
