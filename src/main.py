"""FastAPI server for mocking VeSync devices."""

from fastapi import FastAPI
from routes import router

app = FastAPI()

# Include all routes
app.include_router(router)

@app.get("/health")
async def health_check():
    """Health check endpoint for tests."""
    return {"status": "healthy"}

 