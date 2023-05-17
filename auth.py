from fastapi import APIRouter, Depends
from models import UserCreate, User, BusinessOwnerCreate, InfluencerCreate

router = APIRouter()

@router.post