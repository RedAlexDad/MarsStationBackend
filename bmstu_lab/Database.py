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
                database='web_mars',
            )

            print("[INFO] Успешное подключение к базе данных")

        except Exception as ex:
            print("[INFO] Ошибка при работе с PostgreSQL:", ex)

    # Удаление БД
    def drop_table(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""DROP TABLE geografic_object, transport, location, history_movement CASCADE;""")

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
                    CREATE TABLE geografic_object (
                        id SERIAL PRIMARY KEY,
                        feature VARCHAR NOT NULL,
                        type VARCHAR NOT NULL,
                        size INT NOT NULL,
                        named_in_year INT NOT NULL,
                        named_for VARCHAR NOT NULL
                    );
                    -- Транспортом могжет быть: посадочные, марсоходы, марсолеты и т.д.
                    CREATE TABLE transport (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR NOT NULL,
                        type_transport VARCHAR NOT NULL,
                        feature VARCHAR NULL,
                        describe VARCHAR NULL
                    );
                    -- Точные местоположения
                    CREATE TABLE location (
                        id SERIAL PRIMARY KEY,
                        id_geografic_object INT NOT NULL,
                        id_transport INT NOT NULL,
                        -- Долгота, широта, высота
                        location VARCHAR NOT NULL,
                        describe VARCHAR NULL
                    );
                    -- История передвижения
                    CREATE TABLE history_movement (
                        id SERIAL PRIMARY KEY,
                        id_begin_location INT NOT NULL,
                        id_end_location INT NOT NULL,
                        begin_data_movement DATE NOT NULL,
                        end_data_movement DATE NOT NULL,
                        distance_traveled FLOAT NOT NULL,
                        purpose VARCHAR NOT NULL,
                        results VARCHAR NOT NULL
                    );
                    
                    
                                            -- СВЯЗЫВАНИЕ БД ВНЕШНИМИ КЛЮЧАМИ --
                    
                    ALTER TABLE location
                    ADD CONSTRAINT FR_location_geografic_object
                        FOREIGN KEY (id_geografic_object) REFERENCES geografic_object (id);
                    
                    ALTER TABLE location
                    ADD CONSTRAINT FR_location_transport
                        FOREIGN KEY (id_transport) REFERENCES transport (id);
                    
                    ALTER TABLE history_movement
                    ADD CONSTRAINT FR_history_movement_begin_location
                        FOREIGN KEY (id_begin_location) REFERENCES location (id);
                    
                    ALTER TABLE history_movement
                    ADD CONSTRAINT FR_history_movement_end_location
                        FOREIGN KEY (id_end_location) REFERENCES location (id);
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
                        INSERT INTO geografic_object (feature, type, size, named_in_year, named_for) VALUES
                            ('Acidalia Planitia', 'Planitia, planitiae', 2300, 1973, 'Classical albedo feature at 44N, 21W'),
                            ('Alba Patera', 'Patera, paterae', 530, 1973, 'Latin, "white region'),
                            ('Albor Tholus', 'Tholus, tholi', 170, 1973, 'Classical albedo feature name'),
                            ('Amazonis Planitia', 'Planitia, planitiae', 2800, 1973, 'Land of the Amazons; on the island Hesperia'),
                            ('Arabia Terra', 'Terra, terrae', 5100, 1979, 'Classical albedo feature name');
                                                
                        INSERT INTO transport (name, type_transport, feature, describe) VALUES
                            ('Mars Pathfinder Rover (USA)', 'Rover', '', ''),
                            ('Mars 2 Lander (USSR)', 'Spacecraft', '', '');
                                                
                        INSERT INTO location (id_geografic_object, id_transport, location, describe) VALUES
                            (1, 1, '46.7N, 22W', ''),
                            (2, 1, '40.4N, 109.6W', ''),
                            (3, 1, '18.8N, 150.4E', ''),
                            (4, 2, '24.8N, 164W', ''),
                            (5, 2, '22.8N, 5E', '');
                                                
                        INSERT INTO history_movement (id, id_begin_location, id_end_location, begin_data_movement, end_data_movement, distance_traveled, purpose, results) VALUES
                            (1, 1, 2, '1996-05-01', '1996-07-20', 100, 'science', 'Landed successfully, operated for just under 3 months'),
                            (2, 3, 4, '1996-05-01', '1996-06-01', 0, 'science', 'Failed during descent. First man-made object on Mars.');
                    """)

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] location, geografic_object: Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] location, geografic_object: Ошибка при заполнение данных:", ex)

    def insert_geografic_object(self, feature, type, size, named_in_year, named_for):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO geografic_object (feature, type, size, named_in_year, named_for) VALUES
                            (%s, %s, %s, %s, %s);""",
                    (feature, type, size, named_in_year, named_for)
                )

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] [geografic_object] Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] [geografic_object] Ошибка при заполнение данных:", ex)

    def insert_transport(self, name, type_transport, feature, describe):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO transport (name, type_transport, feature, describe) VALUES
                            (%s, %s, %s, %s);""",
                    (name, type_transport, feature, describe)
                )

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] [transport] Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] [transport] Ошибка при заполнение данных:", ex)

    def insert_location(self, id_geografic_object, id_transport, location, describe):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO location (id_geografic_object, id_transport, location, describe) VALUES
                             (%s, %s, %s, %s);""",
                    (id_geografic_object, id_transport, location, describe)
                )

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] [location] Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] [location] Ошибка при заполнение данных:", ex)

    def insert_location(self, id_begin_location, id_end_location, begin_data_movement, end_data_movement, distance_traveled, purpose, results):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO history_movement (id_begin_location, id_end_location, begin_data_movement, end_data_movement, distance_traveled, purpose, results) VALUES
                               (%s, %s, %s, %s, %s, %s, %s);""",
                    (id_begin_location, id_end_location, begin_data_movement, end_data_movement, distance_traveled, purpose, results)
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
                name_table = ['geografic_object', 'transport', 'location', 'history_movement']
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

# DB = Database()
# DB.connect()
# # DB.insert_default_value()
# database = DB.select_all()
# for table in DB.print_select_all(database):
#     print(table)
# DB.close()
