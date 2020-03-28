from captcha.image import ImageCaptcha
from werkzeug.wsgi import FileWrapper
from flask import Response
from config import captcha_letters
import random


def _random_string(stringLength):
    """Generate a random string of fixed length """
    return ''.join(random.choice(captcha_letters) for i in range(stringLength))


def captcha_response():
    image = ImageCaptcha()
    answer = _random_string(4)
    data = image.generate(answer)
    file = FileWrapper(data)
    return Response(file, mimetype='image/png'), answer
