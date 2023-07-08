'''
Скрипт отправки картинки hyperion. Для очистки\отключения необходимо запустить скрипт без file_path
Пример вызова скрипта:

service: python_script.exec
data:
        file: /config/python_scripts/hyperion_set_image.py
        file_path: Путь к картинке. Обязательно
        duration: Время задержки в ms установки картинки. Необязательно
        run_instance: Массив номеров instance, например [4] или [0,2]. Если не указано, то запсукается на всех. Необязательно
        priority: Приоритет источника hyperion. По умолчанию 50. Необязательно

'''
import json
import base64
from websocket import create_connection

hyperion_host = "192.168.1.2:8090" # Хост и порт Hyperion
file_path = data.get("file_path", False)
duration = data.get("duration", -1)
run_instance = data.get("run_instance", [-1])
priority = data.get("priority", 50)
encoded_string = None

# Переводим картинку в формат base64
if file_path:
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

# Получаем список instance
ws = create_connection(f"ws://{hyperion_host}/json-rpc")
data = {"command":"serverinfo"}
ws.send(json.dumps(data))
serverinfo = json.loads(ws.recv())
# Проходимся по каждому instance и отправляем картинку или очищаем 
for inst in serverinfo["info"]["instance"]:
    num_instance = inst["instance"]
    if num_instance != 0:
        data_i = {"command" : "instance", 
                    "subcommand" : "switchTo", 
                    "instance" : num_instance}
        ws.send(json.dumps(data_i))
    if (inst["running"] and run_instance == [-1]) or (inst["running"] and num_instance in run_instance):
        if file_path:
            # Включаем LED Device
            data_led = {"command":"componentstate",
                        "componentstate":{
                                "component":"LEDDEVICE",
                                "state": True
                                }
                        }
            ws.send(json.dumps(data_led))
            # Пакет для отправки картинки
            data_p = {"command": "image",
                    "imagedata": encoded_string, 
                    "name": "ha py script",
                    "format": "auto",
                    "priority": priority,
                    "duration": duration,
                    "origin": "HA py script"}
        else:
            # Пакет для очистки
            data_p = {"command":"clear",
                    "priority":priority}
        ws.send(json.dumps(data_p))
ws.close()

