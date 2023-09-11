import psycopg2

class Database():
    # Подключение к БД
    def connect(self):
        try:
            # Подключение к базе данных
            self.connection = psycopg2.connect(
                host=5432,
                user='postgresql',
                password='postgresql',
                database='web_mars',
                connect_timeout=1
            )

            print("[INFO] Успешное подключение к базе данных")

        except Exception as ex:
            print("[INFO] Ошибка при работе с PostgreSQL:", ex)

    # Удаление БД
    def drop_table(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                DROP TABLE geografic_object CASCADE;
                DROP TABLE transport CASCADE;
                DROP TABLE location CASCADE;
                DROP TABLE history_movement CASCADE;
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
                    CREATE TABLE geografic_object (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR,
                        type_locality VARCHAR,
                        describe VARCHAR
                    );

                    CREATE TABLE transport (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR,
                        type_transport VARCHAR,
                        feature VARCHAR,
                        describe VARCHAR
                    );

                    CREATE TABLE location (
                        id SERIAL PRIMARY KEY,
                        id_geografic_object INT,
                        id_transport INT,
                        date_arrival DATE,
                        location VARCHAR,
                        describe VARCHAR
                    );

                    CREATE TABLE history_movement (
                        id SERIAL PRIMARY KEY,
                        id_begin_location INT,
                        id_end_location INT,
                        begin_data_movement DATE,
                        end_data_movement DATE,
                        distance_traveled FLOAT,
                        purpose VARCHAR
                    );


                                            -- СВЯЗЫВАНИЕ БД ВНЕШНИМИ КЛЮЧАМИ --
                    ALTER TABLE geografic_object
                    ADD CONSTRAINT FR_geografic_object_location
                        FOREIGN KEY (id) REFERENCES location (id);

                    ALTER TABLE transport
                    ADD CONSTRAINT FR_transport_location
                        FOREIGN KEY (id) REFERENCES location (id);

                    -- [2023-09-11 23:59:57] [42830] ОШИБКА: в целевой внешней таблице "history_movement" нет ограничения уникальности, соответствующего данным ключам
                    -- ALTER TABLE location
                    -- ADD CONSTRAINT FR_location_history_movement
                    -- 	FOREIGN KEY (id_transport) REFERENCES history_movement (id_begin_location, id_end_location);

                    ALTER TABLE history_movement
                    ADD CONSTRAINT unique_movement_locations
                        UNIQUE (id_begin_location, id_end_location);
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
                        INSERT INTO location (id_geografic_object, id_transport, date_arrival, location, describe) VALUES
                            (0, 0, '2023-05-20', '14.57S, 175.47E', 'Landed successfully in January of 2004, operated for just over 6 years, 2 months'),
                            (1, 1, '2035-01-04', '14.57S, 175.47E', 'Landed successfully in January of 2004, operated for just over 6 years, 2 months'),
                            (2, 2, '2020-10-01', '14.57S, 175.47E', 'Landed successfully in January of 2004, operated for just over 6 years, 2 months'),
                            (3, 3, '2009-03-11', '14.57S, 175.47E', 'Landed successfully in January of 2004, operated for just over 6 years, 2 months'),
                            (4, 4, '2001-12-23', '14.57S, 175.47E', 'Landed successfully in January of 2004, operated for just over 6 years, 2 months');

                        INSERT INTO geografic_object (name, type_locality, describe) VALUES
                            ('Копрат', 'Каньоны', 'обширная равнина на Марсе, расположенная в южном полушарии планеты. Известна своими бескрайними песчаными дюнами и кратерами, а также редкими признаками водной активности в прошлом. В районе Копрата были обнаружены остатки каналов и дренажных систем, которые свидетельствуют о том, что здесь могла быть жизнь в прошлом. Также на этой равнине были обнаружены следы космических аппаратов, отправленных для исследования Марса.'),
                            ('Маринер', 'Долина', 'долина на Марсе, которая была открыта и изучена зондами Маринер 9 и Викинг в 1970-х годах. Она находится на северном полушарии планеты и протянулась на более чем 4000 км. Долина Маринер считается одним из самых больших каньонов в Солнечной системе. Ее ширина достигает 200 км, а глубина - 4 км. Изучение долины Маринер помогло ученым понять, как формируются каньоны на планетах и какие процессы приводят к изменению ландшафта на Марсе'),
                            ('Фарсида', 'Равнины', 'кратер на Марсе диаметром около 100 км, расположенный в районе Южного полюса планеты. В кратере Фарсида обнаружены следы ледяных образований, которые могут свидетельствовать о наличии подземных водных ресурсов на Марсе'),
                            ('Ксанфа', 'Земля', 'кратер на Марсе диаметром около 170 км, расположенный в районе Эдомского плато. В кратере Ксанфа обнаружены следы ледяных образований и многочисленные каньоны, которые свидетельствуют о том, что здесь могла быть водная активность в прошлом'),
                            ('Мелас', 'Расщелины', 'кратер на Марсе диаметром около 90 км, расположенный в районе Хребта Терберг. В кратере Мелас обнаружены следы ледяных образований и дренажных систем, которые свидетельствуют о том, что здесь могла быть жизнь в прошлом');

                    """)

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] location, geografic_object: Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] location, geografic_object: Ошибка при заполнение данных:", ex)

    def close(self):
        # Закрытие соединения
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто")

DB = Database()
DB.connect()
DB.insert_default_value()
DB.close()