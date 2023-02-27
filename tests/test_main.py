import os

import requests

URL = "http://127.0.0.1:8000/"
PATH = "C:/Users/user/Downloads/testing/"

PATHS = [
    PATH+"education.jpg",
    PATH+"png-transparent-spider-man-heroes-download-with-transparent-background-free-thumbnail.png",
    PATH+"K-pop.jpeg",
    PATH+"Fhxmn2eWAAQ4OSr.jfif",
    PATH+"blackbuck.bmp"
]

DATA_URL = [
        {
            "source": "https://filesamples.com/samples/image/jfif/sample1.jfif"
        },
        {
            "source": "https://w7.pngwing.com/pngs/895/199/png-transparent-spider-man-heroes-download-with-transparent-background-free-thumbnail.png"
        },
        {
            "source": "http://digitalcommunications.wp.st-andrews.ac.uk/files/2019/04/JPEG_compression_Example.jpg"
        },
        {
            "source": "https://filesamples.com/samples/image/jpeg/sample_640%C3%97426.jpeg"
        },
        {
            "source": "https://people.math.sc.edu/Burkardt/data/bmp/blackbuck.bmp"
        }
    ]

# Invalid method


def test_classify_method():
    response = requests.get("http://127.0.0.1:8000/classify")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}


def test_classify_url_method():
    response = requests.get("http://127.0.0.1:8000/classify-url")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}


def test_detect_method():
    response = requests.get("http://127.0.0.1:8000/detect")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}


def test_detect_url_method():
    response = requests.get("http://127.0.0.1:8000/detect-url")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}


def test_censor_method():
    response = requests.get("http://127.0.0.1:8000/censor")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}


def test_censor_url_method():
    response = requests.get("http://127.0.0.1:8000/censor-url")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

# Empty Payload


def test_classify_empty():
    response = requests.post("http://127.0.0.1:8000/classify")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": [
                    "body",
                    "files"
                ],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
    }


def test_detect_empty():
    response = requests.post("http://127.0.0.1:8000/detect")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": [
                    "body",
                    "files"
                ],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
    }


def test_censor_empty():
    response = requests.post("http://127.0.0.1:8000/censor")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": [
                    "body",
                    "files"
                ],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
    }

# Empty Sources


def test_classify_url_empty():
    response = requests.post("http://127.0.0.1:8000/classify-url")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": [
                    "body"
                ],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
    }


def test_detect_url_empty():
    response = requests.post("http://127.0.0.1:8000/detect-url")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": [
                    "body"
                ],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
    }


def test_censor_url_empty():
    response = requests.post("http://127.0.0.1:8000/censor-url")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": [
                    "body"
                ],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
    }

# Empty List Sources


def test_classify_url_empty_source():
    response = requests.post("http://127.0.0.1:8000/classify-url", json=[])
    assert response.status_code == 400
    assert response.json() == {"detail": "No source(s) provided."}


def test_detect_url_empty_source():
    response = requests.post("http://127.0.0.1:8000/detect-url", json=[])
    assert response.status_code == 400
    assert response.json() == {"detail": "No source(s) provided."}


def test_censor_url_empty_source():
    response = requests.post("http://127.0.0.1:8000/censor-url", json=[])
    assert response.status_code == 400
    assert response.json() == {"detail": "No source(s) provided."}

# Send valid file types (PNG, JPG/JPEG, BMP, JFIF)


def test_classify():
    files = []
    for path in PATHS:
        if not os.path.exists(path):
            raise Exception("Path provided does not exists.")
        files.append(('files', open(path, 'rb')))
    response = requests.post("http://127.0.0.1:8000/classify", files=files)
    assert response.status_code == 200


def test_detect():
    files = []
    for path in PATHS:
        if not os.path.exists(path):
            raise Exception("Path provided does not exists.")
        files.append(('files', open(path, 'rb')))
    response = requests.post("http://127.0.0.1:8000/detect", files=files)
    assert response.status_code == 200


def test_censor():
    files = []
    for path in PATHS:
        if not os.path.exists(path):
            raise Exception("Path provided does not exists.")
        files.append(('files', open(path, 'rb')))
    response = requests.post("http://127.0.0.1:8000/censor", files=files)
    assert response.status_code == 200

# Send valid URL

def test_classify_url():
    response = requests.post("http://127.0.0.1:8000/classify-url", json=DATA_URL)
    assert response.status_code == 200


def test_detect_url():
    response = requests.post("http://127.0.0.1:8000/detect-url", json=DATA_URL)
    assert response.status_code == 200


def test_censor_url():
    response = requests.post("http://127.0.0.1:8000/censor-url", json=DATA_URL)
    assert response.status_code == 200
