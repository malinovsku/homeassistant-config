## Скрипт выгружает данные из статистики по выбранным объектам.
Для наглядности создан скрипт statistics_during_period.yaml, в котором можно выбрать через GUI параметры для выгрузки.

Поля "Время окончания" и "Формат времени" необязательные.

Пример запуска напрямую или через скрипт statistics_during_period.yaml
```yaml
  - action: python_script.exec
    data:
      cache: true
      file: /config/python_scripts/statistics.py
      start_time: "{{start_time}}"
      end_time: "{{end_time|default(None)}}"
      statistic_ids: "{{statistic_ids}}"
      period: "{{period}}"
      types: "{{types}}"
      date_format: "{{date_format|default(None)}}"
```
```yaml
  - action: script.statistics_during_period
    data:
      start_time: "2025-03-01 00:00:00"
      statistic_ids:
        - sensor.kyxna_vitaj_power
      period: day
      types:
        - state
      date_format: "%Y-%m-%dT%H:%M:%SZ"
```