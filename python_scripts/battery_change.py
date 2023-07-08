import yaml
from datetime import datetime

filename = './packages/battery_change_customize.yaml'
new_sensor = True
data_name = data["data_name"]
data_state = data["data_state"] if data.get("data_state", False) else datetime.now().strftime('%d-%m-%Y')
data_battery_type = data.get("data_battery_type", False)

# logger.warning(f"battery_change SERVICE: {data}")
with open(filename) as f:
    doc = yaml.safe_load(f)
for row in doc['homeassistant']['customize']:
    print(doc['homeassistant']['customize'][row])
    if row == data_name:
        doc['homeassistant']['customize'][row]['battery_change'] = data_state
        if data_battery_type:
            doc['homeassistant']['customize'][row]['battery_type'] = data_battery_type
        new_sensor = False
if new_sensor:
    state_upd = {
        data_name: {
            'battery_change': data_state, 
            'battery_type': data_battery_type
        }
    }
    doc['homeassistant']['customize'].update(state_upd)
with open(filename, 'w') as f:
    yaml.safe_dump(doc, f, default_flow_style=False)