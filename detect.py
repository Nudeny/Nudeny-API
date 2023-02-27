import warnings
from io import BytesIO
import numpy as np
from object_detection.utils import visualization_utils as viz_utils
import cv2
import tensorflow as tf
import os
import time
import base64
import requests
from dotenv import load_dotenv
import uuid
import boto3

import imghdr

from utils import is_supported_file_type, is_url_or_data_uri, is_valid_url, is_valid_data_uri
from utils import is_data_uri_image, is_image_url

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore')


PATH_TO_SAVED_MODEL = ".\models\detection\saved_model"


class NudenyDetect:

    def __init__(self):
        print('Loading model...', end='')
        start_time = time.time()
        self.detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print('Done! Took {} seconds'.format(elapsed_time))

        load_dotenv()
        session = boto3.Session(
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_DEFAULT_REGION')
        )
        self.s3_client = session.client('s3')

        self.category_index = {1: {'id': 1, 'name': 'buttocks'}, 2: {'id': 2, 'name': 'female_breast'}, 3: {
            'id': 3, 'name': 'female_genitalia'}, 4: {'id': 4, 'name': 'male_genitalia'}}

    def inference(self, file):
        """
        Detect exposed body parts in an image file

        Args:
            file (<class 'bytes'>): Image file.

        Returns:
            Any: Image with detection
            dict: Detections
        """
        img_stream = BytesIO(file)
        img = cv2.imdecode(np.frombuffer(img_stream.read(), np.uint8), 1)
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image_expanded = np.expand_dims(image_rgb, axis=0)
        input_tensor = tf.convert_to_tensor(img)
        input_tensor = input_tensor[tf.newaxis, ...]
        detections = self.detect_fn(input_tensor)

        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy()
                      for key, value in detections.items()}
        detections['num_detections'] = num_detections

        detections['detection_classes'] = detections['detection_classes'].astype(
            np.int64)

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

        image_with_detections, detections = self.inference(file)
        height = image_with_detections.shape[0]
        width = image_with_detections.shape[1]

        # viz_utils.visualize_boxes_and_labels_on_image_array(
        #     image_with_detections,
        #     detections['detection_boxes'],
        #     detections['detection_classes'],
        #     detections['detection_scores'],
        #     self.category_index,
        #     use_normalized_coordinates=True,
        #     max_boxes_to_draw=200,
        #     min_score_thresh=0.5,
        #     agnostic_mode=False)

        exposed_parts = {
            "female_breast": [],
            "female_genitalia": [],
            "male_genitalia": [],
            "buttocks": []
        }

        index = 0
        for scores in detections['detection_scores']:
            if scores >= 0.5:
                bottom = detections['detection_boxes'][index][2] * height
                top = detections['detection_boxes'][index][0] * height

                right = detections['detection_boxes'][index][3] * width
                left = detections['detection_boxes'][index][1] * width

                key = self.category_index[detections['detection_classes']
                                          [index]]['name']
                # exposed_parts[key] = {"confidence_score": scores * 100, "top": int(
                #     top), "left": int(left), "bottom": int(bottom), "right": int(right)}
                exposed_parts[key].append({"confidence_score": scores * 100, "top": int(
                    top), "left": int(left), "bottom": int(bottom), "right": int(right)})
            else:
                break
            index += 1

        return {
            "filename": filename,
            "exposed_parts": exposed_parts
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

        image_with_detections, detections = self.inference(file)
        height = image_with_detections.shape[0]
        width = image_with_detections.shape[1]

        # viz_utils.visualize_boxes_and_labels_on_image_array(
        #     image_with_detections,
        #     detections['detection_boxes'],
        #     detections['detection_classes'],
        #     detections['detection_scores'],
        #     self.category_index,
        #     use_normalized_coordinates=True,
        #     max_boxes_to_draw=200,
        #     min_score_thresh=0.5,
        #     agnostic_mode=False)

        exposed_parts = {
            "female_breast": [],
            "female_genitalia": [],
            "male_genitalia": [],
            "buttocks": []
        }
        index = 0
        for scores in detections['detection_scores']:
            if scores >= 0.5:
                bottom = detections['detection_boxes'][index][2] * height
                top = detections['detection_boxes'][index][0] * height

                right = detections['detection_boxes'][index][3] * width
                left = detections['detection_boxes'][index][1] * width

                key = self.category_index[detections['detection_classes']
                                          [index]]['name']
                # exposed_parts[key] = {"confidence_score": scores * 100, "top": int(
                #     top), "left": int(left), "bottom": int(bottom), "right": int(right)}
                exposed_parts[key].append({"confidence_score": scores * 100, "top": int(
                    top), "left": int(left), "bottom": int(bottom), "right": int(right)})
            else:
                break
            index += 1

        return {
            "source": source,
            "exposed_parts": exposed_parts
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
        height = censored_image.shape[0]
        width = censored_image.shape[1]

        # self.category_index = {1: {'id': 1, 'name': 'buttocks'}, 2: {'id': 2, 'name': 'female_breast'}, 3: {
        #     'id': 3, 'name': 'female_genitalia'}, 4: {'id': 4, 'name': 'male_genitalia'}}

        exposed_parts = {
            "female_breast": [],
            "female_genitalia": [],
            "male_genitalia": [],
            "buttocks": []
        }

        index = 0
        exposed_count = 0
        for scores in detections['detection_scores']:
            if scores >= 0.5:
                exposed_count += 1
                bottom = detections['detection_boxes'][index][2] * height
                top = detections['detection_boxes'][index][0] * height

                right = detections['detection_boxes'][index][3] * width
                left = detections['detection_boxes'][index][1] * width

                start_point = (int(left) - 20, int(top) - 20)
                end_point = (int(right) + 20, int(bottom) + 20)
                censored_image = cv2.rectangle(
                    censored_image, start_point, end_point, (0, 0, 0), -1)

                key = self.category_index[detections['detection_classes']
                                          [index]]['name']

                # exposed_parts[key] = {"confidence_score": scores * 100, "top": int(
                #     top), "left": int(left), "bottom": int(bottom), "right": int(right)}
                exposed_parts[key].append({"confidence_score": scores * 100, "top": int(
                    top), "left": int(left), "bottom": int(bottom), "right": int(right)})
            else:
                break
            index += 1

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
            "exposed_parts": exposed_parts
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
        height = censored_image.shape[0]
        width = censored_image.shape[1]

        exposed_parts = {
            "female_breast": [],
            "female_genitalia": [],
            "male_genitalia": [],
            "buttocks": []
        }
        index = 0
        exposed_count = 0
        for scores in detections['detection_scores']:
            if scores >= 0.5:
                exposed_count += 1
                bottom = detections['detection_boxes'][index][2] * height
                top = detections['detection_boxes'][index][0] * height

                right = detections['detection_boxes'][index][3] * width
                left = detections['detection_boxes'][index][1] * width

                start_point = (int(left) - 20, int(top) - 20)
                end_point = (int(right) + 20, int(bottom) + 20)
                censored_image = cv2.rectangle(
                    censored_image, start_point, end_point, (0, 0, 0), -1)

                key = self.category_index[detections['detection_classes']
                                          [index]]['name']

                exposed_parts[key].append({"confidence_score": scores * 100, "top": int(
                    top), "left": int(left), "bottom": int(bottom), "right": int(right)})
            else:
                break
            index += 1

        if exposed_count == 0:
            return {
                "source": source,
                "url": "",
                "exposed_parts": {}
            }

        new_filename = str(uuid.uuid4())
        image_type = imghdr.what(file="", h=file)
        success, encoded_image = cv2.imencode("."+image_type, censored_image)

        if not success:
            raise Exception("Failed to encode image")

        self.s3_client.upload_fileobj(BytesIO(encoded_image), "nudeny-storage", new_filename, ExtraArgs={
            'ContentType': 'image/'+image_type})

        return {
            "source": source,
            "url": "https://nudeny-storage.s3.ap-southeast-1.amazonaws.com/{}".format(new_filename),
            "exposed_parts": exposed_parts
        }
