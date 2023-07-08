'''
Скрипт для отправки в telegram картинок или видео группой в альбоме, каждая группа разбивается на 10 файлов. Для работы необходимо заполнить token. 
Пример вызова скрипта:

service: python_script.exec
data:
    file: /config/python_scripts/telegram_group_media.py
    send_files: Список путей к файлу или ссылок, пример ['/config/pic/1.png', '/config/pic/2.png']
    chat_id: Чат для отправки

'''
import telegram
import requests
import io

token = "token" #Заменить на свой токен бота

try:
    bot = telegram.Bot(token)
    send_files = data["send_files"]
    chat_id = int(data["chat_id"])
    caption = data.get("caption", None)
    inline_keyboard = data.get("inline_keyboard", False)
    new_file = None
    send_files_groups = []
    n=10
    for i in range(n, len(send_files) + n, n):
        send_files_groups.append(send_files[i-n:i])
    for send_files in send_files_groups:
        media_out = []
        for new_file in send_files:
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
                media_out.append(telegram.InputMediaVideo(media, caption))
            elif new_file.endswith('.jpg') or new_file.endswith('.png') or new_file.endswith('.jpeg'):
                media_out.append(telegram.InputMediaPhoto(media, caption))
            else:
                raise Exception('Расширение файла не определено! Возможно только mp4, jpg, png, jpeg')
        bot.sendMediaGroup(chat_id=chat_id, 
                            media = media_out,
                            timeout=20000)
    script_message = "Успешно отправлена группа медиа в TG"
    script_status = "success"
except Exception as e:
    script_status = "error"
    script_message = f"Ошибка отправки группы медиа в строке {e.__traceback__.tb_lineno}: {type(e).__name__} {e}. Файл: {new_file}"
    logger.error(script_message)

hass.bus.fire("py_script", {"script_name": "telegram_group_media",
                "script_status": script_status,
                "script_message": script_message})
