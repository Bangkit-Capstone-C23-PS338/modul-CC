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
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # Set the expiration time for the access token (in minutes)

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
    address: str
    photo_profile_url: str
    
class Product(BaseModel):
    name: str
    description: str
    price: float
    to_do: List[str]
    social_media_type: str

class Order(BaseModel):
    order_id: str
    order_date: datetime
    influencer_username: str
    Business_owner: str
    product_id: int
    product_name: str
    product_type: str
    product_link: str
    sender_address: str
    receiver_address: str
    order_courier: str
    payment_method: str
    status: str
    brief: str
    payment_date: datetime
    selected_package: Product
    posting_date: str
    content_link: str

class Review(BaseModel):
    order_id: str
    rating: int
    comment: str

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

    doc_ref = db.collection("influencers").document(influencer.username)
    doc = doc_ref.get()
    if doc.exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Influencer already exists")
    
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
        influencers_ref = db.collection("influencers").document(username).get()
        
        if influencers_ref.exists:
            influencer_review = []
            for i in influencers_ref.get("reviews"):
                influencer_review.append(i)

            influencer_rating = []
            for i in range (len(influencer_review)):
                influencer_rating.append(influencer_review[i]["rating"])
            
            influencer_rating = sum(influencer_rating)/len(influencer_rating)

            influencers.append(influencers_ref.to_dict())
            influencers[0]["rating"] = influencer_rating
            
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
            if len(influencer["products"]) == 0:
                product_dict["product_id"] = 0
            else:
                product_list =[]

                for x in range (len(influencer["products"])):
                    product_list.append(influencer["products"][x]["name"])

                for x in range (len(influencer["products"])):
                    if product_dict["name"] == product_list[x]:
                        check = False
                    else:
                        check = True

                if check == True:
                    product_dict["product_id"] = influencer["products"][-1]["product_id"] + 1
                    influencer["products"].append(product_dict)
                    doc_ref.set(influencer)
                    return {"message": "Product added to influencer successfully"}
                else:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Product already exists"
                    )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Influencer not found"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
        
#For debugging purposes
@app.get("/influencers/{username}/product_ids")
async def get_product_ids(username: str, token: dict = Depends(get_current_user)):
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
async def update_product(username: str, product_id: int, updated_product: Product, token: dict = Depends(get_current_user)):
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

            # Update the product with the provided fields (partial update)
            updated_product_data = updated_product.dict(exclude_unset=True)
            existing_product.update(updated_product_data)

            # Assign the updated product back to the list
            products[product_id] = existing_product

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
async def delete_product(username: str, product_id: int, token: dict = Depends(get_current_user)):
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
async def get_all_products(username: str, token: dict = Depends(get_current_user)):
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
    
@app.get("/influencers/{username}/products/{product_id}")
async def get_product(username: str, product_id: int, token: dict = Depends(get_current_user)):
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

            # Get the product
            product = products[product_id]

            ig_uname = influencer.get("ig_username")
            ig_foll = influencer.get("ig_followers")

            product["ig_uname"] = ig_uname
            product["ig_foll"] = ig_foll
            return (product)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Influencer not found"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.post("/add_influencer_order/{influencer_username}")
async def add_influencer_order(
    influencer_username: str,
    order_data: dict,
    token: dict = Depends(get_current_user)
):
    try:
        # Check if the authenticated user is a business owner
        if token.get("type") != "business_owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to place orders"
            )

        # Retrieve the influencer
        doc_ref = db.collection("influencers").document(influencer_username)
        doc = doc_ref.get()
        if doc.exists:
            influencer = doc.to_dict()
            products = influencer.get("products", [])

            # Find the product by name
            product_name = order_data.get("name")
            selected_product = None
            for product in products:
                if product.get("name") == product_name:
                    selected_product = product
                    break

            # Check if the product is found
            if selected_product is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )

            # Retrieve the business owner
            business_owner = get_user_by_username(token.get("sub"), "business_owners")

            # Store the order data in Firestore
            order = {
                "order_id": str(uuid.uuid4()),
                "order_date": datetime.now(),
                "influencer_username": influencer_username,
                "business_owner": token.get("sub"),
                "product_name": order_data.get("product_name"),
                "product_type": order_data.get("product_type"),
                "product_link": order_data.get("product_link"),
                "sender_address": order_data.get("sender_address"),
                "receiver_address": influencer.get("address"),
                "order_courier": order_data.get("courier"),
                "payment_method": order_data.get("payment_method"),
                "brief": order_data.get("brief"),
                "status": "pending",
                "payment_date": None,
                "selected_package": selected_product,
                "posting_date": order_data.get("posting_date"),
                "content_link": None            
                }
            
            doc_ref = db.collection("orders").document(order.get("order_id"))
            doc_ref.set(order)

            return {
                "message": "Order placed successfully",
                "order": order
            }

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Influencer not found"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.put("/update_order/{order_id}")
async def update_order(
    order_id: str,
    update_data: dict,
    token: dict = Depends(get_current_user)
):
    try:
        # Check if the authenticated user is a business owner
        if token.get("type") != "business_owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update payments"
            )

        # Retrieve the order
        doc_ref = db.collection("orders").document(order_id)
        doc = doc_ref.get()
        if doc.exists:
            order = doc.to_dict()

            # Check if the order belongs to the authenticated business owner
            if order.get("business_owner") != token.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to update this order"
                )

            # Update the payment status
            order["status"] = update_data.get("status")
            order["payment_date"] = datetime.now()

            # Update the content link
            order["content_link"] = update_data.get("content_link")

            # Update the order in the database
            doc_ref.update(order)

            return {"message": "order updated successfully"}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Add the following function to handle adding order reviews
@app.post("/add_influencer_review/{order_id}")
async def add_order_review(
    order_id: str,
    review_data: dict,
    token: dict = Depends(get_current_user)
):
    
    # Check if the authenticated user is a business owner
    if token.get("type") != "business_owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to add reviews"
        )
    order_influencer_db = db.collection("orders").document(order_id)
    order = order_influencer_db.get()
    
    if order.exists:
        order = order.to_dict()

        order_influencer = order.get("influencer_username")

    doc_order_ref = db.collection("influencers").document(order_influencer)
    doc_order = doc_order_ref.get()

    if doc_order.exists:
        influencer = doc_order.to_dict()

        reviews = influencer.get("reviews")

        if reviews is None:
            reviews = []
            reviews.append(review_data)
            influencer["reviews"] = reviews
            doc_order_ref.update(influencer)
        else:
            data_reviews = []
            for i in range (len(reviews)):
                data_reviews.append(reviews[i]["order_id"])


            for x in range (len(reviews)):
                if order_id == data_reviews[x]:
                    check = False
                else:
                    check = True

            if check == True:
                reviews.append(review_data)
                influencer["reviews"] = reviews
                doc_order_ref.update(influencer)
                return {"message": "Review added successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You have already added a review for this order"
                )
            

@app.get("/orders_business_owner/{business_owner}")
async def get_orders_business_owner(
    business_owner: str,
    token: dict = Depends(get_current_user)
):
    try:
        # Check if the authenticated user is a business owner
        if token.get("type") != "business_owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view orders"
            )

        # Retrieve the business owner
        doc_ref = db.collection("business_owners").document(business_owner)
        doc = doc_ref.get()
        if doc.exists:
            business_owner = doc.to_dict()

            # Check if the order belongs to the authenticated business owner
            if business_owner.get("username") != token.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to view orders for this business owner"
                )

            # Retrieve the orders
            orders = []
            docs = db.collection("orders").where("business_owner", "==", business_owner.get("username")).stream()
            for doc in docs:
                order = doc.to_dict()
                order["order_date"] = order["order_date"].strftime("%d/%m/%Y %H:%M:%S")
                if order.get("payment_date"):
                    order["payment_date"] = order["payment_date"].strftime("%d/%m/%Y %H:%M:%S")
                orders.append(order)

            return {"orders": orders}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business owner not found"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.get("/influencer_orders/{influencer}")
async def get_influencer_orders(
    influencer: str,
    token: dict = Depends(get_current_user)
):
    try:
        # Check if the authenticated user is an influencer
        if token.get("type") != "influencer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view orders"
            )

        # Retrieve the influencer
        doc_ref = db.collection("influencers").document(influencer)
        doc = doc_ref.get()
        if doc.exists:
            influencer = doc.to_dict()

            # Check if the order belongs to the authenticated influencer
            if influencer.get("username") != token.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to view orders for this influencer"
                )

            # Retrieve the orders
            orders = []
            docs = db.collection("orders").where("influencer_username", "==", influencer.get("username")).stream()
            for doc in docs:
                order = doc.to_dict()
                order["order_date"] = order["order_date"].strftime("%d/%m/%Y %H:%M:%S")
                if order.get("payment_date"):
                    order["payment_date"] = order["payment_date"].strftime("%d/%m/%Y %H:%M:%S")
                orders.append(order)

            return {"orders": orders}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Influencer not found"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.get("/influencer_reviews/{influencer}")
async def get_influencer_review(
    influencer: str,
    token: dict = Depends(get_current_user)
):
    try:
        # Retrieve the influencer
        doc_ref = db.collection("influencers").document(influencer)
        doc = doc_ref.get()
        if doc.exists:
            influencer = doc.to_dict()

            # Retrieve the reviews
            reviews = influencer.get("reviews", [])
            return {"reviews": reviews}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Influencer not found"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.get("/get_business_owner/{business_owner}")
async def get_business_owner(
    business_owner: str,
    token: dict = Depends(get_current_user)
):
    try:
        # Retrieve the business owner
        doc_ref = db.collection("business_owners").document(business_owner)
        doc = doc_ref.get()
        if doc.exists:
            business_owner = doc.to_dict()
            return business_owner

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business owner not found"
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

@app.get("/get_order_details/{order_id}")
async def get_order_details(
    order_id: str,
    token: dict = Depends(get_current_user)
):
    try:
        # Retrieve the order
        doc_ref = db.collection("orders").document(order_id)
        doc = doc_ref.get()
        if doc.exists:
            order = doc.to_dict()
            order["order_date"] = order["order_date"].strftime("%d/%m/%Y %H:%M:%S")
            if order.get("payment_date"):
                order["payment_date"] = order["payment_date"].strftime("%d/%m/%Y %H:%M:%S")
            return order

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Common error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )