import uvicorn
import os
from datetime import datetime, timedelta, date
from typing import Union
from enum import Enum
from fastapi import Depends, FastAPI, HTTPException, status, Form, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from libs.mongo_db_handler import MongoDbGed
from libs.ged_file_handler import GedFileHandler
from emoji import emojize


nok_string = "   " + emojize(":no_entry:" + ":musical_note:", language='alias') + "something went wrong for Fay Wray and King Kong" \
             + emojize(":musical_note:" + ":lips:", language='alias')


class Roles(str, Enum):
    admin = "admin"
    user = "user"



# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "11088b752484acda51943b487d8657e142e91e085187c110e0967650e7526784"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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

app = FastAPI()


def time_window_control(date_start: datetime, date_end: datetime, current_user: User):
    time_window_validated = False
    diff_time = date_end - date_start

    if date_start.date() != date_end.date():
        status_date = "hi " + str(current_user.username) + nok_string + " the dates of start and stop must be the same"
        time_window_validated = False
    elif date_start > date_end:
        status_date = "hi " + str(current_user.username) + nok_string + " you can't finish before you start"
        time_window_validated = False
    elif diff_time.total_seconds() > 10800.0:
        status_date = "hi " + str(current_user.username) + nok_string + " for the sake of our servers," \
                                                                      " time window limited to three hours"
        time_window_validated = False
    elif date_start > datetime.utcnow() or date_end > datetime.utcnow():
        status_date = "hi " + str(current_user.username) + nok_string + " Fylakio is futuristic but does not accept" \
                                                                        " dates in the future"
        time_window_validated = False
    else:
        time_window_validated = True
        status_date = nok_string + "Unhandled time_window_control case"

    return {'status_date': status_date, 'time_window_validated': time_window_validated}


def el_parametrizor(mode_debug=False):
    if mode_debug:
        os.environ['URL_MONGO'] = "localhost:27017"

        os.environ['USR_MONGO'] = "root"

        os.environ['PWD_MONGO'] = "rootmongopwd"


el_parametrizor(True)

mongo_handler = MongoDbGed(address=os.environ['URL_MONGO'], user=os.environ['USR_MONGO'],
                           password=os.environ['PWD_MONGO'])


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


@app.post("/token", response_model=Token)
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


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.post("/create_user")
async def create_user(user_name: str = Form(),
                      email: str = Form(regex=r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                                        description="must be an email adress"),
                      full_name: str = Form(),
                      password: str = Form(min_length=10, description="mini. 10 characters"),
                      role: Roles = Form(),
                      current_user: User = Depends(get_current_active_user)):
    if current_user.role == "admin":
        return mongo_handler.insert_user(user_name, full_name, email, get_password_hash(password),
                                         current_user.username, role)
    else:
        return {'response': emojize(":no_entry:", language="alias") + "vous n'avez pas dit le mot magigue"}


@app.post("/ged_file")
async def upload_ged_file(file: UploadFile,
                      ged_import_name: str = Form(description="import name: must not exist already"),
                      current_user: User = Depends(get_current_active_user)):
    if current_user.role == "admin":
        ged_handler = GedFileHandler()
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
        ged_handler.from_file_to_list_of_dict(file=file.filename)
        return mongo_handler.insert_list_of_ged_objets(collection_name=ged_import_name, ged_handler=ged_handler)

    else:
        return {'response': emojize(":no_entry:", language="alias") + "vous n'avez pas dit le mot magigue"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

