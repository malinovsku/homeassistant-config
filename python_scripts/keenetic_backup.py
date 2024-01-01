'''
*Параметры в data, кроме file, не обязательны, их default расписаны ниже с комментариями

service: python_script.exec
data:
    file: /config/python_scripts/keenetic_backup.py
    ip: "192.168.1.1"
    folder_bk: "./"
    login: "admin"
    passw: "admin"
    name_file: "startup-config"
'''

import requests
import hashlib

url = f"http://{data.get('ip', '192.168.1.1')}" # ip адрес - '192.168.1.1' , если не указан параметр "ip" при вызове скрипта
folder_bk = data.get('folder_bk', './') # папка для сохранения - './' , если не указан параметр "folder_bk" при вызове скрипта
login = data.get('login', 'admin') # логин - 'admin', если не указан параметр "login" при вызове скрипта
passw = data.get('passw', 'admin') # пароль - 'admin', если не указан параметр "passw" при вызове скрипта
name_file = data.get('name_file', 'startup-config') # имя файла - 'startup-config', если не указан параметр "name_file" при вызове скрипта

seskeen = requests.session()    
response_ver = seskeen.get(f"{url}/auth")
md5 = login + ":" + response_ver.headers["X-NDM-Realm"] + ":" + passw
md5 = hashlib.md5(md5.encode('utf-8'))
sha = response_ver.headers["X-NDM-Challenge"] + md5.hexdigest()
sha = hashlib.sha256(sha.encode('utf-8'))
response_auth = seskeen.post(f"{url}/auth", json={"login": login, "password": sha.hexdigest()})
response_data = seskeen.get(f"{url}/ci/startup-config")
seskeen.close()

with open(f"{folder_bk}/{name_file}.txt", "wb") as file_backup:
    file_backup.write(response_data.content)
