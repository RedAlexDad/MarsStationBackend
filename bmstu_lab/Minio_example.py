from minio import Minio
import os
from pathlib import Path

# Установка соединения
client = Minio(
    # адрес сервера
    endpoint="192.168.1.53:9000",
    # логин админа
    access_key='minioadmin',
    # пароль админа
    secret_key='minioadmin',
    # опциональный параметр, отвечающий за вкл/выкл защищенное TLS соединение
    secure=False
)


# Управление бакетами

## Для создания бакета используется функция make_buсket:
# def add_new_bucket(name: str):
#     client = Minio(
#         endpoint='play.min.io:9000',
#         access_key='minio',
#         secret_key='minio124'
#     )
#     # создание бакета
#     client.make_bucket(bucket_name=name)


## Другие функции для манипуляции бакетами:
# Для создания бакета
BUCKET_NAME = 'mars'

# add_new_bucket(BUCKET_NAME)

# возвращает список всех бакетов
list = client.list_buckets()
print(list)

# проверяет существование бакета с данным названием
# возвращает true или false
info_bucket = client.bucket_exists(BUCKET_NAME)
if(info_bucket):
    print(f'Бакет "{BUCKET_NAME}" существует, {info_bucket}')
else:
    print(f'Бакет "{BUCKET_NAME}" не существует, {info_bucket}')

# удаление бакета
# client.remove_bucket(BUCKET_NAME)


# Управление объектами

# запись объекта в хранилище из файла
# client.fput_object(
#     # необходимо указать имя бакета,
#     bucket_name=BUCKET_NAME,
#     # имя для нового файла в хринилище
#     object_name='new_object_name',
#     # и путь к исходному файлу
#     file_path='/files/your_file'
# )

BASE_DIR = Path(__file__).resolve().parent.parent

# выгрузка объекта из хранилища в ваш файл
client.fget_object(
    # необходимо указать имя бакета,
    bucket_name=BUCKET_NAME,
    # имя файла в хранилище
    object_name='Фарсида.jpg',
    # и путь к файлу для записи
    file_path=f'{BASE_DIR}/database/Фарсида.jpg'
)

# пример записи строковых данных в хранилище через поток
import io

# перевод из строки в поток
str_io_object = io.StringIO('some data in string format')
# считывание потока
data_stream = str_io_object.read().encode('utf8')
# байтовые данные
data_bytes = b'some data in bytes format'
client.put_object(
    bucket_name=BUCKET_NAME,
    object_name='filename',
    data=data_stream,
    # data=data_bytes,
    length=len(data_stream)
    # length=len(data_bytes)
)

# пример считывания данных из хранилища через объект
data_object = client.get_object(bucket_name=BUCKET_NAME, object_name='filename')
# данный метод возвращает urllib3.response.HTTPResponse object
# для получения самих данных необходимо обратиться к атрибуту data
data = data_object.data  # в некоторых случаях придется использовать data_object.data.decode()
print(data)
