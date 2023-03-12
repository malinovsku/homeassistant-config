## 📸Отправка в телеграм скринов событий Frigate и действия по клавиатуре сообщения
#### Отправляет сообщения с фото события и с возможностью заменить в текущем сообщении фото на видео и обратно по кнопкам. После замены, видео автоматически меняется на фото через указанное время.
**В сообщении доступны кнопки:**
- 📲 Отправить стрим на мобильное приложение.
- ❌ Удалить событие Frigate и сообщение в telegram.
- 📼 Заменить фото на видео.
- 🔚 Заменить видео на фото. 
- 🔄 Обновление текущего сообщения, если не срабатывает возврат.

### **Шаги по установке:**
 1) Установить интеграцию [PythonScriptsPro](https://github.com/AlexxIT/PythonScriptsPro) (необходимо для скрипта замены медиа в телеграм, тк нет такой службы)
 2) Файл frigate_sent_telegram.yaml разместить в папке /config/blueprints/automation
 3) Файл edit_media_telegram.py разместить в папке /config/python_scripts
 4) Добавить как удобно скрипт script.edit_media_telegram указанный ниже
 5) В файле secrets.yaml указать bot_token telegram, для скрипта замены медиа
 6) Добавить rest_command (необходим для удаления события в Frigate)
 7) Перезагрузить Home Assistant
 8) Добавить в Home Assistant автоматизацию, выбрав данный проект frigate_sent_telegram и заполнить необходимые параметры.

```yaml
rest_command:
  delete_event_frigate:
    url: "http://IP_FRIGATE:PORT_FRIGATE/api/events/{{event_id}}"
    method: delete
```

```yaml
script:
    edit_media_telegram:
        alias: "Замена медиа в сообщениях телеграм"
        mode: parallel
        max: 1000
        sequence:
        - service: python_script.exec
          data:
            cache: true
            new_file: '{{new_file}}'
            message_id: '{{message_id}}'
            new_message: '{{new_message}}'
            chat_id: '{{chat_id|default(None)}}'
            button_id: '{{button_id|default(False)}}'
            keyboard: '{{keyboard|default(False)}}'
            file: /config/python_scripts/edit_media_telegram.py
```
<img src="1.png">