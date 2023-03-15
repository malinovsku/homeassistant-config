import json
import psycopg2

status_script = "running"
hass.services.call('input_text', 'set_value', 
        { "value": status_script , "entity_id": "input_text.delete_entity_history_status"} )

try:
        ### Получаем секретные данные
        with open('/config/secrets.yaml') as f:
                for line in f:
                        if line.split(":")[0] == "password_postgres":
                                password_postgres = line.replace("password_postgres: ","").replace("\n","").replace(" ","")
                        if line.split(":")[0] == "user_postgres":
                                user_postgres = line.replace("user_postgres: ","").replace("\n","").replace(" ","")
                        if line.split(":")[0] == "host_postgres":
                                host_postgres = line.replace("host_postgres: ","").replace("\n","").replace(" ","")
                        if line.split(":")[0] == "port_postgres":
                                port_postgres = line.replace("port_postgres: ","").replace("\n","").replace(" ","")

        ### Подключение к базе
        conn = psycopg2.connect(dbname='homeassistant', user=user_postgres,
                                password=password_postgres, host=host_postgres, port=port_postgres)
        cursor = conn.cursor() 

        ### Входные данные
        d_entity = []
        if data.get("d_entity") != 0:
                if (isinstance(data["d_entity"]['entity_id'], list)):
                        for row in data["d_entity"]['entity_id']:
                                d_entity.append(row)
                else:
                        d_entity.append(data["d_entity"]['entity_id'])

        d_text = data.get("d_text", None)
        d_day = str(data.get("d_day", 30))
        d_del_attr = str(data.get("d_del_attr", False))
        povtor = 1


        ### Если заполнен поиск по совпадениям с именем
        if d_text:
                y_entity = ''
                for row in d_text:
                        y_entity += "entity_id LIKE '" + row.replace("*", "%") + "' OR "
                y_entity = y_entity[:-3]

                cursor.execute('SELECT DISTINCT entity_id FROM homeassistant.states WHERE ' + str(y_entity) )
                rez_text = cursor.fetchall()
                ### Добавляем в найденые имена по совпадению
                for row in rez_text:
                        d_entity.append(row[0])

        ### Формируем строчку из имен для запроса
        new_d_entity = ""
        for row in d_entity:
                new_d_entity += "'"+str(row)+"'"+","
        new_d_entity = new_d_entity[:-1]
        logger.warning("обекты на удаление  =  " + str(new_d_entity) )

        ### Удаление
        if len(d_entity) != 0:
                ### Запрос сколько всего записей для расчета в конце удаленных
                cursor.execute("SELECT COUNT(*) AS count FROM homeassistant.states;")
                start_count = cursor.fetchone()

                while povtor < 50:
                        povtor += 1
                        cursor.execute('SELECT event_id,state_id FROM homeassistant.states WHERE entity_id IN (' + new_d_entity +  ') AND last_updated::date <= now()::date - ' + d_day +  ' ORDER BY last_updated ASC LIMIT 80000;')
                        resultat = cursor.fetchall()

                        ### проверка на необходимость удаления
                        if not resultat:
                                povtor = 51
                                break
                        if len(resultat) < 70000:
                                povtor = 51

                        ### формируем строчку из ИД состояний и событий
                        resu_s = ""
                        resu_e = ""
                        for row in resultat:
                                resu_s += "'"+str(row[1])+"'"+","
                                resu_e += "'"+str(row[0])+"'"+","
                        resu_s = resu_s[:-1]
                        resu_e = resu_e[:-1]

                        ### Изменение записи удаление OLD states
                        cursor.execute( "UPDATE homeassistant.states SET old_state_id=null WHERE old_state_id IN (%s)" % (resu_s))
                        conn.commit()

                        ### Удаление из таблицы событий
                        cursor.execute("DELETE FROM homeassistant.events WHERE event_id IN " + "("+resu_e+")")
                        conn.commit()

                        ### Удаление из таблицы состояний
                        cursor.execute("DELETE FROM homeassistant.states WHERE state_id IN " + "("+resu_s+")")
                        conn.commit()


                cursor.execute("SELECT COUNT(*) AS count FROM homeassistant.states;")
                stop_count = cursor.fetchone()

                dell_count = start_count[0] - stop_count[0]
                logger.warning("удалено записей из states    " + str(dell_count))



        ### Удалем утрибуты
        if d_del_attr:
                cursor.execute('SELECT * FROM (SELECT a.attributes_id ,s.state_id FROM homeassistant.state_attributes AS a LEFT JOIN homeassistant.states AS s ON (a.attributes_id = s.attributes_id) ) AS r WHERE r.state_id IS NULL LIMIT 200000;')
                resultat = cursor.fetchall()

                ### формируем строчку из id атрибутов и удаляем
                if resultat:
                        resu_a = ''
                        for row in resultat:
                                resu_a += "'"+str(row[0])+"'"+","
                        resu_a = resu_a[:-1]

                        cursor.execute("DELETE FROM homeassistant.state_attributes WHERE attributes_id IN " + "("+resu_a+")")
                        conn.commit()



        cursor.close()
        conn.close()
        status_script = "complete"

except Exception as msg:
        logger.error("Произошла ошибка при чистке истории  =  " + str(msg) )
        status_script = "error"

hass.services.call('input_text', 'set_value', 
        { "value": status_script , "entity_id": "input_text.delete_entity_history_status"} )
