from fastapi import FastAPI

app = FastAPI(title="Vets API", version="1.0.0")

@app.get("/vets")
def read_vets():
    return {
        "service": "vets-api",
        "status": "ok",
        "animals": ["canino", "felino", "bovino"]
    }
