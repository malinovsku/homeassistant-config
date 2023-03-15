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
 4) Должна быть установлена интеграция [frigate-hass-integration](https://github.com/blakeblackshear/frigate-hass-integration), так как ее объект камеры используется для выбора.
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

