from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import concurrent.futures

from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from classify import NudenyClassify
from detect import NudenyDetect

classification_model = NudenyClassify()
detection_model = NudenyDetect()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = ["*"]  # This will allow all sites to access your backend
methods = ["POST"]  # This will only allow the POST method
app.add_middleware( 
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=methods,
)

class Image(BaseModel):
    source: str

@app.post("/classify/")
@limiter.limit("30000/minute")
async def create_upload_files(request: Request, files: List[UploadFile]):
    """
    Receive image file request.
    """
    return {"Prediction": [classification_model.classify(await file.read(), file.filename) for file in files]}

@app.post("/classify-url/")
@limiter.limit("30000/minute")
async def create_item(request: Request, images: List[Image]):
    """
    Receive URL JSON request.
    """
    if len(images) == 0:
        raise HTTPException(status_code=400, detail="No source(s) provided.")
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = list(executor.map(classification_model.classifyUrl, [image.source for image in images]))
    
    # return {"Prediction": results}
    return {"Prediction": [classification_model.classifyUrl(image.source) for image in images]}

@app.post("/detect/")
@limiter.limit("30000/minute")
async def create_upload_files(request: Request, files: List[UploadFile]):
    """
    Receive image file request.
    """
    return {"Prediction": [detection_model.detect(await file.read(), file.filename) for file in files]}

@app.post("/detect-url/")
@limiter.limit("30000/minute")
async def create_item(request: Request, images: List[Image]):
    """
    Receive URL JSON request.
    """
    if len(images) == 0:
        raise HTTPException(status_code=400, detail="No source(s) provided.")
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = list(executor.map(detection_model.detectUrl, [image.source for image in images]))
    
    # return {"Prediction": results}
    return {"Prediction": [detection_model.detectUrl(image.source) for image in images]}

@app.post("/censor/")
@limiter.limit("30000/minute")
async def create_upload_files(request: Request, files: List[UploadFile]):
    """
    Receive image file request.
    """
    return {"Prediction": [detection_model.censor(await file.read(), file.filename) for file in files]}

@app.post("/censor-url/")
@limiter.limit("30000/minute")
async def create_item(request: Request, images: List[Image]):
    """
    Receive URL JSON request.
    """
    if len(images) == 0:
        raise HTTPException(status_code=400, detail="No source(s) provided.")
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = list(executor.map(detection_model.censorUrl, [image.source for image in images]))
    
    # return {"Prediction": results}
    return {"Prediction": [detection_model.censorUrl(image.source) for image in images]}
    