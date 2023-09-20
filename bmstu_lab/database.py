import psycopg2
from prettytable import PrettyTable

class Database():
    # Подключение к БД
    def connect(self):
        try:
            # Подключение к базе данных
            self.connection = psycopg2.connect(
                # connect_timeout=1,
                host='localhost',
                port=5432,
                user='postgres',
                password='postgres',
                database='mars',
            )

            print("[INFO] Успешное подключение к базе данных")

        except Exception as ex:
            print("[INFO] Ошибка при работе с PostgreSQL:", ex)

    # Удаление БД
    def drop_table(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    DROP TABLE geographical_object, transport, location, mars_station, status, employee_organization, employee_space_agency, users CASCADE;
                    """)

            # Подтверждение изменений
            self.connection.commit()
            print("[INFO] Успешно удалены таблицы в базе данных")

        except Exception as ex:
            print("[INFO] Ошибка при работе с PostgreSQL:", ex)

    # Создание таблицы БД и связанные таблицы
    def create_table(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""                             
                    -- Географические объекты
                    CREATE TABLE geographical_object (
                        id SERIAL PRIMARY KEY,
                        type VARCHAR NOT NULL,
                        feature VARCHAR NOT NULL,
                        size INT NULL,
                        describe VARCHAR NULL
                    );
                    
                    -- Транспортом могжет быть: посадочные, марсоходы, марсолеты и т.д.
                    CREATE TABLE transport (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR NOT NULL,
                        type VARCHAR NOT NULL,
                        describe VARCHAR NULL
                    );
                    
                    -- Местоположение
                    CREATE TABLE location (
                        id SERIAL PRIMARY KEY,
                        id_geographical_object INT NOT NULL,
                        id_transport INT NOT NULL,
                        id_mars_station INT NOT NULL,
                        purpose VARCHAR NOT NULL,
                        results VARCHAR NOT NULL
                    );
                    
                    -- Марсианская станция
                    CREATE TABLE mars_station (
                        id SERIAL PRIMARY KEY,
                        landing_date INT NULL,
                        -- Долгота, широта, высота
                        location VARCHAR NOT NULL,
                        id_employee_organization INT NOT NULL,
                        id_employee_space_agency INT NOT NULL,
                        id_status INT NOT NULL
                    );
                    
                    -- Статус
                    -- Note:
                    -- status_task: entered, in operation, completed, canceled, deleted
                    -- status_mission: success/loss/running
                    CREATE TABLE status (
                        id SERIAL PRIMARY KEY,
                        status_task VARCHAR NOT NULL,
                        status_mission VARCHAR NOT NULL
                    );
                    
                    CREATE TABLE employee_organization (
                        id SERIAL PRIMARY KEY,
                        full_name VARCHAR NOT NULL,
                        post VARCHAR NOT NULL,
                        name_organization VARCHAR NOT NULL,
                        address_organization VARCHAR NULL,
                        id_user INT NOT NULL
                    );
                    
                    CREATE TABLE employee_space_agency (
                        id SERIAL PRIMARY KEY,
                        full_name VARCHAR NOT NULL,
                        post VARCHAR NOT NULL,
                        name_space_agency VARCHAR NOT NULL,
                        address_space_agency VARCHAR NULL,
                        id_user INT NOT NULL
                    );
                    
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        login VARCHAR NOT NULL,
                        password VARCHAR NOT NULL,
                        admin BOOLEAN NOT NULL
                    );
                    
                                            -- СВЯЗЫВАНИЕ БД ВНЕШНИМИ КЛЮЧАМИ --
                    ALTER TABLE location
                    ADD CONSTRAINT FR_location_of_geographical_object
                        FOREIGN KEY (id_geographical_object) REFERENCES geographical_object (id);
                    
                    ALTER TABLE location
                    ADD CONSTRAINT FR_location_of_transport
                        FOREIGN KEY (id_transport) REFERENCES transport (id);
                    
                    ALTER TABLE location
                    ADD CONSTRAINT FR_location_of_mars_station
                        FOREIGN KEY (id_mars_station) REFERENCES mars_station (id);
                    
                    ALTER TABLE mars_station
                    ADD CONSTRAINT FR_mars_station_of_status
                        FOREIGN KEY (id_status) REFERENCES status (id);
                    
                    ALTER TABLE mars_station
                    ADD CONSTRAINT FR_mars_station_of_viewer
                        FOREIGN KEY (id_employee_organization) REFERENCES employee_organization (id);
                    
                    ALTER TABLE mars_station
                    ADD CONSTRAINT FR_mars_station_of_employee
                        FOREIGN KEY (id_employee_space_agency) REFERENCES employee_space_agency (id);
                    
                    ALTER TABLE employee_organization
                    ADD CONSTRAINT FR_employee_organization_of_users
                        FOREIGN KEY (id_user) REFERENCES users (id);
                    
                    ALTER TABLE employee_space_agency
                    ADD CONSTRAINT FR_employee_space_agency_of_users
                        FOREIGN KEY (id_user) REFERENCES users (id);
            """)

            # Подтверждение изменений
            self.connection.commit()
            print("[INFO] Успешно созданы таблицы в базе данных")

        except Exception as ex:
            print("[INFO] Ошибка при работе с PostgreSQL:", ex)

    def insert_default_value(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    -- ПОЛЬЗОВАТЕЛЬ (АУТЕНФИКАЦИЯ)
                    INSERT INTO users (login, password, admin) VALUES
                        ('user001', '123456', false),
                        ('user002', '123456', false),
                        ('user003', '123456', true),
                        ('user004', '123456', true);
                    -- СОТРУДНИК ОРГАНИЗАЦИИ (ЗАКАЗЧИК)
                    INSERT INTO employee_organization (full_name, post, name_organization, address_organization, id_user) VALUES
                        ('Джон Гротцингер', 'Профессор геологии, главный ученый миссии марсохода Curiosity', 'Калифорнийский технологический институт (Caltech)', '', 1),
                        ('Сергей Павлович Королев', 'Руководитель', 'Главное управление по ракетостроению и ракетным двигателям (ГУРРД)', '', 2);
                    -- СОТРУДНИК КОСМИЧЕСКОГО АГЕНСТВА (ПРИНИМАЮЩИЙ ЗАКАЗЧИКА)
                    INSERT INTO employee_space_agency (full_name, post, name_space_agency, address_space_agency, id_user) VALUES
                        ('Джеймс М. Бегс', 'Руководитель NASA', 'NASA', '', 3),
                        ('Георгий Тимофеевич Береговой', 'Начальник', 'Межпланетный отдел Центрального научно-исследовательского института машиностроения (ЦНИИмаш) имени академика М. В. Хруничева', '', 4);
                    -- ГЕОГРАФИЧЕСКИЙ ОБЪЕКТ (УСЛУГА)
                    INSERT INTO geographical_object (type, feature, size, describe) VALUES
                        ('Planitia, planitiae', 'Acidalia Planitia', 2300, 'обширная тёмная равнина на Марсе. Размер — около 3 тысяч км, координаты центра — 50° с. ш. 339°. Расположена между вулканическим регионом Тарсис и Землёй Аравия, к северо-востоку от долин Маринера. На севере переходит в Великую Северную равнину, на юге — в равнину Хриса; на восточном краю равнины находится регион Кидония. Диаметр около 3000 км.'),
                        ('Patera, paterae', 'Alba Patera', 530, 'Огромный низкий вулкан, расположенный в северной части региона Фарсида на планете Марс. Это самый большой по площади вулкан на Марсе: потоки извергнутой из него породы прослеживаются на расстоянии как минимум 1350 км от его пика.'),
                        ('Tholus, tholi', 'Albor Tholus', 170, 'Потухший вулкан нагорья Элизий, расположенный на Марсе. Находится к югу от соседних горы Элизий и купола Гекаты. Вулкан достигает 4,5 километров в высоту и 160 километров в диаметре основания.'),
                        ('Planitia, planitiae', 'Amazonis Planitia', 2800, 'Слабоокрашенная равнина в северной экваториальной области Марса. Довольно молода, породы имеют возраст 10-100 млн. лет. Часть этих пород представляют собой застывшую вулканическую лаву.'),
                        ('Terra, terrae', 'Arabia Terra', 5100, 'Большая возвышенная область на севере Марса, которая лежит в основном в четырехугольнике Аравия, но небольшая часть находится в четырехугольнике Маре Ацидалиум. Она густо изрыта кратерами и сильно разрушена.');
                    -- ТРАНСПОРТ (ДОП. ИНФА К УСЛУГЕ)
                    INSERT INTO transport (name, type, describe) VALUES
                        ('Mars Pathfinder Rover (USA)', 'Rover', ''),
                        ('Viking 1 Lander (USA)', 'Spacecraft', ''),
                        ('Viking 2 Lander (USA)', 'Spacecraft', ''),
                        ('Mars 6 Lander (USSR)', 'Spacecraft', ''),
                        ('Mars 2 Lander (USSR)', 'Spacecraft', '');
                    
                    -- СТАТУС (ДЛЯ ЗАЯВКИ)
                    INSERT INTO status (status_task, status_mission) VALUES
                        ('Ввведен', 'Успех'),
                        ('В работе', 'Работает'),
                        ('Завершен', 'Успех'),
                        ('Отменен', 'Потеря'),
                        ('Удален', 'Успех');
                    
                    -- МАРСИАНСКАЯ СТАНЦИЯ (ЗАЯВКА)
                    INSERT INTO mars_station (landing_date, location, id_employee_organization, id_employee_space_agency, id_status) VALUES
                        (1980, '19.26N, 33.25W', 1, 1, 1),
                        (1975, '22.46N, 47.95W', 1, 1, 2),
                        (1975, '47.93N, 133.74E', 1, 1, 3),
                        (1973, '23.92S, 19.45W', 2, 2, 4),
                        (1971, '45.04S, 47E', 2, 2, 5);
                    
                    -- МЕСТОПОЛОЖЕНИЕ (ВСПОМОГАТЕЛЬНАЯ ТАБЛИЦА ДЛЯ М-М УСЛУГА-ЗАЯВКА)
                    INSERT INTO location (id_geographical_object, id_transport, id_mars_station, purpose, results) VALUES
                        (1, 1, 1, 'Исследование', 'Успешное испытание'),
                        (2, 2, 2, 'Исследование', 'Разбился'),
                        (3, 3, 3, 'Исследование', 'Потеря связи'),
                        (4, 4, 4, 'Исследование', 'Разбился'),
                        (5, 5, 5, 'Добыча', 'В процессе');
                    """)

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] location, geografic_object: Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] location, geografic_object: Ошибка при заполнение данных:", ex)

    def insert_geographical_object(self, type, feature, size, describe):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO geographical_object (type, feature, size, describe) VALUES
                            (%s, %s, %s, %s);""",
                    (type, feature, size, describe)
                )

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] [geographical_object] Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] [geographical_object] Ошибка при заполнение данных:", ex)

    def insert_transport(self, name, type, describe):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO transport (name, type, describe) VALUES
                            (%s, %s, %s);""",
                    (name, type, describe)
                )

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] [transport] Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] [transport] Ошибка при заполнение данных:", ex)

    def insert_mars_station(self, landing_date, location, id_employee_organization, id_employee_space_agency, id_status):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO location (landing_date, location, id_employee_organization, id_employee_space_agency, id_status) VALUES
                             (%s, %s, %s, %s, %s);""",
                    (landing_date, location, id_employee_organization, id_employee_space_agency, id_status)
                )

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] [location] Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] [location] Ошибка при заполнение данных:", ex)

    def insert_location(self, id_geographical_object, id_transport, id_mars_station, purpose, results):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO history_movement (id_geographical_object, id_transport, id_mars_station, purpose, results) VALUES
                               (%s, %s, %s, %s, %s);""",
                    (id_geographical_object, id_transport, id_mars_station, purpose, results)
                )

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] [history_movement] Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] [history_movement] Ошибка при заполнение данных:", ex)

    def select_all(self):
        try:
            with self.connection.cursor() as cursor:
                database = {}
                name_table = ['mars_station', 'employee_space_agency', 'employee_organization', 'location', 'geographical_object', 'status', 'users', 'transport']
                database['name_table'] = name_table
                for name in name_table:
                    cursor.execute(f"""SELECT * FROM {name};""")
                    database[name] = cursor.fetchall()
                    # Получим названия колонок из cursor.description
                    database[f'{name}_name_col'] = [col[0] for col in cursor.description]

                return database
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] Ошибка при чтении данных:", ex)

    def print_select_all(self, database):
        data_print = []

        for name in database['name_table']:
            table = PrettyTable()
            table.field_names = database[f'{name}_name_col']
            for row in database[name]:
                table.add_row(row)
            # Выводим таблицу на консоль
            # print(table)
            data_print.append(table)

        return data_print

    def close(self):
        # Закрытие соединения
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто")

    def update_status_delete_geografical_object(self, status_task, id_geografical_object):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE status SET status_task = %s WHERE id = %s;""",
                    (status_task, id_geografical_object)
                )

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] [Status] Данные успешно обновлено")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] [Status] Ошибка при обновление данных:", ex)

    def update_status(self, status_task, status_mission, id_mars_station):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE status SET status_task = %s, status_mission = %s WHERE id = %s;""",
                    (status_task, status_mission, id_mars_station)
                )

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] [Status] Данные успешно обновлено")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] [Status] Ошибка при обновление данных:", ex)
    def get_geografical_object_with_status(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        GO.id,
                        GO.type,
                        GO.feature,
                        GO.describe,
                        GO.url_photo
                    FROM location as L
                    INNER JOIN geographical_object as GO ON L.id_geographical_object = GO.id
                    INNER JOIN mars_station as MS ON L.id_mars_station = MS.id
                    INNER JOIN status as S ON MS.id_status = S.id
                    WHERE S.status_task NOT LIKE ('Удален')
                    """)
                # Получаем данные
                results = cursor.fetchall()
                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] [GeographicalObject] Данные успешно прочитано")

                database = []
                for obj in results:
                    data = {
                        'id': obj[0],
                        'type': obj[1],
                        'feature': obj[2],
                        'describe': obj[3],
                        'url_photo': obj[4],
                    }
                    database.append(data)

                return database
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] [GeographicalObject] Ошибка при чтение данных:", ex)

    def get_locations(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """SELECT
                            L.id,
                            GO.feature,
                            GO.type,
                            T.name,
                            T.type,
                            L.purpose,
                            L.results,
                            S.status_mission,
                            S.status_task
                        FROM location as L
                        INNER JOIN geographical_object as GO ON L.id_geographical_object = GO.id
                        INNER JOIN transport as T ON L.id_transport = T.id
                        INNER JOIN mars_station as MS ON L.id_mars_station = MS.id
                        INNER JOIN status as S ON MS.id_status = S.id;
                    """)
                # Получаем данные
                results = cursor.fetchall()
                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] [Location] Данные успешно прочитано")

                database = []
                for obj in results:
                    data = {
                        'id': obj[0],
                        'feature': obj[1],
                        'type': obj[2],
                        'purpose': obj[3],
                        'results': obj[4],
                        'status_mission': obj[5],
                        'status_task': obj[6],
                    }
                    database.append(data)

                return database
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] [Location] Ошибка при чтение данных:", ex)

    def get_locations_by_id(self, id_geographical_object):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """SELECT
                            L.id,
                            GO.feature,
                            GO.type,
                            T.name,
                            T.type,
                            T.url_photo,
                            L.purpose,
                            L.results,
                            S.status_mission,
                            S.status_task
                        FROM location as L
                        INNER JOIN geographical_object as GO ON L.id_geographical_object = GO.id
                        INNER JOIN transport as T ON L.id_transport = T.id
                        INNER JOIN mars_station as MS ON L.id_mars_station = MS.id
                        INNER JOIN status as S ON MS.id_status = S.id
                        WHERE GO.id = %s;
                    """, (id_geographical_object, )
                )
                # Получаем данные
                results = cursor.fetchall()
                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] [Location] Данные успешно прочитано")

                database = []
                for obj in results:
                    data = {
                        'l_id': obj[0],
                        'go_feature': obj[1],
                        'go_type': obj[2],
                        't_name': obj[3],
                        't_type': obj[4],
                        't_url_photo': obj[5],
                        'l_purpose': obj[6],
                        'l_results': obj[7],
                        'status_mission': obj[8],
                        'status_task': obj[9],
                    }
                    database.append(data)

                return database
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] [Location] Ошибка при чтение данных:", ex)

# DB = Database()
# DB.connect()
# # DB.insert_default_value()
# database = DB.select_all()
# for table in DB.print_select_all(database):
#     print(table)

# database = DB.get_locations()
# print(database)
# DB.close()
