from homeassistant.components.recorder.statistics import statistics_during_period
from homeassistant.util import dt as dt_util

start_time_str = data.get('start_time')
end_time_str = data.get('end_time')
date_format = data.get('date_format', None)
units = None # {"energy": "kWh"}
if start_time := dt_util.parse_datetime(start_time_str):
        start_time = dt_util.as_utc(start_time)
if end_time_str:
    if end_time := dt_util.parse_datetime(end_time_str):
        end_time = dt_util.as_utc(end_time)
else:
    end_time = None
result = statistics_during_period(
        hass,
        start_time,
        end_time,
        data.get('statistic_ids'),
        data.get('period'),
        units,
        data.get('types'),
    )
if date_format not in [None, "None"]:
    for datalists in result:
        for datalist in result[datalists]:
            for key, value in datalist.items():
                if key in ["start", "end"]:
                    ttm = dt_util.utc_from_timestamp(value)
                    datalist[key] = dt_util.as_local(ttm).strftime(date_format)
            del key
            del value
            del datalist
        del datalists
del start_time_str
del end_time_str
del end_time
del units
del date_format
del data
