import requests
import hashlib

url = 'http://192.168.1.1'
login="admin"
passw="admin"
folder_bk = "./"

seskeen = requests.session()    
response = seskeen.get(f"{url}/auth")
md5 = login + ":" + response.headers["X-NDM-Realm"] + ":" + passw
md5 = hashlib.md5(md5.encode('utf-8'))
sha = response.headers["X-NDM-Challenge"] + md5.hexdigest()
sha = hashlib.sha256(sha.encode('utf-8'))
response_auth = seskeen.post(f"{url}/auth", json={"login": login, "password": sha.hexdigest()})
response = seskeen.get(f"{url}/ci/startup-config", json={"login": login, "password": sha.hexdigest()})
seskeen.close()

with open(f"{folder_bk}/startup-config.txt", "wb") as file_backup:
    file_backup.write(response.content)
