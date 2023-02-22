from fastapi import FastAPI, UploadFile
from typing import List
from pydantic import BaseModel

from utils import is_valid_url

from classify import NudenyClassify

classification_model = NudenyClassify()

app = FastAPI()

class Image(BaseModel):
    source: str

@app.post("/classify/")
async def create_upload_files(files: List[UploadFile]):
    """
    Receive image file request.
    """
    return {"Prediction": [classification_model.classify(await file.read(), file.filename) for file in files]}

@app.post("/classify-url/")
async def create_item(images: List[Image]):
    """
    Receive URL JSON request.
    """
    return {"Prediction": [classification_model.classifyUrl(image.source) for image in images]}
    #return {"Prediction": images}