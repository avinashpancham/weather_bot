import os


def get_secret_from_file(secret: str) -> str:
    with open(os.environ[secret], 'r') as file:
        return file.read()
