from fastapi import FastAPI
from .routes import hello
from . import query # Import the new query module

# Initialize the FastAPI application with a title
app = FastAPI(title="Qual-AI")

app.include_router(hello.router)  # Mount hello routes
app.include_router(query.router)  # Mount query routes (this is the new line)


