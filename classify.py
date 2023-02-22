import os
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np

from PIL import Image
from io import BytesIO

from utils import is_supported_file_type, is_url_or_data_uri, is_valid_url
from utils import download_image_url, decode_data_uri, is_data_uri_image


MODEL_NAME = "nudeny-classifier.hdf5"
MODEL_DIR = ".\models\classification"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)


class NudenyClassify:
    def __init__(self):
        self.model = load_model(MODEL_PATH)

    def classify(self, file, filename):
        """
        Classifies an image file

        Args:
            file (<class 'bytes'>): Image file.
            filename (str): Image filename.

        Returns:
            dict: Returns a dictionary with filename as a key and 
            prediction class as value.
        """
        if not is_supported_file_type(file):
            return {filename: "invalid-file-type"}

        img = Image.open(BytesIO(file))

        if filename.endswith('.png'):
            img = img.convert('RGB')

        img_input = tf.image.resize(img, (224, 224))
        resized_img = np.expand_dims(img_input, 0)
        prediction = self.model.predict_on_batch(resized_img).flatten()
        max_index = np.argmax(prediction)
        if (max_index == 0):
            return {
                "filename": filename,
                "class": "nude"
            }
        elif (max_index == 2):
            return {
                "filename": filename,
                "class": "sexy"
            }
        else:
            return {
                "filename": filename,
                "class": "safe"
            }

    def classifyUrl(self, source):
        """
        Classifies an image URL or data URI source.

        Args:
            source (str): Image source.

        Returns:
            dict: Returns a dictionary with filename as a key and 
            prediction class as value.
        """
        source_type = is_url_or_data_uri(source)
        if source_type == "url":
            if not is_valid_url(source):
                return {
                    "source": source,
                    "class": "invalid"
                }
            else:
                bytes_io, type = download_image_url(source)
                img = Image.open(bytes_io)

        elif source_type == "data_uri":
            if not is_data_uri_image(source):
                return {
                    "source": source,
                    "class": "invalid"
                }
            else:
                bytes_io, type = decode_data_uri(source)
                img = Image.open(bytes_io)
        elif source_type == "unknown":
            return {
                "source": source,
                "class": "invalid"
            }

        if type == 'png':
            img = img.convert('RGB')

        img_input = tf.image.resize(img, (224, 224))
        resized_img = np.expand_dims(img_input, 0)
        prediction = self.model.predict_on_batch(resized_img).flatten()
        max_index = np.argmax(prediction)
        if (max_index == 0):
            return {
                "source": source,
                "class": "nude"
            }
        elif (max_index == 2):
            return {
                "source": source,
                "class": "sexy"
            }
        else:
            return {
                "source": source,
                "class": "safe"
            }
