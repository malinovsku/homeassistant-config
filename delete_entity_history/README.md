### Скрипт для удаления объектов истории Home Assistant старше N дней, DB Postgres.
Для запуска необходим кастомный компонент PythonScriptsPro https://github.com/AlexxIT/PythonScriptsPro . Скрипт .py необходимо поместить в папку /config/python_scripts 
***
В файле secrets.yaml необходимо прописать настройки:
- password_postgres: password
- user_postgres: user
- host_postgres: host
- port_postgres: port
