from fastapi import FastAPI
from app.api import routes
from app.core.database import engine, Base


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

app.include_router(routes.router)
from app.models import pdf_file, organize_rules, organization_report

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lazy-Org-AI API")
app.include_router(routes.router)
