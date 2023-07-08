'''
Скрипт отправки картинки hyperion.
Пример вызова скрипта:

service: python_script.exec
data:
        file: /config/python_scripts/hyperion_set_image.py
        file_path: Путь к картинке. Обязательно
        duration: Время задержки в ms установки картинки. Необязательно

'''
import json
import base64
from websocket import create_connection

hyperion_host = "192.168.1.2:8090" # Хост и порт Hyperion
file_path = data["file_path"]
duration = data.get("duration", -1)

# Переводим картинку в формат base64
with open(file_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

# Получаем список instance
ws = create_connection(f"ws://{hyperion_host}/json-rpc")
data = {"command":"serverinfo"}
ws.send(json.dumps(data))
serverinfo = json.loads(ws.recv())
# Проходимся по каждому instance и отправляем картинку
for inst in serverinfo["info"]["instance"]:
    num_instance = inst["instance"]
    if num_instance != 0:
        data_i = {"command" : "instance", 
                    "subcommand" : "switchTo", 
                    "instance" : num_instance}
        ws.send(json.dumps(data_i))
    if inst["running"]:
        # Включаем LED Device
        data_led = {"command":"componentstate",
                    "componentstate":{
                            "component":"LEDDEVICE",
                            "state": True
                            }
                    }
        ws.send(json.dumps(data_led))
        # Отправляем картинку
        data_p = {"command": "image",
                "imagedata": encoded_string, 
                "name": "ha py script",
                "format": "auto",
                "priority": 50,
                "duration": duration,
                "origin": "HA py script"}
        ws.send(json.dumps(data_p))
ws.close()

