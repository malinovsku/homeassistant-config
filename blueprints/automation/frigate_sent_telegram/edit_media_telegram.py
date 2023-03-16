from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
import telegram
import requests
import io
from .secrets import get_secret

token = get_secret('bot_token')

try:
        bot = telegram.Bot(token)
        chat_id = data["chat_id"]
        message_id = data["message_id"]
        new_file = data["new_file"]
        caption = data.get("new_message", None)
        button_id = data.get("button_id", False)
        keyboard = data.get("keyboard", False)

        if new_file.startswith("http"):
                req = requests.get(new_file)
                if not req.ok:
                        raise Exception(f'Ошибка! Не найден файл по url: {new_file}')
                media = io.BytesIO(req.content)
        else:
                media = open(new_file, 'rb')
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
        if keyboard:
                inline_kb=[]
                keyboard = keyboard if isinstance(keyboard, list) else [keyboard]
                for row in keyboard:
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
                "name": "Замена медиа в telegram. ",
                "message": f"Результат: {script_message}",
                "entity_id": "script.edit_media_telegram"})

hass.bus.fire("edit_media_telegram", {"script_status": script_status,
                                        "script_message": script_message})

if (button_id):
        show_alert = False if script_status == "success" else True
        hass.services.call('telegram_bot', 'answer_callback_query', {
                        "callback_query_id": button_id,
                        "message": f"{script_message[:200]}",
                        "show_alert": show_alert })
