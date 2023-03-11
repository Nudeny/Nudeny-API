from fastapi import FastAPI, UploadFile, HTTPException
from typing import List
from pydantic import BaseModel
import concurrent.futures

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
    if len(images) == 0:
        raise HTTPException(status_code=400, detail="No source(s) provided.")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(classification_model.classifyUrl, [image.source for image in images]))
    
    return {"Prediction": results}
    # return {"Prediction": [classification_model.classifyUrl(image.source) for image in images]}

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
    if len(images) == 0:
        raise HTTPException(status_code=400, detail="No source(s) provided.")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(detection_model.detectUrl, [image.source for image in images]))
    
    return {"Prediction": results}
    #return {"Prediction": [detection_model.detectUrl(image.source) for image in images]}

@app.post("/censor/")
async def create_upload_files(files: List[UploadFile]):
    """
    Receive image file request.
    """
    return {"Prediction": [detection_model.censor(await file.read(), file.filename) for file in files]}

@app.post("/censor-url/")
async def create_item(images: List[Image]):
    """
    Receive URL JSON request.
    """
    if len(images) == 0:
        raise HTTPException(status_code=400, detail="No source(s) provided.")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(detection_model.censorUrl, [image.source for image in images]))
    
    return {"Prediction": results}
    #return {"Prediction": [detection_model.censorUrl(image.source) for image in images]}
    