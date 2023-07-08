'''
Скрипт для замены медиа в telegram, дополнительно необходима интеграция PythonScriptsPro. Для работы необходимо заполнить token. 
Пример вызова скрипта:

service: python_script.exec
data:
    file: /config/python_scripts/telegram_edit_media.py
    new_file: Путь или ссылка к новому файлу для замены
    message_id: Message_id сообщения в котором необходимо заменить
    new_message: Тест сообщения
    chat_id: Сhat_id чата в котором необходимо заменить
    keyboard: Дополнительно, если необходима клавиатура под файлом, заполняется по стандарту HA
    button_id: Дополнительно, button_id сообщения если необходим ответ в виде уведомления при нажатии на клавиатуру

'''
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
import telegram
import requests
import io

token = "token" #Заменить на свой токен бота

try:
        bot = telegram.Bot(token)
        chat_id = data["chat_id"]
        message_id = data["message_id"]
        new_file = data["new_file"]
        caption = data.get("new_message", None)
        button_id = data.get("button_id", False)
        inline_keyboard = data.get("inline_keyboard", False)

        if new_file.startswith("http"):
                req = requests.get(new_file)
                if not req.ok:
                        raise Exception(f'Ошибка! Не найден файл по url: {new_file}')
                media = io.BytesIO(req.content)
        else:
                with open(new_file, 'rb') as f:
                        media = io.BytesIO(f.read())
        media.seek(0)

        size_file = media.getbuffer().nbytes / (1024*1024)
        if int(size_file) >= 50:
                raise Exception(f'Размер файла превышает 50Мб, составляет: {round(size_file, 2)}Мб')

        if new_file.endswith('.mp4'): 
                media_out = telegram.InputMediaVideo(media, caption)
        elif new_file.endswith('.jpg') or new_file.endswith('.png') or new_file.endswith('.jpeg'):
                media_out = telegram.InputMediaPhoto(media, caption)
        elif new_file.endswith('.gif'):
                media_out = telegram.InputMediaAnimation(media, caption)
        else:
                raise Exception('Расширение файла не определено! Возможно только mp4, jpg, png, jpeg, gif')

        reply_markup = None
        if inline_keyboard:
                inline_kb=[]
                inline_keyboard = inline_keyboard if isinstance(inline_keyboard, list) else [inline_keyboard]
                for row in inline_keyboard:
                        buttons = []
                        for key in row.split(","):
                                if ":/" in key:
                                        label = key.split(":/")[0]
                                        command = key[len(label) + 1 :]
                                        buttons.append(InlineKeyboardButton(label, callback_data=command))
                        inline_kb.append(buttons)
                reply_markup = InlineKeyboardMarkup(inline_kb)

        bot.editMessageMedia(chat_id=int(chat_id), 
                                message_id=message_id, 
                                reply_markup=reply_markup, 
                                media = media_out,
                                timeout=20000)
        script_message = "Успешно заменено медиа в TG"
        script_status = "success"
except Exception as e:
        script_status = "error"
        script_message = f"Ошибка при замене медиа в TG в строке {e.__traceback__.tb_lineno}: {type(e).__name__} {e}. Файл: {new_file}"
        logger.error(script_message)

hass.services.call('logbook', 'log', {
                "name": "📤Telegram замена медиа. ",
                "message": f"Результат: {script_message}",
                "entity_id": "script.telegram_edit_media"})

hass.bus.fire("py_script", {"script_name": "telegram_edit_media",
                        "script_status": script_status,
                        "script_message": script_message})

if (button_id):
        show_alert = False if script_status == "success" else True
        hass.services.call('telegram_bot', 'answer_callback_query', {
                        "callback_query_id": button_id,
                        "message": f"{script_message[:200]}",
                        "show_alert": show_alert })
