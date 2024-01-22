"""
    service: python_script.exec
    data:
        cache: false
        file: /config/python_scripts/create_image_base64.py
        img_name: img_name
        img_base64: img_base64
"""
import base64

binary_data = base64.b64decode(data["img_base64"])
with open(data["img_name"], "wb") as f:
    f.write(binary_data)
