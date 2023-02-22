from urllib.parse import urlparse
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
