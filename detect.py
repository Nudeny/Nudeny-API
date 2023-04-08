from io import BytesIO
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.lite.python.interpreter import Interpreter
import os
import base64
import requests
from dotenv import load_dotenv
import uuid
import boto3
import mimetypes
import imghdr

from utils import is_supported_file_type, is_url_or_data_uri, is_valid_url, is_valid_data_uri
from utils import is_data_uri_image, is_image_url

PATH_TO_SAVED_MODEL = ".\models\detection\EfficientDet2.tflite"
PATH_TO_LABELS = ".\models\detection\labelmap.txt"
min_conf_threshold = 0.5


class NudenyDetect:

    def __init__(self):
        # Load the label map into memory
        with open(PATH_TO_LABELS, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]

        # Load the Tensorflow Lite model into memory
        self.interpreter = Interpreter(model_path=PATH_TO_SAVED_MODEL)
        self.interpreter.allocate_tensors()

        # Get model details
        self.input_details = self.interpreter.get_input_details()

        self.output_details = self.interpreter.get_output_details()
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]

        self.float_input = (self.input_details[0]['dtype'] == np.float32)

        self.input_mean = 127.5
        self.input_std = 127.5

        load_dotenv()
        session = boto3.Session(
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_DEFAULT_REGION')
        )
        self.s3_client = session.client('s3')

    def inference(self, file):
        """
        Detect exposed body parts in an image file

        Args:
            file (<class 'bytes'>): Image file.

        Returns:
            Any: Image with detection
            dict: Detections
        """

        # Load image and resize to expected shape [1xHxWx3]
        img_stream = BytesIO(file)
        img = cv2.imdecode(np.frombuffer(img_stream.read(), np.uint8), 1)
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imH, imW, _ = img.shape
        image_resized = cv2.resize(image_rgb, (self.width, self.height))
        input_data = np.expand_dims(image_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if self.float_input:
            input_data = (np.float32(input_data) -
                          self.input_mean) / self.input_std

        # Perform the actual detection by running the model with the image as input
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()

        # Retrieve detection results
        boxes = self.interpreter.get_tensor(self.output_details[1]['index'])[
            0]  # Bounding box coordinates of detected objects
        classes = self.interpreter.get_tensor(self.output_details[3]['index'])[
            0]  # Class index of detected objects
        scores = self.interpreter.get_tensor(self.output_details[0]['index'])[
            0]  # Confidence of detected objects

        # detections = []

        detections = {
            "female_breast": [],
            "female_genitalia": [],
            "male_genitalia": [],
            "buttocks": []
        }

        for i in range(len(scores)):
            if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):
                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1, (boxes[i][0] * imH)))
                xmin = int(max(1, (boxes[i][1] * imW)))
                ymax = int(min(imH, (boxes[i][2] * imH)))
                xmax = int(min(imW, (boxes[i][3] * imW)))

                object_name = self.labels[int(classes[i])]

                exposed = {
                    "confidence_score": scores[i] * 100,
                    "top": ymin,
                    "left": xmin,
                    "bottom": ymax,
                    "right": xmax
                }
                
                detections[object_name].append(exposed)

        return img.copy(), detections

    def detect(self, file, filename):
        """
        Detect exposed body parts in an image file

        Args:
            file (<class 'bytes'>): Image file.
            filename (str): Filename of the image.
        Returns:
            dict: predictions
        """
        if not is_supported_file_type(file):
            return {
                "filename": filename,
                "exposed_parts": {}
            }

        _, detections = self.inference(file)

        return {
            "filename": filename,
            "exposed_parts": detections
        }

    def detectUrl(self, source):
        """
        Detect exposed body parts in an image URL or data URI

        Args:
            source (str): Image URL or data URI.
        Returns:
            dict: predictions
        """
        source_type = is_url_or_data_uri(source)
        if source_type == "url":
            if not is_valid_url(source):
                return {
                    "source": source,
                    "exposed_parts": {}
                }
            elif not is_image_url(source):
                return {
                    "source": source,
                    "exposed_parts": {}
                }
            else:
                response = requests.get(source)
                if response.status_code != 200:
                    return {
                        "source": source,
                        "exposed_parts": {}
                    }
                file = response.content

        elif source_type == "data_uri":
            if not is_data_uri_image(source):
                return {
                    "source": source,
                    "exposed_parts": {}
                }
            elif not is_valid_data_uri(source):
                return {
                    "source": source,
                    "exposed_parts": {}
                }
            else:
                file = base64.b64decode(source.split(",")[1])
        elif source_type == "unknown":
            return {
                "source": source,
                "exposed_parts": {}
            }

        _, detections = self.inference(file)

        return {
            "source": source,
            "exposed_parts": detections
        }

    def censor(self, file, filename):
        """
        Censor exposed body parts in an image file

        Args:
            file (<class 'bytes'>): Image file.
            filename (str): Filename of the image.
        Returns:
            dict: predictions
        """
        if not is_supported_file_type(file):
            return {
                "filename": filename,
                "url": "",
                "exposed_parts": {}
            }

        censored_image, detections = self.inference(file)

        exposed_count = 0
        for exposed_part in detections.values():
            for prediction in exposed_part:
                exposed_count += 1
                start_point = (int(prediction['left']) - 20, int(prediction['top']) - 20)
                end_point = (int(prediction['right']) + 20, int(prediction['bottom']) + 20)
                censored_image = cv2.rectangle(censored_image, start_point, end_point, (0, 0, 0), -1)

        if exposed_count == 0:
            return {
                "filename": filename,
                "url": "",
                "exposed_parts": {}
            }

        new_filename = str(uuid.uuid4()) + "-" + filename

        # This one is to write into disk and upload to S3 bucket.
        # For this one create a tmp folder in root dir.
        # local_path = os.path.join('tmp', new_filename)
        # cv2.imwrite(local_path, censored_image)

        # with open(local_path, 'rb') as f:
        #     self.s3_client.upload_file(f, "nudeny-storage", new_filename)

        # os.remove(local_path)

        image_type = imghdr.what(file="", h=file)
        success, encoded_image = cv2.imencode("."+image_type, censored_image)

        if not success:
            raise Exception("Failed to encode image")
        self.s3_client.upload_fileobj(BytesIO(encoded_image), "nudeny-storage", new_filename, ExtraArgs={
            'ContentType': 'image/'+image_type})

        return {
            "filename": filename,
            "url": "https://nudeny-storage.s3.ap-southeast-1.amazonaws.com/{}".format(new_filename),
            "exposed_parts": detections
        }
    
    def censorUrl(self, source):
        """
        Censor exposed body parts in an image URL or data URI

        Args:
            source (str): Image URL or data URI.
        Returns:
            dict: predictions
        """
        source_type = is_url_or_data_uri(source)
        if source_type == "url":
            if not is_valid_url(source):
                return {
                    "source": source,
                    "exposed_parts": {}
                }
            elif not is_image_url(source):
                return {
                    "source": source,
                    "exposed_parts": {}
                }
            else:
                response = requests.get(source)
                if response.status_code != 200:
                    return {
                        "source": source,
                        "exposed_parts": {}
                    }
                file = response.content

        elif source_type == "data_uri":
            if not is_data_uri_image(source):
                return {
                    "source": source,
                    "exposed_parts": {}
                }
            elif not is_valid_data_uri(source):
                return {
                    "source": source,
                    "exposed_parts": {}
                }
            else:
                file = base64.b64decode(source.split(",")[1])
        elif source_type == "unknown":
            return {
                "source": source,
                "exposed_parts": {}
            }

        censored_image, detections = self.inference(file)

        exposed_count = 0
        for exposed_part in detections.values():
            for prediction in exposed_part:
                exposed_count += 1
                start_point = (int(prediction['left']) - 20, int(prediction['top']) - 20)
                end_point = (int(prediction['right']) + 20, int(prediction['bottom']) + 20)
                censored_image = cv2.rectangle(censored_image, start_point, end_point, (0, 0, 0), -1)

        if exposed_count == 0:
            return {
                "source": source,
                "url": "",
                "exposed_parts": {}
            }

        image_type = imghdr.what(file="", h=file)

        if image_type == None:
            content_type = response.headers.get('Content-Type')
            if content_type is not None:
                image_type = mimetypes.guess_extension(content_type.split(';')[0])[1:]
            else:
                print("Content type not found in headers")

        new_filename = str(uuid.uuid4()) + "." + image_type
        success, encoded_image = cv2.imencode("."+image_type, censored_image)

        if not success:
            raise Exception("Failed to encode image")

        self.s3_client.upload_fileobj(BytesIO(encoded_image), "nudeny-storage", new_filename, ExtraArgs={
            'ContentType': 'image/'+image_type})

        return {
            "source": source,
            "url": "https://nudeny-storage.s3.ap-southeast-1.amazonaws.com/{}".format(new_filename),
            "exposed_parts": detections
        }

