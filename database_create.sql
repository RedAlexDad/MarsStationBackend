-- CREATE DATABASE mars;
-- /connect web_mars;
-- DROP DATABASE mars;

-- DROP TABLE geographical_object, transport, location, mars_station, employee CASCADE;

-- Географические объекты
CREATE TABLE geographical_object
(
    id       SERIAL PRIMARY KEY,
    feature  VARCHAR NOT NULL,
    type     VARCHAR NOT NULL,
    size     INT     NULL,
    describe VARCHAR NULL,
    photo    VARCHAR NULL,
    -- Доступен / недоступен
    status   BOOLEAN NOT NULL
);

-- Транспортом могжет быть: посадочные, марсоходы, марсолеты и т.д.
CREATE TABLE transport
(
    id       SERIAL PRIMARY KEY,
    name     VARCHAR NOT NULL,
    type     VARCHAR NOT NULL,
    describe VARCHAR NULL,
    photo    VARCHAR NULL
);

-- Местоположение
CREATE TABLE location
(
    -- Порядковый номер
    id                     SERIAL PRIMARY KEY,
    id_geographical_object INT NOT NULL,
    id_mars_station        INT NOT NULL
);

-- Марсианская станция
CREATE TABLE mars_station
(
    id             SERIAL PRIMARY KEY,
    type_status    VARCHAR NOT NULL,
    date_create    DATE    NOT NULL,
    date_form      DATE    NULL,
    date_close     DATE    NULL,
    id_employee    INT     NULL,
    id_moderator   INT     NULL,
    id_transport   INT     NULL,
    -- СТАТУС (ДЛЯ ЗАЯВКИ)
    -- status_task
    -- 1: Черновик: Заявка только что создана и ожидает обработки.
    -- 2: В работе: Заявка была принята и находится в процессе выполнения.
    -- 3: Завершена: Заявка успешно выполнена.
    -- 4: Отменена: Заявка была отменена по каким-либо причинам.
    -- 5: Удалена: Заявка была удалена из системы.
    -- status_mission
    -- 1: Успех
    -- 2: Потеря
    -- 3: Работает
    status_task    INT     NOT NULL,
    status_mission INT     NOT NULL
);

CREATE TABLE employee
(
    id                SERIAL PRIMARY KEY,
    full_name         VARCHAR NOT NULL,
    post              VARCHAR NOT NULL,
    name_organization VARCHAR NOT NULL,
    address           VARCHAR NULL,
    id_user           INT     NOT NULL
);

-- СВЯЗЫВАНИЕ БД ВНЕШНИМИ КЛЮЧАМИ --
ALTER TABLE location
    ADD CONSTRAINT FR_location_of_geographical_object
        FOREIGN KEY (id_geographical_object) REFERENCES geographical_object (id);

ALTER TABLE location
    ADD CONSTRAINT FR_location_of_mars_station
        FOREIGN KEY (id_mars_station) REFERENCES mars_station (id);

ALTER TABLE mars_station
    ADD CONSTRAINT FR_mars_station_of_transport
        FOREIGN KEY (id_transport) REFERENCES transport (id);

ALTER TABLE mars_station
    ADD CONSTRAINT FR_mars_station_of_employee
        FOREIGN KEY (id_employee) REFERENCES employee (id);

ALTER TABLE mars_station
    ADD CONSTRAINT FR_mars_station_of_moderator
        FOREIGN KEY (id_moderator) REFERENCES employee (id)
;
ALTER TABLE employee
    ADD CONSTRAINT FR_employee_organization_of_users
        FOREIGN KEY (id_user) REFERENCES users (id);