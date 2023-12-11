import numpy as np
from PIL import Image
import requests
from io import BytesIO


media_player = data["media_player"]

entity_picture_local = hass.states.get(media_player).attributes['entity_picture_local']


response = requests.get(f"http://homeassistant.local:8123{entity_picture_local}")
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

                # Map the RGB values to 16-bit color values
img_data = img_data * 257
led_matrix = ((img_data[:, :, 0] >> 3) << 11) | ((img_data[:, :, 1] >> 2) << 5) | (img_data[:, :, 2] >> 3)

                # Flatten the numpy array to a 1D list
led_matrix = led_matrix.flatten().tolist()

                # Log the LED matrix
new_attributes = {
                    "album_art": led_matrix,
                }

logger.info(f"Album Art led_matrix: {led_matrix}")
hass.states.set(f"sensor.{media_player.replace('media_player.', '')}_8x8_pic", "on", attributes=new_attributes)
