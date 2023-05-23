from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from google.cloud import firestore
import uuid
import secrets
from datetime import datetime, timedelta
from typing import Union

import os, json
from dotenv import load_dotenv
load_dotenv()

import os
import json

# Set the 'CREDENTIALS' environment variable with a valid JSON string
os.environ['CREDENTIALS'] = '{"key": "value"}'

CREDENTIALS = json.loads(os.environ.get('CREDENTIALS'))

if os.path.exists('credentials.json'):
    pass
else:
    with open('credentials.json', 'w') as credFile:
        json.dump(CREDENTIALS, credFile)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'

app = FastAPI()

SECRET_KEY = "inirahasia"  # Replace with your own secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Set the expiration time for the access token (in minutes)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Initialize Google Cloud Firestore client
db = firestore.Client(project='promosee-capstone')

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
    products: List[str] = []
    
class Product(BaseModel):
    name: str
    price: float
    to_do: List[str]
    social_media_type: str

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

def authenticate_user(username: str, password: str, collection_name: str):
    user = get_user_by_username(username, collection_name)
    if user and verify_password(password, user["password"]):
        return user["userid"], user
    return None, None

def create_access_token(username: str, user_type: str):
    to_encode = {
        "sub": username,
        "type": user_type
    }
    print(username, user_type)
    unique_id = secrets.token_hex(8)  # Generate a unique identifier
    to_encode["jti"] = unique_id  # Add the unique identifier to the token data

    expiration_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expiration_time  # Add the expiration time to the token data

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Token blacklist functions
token_blacklist = set()

def invalidate_token(token: str):
    token_blacklist.add(token)

def is_token_blacklisted(token: str):
    return token in token_blacklist

def is_token_expired(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expiration_timestamp = decoded_token.get("exp")
        if not expiration_timestamp:
            return False  # If the expiration time is not present, consider the token as not expired
        expiration_time = datetime.utcfromtimestamp(expiration_timestamp)
        current_time = datetime.utcnow()
        return current_time > expiration_time
    except JWTError:
        return True

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        if is_token_blacklisted(token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        if is_token_expired(token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")

        # Verify and decode the token
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = decoded_token.get("sub")
        user_type = decoded_token.get("type")
        if not username or not user_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        return {"sub": username, "type": user_type}  # Return the decoded token as a dictionary

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# API endpoints
@app.post("/register/businessowner")
async def register_business_owner(business_owner: BusinessOwner = Body(...)):
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
async def register_influencer(influencer: Influencer = Body(...)):
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
async def login(username: str = Body(...), password: str = Body(...)):
    userid, user = authenticate_user(username, password, "business_owners")
    user_type = "business_owner"

    if not user:
        userid, user = authenticate_user(username, password, "influencers")
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
        user_type = "influencer"

    # Generate the access token
    access_token = create_access_token(username, user_type)

    return {"userid": userid, "username": username, "access_token": access_token, "token_type": "bearer", "user_type": user_type}

@app.put("/update/{username}")
async def update_user_profile(username: str, updated_profile: dict, token: str = Depends(get_current_user)):
    try:
        # Check if the authenticated user is the same as the profile being updated
        if token.get("sub") != username:
            print("Username from token:", token.get("sub"))
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this profile")
            
        # Determine the collection name based on the type of user
        user_type = token.get("type")
        collection_name = "business_owners" if user_type == "business_owner" else "influencers"

        # Update the user profile
        doc_ref = db.collection(collection_name).document(username)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update(updated_profile)
            return {"message": "Profile updated successfully"}

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.put("/update/{username}")
async def update_user_profile(username: str, updated_profile: dict, token: str = Depends(get_current_user)):
    try:
        # Check if the authenticated user is the same as the profile being updated
        if token.get("sub") != username:
            print("Username from token:", token.get("sub"))
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this profile")
            
        # Convert the updated_profile to a dictionary excluding None values
        updated_profile.dict(exclude_unset=True)

        # Determine the collection name based on the type of user
        user_type = token.get("type")
        collection_name = "business_owners" if user_type == "business_owner" else "influencers"

        # Update the user profile
        doc_ref = db.collection(collection_name).document(username)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update(updated_profile)
            return {"message": "Profile updated successfully"}

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.get("/getinfluencers")
async def get_influencers(token: str = Depends(get_current_user)):
    try:
        print(token.get("sub"), token.get("type"))
        # Retrieve influencers
        influencers = []
        influencers_ref = db.collection("influencers").stream()
        for doc in influencers_ref:
            influencers.append(doc.to_dict())

        return {"influencers": influencers}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.get("/getinfluencers/{category}")
async def get_influencers_by_category(category: str, token: str = Depends(get_current_user)):
    try:
        # Retrieve influencers by category
        influencers = []
        influencers_ref = db.collection("influencers").where("categories", "array_contains", category).stream()
        for doc in influencers_ref:
            influencers.append(doc.to_dict())

        return {"influencers": influencers}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.get("/getinfluencer/{username}")
async def get_influencers_by_username(username: str, token: str = Depends(get_current_user)):
    try:
        # Retrieve influencers by username
        influencers = []
        influencers_ref = db.collection("influencers").where("username", "==", username).stream()
        for doc in influencers_ref:
            influencers.append(doc.to_dict())

        return {"influencers": influencers}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
@app.post("/influencers/{username}/products")
async def add_product_to_influencer(
    username: str,
    product: Product,
    token: dict = Depends(get_current_user)
):
    try:
        # Check if the authenticated user is a business owner
        if token.get("type") != "influencer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to add products"
            )

        # Check if the authenticated user's username matches the influencer's username
        if token.get("sub") != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to add products to this influencer"
            )

        # Retrieve the influencer
        doc_ref = db.collection("influencers").document(username)
        doc = doc_ref.get()
        if doc.exists:
            influencer = doc.to_dict()
            # Add the 'products' key to the influencer's data if it doesn't exist
            if "products" not in influencer:
                influencer["products"] = []
            # Add the product to the influencer's products list
            product_dict = product.dict()
            influencer["products"].append(product_dict)
            # Update the influencer's data in the database
            doc_ref.set(influencer)
            return {"message": "Product added to influencer successfully"}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Influencer not found"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
        
@app.get("/influencers/{username}/product_ids")
async def get_product_ids(username: str):
    try:
        # Retrieve the influencer
        doc_ref = db.collection("influencers").document(username)
        doc = doc_ref.get()
        if doc.exists:
            influencer = doc.to_dict()
            products = influencer.get("products", {})
            product_ids = list(products.keys()) if isinstance(products, dict) else []
            return {"product_ids": product_ids}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Influencer not found"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


        
@app.put("/influencers/{username}/products/{product_id}")
async def update_product(username: str, product_id: int, updated_product: Product):
    try:
        # Retrieve the influencer
        doc_ref = db.collection("influencers").document(username)
        doc = doc_ref.get()
        if doc.exists:
            influencer = doc.to_dict()
            products = influencer.get("products", [])

            # Check if the product_id is within the valid range
            if product_id < 0 or product_id >= len(products):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )

            # Get the existing product
            existing_product = products[product_id]

            # Update the product with the updated values
            updated_product_dict = updated_product.dict(exclude_unset=True)
            existing_product.update(updated_product_dict)

            # Update the influencer's data in the database
            doc_ref.update({"products": products})
            return {"message": "Product updated successfully"}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Influencer not found"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.delete("/influencers/{username}/products/{product_id}")
async def delete_product(username: str, product_id: int):
    try:
        # Retrieve the influencer
        doc_ref = db.collection("influencers").document(username)
        doc = doc_ref.get()
        if doc.exists:
            influencer = doc.to_dict()
            products = influencer.get("products", [])

            # Check if the product_id is within the valid range
            if product_id < 0 or product_id >= len(products):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )

            # Remove the product from the influencer's products list
            products.pop(product_id)

            # Update the influencer's data in the database
            doc_ref.update({"products": products})
            return {"message": "Product deleted successfully"}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Influencer not found"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.get("/influencers/{username}/products")
async def get_all_products(username: str):
    try:
        # Retrieve the influencer
        doc_ref = db.collection("influencers").document(username)
        doc = doc_ref.get()
        if doc.exists:
            influencer = doc.to_dict()
            products = influencer.get("products", [])
            product_list = []

            # Iterate over the products and add an identifier
            for index, product in enumerate(products):
                product_dict = product.copy()
                product_dict["id"] = index  # Add an 'id' field to indicate the order
                product_list.append(product_dict)

            return {"products": product_list}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Influencer not found"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    invalidate_token(token)
    return {"message": "User logged out successfully"}

# Common error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )