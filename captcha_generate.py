from captcha.image import ImageCaptcha
from werkzeug.wsgi import FileWrapper
from flask import Response
import string, random


def _random_string(stringLength):
    """Generate a random string of fixed length """
    letters = 'acdefghjkmnprstuwxy1345678'
    return ''.join(random.choice(letters) for i in range(stringLength))


def captcha_response():
    image = ImageCaptcha()
    answer = _random_string(4)
    data = image.generate(answer)
    file = FileWrapper(data)
    return Response(file, mimetype='image/png'), answer
