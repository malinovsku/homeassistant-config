# service: python_script.exec
# data:
#   cache: false
#   file: /config/python_scripts/create_matrix_pic.py
#   media_player: media_player.yandex_station_komnata


# service: python_script.exec
# data:
#   cache: false
#   file: /config/python_scripts/create_matrix_pic.py
#   url_pic: https://bipbap.ru/wp-content/uploads/2017/04/priroda_kartinki_foto_03.jpg
#   name_pic: ентити будущего сенсора, например picpic ( не обзятельно, если нету, то последняя группа слов после / в url_pic )

import numpy as np
from PIL import Image
import requests
from io import BytesIO


media_player = data.get("media_player", None)
url_pic = data.get("url_pic", None)

if media_player != None:
    entity_picture_local = name1 = hass.states.get(media_player).attributes['entity_picture_local']
    url_pic = f"http://localhost:8123{entity_picture_local}"
else:
    media_player = data.get("name_pic", url_pic.split('/')[len(url_pic.split('/'))-1].replace('.', '_'))

response = requests.get(url_pic)
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

# Log the LED matrix
new_attributes = {"led_matrix": led_matrix,}

logger.debug(f"create_matrix_pic.py: {led_matrix}")
hass.states.set(f"sensor.{media_player.replace('media_player.', '')}_8x8_pic", "on", attributes=new_attributes)
