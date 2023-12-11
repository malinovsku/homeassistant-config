# service: python_script.exec
# data:
#   cache: false
#   file: /config/python_scripts/create_matrix_pic.py
#   media_player: media_player.yandex_station_komnata
#   name_sensor: ентити будущего сенсора, например picpic ( не обзятельно, если нету, то entity media_player )


# service: python_script.exec
# data:
#   cache: false
#   file: /config/python_scripts/create_matrix_pic.py
#   url_picture: https://bipbap.ru/wp-content/uploads/2017/04/priroda_kartinki_foto_03.jpg
#   name_sensor: ентити будущего сенсора, например picpic ( не обзятельно, если нету, то последняя группа слов после / в url_pic )

# После успешного выполнения будет создан sensor c входным name_sensor или заменой описанной выше + _8x8_pic с данными в атрибуте led_matrix

import numpy as np
from PIL import Image
import requests
from io import BytesIO


media_player = data.get("media_player", None)
url_picture = data.get("url_picture", None)
name_sensor = data.get("name_sensor", None)

if media_player != None:
    entity_picture = hass.states.get(media_player).attributes['entity_picture']
    if not entity_picture.startswith('http'):
        url_picture = f"http://localhost:8123{entity_picture}"
    else:
        url_picture = entity_picture
    name_sensor = name_sensor if name_sensor != None else f"{media_player.replace('media_player.', '')}"
else:
    name_sensor = name_sensor if name_sensor != None else f"{url_picture.split('/')[len(url_picture.split('/'))-1].replace('.', '_')}" 

response = requests.get(url_picture)
img = Image.open(BytesIO(response.content))

img = img.convert("RGB")
img.thumbnail((64, 64), Image.Resampling.LANCZOS)

# Ensure the image is in RGB format
if img.mode != "RGB":
    img = img.convert("RGB")

# Resize the image to 8x8
img = img.resize((8, 8))

# Convert the image data to a numpy array
img_data = np.array(img)

# Assemble components into RGB565 uint16 image
led_matrix = (img_data[...,0]>>3).astype(np.uint16) << 11 | (img_data[...,1]>>2).astype(np.uint16) << 5 | (img_data[...,2]>>3).astype(np.uint16)

# Flatten the numpy array to a 1D list
led_matrix = led_matrix.flatten().tolist()

new_attributes = {"led_matrix": led_matrix,}
logger.debug(f"create_matrix_pic.py: {led_matrix}")
hass.states.set(f"sensor.{name_sensor}_8x8_pic", "on", attributes=new_attributes)
