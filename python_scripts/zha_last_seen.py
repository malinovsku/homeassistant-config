import json
from websocket import create_connection
from datetime import datetime
from transliterate import translit

access_token = "access_token" #Заменить на свой токен
ha_host = "192.168.1.2:8123" #Заменить на свой хост ха
count_alarm_d = 0
attributes = {}
all_seen_device={}
alarm_device=[]
min_time = 60 * 55 # minutes
min_time_device = ['LUMI', 'xiaomi']
max_time = 60 * 120 # minutes
router_time = 60 * 15 # minutes
now = datetime.now()

try:
    ws = create_connection(f"ws://{ha_host}/api/websocket")
    result =  ws.recv()
    ws.send(json.dumps( {'type': 'auth', 'access_token': access_token} ))
    result = ws.recv()
    ident = 1
    ws.send(json.dumps({'id': ident, 'type': 'zha/devices'}))
    result = ws.recv()
    ws.close()
    json_result = json.loads(result)
    for device in json_result["result"]:
        try:
            last_date = str(device["last_seen"])
            last_dat2 = last_date[:19]
            last_dat3 = datetime.strptime(last_dat2, '%Y-%m-%dT%H:%M:%S')
            diff = (now - last_dat3).seconds
            mark_device = device.get('manufacturer')
            device_type = device["device_type"]
            if device_type != "Coordinator" and \
                ((device_type == 'EndDevice' and ((diff > min_time and min_time_device in mark_device) or diff > max_time)) \
                or (device_type == 'Router' and diff > router_time)):
            # if device["device_type"] != "Coordinator" and diff > max_time:
                count_alarm_d += 1
                status_device = "off"
                alarm_device.append(device["user_given_name"])
            else:
                status_device = "on"
            if device["device_type"] != "Coordinator":
                if device.get('user_given_name') != None:
                    user_given_name = device.get('user_given_name')
                else:
                    user_given_name = device.get('name', 'no_fr_name')
                    user_given_name = user_given_name.replace('_', '', 1)
                user_given_name_en = translit(user_given_name, language_code='ru', reversed=True)
                user_given_name_en = user_given_name_en.replace("'","").replace(' ','_')
                name_sensor_zha_seen = f"binary_sensor.{user_given_name_en}_status_zha"
                attributes_bs={}
                attributes_bs['device_class'] = 'connectivity'
                attributes_bs['device_id'] = device.get('device_reg_id')
                attributes_bs['friendly_name'] = f"{user_given_name} status zha"
                attributes_bs['last_seen'] = last_date
                attributes_bs['model'] = device.get('model')
                attributes_bs['quirk_class'] = device.get('quirk_class')
                self.hass.states.set(name_sensor_zha_seen, status_device, attributes_bs)
                all_seen_device[str(device["user_given_name"])] = f"{divmod(diff, 60)[0]} min"
        except Exception as e:
            self.state = 'unknown'
            pass
            # logger.warning(f"Ошибка ZHA last_seen. {e}")
    attributes['alarm_device'] = alarm_device
    attributes['all_seen_device'] = all_seen_device
    attributes['update_time'] = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
    self.state = count_alarm_d
    self.attributes = attributes
except Exception as e:
    self.state = 'unknown'
    # logger.warning(f"Ошибка ZHA last_seen. {e}")
