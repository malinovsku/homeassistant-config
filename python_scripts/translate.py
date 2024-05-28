"""
    service: python_script.exec
    data:
        file: /config/python_scripts/translate.py
        string: Hello
"""
from googletrans import Translator

try:
    string = data['string']
    string = Translator().translate(string, dest='ru').text
except Exception as err:
    error = f"Произошла ошибка при переводе: {string}. ERROR: {err}"
    logger.error(error)
