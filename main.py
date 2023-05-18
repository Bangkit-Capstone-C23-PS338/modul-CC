from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from google.cloud import firestore
from google.oauth2 import service_account
import uuid

app = FastAPI()

key_path = 'path/service-account-widhy.json'

credentials = service_account.Credentials.from_service_account_file(key_path)
client = firestore.Client(credentials=credentials)

SECRET_KEY = "inirahasia"  # Replace with your own secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Set the expiration time for the access token (in minutes)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Initialize Google Cloud Firestore client
db = firestore.Client(project='promosee')

# Sample data structures for BusinessOwner and Influencer
class BusinessOwner(BaseModel):
    username: str
    email: str
    password: str
    company_name: str
    categories: List[str]

class Influencer(BaseModel):
    username: str
    email: str
    password: str
    categories: List[str]
    ig_username: str
    ig_followers: int
    tt_username: str
    tt_followers: int
    yt_username: str
    yt_followers: int

# User authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_username(username: str, collection_name: str):
    doc_ref = db.collection(collection_name).document(username)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

def get_user_by_userid(userid: str, collection_name: str):
    doc_ref = db.collection(collection_name).document(userid)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

def authenticate_user(username: str, password: str, collection_name: str):
    user = get_user_by_username(username, collection_name)
    if user and verify_password(password, user["password"]):
        return user["userid"], user
    return None, None

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# API endpoints
@app.post("/register/businessowner")
async def register_business_owner(business_owner: BusinessOwner):
    # Hash the password
    hashed_password = get_password_hash(business_owner.password)
    business_owner_dict = business_owner.dict()
    business_owner_dict["password"] = hashed_password

    # Generate a random userid
    userid = str(uuid.uuid4())
    business_owner_dict["userid"] = userid

    # Save the business owner data to the database
    doc_ref = db.collection("business_owners").document(business_owner.username)
    doc_ref.set(business_owner_dict)
    return {"message": "Business owner registered successfully"}

@app.post("/register/influencer")
async def register_influencer(influencer: Influencer):
    # Hash the password
    hashed_password = get_password_hash(influencer.password)
    influencer_dict = influencer.dict()
    influencer_dict["password"] = hashed_password

    # Generate a random userid
    userid = str(uuid.uuid4())
    influencer_dict["userid"] = userid

    # Save the influencer data to the database
    doc_ref = db.collection("influencers").document(influencer.username)
    doc_ref.set(influencer_dict)
    return {"message": "Influencer registered successfully"}

@app.post("/login")
async def login(username: str, password: str):
    userid, user = authenticate_user(username, password, "business_owners")
    if not user:
        userid, user = authenticate_user(username, password, "influencers")
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    # Create the token data
    token_data = {"sub": user["username"], "type": user.get("type")}

    # Generate the access token
    access_token = create_access_token(token_data)

    return {"userid": userid, "username": user["username"], "access_token": access_token, "token_type": "bearer"}

@app.get("/profile/{id}")
async def get_profile(id: str, token: str = Depends(oauth2_scheme)):
    try:
        # Verify and decode the token
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = decoded_token.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Retrieve the user profile based on the ID
        doc_ref = db.collection("business_owners").document(username)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()

        doc_ref = db.collection("influencers").document(username)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.get("/profile/{username}")
async def get_user_by_username_endpoint(username: str, token: str = Depends(oauth2_scheme)):
    try:
        # Verify and decode the token
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        auth_username = decoded_token.get("sub")
        if not auth_username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Retrieve the user by username
        doc_ref = db.collection("business_owners").document(username)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()

        doc_ref = db.collection("influencers").document(username)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.put("/profile/update/{id}")
async def update_profile(id: int, token: str = Depends(oauth2_scheme)):
    try:
        # Verify and decode the token
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = decoded_token.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Update the user profile based on the ID
        # Implement your logic here
        # You can retrieve the user profile, make modifications, and update the document in Firestore

        return {"message": f"Profile updated for ID: {id}"}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.get("/getinfluencers")
async def get_influencers(token: str = Depends(oauth2_scheme)):
    try:
        # Verify and decode the token
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = decoded_token.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Retrieve influencers
        influencers = []
        influencers_ref = db.collection("influencers").stream()
        for doc in influencers_ref:
            influencers.append(doc.to_dict())

        return {"influencers": influencers}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.get("/getinfluencers/category")
async def get_influencers_by_category(category: str, token: str = Depends(oauth2_scheme)):
    try:
        # Verify and decode the token
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = decoded_token.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Retrieve influencers by category
        influencers = []
        influencers_ref = db.collection("influencers").where("categories", "array_contains", category).stream()
        for doc in influencers_ref:
            influencers.append(doc.to_dict())

        return {"influencers": influencers}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.get("/getinfluencers/{username}")
async def get_influencers_by_username(username: str, token: str = Depends(oauth2_scheme)):
    try:
        # Verify and decode the token
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        auth_username = decoded_token.get("sub")
        if not auth_username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Retrieve influencers by username
        influencers = []
        influencers_ref = db.collection("influencers").where("username", "==", username).stream()
        for doc in influencers_ref:
            influencers.append(doc.to_dict())

        return {"influencers": influencers}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.get("/getinfluencers/{id}")
async def get_influencer_by_id(id: int, token: str = Depends(oauth2_scheme)):
    try:
        # Verify and decode the token
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = decoded_token.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Retrieve the influencer by ID
        doc_ref = db.collection("influencers").document(username)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Influencer not found")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Common error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )