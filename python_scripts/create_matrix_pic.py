"""
Примеры вызова службы:
    service: python_script.exec
    data:
        cache: false
        file: /config/python_scripts/create_matrix_pic.py
        media_player: media_player.yandex_station_komnata
        name_sensor: # ентити будущего сенсора, например picpic ( не обзятельно, если нету, то entity media_player )
        length: 32 # длина иконки, по умолчанию 8

    service: python_script.exec
    data:
        cache: false
        file: /config/python_scripts/create_matrix_pic.py
        url_picture: https://bipbap.ru/wp-content/uploads/2017/04/priroda_kartinki_foto_03.jpg
        name_sensor: # ентити будущего сенсора, например picpic ( не обзятельно, если нету, то последняя группа слов после / в url_pic )
        length: 32 # длина иконки, по умолчанию 8

    service: python_script.exec
    data:
        cache: false
        file: /config/python_scripts/create_matrix_pic.py
        media_player: media_player.yandex_station_komnata
        device: koridor_matrix_display
        text: Например шаблон
        screen_time: 10
        lifetime: 5
        default_font: True 
        text_color: # Список цветов текста R G B. Не обязательно
        delta_resize: 2 # Используется при уменьшении картники в цикле, размер изображения делится на данный параметр, пока не достигнет минимума 8\32

*После успешного выполнения будет создан sensor c входным name_sensor или заменой описанной выше + _{length}x8_pic, 
данные матрицы в атрибуте led_matrix, общий цвет aggregate_rgb
**Если в параметрах указан device - имя устройства матрицы, то вместо создания\обновления сенсора, 
будет запускаться сервисы bitmap_small на 8 или bitmap_screen на 32. 
Доступны дополнительные необзятальные параметры text\lifetime\screen_time\default_font\text_color соответсвтенно службам esphome.
"""

import numpy as np
from PIL import Image, ImageFilter
import requests
from io import BytesIO

black_threshold = 150 # Минимальный уровень всех цветов для текста, во избежании черного текста

media_player = data.get("media_player", None)
url_picture = data.get("url_picture", None)
name_sensor = data.get("name_sensor", None)
length = int(data.get("length", 8))
delta_resize = int(data.get("delta_resize", 1)) # Если указана 1, то сразу 64х64 потом 32\8х8
# Переменные для сервисов
device = data.get("device", None)
text = data.get("text", "text")
lifetime = data.get("lifetime", 5)
screen_time = data.get("screen_time", 10)
default_font = data.get("default_font", True)
text_color = data.get("text_color", None)
screen_id = data.get("screen_id", "")
screen_id = f"#{screen_id}" if screen_id != "" else screen_id


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
img = img.filter(ImageFilter.BLUR)
img.thumbnail((img.height, img.width), Image.Resampling.LANCZOS)
img = img.convert("RGB")

if delta_resize != 1:
    while img.height > int(length + length / delta_resize):
        img = img.resize((int(img.height/delta_resize), int(img.width/delta_resize)), Image.Resampling.LANCZOS)
        img = img.filter(ImageFilter.BLUR)
else:
    img.resize((64, 64), Image.Resampling.LANCZOS)
    img = img.filter(ImageFilter.BLUR)

img = img.resize((length, 8), Image.Resampling.LANCZOS)
img_aggregate = img.resize((1, 1), Image.Resampling.LANCZOS)

# Convert the image data to a numpy array
img_data = np.array(img)
img_data_aggregate = np.array(img_aggregate)

# Assemble components into RGB565 uint16 image
led_matrix = (img_data[...,0]>>3).astype(np.uint16) << 11 | (img_data[...,1]>>2).astype(np.uint16) << 5 | (img_data[...,2]>>3).astype(np.uint16)

# Flatten the numpy array to a 1D list
led_matrix = led_matrix.flatten().tolist()
aggregate_rgb = img_data_aggregate.astype(np.uint16).flatten().tolist()

# Color text service
if text_color == None:
    if aggregate_rgb[0] < black_threshold and aggregate_rgb[1] < black_threshold and aggregate_rgb[2] < black_threshold:
        delta = 255 / max(aggregate_rgb)
        text_color = [int(aggregate_rgb[0] * delta), int(aggregate_rgb[1] * delta), int(aggregate_rgb[2] * delta)]
    else:
        text_color = aggregate_rgb

logger.debug(f"create_matrix_pic.py: text_color: {text_color}  aggregate_rgb: {aggregate_rgb}  led_matrix: {led_matrix}")

if device == None:
    attributes = {"led_matrix": led_matrix, "aggregate_rgb": aggregate_rgb, "text_color": text_color,}
    hass.states.set(f"sensor.{name_sensor}_{length}x8_pic", "on", attributes)
else:
    if length == 8:
        hass.services.call('esphome', f'{device}_bitmap_small', {
                            "text": text,
                            "icon": f"{str(led_matrix)}{screen_id}",
                            "lifetime": lifetime,
                            "screen_time": screen_time,
                            "default_font": default_font,
                            "r": text_color[0],
                            "g": text_color[1],
                            "b": text_color[2] })
    else:
        hass.services.call('esphome', f'{device}_bitmap_screen', {
                            "icon": f"{str(led_matrix)}{screen_id}",
                            "lifetime": lifetime,
                            "screen_time": screen_time })
