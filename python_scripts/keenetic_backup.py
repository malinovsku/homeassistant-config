import requests
import hashlib

ip_default = "192.168.1.1"   # если не указан параметр "ip" при вызове скрипта
folder_default = "./"   # если не указан параметр "folder_bk" при вызове скрипта
login_default = "admin"     # если не указан параметр "login" при вызове скрипта
passw_default = "admin"    # если не указан параметр "passw" при вызове скрипта
name_file_default = "startup-config"    # если не указан параметр "name_file" при вызове скрипта

url = f"http://{data.get('ip', ip_default)}"
folder_bk = data.get('folder_bk', folder_default)
login = data.get('login', login_default)
passw = data.get('passw', passw_default)
name_file = data.get('name_file', name_file_default)

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
