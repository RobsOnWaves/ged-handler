import uvicorn
import os
from datetime import datetime, timedelta
from typing import Union
from enum import Enum
from fastapi import Depends, FastAPI, HTTPException, status, Form, UploadFile, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, RedirectResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from libs.mongo_db_handler import MongoDbGed
from libs.ged_file_handler import GedFileHandler
from libs.messages import Messages
from libs.gold_digger import GoldDigger
from libs.meps_handler import MepsHandler
from fastapi.middleware.cors import CORSMiddleware
import re
from pathlib import Path
import json
import logging
from pythonjsonlogger import jsonlogger
import time
from typing import Optional


class Roles(str, Enum):
    admin = "admin"
    user = "user"
    gold_digger = "gold_digger"
    meps = "meps"


# Configuration du Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Créer un gestionnaire de logs qui écrit dans un fichier
logHandler = logging.FileHandler('app_logs.json')

# Utiliser le format JSON pour le gestionnaire de fichier
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)

logger.addHandler(logHandler)

# to get a string like this run:
# openssl rand -hex 32
try:
    SECRET_KEY = os.environ["SECRET_KEY"]
    print("SECRET_KEY set, using it")
except KeyError:
    SECRET_KEY = "11088b752484acda51943b487d8657e142e91e085187c110e0967650e7526784"
    print("SECRET_KEY not set, using default")
except Exception as e:
    print("Error getting SECRET_KEY")
    print(e)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
JSON_EXTENSION = ".json"


class Token(BaseModel):
    access_token: str
    token_type: str
    name: str
    role: str


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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_id_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")  # 'sub' est généralement l'identifiant de l'utilisateur
    except jwt.JWTError:
        return None


def log_to_json_file(log_data):
    log_file_path = 'logz.json'
    try:
        with open(log_file_path, 'a') as log_file:
            json.dump(log_data, log_file)
            log_file.write('\n')  # Ajoute une nouvelle ligne après chaque log
    except Exception as e:
        print(f"Error writing to log file: {e}")


def el_parametrizor(mode_debug=False):
    if mode_debug:
        os.environ['URL_MONGO'] = "localhost:27017"

        os.environ['USR_MONGO'] = "root"

        os.environ['PWD_MONGO'] = "rootmongopwd"

        os.environ['URL_FRONT'] = "http://localhost:8080"

el_parametrizor(False)

mongo_handler = MongoDbGed(address=os.environ['URL_MONGO'], user=os.environ['USR_MONGO'],
                           password=os.environ['PWD_MONGO'])

messages = Messages()
gold_handler = GoldDigger()
meps_handler = MepsHandler()


def time_window_control(date_start: datetime, date_end: datetime, current_user: User):
    time_window_validated = False
    diff_time = date_end - date_start

    if date_start.date() != date_end.date():
        status_date = "hi " + str(current_user.username) + messages.nok_string + \
                      " the dates of start and stop must be the same"

        time_window_validated = False

    elif date_start > date_end:
        status_date = "hi " + str(current_user.username) + messages.nok_string + \
                      " you can't finish before you start"

        time_window_validated = False

    elif diff_time.total_seconds() > 10800.0:
        status_date = "hi " + str(current_user.username) + messages.nok_string + \
                      " for the sake of our servers, time window limited to three hours"

        time_window_validated = False

    elif date_start > datetime.utcnow() or date_end > datetime.utcnow():
        status_date = "hi " + str(current_user.username) + messages.nok_string + \
                      " ged-handler is futuristic but does not accept dates in the future"
        time_window_validated = False
    else:
        time_window_validated = True
        status_date = messages.nok_string + "Unhandled time_window_control case"

    return {'status_date': status_date, 'time_window_validated': time_window_validated}


def sanitize_filename(filename: str):
    """
    Nettoie et valide un nom de fichier pour éviter les injections de chemin.
    Remplace les caractères non autorisés par des underscores.
    """
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def secure_file_path(filename: str, directory="tmp/"):
    """
    Construit un chemin de fichier sécurisé dans un répertoire spécifique.
    """
    sanitized_filename = sanitize_filename(filename)
    return os.path.join(directory, sanitized_filename)


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


# Configurez le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ['URL_FRONT']],  # Les origines autorisées, vous pouvez utiliser ["*"] pour le développement
    allow_credentials=True,
    allow_methods=["*"],  # Les méthodes HTTP autorisées
    allow_headers=["*"],  # Les en-têtes HTTP autorisés
)


async def get_request_body(request: Request):
    body = await request.body()

    async def app(scope, send):
        async def override_receive():
            return {"type": "http.request", "body": body}

        await request.app(scope, override_receive, send)

    # Important: Définir override_receive ici pour qu'elle soit accessible
    async def override_receive():
        return {"type": "http.request", "body": body}

    request._receive = override_receive

    return body


def mask_sensitive_data_and_exclude_files(body: str) -> str:
    # Masquer les données sensibles
    body = re.sub(r'(password=)[^&]*', r'\1[MASKED]', body, flags=re.IGNORECASE)

    # Exclure les fichiers uploadés (ajuster selon la structure de la requête)
    body = re.sub(r'(upload_file=)[^&]*', '[FILE EXCLUDED]', body, flags=re.IGNORECASE)

    return body


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Vérifier le type de contenu
    content_type = request.headers.get('content-type')

    # Traiter différemment les données binaires
    if content_type and ("multipart/form-data" in content_type or "application/octet-stream" in content_type):
        body_text = '[Binary Data]'
    else:
        # Obtenir et nettoyer le corps de la requête pour les types de contenu textuels
        body = await get_request_body(request)
        body_text = body.decode('utf-8') if body else ''
        body_text = mask_sensitive_data_and_exclude_files(body_text)

    try:
        token = await oauth2_scheme(request)
        user_id = get_user_id_from_token(token) if token else "anonymous"
    except Exception as e:
        user_id = "error_in_token" + str(e)

    # Continuer le traitement de la requête
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    # Logger les informations
    logger.info('Request info', extra={
        "timestamp": datetime.fromtimestamp(start_time).isoformat(),
        "user_id": user_id,
        'request_method': request.method,
        'request_url': str(request.url),
        'response_status': response.status_code,
        'process_time_ms': process_time,
        'request_body': body_text,
        # Autres informations...
    })

    return response


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
    return {"access_token": access_token, "name": user.full_name, "token_type": "bearer", "role": user.role}


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
        return mongo_handler.insert_user(user_name, full_name, email, get_password_hash(password),
                                         current_user.username, role)
    else:
        return {'response': 'Access denied'}


@app.post("/ged_file", description="Uploading a ged-file to the database, restricted to admin privileges")
async def upload_ged_file(file: UploadFile,
                          ged_import_name: str = Form(description="import name: must not exist already"),
                          current_user: User = Depends(get_current_active_user)):
    if current_user.role == "admin":
        ged_handler = GedFileHandler()
        ged_handler.from_file_to_list_of_dict_with_cleanup(file, path="tmp/")
        return mongo_handler.insert_list_of_ged_objets(collection_name=ged_import_name, ged_handler=ged_handler)

    else:
        raise HTTPException(status_code=403, detail=messages.denied_entry)


@app.get("/ged_stored_collection_to_json_answer", description="Returns a JSON answer from a stored collection")
async def ged_stored_collection_to_json_answer(ged_collection_name: str,
                                               current_user: User = Depends(get_current_active_user)):
    if current_user.role in ['admin', 'user']:
        return mongo_handler.from_mongo_to_ged_list_dict(collection_name=ged_collection_name)
    else:
        raise HTTPException(status_code=403, detail=messages.denied_entry)


@app.get("/ged_stored_collection_to_json_file", description="Returns a JSON file from a stored collection")
async def ged_stored_collection_to_json_file(ged_collection_name: str,
                                             current_user: User = Depends(get_current_active_user)):
    if current_user.role in ['admin', 'user']:
        safe_path = secure_file_path(ged_collection_name + JSON_EXTENSION)
        with open(safe_path, 'w') as convert_file:
            ged_listed_dict = mongo_handler.from_mongo_to_ged_list_dict(collection_name=ged_collection_name)
            ged_handler = GedFileHandler()
            jsoned_ged = ged_handler.jsonize_ged_dict(ged_listed_dict)
            convert_file.write(jsoned_ged)
        return FileResponse(safe_path)
    else:
        raise HTTPException(status_code=403, detail=messages.denied_entry)


@app.post("/ged_file_to_json_answer", description="Returns a converted JSON file from a ged-file"
                                                  " without storing it in the database")
async def ged_collection_to_json_answer(file: UploadFile,
                                        current_user: User = Depends(get_current_active_user)):
    if current_user.role in ['admin', 'user']:

        ged_handler = GedFileHandler()
        safe_path = secure_file_path(file.filename)
        ged_handler.from_file_to_list_of_dict_with_cleanup(file, path=safe_path)
        return ged_handler.listed_documents

    else:
        raise HTTPException(status_code=403, detail=messages.denied_entry)


@app.get("/ged_stored_collections", description="Returns a list of all stored collections")
async def ged_stored_collections(current_user: User = Depends(get_current_active_user)):
    if current_user.role in ['admin', 'user']:

        return mongo_handler.get_collections()

    else:
        raise HTTPException(status_code=403, detail=messages.denied_entry)


@app.post("/ged_file_to_json_file", description="Returns a converted JSON file from a ged-file"
                                                "without storing it in the database")
async def ged_collection_to_json_file(file: UploadFile,
                                      current_user: User = Depends(get_current_active_user)
                                      ):
    if current_user.role in ['admin', 'user']:

        ged_handler = GedFileHandler()
        safe_path = secure_file_path(file.filename)
        ged_handler.from_file_to_list_of_dict_with_cleanup(file, path=safe_path)

        json_file_path = f"{safe_path}{JSON_EXTENSION}"
        if Path(json_file_path).exists():  # Vérifie si le fichier existe déjà
            raise HTTPException(status_code=400, detail="File already exists")

        with open(json_file_path, 'w') as convert_file:
            convert_file.write(ged_handler.jsonize_ged_dict(ged_handler.listed_documents))
        return FileResponse(json_file_path)

    else:
        raise HTTPException(status_code=403, detail=messages.denied_entry)


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
        raise HTTPException(status_code=403, detail=messages.denied_entry)


@app.post("/gold_file_converter", description="Returns an Excel with the estimated value in euros")
async def gold_file_converter(file: UploadFile, price_per_kg: int,
                              current_user: User = Depends(get_current_active_user)):
    if current_user.role in ['admin', 'gold_digger']:
        coeffs = mongo_handler.get_gold_coeffs()
        # Génération d'un nom de fichier sécurisé pour le fichier Excel
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_excel_filename = sanitize_filename(f"gold_estimate_{timestamp}.xlsx")
        full_safe_path = os.path.join('./data_out', safe_excel_filename)

        # Vérification de l'existence du fichier pour éviter d'écraser un fichier existant
        if Path(full_safe_path).exists():
            raise HTTPException(status_code=400, detail="File already exists")

        # Appel à la méthode de calcul en passant le chemin sécurisé
        await gold_handler.compute_excel_file(upload_file=file, price_per_kg=price_per_kg, gold_coeffs=coeffs,
                                              output_file=full_safe_path)

        return FileResponse(full_safe_path)
    else:
        raise HTTPException(status_code=403, detail=messages.denied_entry)


@app.post("/meps_file",
          description="loads a file with the list pression groups meetings of MEPs into the database")
async def load_meps_file(file: UploadFile, current_user: User = Depends(get_current_active_user)):
    if current_user.role in ['admin']:
        # Génération d'un nom de fichier sécurisé pour le fichier Excel
        answer = {}
        # Appel à la méthode de calcul en passant le chemin sécurisé
        await meps_handler.load_csv_file(upload_file=file, answer=answer)

        if not answer['success']:
            raise HTTPException(status_code=404, detail=messages.nok_string_raw)
        else:
            mongo_handler.from_df_to_mongo_meps(df=answer['df'], collection_name="meps_meetings")
            return {'response': messages.build_ok_action_string(user_name=current_user.username)}
    else:
        raise HTTPException(status_code=403, detail=messages.denied_entry)


@app.get("/meps_file",
         description="loads a file with the list pression groups meetings of MEPs into the database")
async def get_meps_file(mep_name: Optional[str] = None,
                        national_political_group: Optional[str] = None,
                        political_group: Optional[str] = None,
                        title: Optional[str] = None,
                        place: Optional[str] = None,
                        meeting_with: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        current_user: User = Depends(get_current_active_user)):
    if current_user.role in ['admin', 'meps']:
        db_name = meps_handler.get_mep_db_name()
        collection_name = meps_handler.get_mep_collection_name()

        def wild_card(word_to_search: str) :
            word_to_search = re.escape(word_to_search)
            return {"$regex": ".*" + word_to_search + ".*", "$options": "i"}

        query = {
            'MEP Name': wild_card(mep_name) if mep_name is not None else wild_card(''),
            'MEP nationalPoliticalGroup': wild_card(national_political_group) if national_political_group is not None else wild_card(''),
            'MEP politicalGroup': wild_card(political_group) if political_group is not None else wild_card(''),
            'Title': wild_card(title) if title is not None else wild_card(''),
            'Place': wild_card(place) if place is not None else wild_card(''),
            'Meeting With': wild_card(meeting_with) if meeting_with is not None else wild_card('')
        }

        if start_date and end_date:
            query['Date'] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query['Date'] = {"$gte": start_date}
        elif end_date:
            query['Date'] = {"$lte": end_date}

        if mongo_handler.from_mongo_to_xlsx(db_name=db_name, collection_name=collection_name, query=query):
            return FileResponse('export_file.xlsx')
        else:
            raise HTTPException(status_code=404, detail=messages.nok_string_raw)
    else:
        raise HTTPException(status_code=403, detail=messages.denied_entry)


@app.get("/meps_file_fields_values",
         description="gets a file with the list of the values of fields")
async def get_meps_file_selected_fields(current_user: User = Depends(get_current_active_user)):
    if current_user.role in ['admin', 'meps']:
        db_name = meps_handler.get_mep_db_name()
        fields = meps_handler.get_mep_field_list()
        collection_name = meps_handler.get_mep_collection_name()

        try:
            values = mongo_handler.get_unique_values(db_name=db_name, collection_name=collection_name, fields=fields)
        except Exception as e:
            print("get_meps_file_selected_fields : " + str(e), flush=True)
            raise HTTPException(status_code=404, detail=messages.nok_string_raw)

        if values is not None:
            try:
                return values
            except Exception as e:
                print("get_meps_file_selected_fields : " + str(e), flush=True)
                raise HTTPException(status_code=404, detail=messages.nok_string_raw)
        else:
            raise HTTPException(status_code=404, detail=messages.nok_string_raw)
    else:
        raise HTTPException(status_code=403, detail=messages.denied_entry)


@app.get("/meps_stats",
         description="get meps stats")
async def get_meps_stats(mep_name: Optional[str] = None,
                        national_political_group: Optional[str] = None,
                        political_group: Optional[str] = None,
                        title: Optional[str] = None,
                        place: Optional[str] = None,
                        meeting_with: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        current_user: User = Depends(get_current_active_user)):
    if current_user.role in ['admin', 'meps']:
        db_name = meps_handler.get_mep_db_name()
        collection_name = meps_handler.get_mep_collection_name()

        def wild_card(word_to_search: str) :
            word_to_search = re.escape(word_to_search)
            return {"$regex": ".*" + word_to_search + ".*", "$options": "i"}

        query = {
            'MEP Name': wild_card(mep_name) if mep_name is not None else wild_card(''),
            'MEP nationalPoliticalGroup': wild_card(national_political_group) if national_political_group is not None else wild_card(''),
            'MEP politicalGroup': wild_card(political_group) if political_group is not None else wild_card(''),
            'Title': wild_card(title) if title is not None else wild_card(''),
            'Place': wild_card(place) if place is not None else wild_card(''),
            'Meeting With': wild_card(meeting_with) if meeting_with is not None else wild_card('')
        }

        if start_date and end_date:
            query['Date'] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query['Date'] = {"$gte": start_date}
        elif end_date:
            query['Date'] = {"$lte": end_date}

        try:
            df = mongo_handler.get_df(db_name=db_name, collection_name=collection_name, query=query)

            return meps_handler.get_stats(df)

        except Exception as e:
            print("get_meps_stats : " + str(e), flush=True)
            raise HTTPException(status_code=404, detail=messages.nok_string_raw)
    else:
        raise HTTPException(status_code=403, detail=messages.denied_entry)


@app.get("/meps_stats_file",
         description="get meps stats file")
async def get_meps_stats_file(mep_name: Optional[str] = None,
                        national_political_group: Optional[str] = None,
                        political_group: Optional[str] = None,
                        title: Optional[str] = None,
                        place: Optional[str] = None,
                        meeting_with: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        current_user: User = Depends(get_current_active_user)):
    if current_user.role in ['admin', 'meps']:
        try:
            data = await get_meps_stats(mep_name,
                           national_political_group,
                           political_group,
                           title,
                           place,
                           meeting_with,
                           start_date,
                           end_date,
                           current_user)

            return FileResponse(meps_handler.get_stats_file(data))

        except Exception as e:
            print("get_meps_stats_file : " + str(e), flush=True)
            raise HTTPException(status_code=404, detail=messages.nok_string_raw)
    else:
        raise HTTPException(status_code=403, detail=messages.denied_entry)

@app.post("/logout")
async def logout():
    return {"message": "Disconnected, please log in again"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
