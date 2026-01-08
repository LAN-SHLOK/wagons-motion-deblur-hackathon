from fastapi import FastAPI

# This variable NAME must be exactly 'app'
app = FastAPI() 

@app.get("/")
async def root():
    return {"status": "WagonAI Engine Online"}
