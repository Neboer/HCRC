import random


def get_code() -> str:
    code = ''.join([
        str(random.randint(0, 9))
        for _ in range(6)
    ])

    return code


def send_code(phone: str, code: str):
    print(phone)
    print(code)
    pass
