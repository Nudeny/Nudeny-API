from fastapi import FastAPI, UploadFile
from typing import List
from pydantic import BaseModel

from classify import NudenyClassify
from detect import NudenyDetect

classification_model = NudenyClassify()
detection_model = NudenyDetect()

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

@app.post("/detect/")
async def create_upload_files(files: List[UploadFile]):
    """
    Receive image file request.
    """
    return {"Prediction": [detection_model.detect(await file.read(), file.filename) for file in files]}

@app.post("/detect-url/")
async def create_item(images: List[Image]):
    """
    Receive URL JSON request.
    """
    return {"Prediction": [detection_model.detectUrl(image.source) for image in images]}

@app.post("/censor/")
async def create_upload_files(files: List[UploadFile]):
    """
    Receive image file request.
    """
    return {"Prediction": [detection_model.censor(await file.read(), file.filename) for file in files]}
    