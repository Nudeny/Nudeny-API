from urllib.parse import urlparse
from io import BytesIO
import requests
import base64
import imghdr

def is_valid_url(url):
    """
    Checks if URL string is a valid URL.

    Args:
        urls (str): URL string.

    Returns:
        boolean: Returns true if URL is valid, otherwise false.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# def is_image_url(url):
#     """
#     Checks if URL has a content-type of image.

#     Args:
#         urls (str): URL string.

#     Returns:
#         boolean: Returns true if URL has a content-type image and
#         if URL content-type is supported image, otherwise false.
#     """
#     response = requests.get(url)
#     content_type = response.headers['content-type']
#     type = content_type.split('/')[1]
#     if content_type.split('/')[0] != 'image':
#         return False

#     image_types = ['jpg','jpeg','png','bmp', 'jfif']
#     return any(type == image_type for image_type in image_types)

def is_image_url(url):
    """
    Checks if URL has a content-type of image.

    Args:
        urls (str): URL string.

    Returns:
        boolean: Returns true if URL has a content-type image and
        if URL content-type is supported image, otherwise false.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    if '.' in path:
        ext = path.split('.')[-1]
        if ext in ['jpg', 'jpeg', 'png', 'bmp', 'jfif']:
            return True
        else:
            return False
        
    response = requests.head(url)
    content_type = response.headers['content-type']
    type = content_type.split('/')[1]
    if content_type.split('/')[0] != 'image':
        return False

    image_types = ['jpg','jpeg','png','bmp', 'jfif']
    return any(type == image_type for image_type in image_types)

def is_url_or_data_uri(str):
    """
    Checks if the string is URL, data URI or neither.

    Args:
        str (str): String to check.

    Returns:
        string: Returns url, data_uri or unknown.
    """
    if str.startswith("http://") or str.startswith("https://"):
        return "url"
    elif str.startswith("data:"):
        return "data_uri"
    else:
        return "unknown"

def is_data_uri_image(data_uri):
    """
    Checks if the data URI is an image.

    Args:
        data_uri (str): String to check.

    Returns:
        boolean: Returns url, data_uri or unknown.
    """
    if data_uri.startswith("data:image/"):
        image_types = ['jpg','jpeg','png','bmp', 'jfif']
        mime_type = data_uri.split(";")[0][5:]
        return any(mime_type.endswith(image_type) for image_type in image_types)
    else:
        return False

def is_valid_data_uri(data_uri):
    """
    Validate if data URI is a valid base64-encoded string.

    Args:
        uri (str): data URI to decode.

    Returns:
        boolean: Returns True if data_uri is valid, otherwise
        False.
    """
    try:
        base64.b64decode(data_uri.split(",")[1], validate=True)
    except:
        return False
    
    return True


def is_supported_file_type(file):
    """
    Checks if file is a supported file and is an image.

    Args:
        file (<class 'bytes'>): File to check.

    Returns:
        boolean: Returns true if file type is supported and is an image, 
        otherwise false.
    """
    SUPPORTED_FILE_TYPE = ['jpg','jpeg','png','bmp', 'jfif']
    img_type = imghdr.what(file="",h=file)
    if img_type is None:
        return False
    elif img_type not in SUPPORTED_FILE_TYPE:
        return False
    
    return True

def download_image_url(url):
    """
    Download the image URL.

    Args:
        url (str): URL to download.

    Returns:
        BytesIO: BytesIO of the response.content.
        str: The file type of the URL.
        None: If response status code is not equal to 200 (Success)
    """
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        return None, None

    return BytesIO(response.content), response.headers['Content-Type'].split('/')[1]

def decode_data_uri(uri):
    """
    Decode data URI.

    Args:
        uri (str): data URI to decode.

    Returns:
        BytesIO: BytesIO of the decoded data URI.
        str: The file type of the data URI.
    """
    data = base64.b64decode(uri.split(",")[1])
    media_type = uri.split(",")[0]
    type = media_type.split("/")[1].split(";")[0]

    return BytesIO(data), type