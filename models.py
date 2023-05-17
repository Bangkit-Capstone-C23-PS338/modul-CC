from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    
class User(UserBase):
    id: int
    type: str
    
class BusinessOwnerCreate(UserCreate):
    business_name: str
    business_category: 
    
class InfluencerCreate(UserCreate):
    ig_username: str
    tt_username: str
    yt_username: str
    followers: int