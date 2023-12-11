"""
Примеры вызова службы:
    service: python_script.exec
    data:
        cache: false
        file: /config/python_scripts/create_matrix_pic.py
        media_player: media_player.yandex_station_komnata
        name_sensor: ентити будущего сенсора, например picpic ( не обзятельно, если нету, то entity media_player )
        length: 32 - длина иконки, по умолчанию 8

    service: python_script.exec
    data:
        cache: false
        file: /config/python_scripts/create_matrix_pic.py
        url_picture: https://bipbap.ru/wp-content/uploads/2017/04/priroda_kartinki_foto_03.jpg
        name_sensor: ентити будущего сенсора, например picpic ( не обзятельно, если нету, то последняя группа слов после / в url_pic )
        length: 32 - длина иконки, по умолчанию 8

После успешного выполнения будет создан sensor c входным name_sensor или заменой описанной выше + _8x8_pic, данные матрицы в атрибуте led_matrix, общий цвет aggregate_rgb
"""

import numpy as np
from PIL import Image
import requests
from io import BytesIO


media_player = data.get("media_player", None)
url_picture = data.get("url_picture", None)
name_sensor = data.get("name_sensor", None)
length = int(data.get("length", 8))

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
img_agg = img

# Ensure the image is in RGB format
if img.mode != "RGB":
    img = img.convert("RGB")

# Resize the image to 8x8 or 32x8
img = img.resize((length, 8))
img_aggregate = img_agg.resize((1, 1))

# Convert the image data to a numpy array
img_data = np.array(img)
img_data_aggregate = np.array(img_aggregate)

# Assemble components into RGB565 uint16 image
led_matrix = (img_data[...,0]>>3).astype(np.uint16) << 11 | (img_data[...,1]>>2).astype(np.uint16) << 5 | (img_data[...,2]>>3).astype(np.uint16)

# Flatten the numpy array to a 1D list
led_matrix = led_matrix.flatten().tolist()
# led_matrix_agg_rgb = img_data_agg_rgb.astype(np.uint16)
aggregate_rgb = img_data_aggregate.astype(np.uint8).flatten().tolist()


attributes = {"led_matrix": led_matrix, "aggregate_rgb": aggregate_rgb,}
logger.warning(f"create_matrix_pic.py: aggregate_rgb: {aggregate_rgb}   led_matrix: {led_matrix}")
hass.states.set(f"sensor.{name_sensor}_8x8_pic", "on", attributes)
