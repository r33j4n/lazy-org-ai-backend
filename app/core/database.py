from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL= "mysql+pymysql://root:password@localhost:3306/lazy_org"
engine = create_engine(DATABASE_URL,echo=True)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()
