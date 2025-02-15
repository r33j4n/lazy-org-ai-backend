from fastapi import APIRouter,Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.dependencies import get_db
from sqlalchemy import text
router = APIRouter()

@router.get('/test')
async def test():
    return {"message": "API test successful"}

@router.get("/test-db")
async def test_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).scalar()
    return {"db_test": result}