import os
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np

from PIL import Image
from io import BytesIO

from utils import is_supported_file_type

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
            dict: Returns a dictionary with filename as a key and prediction class as value.
        """
        if not is_supported_file_type(file):
            return {filename : "invalid"}

        img = Image.open(BytesIO(file))

        if filename.endswith('.png'):
            img = img.convert('RGB')
        
        img_input = tf.image.resize(img, (224,224))
        resized_img = np.expand_dims(img_input, 0)
        prediction = self.model.predict_on_batch(resized_img).flatten()
        max_index = np.argmax(prediction)
        if(max_index == 0):
            return {filename : "nude"}
        elif(max_index == 2):
            return {filename : "sexy"}
        else:
            return {filename : "safe"}

    